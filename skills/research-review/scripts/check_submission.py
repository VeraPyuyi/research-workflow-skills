#!/usr/bin/env python3
"""Bounded, read-only submission leakage checks; not a submission approval.

Only explicitly supplied regular files are opened. Archives stay in memory;
links, devices, network paths and directory traversal are never followed. Limits
apply across nested archives, including their metadata. Reports deliberately
contain no filenames, matched text, exception messages, or surrounding context.

``automated_passed`` excludes the always-required human/visual review. Neither
an input's claims of clean evidence nor a clean scan set ``submission_ready``.
PDF extraction is best effort in a resource-limited optional pypdf subprocess;
PDFs always retain partial and visual coverage gaps. No dependencies are installed.
"""

import argparse
import bz2
from contextlib import contextmanager
import hashlib
import importlib.util
import io
import ipaddress
import json
import lzma
import os
from pathlib import Path
import re
import stat
import struct
import subprocess
import sys
import tarfile
import zipfile
import zlib


DEFAULT_BYTES = 8 * 1024 * 1024
_PATH = re.compile(
    r"(?i)(?:\b[a-z]:[\\/]+[^\s\"'<>|{}]*|"
    r"(?<!\\)\\{2,}[^\s\\/<>\"']+[\\/][^\s\"'<>|{}]*|"
    r"(?<![:\w/>])//[^\s/<>\"']+/[^\s\"'<>|{}]*|"
    r"\bfile:/+[^\s\"'<>|{}]*|"
    r"(?<![\w/>])/(?:Users|home|root|opt|tmp|var|etc|mnt|media|srv|private|"
    r"Volumes|workspace|workspaces|data|usr|run|scratch|gpfs|lustre|storage|repos|"
    r"app|bin|sbin|dev|net|afs)(?:/[^\s\"'<>|{}]*|(?=$|[\s\"'<>|{}]))|"
    r"(?<!\w)(?:\.\.[\\/])+[^\s\"'<>|{}]*)"
)
_CREDENTIAL = re.compile(
    r"(?ix)\b(?:[a-z0-9]{1,64}[_-]){0,8}(?:api[_-]?key|access[_-]?key(?:[_-]?id)?|"
    r"secret(?:[_-]?(?:key|token|access[_-]?key))?|token|password|passwd|pwd|"
    r"client[_-]?secret|authorization|credential)s?\b[\"']?\s*[:=]\s*"
    r"(?:[\"'](?P<quoted>[^\"'\r\n]+)[\"']|(?P<bare><[^<>\r\n]+>|[^\s,;}\]\"']+))"
)
_TOKEN = re.compile(
    r"\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|"
    r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)\b|"
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----|"
    r"(?i:\bBearer\s+[A-Za-z0-9._~+/-]{8,})"
)
_PRIVATE_HOST = re.compile(
    r"(?i)\b(?:localhost(?:\.localdomain)?|[a-z0-9_-]{1,63}(?:\.[a-z0-9_-]{1,63}){0,10}"
    r"\.(?:internal|local|lan|intranet|corp|localdomain))\b|"
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b|\[[0-9a-fA-F:]+\]|"
    r"(?<![\w:])(?:fc|fd|fe80)[0-9a-fA-F:]*:[0-9a-fA-F:]+|(?<![\w:])::1\b|"
    r"(?i:\b(?:https?|ssh|ftp)://(?:[^\s/@]+@)?[a-z][a-z0-9_-]*(?=[:/\s]|$))|"
    r"(?i:\bssh\s+[a-z0-9_.-]+@[a-z0-9_.-]+)"
)
_INTERNAL = re.compile(
    r"(?i)\b(?:codex_internal_context|spawn_agent|fork_context|"
    r"research-(?:navigate|scope|ideate|design|implement|experiment|review|write|focus|optimize)|"
    r"functions\.(?:exec|wait)|tool_call_id|recipient_name|project-state\.json|"
    r"workflow-runtime|Magpie|smart-split)\b|"
    r"\b(?:thread|chatgpt-conversation)://[^\s<>\"']+|"
    r"</?(?:analysis|tool_call|function_calls)>|"
    r"\bas an AI (?:language )?model\b|"
    r"\b(?:BEGIN|END) (?:SYSTEM|INTERNAL|AGENT) (?:PROMPT|CONTEXT)\b"
)
_DRAFT = re.compile(r"(?i)\b(?:TODO|FIXME|TBD|XXX)\b|\b(?:insert|add) "
                    r"(?:fabricated results|results here|citation here)\b|\[INSERT [^\]\n]+\]")
_PLACEHOLDER = re.compile(r"(?:<[^<>\r\n]+>|\$\{[^}\r\n]+\}|\{\{[^}\r\n]+\}\})\Z")
_FIGURES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".tiff", ".tif", ".bmp", ".svg", ".eps"}
_ARCHIVES = {".zip", ".docx", ".pptx", ".xlsx", ".odt", ".epub", ".tar", ".gz", ".bz2", ".xz"}


class _UnsafePath(Exception):
    pass


@contextmanager
def _open_regular(path, writable=False):
    """Anchor each ancestor without following links (also on Windows).

    Windows directory handles deny delete-sharing until the leaf is open, so a
    checked ancestor cannot be replaced with a junction during this traversal.
    POSIX uses openat/O_NOFOLLOW for each component, rather than resolve()+open().
    """
    raw = os.fspath(path)
    if not isinstance(raw, str) or not raw or "\0" in raw:
        raise _UnsafePath()
    if raw.startswith(("\\\\", "//")) or "://" in raw:
        raise _UnsafePath()
    if ".." in re.split(r"[\\/]", raw):
        raise _UnsafePath()
    absolute = Path(os.path.abspath(raw))
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        import msvcrt

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                      ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
                                      wintypes.HANDLE]
        kernel.CreateFileW.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.GetFileInformationByHandleEx.argtypes = [wintypes.HANDLE, ctypes.c_int,
                                                       ctypes.c_void_p, wintypes.DWORD]

        class Attributes(ctypes.Structure):
            _fields_ = [("attributes", wintypes.DWORD), ("tag", wintypes.DWORD)]

        handles = []
        stream = None
        try:
            current = Path(absolute.anchor)
            parts = [current] + list(absolute.parts[1:])
            for index, part in enumerate(parts):
                if index:
                    current = current / part
                leaf = index == len(parts) - 1
                access = (0x40000000 if writable else 0x80000000) if leaf else 0x80
                creation = 4 if leaf and writable else 3  # OPEN_ALWAYS / OPEN_EXISTING
                handle = kernel.CreateFileW(str(current), access,
                                            3, None, creation, 0x02200000, None)
                if handle == ctypes.c_void_p(-1).value:
                    raise _UnsafePath()
                handles.append(handle)
                attributes = Attributes()
                if not kernel.GetFileInformationByHandleEx(handle, 9, ctypes.byref(attributes),
                                                           ctypes.sizeof(attributes)):
                    raise _UnsafePath()
                if attributes.attributes & 0x400:
                    raise _UnsafePath()
                if bool(attributes.attributes & 0x10) == leaf:
                    raise _UnsafePath()
            # Ownership of the leaf handle transfers to the Python stream.
            fd = msvcrt.open_osfhandle(handles[-1],
                                      (os.O_WRONLY if writable else os.O_RDONLY) | os.O_BINARY)
            handles.pop()
            stream = os.fdopen(fd, "wb" if writable else "rb")
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise _UnsafePath()
            yield stream
        finally:
            if stream is not None:
                stream.close()
            for handle in reversed(handles):
                kernel.CloseHandle(handle)
    elif os.open in os.supports_dir_fd and hasattr(os, "O_NOFOLLOW"):
        handles = []
        stream = None
        try:
            handles.append(os.open(absolute.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW))
            for part in absolute.parts[1:-1]:
                handles.append(os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                       dir_fd=handles[-1]))
            flags = os.O_WRONLY | os.O_CREAT if writable else os.O_RDONLY
            fd = os.open(absolute.name, flags | os.O_NOFOLLOW | os.O_NONBLOCK,
                         0o600, dir_fd=handles[-1])
            stream = os.fdopen(fd, "wb" if writable else "rb")
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise _UnsafePath()
            yield stream
        finally:
            if stream is not None:
                stream.close()
            for handle in reversed(handles):
                os.close(handle)
    else:
        # Fail closed on platforms without an ancestor-safe opening primitive.
        raise _UnsafePath()


def _digest(value):
    if isinstance(value, str):
        value = value.encode("utf-8", "surrogatepass")
    return hashlib.sha256(value).hexdigest()


class _Scanner:
    def __init__(self, max_bytes, max_depth, max_members, max_total_bytes,
                 max_member_bytes, max_findings, max_artifacts):
        self.max_bytes = max_bytes
        self.max_depth = max_depth
        self.max_members = max_members
        self.remaining = max_total_bytes
        self.max_member_bytes = max_member_bytes
        self.max_findings = max_findings
        self.max_artifacts = max_artifacts
        self.members = 0
        self.pdf_worker_allowed = True
        self.seen = set()
        self.report = {"schema_version": 1, "findings": [], "coverage_gaps": [],
                       "artifacts": [], "automated_passed": False, "submission_ready": False}

    def gap(self, kind, artifact=None, blocking=True):
        gap = {"kind": kind, "artifact": artifact, "blocking": blocking}
        if gap not in self.report["coverage_gaps"]:
            self.report["coverage_gaps"].append(gap)

    def finding(self, kind, value, artifact, source, line=None):
        digest = _digest(value)
        key = kind, digest, artifact, source
        if key in self.seen:
            return
        if len(self.report["findings"]) >= self.max_findings:
            self.gap("finding_limit", artifact)
            return
        self.seen.add(key)
        locator = {"artifact": artifact, "source": source}
        if line is not None:
            locator["line"] = line
        self.report["findings"].append({"kind": kind, "sha256": digest,
                                         "preview": "[redacted]", "locator": locator})

    def text(self, text, artifact, source="text"):
        # Recognise JSON escape layers without using unicode_escape on Unicode
        # scientific text (which would corrupt it or interpret arbitrary bytes).
        for _ in range(3):
            decoded = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m[1], 16)), text)
            decoded = decoded.replace(r"\/", "/")
            if decoded == text:
                break
            text = decoded
        for kind, pattern in (("local_path", _PATH), ("credential", _CREDENTIAL),
                              ("credential", _TOKEN), ("private_endpoint", _PRIVATE_HOST),
                              ("internal_process", _INTERNAL), ("draft_scaffold", _DRAFT)):
            for match in pattern.finditer(text):
                if len(self.report["findings"]) >= self.max_findings:
                    self.gap("finding_limit", artifact)
                    return
                value = match.group(0)
                if pattern is _CREDENTIAL:
                    value = (match.group("quoted") or match.group("bare")).strip()
                    if _PLACEHOLDER.fullmatch(value):
                        continue
                if pattern is _PRIVATE_HOST:
                    try:
                        address = ipaddress.ip_address(value.strip("[]"))
                    except ValueError:
                        # A syntactically invalid dotted address is not evidence.
                        if re.fullmatch(r"[\d.]+", value) or value.startswith("["):
                            continue
                    else:
                        if address.is_global:
                            continue
                self.finding(kind, value, artifact, source,
                             text.count("\n", 0, match.start()) + 1)

    def strings(self, data, artifact, source="metadata"):
        self.text(data.decode("latin-1"), artifact, source)
        for encoding in ("utf-16-le", "utf-16-be"):
            self.text(data.decode(encoding, errors="ignore"), artifact, source)

    def artifact(self, data, parent=None):
        if len(self.report["artifacts"]) >= self.max_artifacts:
            self.gap("artifact_limit", parent)
            return None
        ident = "artifact-%04d" % (len(self.report["artifacts"]) + 1)
        self.report["artifacts"].append({"id": ident, "parent": parent,
                                         "bytes": len(data), "sha256": _digest(data)})
        return ident

    def process(self, data, name, depth=0, parent=None):
        ident = self.artifact(data, parent)
        if ident is None:
            return
        suffix = Path(name).suffix.lower()
        # Scan names but never the implicit parent directories of supplied paths.
        self.text(name, ident, "member_name" if parent else "filename")
        is_zip = data.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"))
        is_tar = len(data) >= 512 and (data[257:262] == b"ustar" or suffix == ".tar")
        compressed = data.startswith((b"\x1f\x8b", b"BZh", b"\xfd7zXZ\x00"))
        if is_zip or is_tar or compressed or suffix in _ARCHIVES:
            if depth >= self.max_depth:
                self.gap("depth_limit", ident)
            elif is_zip:
                self.zip(data, ident, depth)
            elif compressed:
                self.compressed(data, name, ident, depth)
            elif is_tar:
                self.tar(data, ident, depth)
            else:
                self.strings(data, ident)
                self.gap("unsupported_archive", ident)
            return
        if data.startswith(b"%PDF-") or suffix == ".pdf":
            self.pdf(data, ident)
            return
        if suffix in _FIGURES:
            self.gap("figure_visual_review", ident)
        text = None
        try:
            if data.startswith((b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
                text = data.decode("utf-32")
            elif data.startswith((b"\xff\xfe", b"\xfe\xff")):
                text = data.decode("utf-16")
            elif b"\x00" not in data:
                text = data.decode("utf-8-sig")
                if any(ord(c) < 32 and c not in "\r\n\t\f" for c in text):
                    text = None
        except UnicodeError:
            pass
        if text is None:
            self.strings(data, ident)
            self.gap("opaque_binary", ident)
        else:
            self.text(text, ident)

    def member(self, ident):
        if self.members >= self.max_members:
            self.gap("member_limit", ident)
            return False
        self.members += 1
        return True

    def allowance(self, size, ident):
        limit = min(self.max_member_bytes, self.remaining)
        if size < 0 or size > limit:
            self.gap("byte_limit", ident)
            return None
        return limit

    def zip(self, data, ident, depth):
        try:
            # Preflight the *actual* central directory before ZipFile allocates
            # one object per entry. Do not trust the EOCD's claimed entry count.
            end = data.rfind(b"PK\x05\x06", max(0, len(data) - 65557))
            if end < 0 or end + 22 > len(data):
                raise ValueError()
            disk, cd_disk, on_disk, count, cd_size, cd_offset, comment_size = struct.unpack_from(
                "<4H2LH", data, end + 4)
            self.strings(data[end + 22:end + 22 + comment_size], ident)
            if disk or cd_disk or on_disk != count or count == 0xffff or cd_size == 0xffffffff:
                self.gap("unsupported_archive", ident)
                return
            start = end - cd_size
            if start < 0 or cd_offset != start or end + 22 + comment_size != len(data):
                raise ValueError()
            pos, actual = start, 0
            while pos < end:
                if data[pos:pos + 4] != b"PK\x01\x02" or pos + 46 > end:
                    raise ValueError()
                actual += 1
                if actual > self.max_members - self.members:
                    self.gap("member_limit", ident)
                    return
                n, e, c = struct.unpack_from("<3H", data, pos + 28)
                finish = pos + 46 + n + e + c
                if finish > end:
                    raise ValueError()
                # Includes extra fields, comments, and names even for encrypted,
                # unsupported, or otherwise unreadable payloads.
                self.strings(data[pos + 46:finish], ident, "member_metadata")
                pos = finish
            if actual != count:
                raise ValueError()
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                for member in archive.infolist():
                    if not self.member(ident):
                        break
                    self.text(member.orig_filename, ident, "member_name")
                    # Local-header extra fields are separate metadata from the
                    # central directory and must not escape inspection.
                    offset = member.header_offset
                    if offset < 0 or offset + 30 > start:
                        raise ValueError()
                    header = struct.unpack_from("<4s5H3L2H", data, offset)
                    if header[0] != b"PK\x03\x04":
                        raise ValueError()
                    body = offset + 30 + header[9] + header[10]
                    finish = body + member.compress_size
                    if body > start or finish > start or header[2] != member.flag_bits or header[3] != member.compress_type:
                        raise ValueError()
                    self.strings(data[offset + 30:body], ident, "member_metadata")
                    mode = member.external_attr >> 16
                    if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR)):
                        self.gap("archive_link_or_special", ident)
                        continue
                    if member.flag_bits & 1:
                        self.gap("encrypted_stream", ident)
                        continue
                    if member.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                        # stdlib BZIP2/LZMA ZIP readers can allocate unbounded
                        # decoder buffers. Only bounded stored/deflate is used.
                        self.gap("unsupported_stream", ident)
                        continue
                    if member.is_dir():
                        continue
                    limit = self.allowance(member.file_size, ident)
                    if limit is None:
                        continue
                    packed = data[body:finish]
                    if member.compress_type == zipfile.ZIP_STORED:
                        payload = packed[:limit + 1]
                    else:
                        decoder = zlib.decompressobj(-15)
                        payload = decoder.decompress(packed, limit + 1)
                        if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
                            self.gap("archive_unreadable", ident)
                    self.remaining -= min(len(payload), limit)
                    if len(payload) > limit:
                        self.gap("byte_limit", ident)
                        continue
                    # Never rely on ZipExtFile's declared-size truncation: a
                    # forged short size+CRC can otherwise look perfectly clean.
                    if len(payload) != member.file_size or zlib.crc32(payload) != member.CRC:
                        self.gap("archive_unreadable", ident)
                    self.process(payload, member.filename, depth + 1, ident)
        except Exception:
            # Do not put dependency exception messages (often names) in JSON.
            self.gap("archive_unreadable", ident)

    def compressed(self, data, name, ident, depth):
        limit = min(self.max_member_bytes, self.remaining)
        try:
            if data.startswith(b"\x1f\x8b"):
                decoder = zlib.decompressobj(31)
                payload = decoder.decompress(data, limit + 1)
                unused = decoder.unused_data
                # GZIP FNAME/FCOMMENT are user-controlled metadata.
                flags = data[3] if len(data) > 3 else 0
                pos = 10
                if flags & 4:
                    extra_size = struct.unpack_from("<H", data, pos)[0]
                    self.strings(data[pos + 2:pos + 2 + extra_size], ident)
                    pos += 2 + extra_size
                for mask in (8, 16):
                    if flags & mask:
                        end = data.index(b"\x00", pos)
                        self.strings(data[pos:end], ident)
                        pos = end + 1
            elif data.startswith(b"BZh"):
                decoder = bz2.BZ2Decompressor()
                payload = decoder.decompress(data, max_length=limit + 1)
                unused = decoder.unused_data if decoder.eof else b""
            else:
                decoder = lzma.LZMADecompressor(memlimit=64 * 1024 * 1024)
                payload = decoder.decompress(data, max_length=limit + 1)
                unused = decoder.unused_data if decoder.eof else b""
            self.remaining -= min(len(payload), limit)
            if len(payload) > limit or not decoder.eof:
                self.gap("byte_limit", ident)
                return
            if unused:
                # Never silently ignore concatenated streams or trailing data.
                self.strings(unused, ident)
                self.gap("unsupported_stream", ident)
            # Compression is a container layer and consumes a member slot.
            if self.member(ident):
                self.process(payload, Path(name).stem, depth + 1, ident)
        except Exception:
            self.gap("archive_unreadable", ident)

    def tar(self, data, ident, depth):
        try:
            # Already decompressed under a hard output cap. tarfile never gets
            # a compressor, preventing unbounded header/pax decompression.
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as archive:
                while True:
                    if self.members >= self.max_members:
                        # Even parsing the next header could consume huge PAX
                        # metadata. Stop before asking tarfile for that member.
                        if archive.offset < len(data) and any(data[archive.offset:archive.offset + 512]):
                            self.gap("member_limit", ident)
                        break
                    member = archive.next()
                    if member is None:
                        break
                    self.member(ident)
                    for value in (member.name, member.linkname, member.uname, member.gname,
                                  json.dumps(member.pax_headers, ensure_ascii=True),
                                  json.dumps(archive.pax_headers, ensure_ascii=True)):
                        self.text(value, ident, "member_metadata")
                    if member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                        self.gap("archive_link_or_special", ident)
                        continue
                    if member.isdir():
                        continue
                    # Sparse files can expand far beyond their on-disk extent.
                    if member.sparse is not None:
                        self.gap("unsupported_stream", ident)
                        continue
                    limit = self.allowance(member.size, ident)
                    if limit is None:
                        continue
                    with archive.extractfile(member) as stream:
                        payload = stream.read(member.size + 1)
                    self.remaining -= len(payload)
                    if len(payload) != member.size:
                        self.gap("archive_unreadable", ident)
                    else:
                        self.process(payload, member.name, depth + 1, ident)
                # tarfile stops at the first terminator, including for a
                # concatenated archive. Zero padding is permitted; other tails
                # must not silently acquire clean coverage.
                tail = data[archive.offset:]
                if any(tail):
                    self.strings(tail, ident, "archive_trailer")
                    self.gap("unparsed_archive_trailer", ident)
        except Exception:
            self.gap("archive_unreadable", ident)

    def pdf(self, data, ident):
        self.gap("pdf_visual_review", ident)
        self.gap("pdf_partial", ident)
        self.strings(data, ident, "pdf_raw")
        # Decode bounded literal/octal and hexadecimal PDF strings without
        # attempting stream decompression or interpreting document actions.
        for match in re.finditer(rb"\(((?:\\.|[^()\\])*)\)|<([0-9a-fA-F\s]+)>", data):
            if match[1] is not None:
                value = re.sub(rb"\\([0-7]{1,3}|[nrtbf()\\])", _pdf_escape, match[1])
            else:
                hex_value = re.sub(rb"\s", b"", match[2])
                if len(hex_value) % 2:
                    hex_value += b"0"
                value = bytes.fromhex(hex_value.decode("ascii"))
            self.strings(value, ident, "pdf_decoded")
        if not self.pdf_worker_allowed:
            return
        try:
            available = importlib.util.find_spec("pypdf") is not None
        except (ValueError, ImportError):
            available = False
        if not available:
            self.gap("pdf_unavailable", ident)
            return
        # Untrusted PDF parser output and decompression have their own hard
        # memory/CPU/time boundary; no library monkeypatches in the caller.
        try:
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run(
                [sys.executable, "-B", str(Path(__file__).absolute()), "--pdf-worker",
                 str(min(self.remaining, self.max_member_bytes)), str(self.max_members),
                 str(min(self.max_findings, 1000))], input=data, capture_output=True,
                timeout=8, env=env)
            if result.returncode or len(result.stdout) > 1024 * 1024:
                self.gap("pdf_extraction_failed", ident)
                return
            extracted = json.loads(result.stdout)
            consumed = extracted.get("bytes_consumed", 0)
            if type(consumed) is not int or not 0 <= consumed <= min(self.remaining, self.max_member_bytes):
                raise ValueError()
            self.remaining -= consumed
            # The worker already redacts. Rebuild from a closed schema so no
            # parser-produced strings can accidentally enter the public report.
            for finding in extracted["findings"]:
                if finding["kind"] in {"local_path", "credential", "private_endpoint",
                                       "internal_process", "draft_scaffold"}:
                    if len(self.report["findings"]) >= self.max_findings:
                        self.gap("finding_limit", ident)
                        break
                    digest = finding["sha256"]
                    if re.fullmatch(r"[a-f0-9]{64}", digest):
                        self.report["findings"].append({"kind": finding["kind"], "sha256": digest,
                            "preview": "[redacted]", "locator": {"artifact": ident, "source": "pdf_extracted"}})
            if extracted["coverage_gaps"]:
                self.gap("pdf_extraction_partial", ident)
        except Exception:
            self.gap("pdf_extraction_failed", ident)


def _pdf_escape(match):
    value = match[1]
    if value[:1] in b"01234567":
        return bytes([int(value, 8) & 255])
    return {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f"}.get(value, value)


def _pdf_resource_limits():
    """Return retained OS handles, or fail closed before importing pypdf."""
    if os.name != "nt":
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (384 * 1024 * 1024,) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
        return None
    import ctypes
    from ctypes import wintypes

    class Basic(ctypes.Structure):
        _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                    ("flags", wintypes.DWORD), ("min_ws", ctypes.c_size_t),
                    ("max_ws", ctypes.c_size_t), ("active", wintypes.DWORD),
                    ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD),
                    ("scheduling", wintypes.DWORD)]

    class Counters(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint64) for name in
                    ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]

    class Extended(ctypes.Structure):
        _fields_ = [("basic", Basic), ("io", Counters), ("process_memory", ctypes.c_size_t),
                    ("job_memory", ctypes.c_size_t), ("peak_process", ctypes.c_size_t),
                    ("peak_job", ctypes.c_size_t)]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int,
                                               ctypes.c_void_p, wintypes.DWORD]
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    job = kernel.CreateJobObjectW(None, None)
    info = Extended()
    info.basic.flags = 0x100 | 0x2  # process memory and per-process CPU time
    info.basic.process_time = 5 * 10_000_000
    info.process_memory = 384 * 1024 * 1024
    if not job or not kernel.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info)):
        raise RuntimeError()
    if not kernel.AssignProcessToJobObject(job, kernel.GetCurrentProcess()):
        raise RuntimeError()
    return kernel, job


def _pdf_worker():
    # The worker sends only bounded redacted findings, never extracted text.
    retained_limits = _pdf_resource_limits()
    import logging
    logging.disable(logging.CRITICAL)
    from pypdf import PdfReader
    limit, members, findings = map(int, sys.argv[2:5])
    data = sys.stdin.buffer.read(DEFAULT_BYTES + 1)
    if len(data) > DEFAULT_BYTES:
        return 2
    checker = _Scanner(limit, 0, members, limit, limit, findings, members)
    checker.pdf_worker_allowed = False
    reader = PdfReader(io.BytesIO(data), strict=False)
    if reader.is_encrypted:
        return 2

    def inspect(value):
        if isinstance(value, str):
            value = value.encode("utf-8", "replace")
        take = min(len(value), checker.remaining)
        checker.strings(value[:take], "pdf", "pdf_extracted")
        checker.remaining -= take
        if take < len(value):
            checker.gap("byte_limit")

    for key, value in (reader.metadata or {}).items():
        inspect(str(key))
        inspect(str(value))
    for index, page in enumerate(reader.pages):
        if index >= members or checker.remaining <= 0:
            checker.gap("member_limit")
            break
        inspect(page.extract_text() or "")
    # Attachment access may decompress; the worker's OS limits cover that too.
    for index, (name, payloads) in enumerate(reader.attachments.items()):
        if index >= members or checker.remaining <= 0:
            checker.gap("member_limit")
            break
        inspect(name)
        for payload in payloads:
            if checker.remaining <= 0:
                checker.gap("byte_limit")
                break
            take = min(len(payload), checker.remaining, limit)
            checker.remaining -= take
            checker.process(payload[:take], name)
            if take < len(payload):
                checker.gap("byte_limit")
    checker.report["bytes_consumed"] = limit - checker.remaining
    sys.stdout.write(json.dumps(checker.report, separators=(",", ":")))
    return 0


def scan(paths, max_bytes=DEFAULT_BYTES, max_depth=4, max_members=256,
         max_total_bytes=32 * 1024 * 1024, max_member_bytes=None,
         max_findings=1000, max_artifacts=512):
    """Scan explicit paths; caps are per input/member and shared across nesting.

    Over-size files/members are skipped *before* reading/decompression. A byte
    budget also covers container expansion, not just leaf content. Zero limits
    are supported; invalid limits produce a failed report without opening files.
    Directories are not enumerated. The API itself never writes any files.
    """
    if max_member_bytes is None:
        max_member_bytes = max_bytes
    limits = (max_bytes, max_depth, max_members, max_total_bytes, max_member_bytes,
              max_findings, max_artifacts)
    checker = _Scanner(*limits)
    checker.gap("manual_review", blocking=False)
    if any(type(value) is not int or value < 0 for value in limits):
        checker.gap("invalid_limits")
        return checker.report
    if isinstance(paths, (str, bytes, os.PathLike)):
        paths = [paths]
    supplied = False
    try:
        for index, path in enumerate(paths):
            supplied = True
            if index >= max_artifacts:
                checker.gap("artifact_limit")
                break
            try:
                with _open_regular(path) as stream:
                    size = os.fstat(stream.fileno()).st_size
                    limit = min(max_bytes, checker.remaining)
                    if size > limit:
                        checker.gap("byte_limit")
                        continue
                    data = stream.read(limit + 1)
                    if len(data) > limit:
                        checker.gap("byte_limit")
                        continue
                checker.remaining -= len(data)
                checker.process(data, Path(path).name)
            except (_UnsafePath, OSError, ValueError, TypeError):
                checker.gap("unsafe_or_unreadable_path")
    except Exception:
        checker.gap("scan_failed")
    if not supplied:
        checker.gap("no_artifacts")
    checker.report["automated_passed"] = (
        not checker.report["findings"] and
        not any(gap["blocking"] for gap in checker.report["coverage_gaps"]))
    return checker.report


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        # argparse's ordinary errors echo caller-supplied names and values.
        raise ValueError()


def main(argv=None):
    parser = _Parser(description=__doc__)
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--output", help="write redacted JSON to this explicit output file")
    for option, default in (("max-bytes", DEFAULT_BYTES), ("max-depth", 4),
                            ("max-members", 256), ("max-total-bytes", 32 * 1024 * 1024),
                            ("max-member-bytes", None), ("max-findings", 1000),
                            ("max-artifacts", 512)):
        parser.add_argument("--" + option, type=int, default=default)
    try:
        args = parser.parse_args(argv)
        options = vars(args).copy()
        paths, output = options.pop("paths"), options.pop("output")
        report = scan(paths, **options)
        serialized = json.dumps(report, indent=2) + "\n"
        if output:
            # Never overwrite submission artifacts or follow output symlinks.
            # Existing regular reports may be replaced; parent links are rejected.
            _write_report(output, serialized, paths)
        else:
            sys.stdout.write(serialized)
        return 0 if report["automated_passed"] else 2
    except Exception:
        sys.stderr.write('{"error":"scan_or_output_failed","submission_ready":false}\n')
        return 2


def _write_report(output, serialized, inputs):
    target = Path(os.path.abspath(output))
    if any(os.path.normcase(str(target)) == os.path.normcase(os.path.abspath(p)) for p in inputs):
        raise _UnsafePath()
    # Anchor ancestors exactly as for input reads; truncate only *after* the
    # open handle is verified regular and not a hard-link alias of a source.
    # This explicit CLI destination is the only write in the scanner.
    with _open_regular(output, writable=True) as stream:
        if os.fstat(stream.fileno()).st_nlink != 1:
            raise _UnsafePath()
        stream.truncate(0)
        stream.write(serialized.encode("utf-8"))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--pdf-worker":
        try:
            sys.exit(_pdf_worker())
        except Exception:
            sys.exit(2)
    sys.exit(main())
