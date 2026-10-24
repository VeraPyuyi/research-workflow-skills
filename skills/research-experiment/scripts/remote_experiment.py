"""SSH experiment adapter with pinned host keys and Windows credential references."""

import argparse
import base64
import ctypes
from ctypes import wintypes
import getpass
import hashlib
import hmac
import json
import os
from pathlib import Path, PurePosixPath
import shlex
import socket
import stat
import sys
import uuid


def relative_path(value):
    if (not isinstance(value, str) or not value or "\\" in value or "\0" in value
            or PurePosixPath(value).is_absolute()
            or any(part in ("..", ".") for part in value.split("/"))
            or any(not part for part in value.split("/"))):
        raise ValueError("Expected a contained relative path")
    return value


def validate_profile(profile, require_pin=True):
    if not isinstance(profile, dict):
        raise ValueError("Host profile must be an object")
    if any(key in profile for key in ("password", "secret", "token", "private_key", "api_key")):
        raise ValueError("Use a credential reference, never an inline secret")
    for field in ("id", "host", "user"):
        if not isinstance(profile.get(field), str) or not profile[field] or "\0" in profile[field]:
            raise ValueError("Missing host " + field)
    if type(profile.get("port")) is not int or not 1 <= profile["port"] <= 65535:
        raise ValueError("Invalid SSH port")
    root = profile.get("root")
    if (not isinstance(root, str) or not root.startswith("/") or root == "/"
            or ".." in root.split("/") or "\\" in root):
        raise ValueError("Explicit contained server root is required")
    ref = profile.get("credential_ref")
    if not isinstance(ref, str) or not ref.startswith("wincred:research/"):
        raise ValueError("Expected a research Windows Credential Manager reference")
    if require_pin and not str(profile.get("host_key_sha256", "")).startswith("SHA256:"):
        raise ValueError("Read and pin the host key before authentication")
    return profile


class Credential(ctypes.Structure):
    _fields_ = [
        ("Flags", wintypes.DWORD), ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR), ("Comment", wintypes.LPWSTR),
        ("LastWritten", wintypes.FILETIME), ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
        ("Persist", wintypes.DWORD), ("AttributeCount", wintypes.DWORD),
        ("Attributes", ctypes.c_void_p), ("TargetAlias", wintypes.LPWSTR),
        ("UserName", wintypes.LPWSTR),
    ]


def credential_api():
    if os.name != "nt":
        raise ValueError("This credential backend is available only on Windows")
    library = ctypes.WinDLL("Advapi32.dll", use_last_error=True)
    library.CredReadW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                 ctypes.POINTER(ctypes.POINTER(Credential))]
    library.CredReadW.restype = wintypes.BOOL
    library.CredWriteW.argtypes = [ctypes.POINTER(Credential), wintypes.DWORD]
    library.CredWriteW.restype = wintypes.BOOL
    library.CredFree.argtypes = [ctypes.c_void_p]
    return library


def read_credential(reference):
    api = credential_api()
    pointer = ctypes.POINTER(Credential)()
    if not api.CredReadW(reference.removeprefix("wincred:"), 1, 0, ctypes.byref(pointer)):
        raise ValueError("Referenced credential is unavailable")
    try:
        entry = pointer.contents
        return ctypes.string_at(entry.CredentialBlob, entry.CredentialBlobSize).decode("utf-16-le")
    finally:
        api.CredFree(pointer)


def store_credential(reference, username, secret):
    if not reference.startswith("wincred:research/") or not secret:
        raise ValueError("Invalid credential reference or empty credential")
    encoded = secret.encode("utf-16-le")
    blob = (ctypes.c_ubyte * len(encoded)).from_buffer_copy(encoded)
    entry = Credential()
    entry.Type = 1
    entry.TargetName = reference.removeprefix("wincred:")
    entry.UserName = username
    entry.Persist = 2
    entry.CredentialBlobSize = len(encoded)
    entry.CredentialBlob = ctypes.cast(blob, ctypes.POINTER(ctypes.c_ubyte))
    try:
        if not credential_api().CredWriteW(ctypes.byref(entry), 0):
            raise ValueError("Credential Manager rejected the write")
    finally:
        ctypes.memset(blob, 0, len(encoded))


def paramiko_module():
    try:
        import paramiko
        return paramiko
    except ImportError:
        raise ValueError("Install the optional SSH requirements in the active environment")


def fingerprint(key):
    return "SHA256:" + base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode().rstrip("=")


def connect(profile, authenticate=True):
    validate_profile(profile, require_pin=authenticate)
    paramiko = paramiko_module()
    connection = socket.create_connection((profile["host"], profile["port"]), timeout=10)
    transport = paramiko.Transport(connection)
    try:
        transport.start_client(timeout=10)
        observed = fingerprint(transport.get_remote_server_key())
        if authenticate:
            if not hmac.compare_digest(observed, profile["host_key_sha256"]):
                raise ValueError("Server host key changed; authentication was not attempted")
            secret = read_credential(profile["credential_ref"])
            try:
                transport.auth_password(profile["user"], secret, fallback=False)
            finally:
                secret = None
        return transport, observed
    except BaseException:
        transport.close()
        connection.close()
        raise


def mkdirs(sftp, absolute):
    current = ""
    for part in PurePosixPath(absolute).parts:
        if part == "/":
            current = "/"
            continue
        current = current.rstrip("/") + "/" + part
        try:
            info = sftp.lstat(current)
        except FileNotFoundError:
            sftp.mkdir(current, mode=0o700)
            info = sftp.lstat(current)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise ValueError("Remote transfer path is linked or not a directory")


def upload_new(sftp, remote, payload):
    mkdirs(sftp, str(PurePosixPath(remote).parent))
    try:
        info = sftp.lstat(remote)
    except FileNotFoundError:
        info = None
    if info is not None:
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("Remote target is not a regular file")
        with sftp.open(remote, "rb") as stream:
            if stream.read() != payload:
                raise ValueError("Existing different remote content is preserved")
        return
    staging = remote + "." + uuid.uuid4().hex + ".partial"
    try:
        with sftp.open(staging, "wx") as stream:
            stream.write(payload)
        sftp.chmod(staging, 0o600)
        # Standard SFTP rename refuses an existing target; no partial final file.
        sftp.rename(staging, remote)
    finally:
        try:
            sftp.remove(staging)
        except FileNotFoundError:
            pass


def worker_command(transport, profile, action, packet=None, project=None, job=None):
    paramiko = paramiko_module()
    payload = Path(__file__).with_name("remote_worker.py").read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    remote = profile["root"].rstrip("/") + "/.tools/remote-worker-" + digest + ".py"
    with paramiko.SFTPClient.from_transport(transport) as sftp:
        upload_new(sftp, remote, payload)
    args = [profile.get("python", "python3"), remote, action, "--root", profile["root"]]
    if project:
        args.extend(["--project", project])
    if job:
        args.extend(["--job", job])
    with transport.open_session(timeout=15) as channel:
        channel.settimeout(20)
        channel.exec_command(" ".join(shlex.quote(arg) for arg in args))
        if packet is not None:
            channel.sendall(json.dumps(packet, allow_nan=False).encode("utf-8"))
        channel.shutdown_write()
        output = channel.makefile("rb").read()
        code = channel.recv_exit_status()
        if code != 0:
            raise ValueError("Remote action failed; inspect its recorded state before retrying")
        result = json.loads(output)
    return result


def transfer(transport, profile, action, project, local, relative, job=None):
    if not project or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-" for character in project):
        raise ValueError("Invalid project")
    relative_path(project)
    relative = relative_path(relative)
    root = profile["root"].rstrip("/")
    paramiko = paramiko_module()
    with paramiko.SFTPClient.from_transport(transport) as sftp:
        if action == "upload":
            remote = root + "/" + project + "/inputs/" + relative
            source = Path(local)
            if source.is_symlink() or (hasattr(source, "is_junction") and source.is_junction()):
                raise ValueError("Linked input files are not transferred")
            payload = source.read_bytes()
            upload_new(sftp, remote, payload)
            return {"status": "uploaded", "remote": remote,
                    "sha256": hashlib.sha256(payload).hexdigest()}
        if not job:
            raise ValueError("Fetch requires a job identity")
        relative_path(job)
        remote = root + "/" + project + "/runs/" + job + "/" + relative
        current = "/"
        for part in PurePosixPath(remote).parts[1:]:
            current = current.rstrip("/") + "/" + part
            if stat.S_ISLNK(sftp.lstat(current).st_mode):
                raise ValueError("Linked remote output is not fetched")
        target = Path(local)
        if target.exists() or target.is_symlink():
            raise ValueError("Existing local destination is preserved")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as output, sftp.open(remote, "rb") as source:
            while True:
                chunk = source.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
        return {"status": "fetched", "path": str(target),
                "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=[
        "probe-key", "probe", "submit", "status", "cancel",
        "upload", "fetch", "store-credential",
    ])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--host", default="research-shared")
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--project")
    parser.add_argument("--job")
    parser.add_argument("--local", type=Path)
    parser.add_argument("--relative")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    transport = None
    try:
        config = json.loads(args.config.read_text(encoding="utf-8-sig"))
        profile = next(item for item in config["hosts"] if item["id"] == args.host)
        validate_profile(profile, require_pin=args.action not in {"probe-key", "store-credential"})
        packet = json.loads(args.packet.read_text(encoding="utf-8-sig")) if args.packet else None
        if args.action in {"submit", "cancel", "upload", "fetch", "store-credential"} and not args.apply:
            print(json.dumps({"status": "planned", "action": args.action, "executed": False}))
            return 0
        if args.action == "store-credential":
            secret = getpass.getpass("SSH password (stored only in Windows Credential Manager): ")
            store_credential(profile["credential_ref"], profile["user"], secret)
            secret = None
            result = {"status": "stored", "credential_ref": profile["credential_ref"]}
        else:
            transport, observed = connect(profile, authenticate=args.action != "probe-key")
            if args.action == "probe-key":
                result = {"host_key_sha256": observed, "authenticated": False}
            elif args.action in {"upload", "fetch"}:
                result = transfer(transport, profile, args.action, args.project,
                                  args.local, args.relative, args.job)
            else:
                result = worker_command(transport, profile, args.action, packet,
                                        args.project, args.job)
        print(json.dumps(result, allow_nan=False))
        return 0
    except Exception as exc:
        # Network and authentication exceptions may contain provider/server data.
        print(json.dumps({"status": "error", "type": type(exc).__name__,
                          "detail": "Action did not complete; reconcile before retrying"}))
        return 1
    finally:
        if transport is not None:
            transport.close()


if __name__ == "__main__":
    raise SystemExit(main())
