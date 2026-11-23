"""Resolve bibliography entries against arXiv, Crossref and OpenAlex.

Input: a BibTeX file or a literature.jsonl (see research-navigate records.md).
Each entry is resolved by arXiv id, then DOI, then title search, and its title
(and first-author surname when available) is compared with the record found:

* ``resolved``        identity confirmed;
* ``title_mismatch``  an identifier resolves to a different title or author;
* ``unresolved``      nothing matching was found;
* ``unchecked``       a lookup failed (network, rate limit) - not a pass.

This checks identity only. Whether the source supports the sentence that cites
it is the separate support check in the evidence ledger.

Exit status: 0 when every entry is resolved, 1 otherwise, 2 on input errors.
"""
import argparse
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

USER_AGENT = "research-workflow-skills verify_refs (mailto:unknown@example.invalid)"
TITLE_THRESHOLD = 0.9


def normalize(text):
    text = unicodedata.normalize("NFKD", text or "")
    text = re.sub(r"\\[a-zA-Z]+|[{}$\\]", " ", text)
    text = re.sub(r"[^a-z0-9 ]", " ", text.lower())
    return " ".join(text.split())


def similar(a, b):
    a, b = normalize(a), normalize(b)
    return bool(a and b) and SequenceMatcher(None, a, b).ratio() >= TITLE_THRESHOLD


def surname(author):
    author = (author or "").strip()
    if "," in author:
        author = author.split(",", 1)[0]
    parts = normalize(author).split()
    return parts[-1] if parts else ""


def parse_bibtex(text):
    entries = []
    for match in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        kind, key = match.group(1).lower(), match.group(2)
        if kind in ("comment", "string", "preamble"):
            continue
        depth, i = 1, match.end()
        while i < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        body = text[match.end():i - 1]
        fields = {}
        for field in re.finditer(r"(\w+)\s*=\s*", body):
            start = field.end()
            if start >= len(body):
                break
            if body[start] == "{":
                depth, j = 1, start + 1
                while j < len(body) and depth:
                    depth += {"{": 1, "}": -1}.get(body[j], 0)
                    j += 1
                value = body[start + 1:j - 1]
            elif body[start] == '"':
                j = body.find('"', start + 1)
                value = body[start + 1:j]
            else:
                value = re.match(r"[^,\n]*", body[start:]).group(0)
            fields.setdefault(field.group(1).lower(), " ".join(value.split()))
        entries.append({"id": key, "title": fields.get("title", ""),
                        "authors": [a.strip() for a in fields.get("author", "").split(" and ") if a.strip()],
                        "doi": fields.get("doi", ""),
                        "arxiv": (fields.get("eprint", "") if "arxiv" in fields.get("archiveprefix", "").lower()
                                  else "") or _arxiv_from(fields.get("journal", "") + " " + fields.get("url", "")
                                                          + " " + fields.get("eprint", ""))})
    return entries


def _arxiv_from(text):
    match = re.search(r"(?:arxiv[:./ ]+(?:abs/)?)(\d{4}\.\d{4,5})", text or "", re.I)
    return match.group(1) if match else ""


def load(path):
    text = Path(path).read_text(encoding="utf-8")
    if path.endswith(".jsonl"):
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]
        return [{"id": r.get("id"), "title": r.get("title", ""), "authors": r.get("authors", []),
                 "doi": r.get("doi", ""), "arxiv": r.get("arxiv", "")} for r in rows]
    return parse_bibtex(text)


def http_get(url, timeout=20):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


class Resolver:
    """Each lookup returns a list of {title, authors} candidates; raises on transport failure."""

    def __init__(self, fetch=http_get, pause=0.5):
        self.fetch, self.pause = fetch, pause

    def _get(self, url):
        if self.pause:
            time.sleep(self.pause)
        return self.fetch(url)

    def arxiv(self, ident):
        data = self._get("https://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(ident))
        ns = {"a": "http://www.w3.org/2005/Atom"}
        out = []
        for entry in ET.fromstring(data).findall("a:entry", ns):
            title = entry.findtext("a:title", "", ns)
            if title and title.strip().lower() != "error":
                out.append({"title": title, "authors": [a.findtext("a:name", "", ns)
                                                        for a in entry.findall("a:author", ns)]})
        return out

    def doi(self, ident):
        try:
            data = json.loads(self._get("https://api.crossref.org/works/" + urllib.parse.quote(ident)))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return []
            raise
        item = data.get("message", {})
        return [{"title": " ".join(item.get("title", [])),
                 "authors": [f"{a.get('given', '')} {a.get('family', '')}" for a in item.get("author", [])]}]

    def title(self, title):
        url = ("https://api.openalex.org/works?per-page=5&search="
               + urllib.parse.quote(normalize(title)))
        data = json.loads(self._get(url))
        return [{"title": w.get("title") or "",
                 "authors": [a.get("author", {}).get("display_name", "") for a in w.get("authorships", [])]}
                for w in data.get("results", [])]


def matches(entry, candidate):
    if not similar(entry.get("title"), candidate.get("title")):
        return False
    authors, found = entry.get("authors") or [], candidate.get("authors") or []
    if authors and found:
        return surname(authors[0]) in {surname(a) for a in found[:max(3, len(authors))]}
    return True


def verify(entry, resolver):
    result = {"id": entry.get("id"), "title": entry.get("title", "")}
    try:
        for method, value in (("arxiv", entry.get("arxiv")), ("doi", entry.get("doi"))):
            if value:
                found = getattr(resolver, method)(value.strip())
                result["via"] = method
                if any(matches(entry, c) for c in found):
                    return dict(result, status="resolved")
                return dict(result, status="title_mismatch" if found else "unresolved",
                            found_title=(found[0]["title"] if found else None))
        if not entry.get("title"):
            return dict(result, status="unresolved", via=None, note="no identifier or title")
        result["via"] = "title"
        found = resolver.title(entry["title"])
        return dict(result, status="resolved" if any(matches(entry, c) for c in found) else "unresolved")
    except (urllib.error.URLError, OSError, ValueError, ET.ParseError) as exc:
        return dict(result, status="unchecked", error=type(exc).__name__)


def run(entries, resolver, manuscript=None):
    results = [verify(e, resolver) for e in entries]
    report = {"entries": results,
              "counts": {s: sum(r["status"] == s for r in results)
                         for s in ("resolved", "title_mismatch", "unresolved", "unchecked")}}
    report["passed"] = bool(results) and report["counts"]["resolved"] == len(results)
    if manuscript:
        report["manuscript_sha256"] = hashlib.sha256(Path(manuscript).read_bytes()).hexdigest()
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", help="references.bib or literature.jsonl")
    parser.add_argument("--manuscript", help="Final manuscript file; its digest binds this report for check_score.py")
    parser.add_argument("--output", help="Write the JSON report here as well")
    args = parser.parse_args(argv)
    try:
        report = run(load(args.source), Resolver(), args.manuscript)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
