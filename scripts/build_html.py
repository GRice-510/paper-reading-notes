#!/usr/bin/env python3
"""Generate searchable HTML from the PDF's actual LaTeX/BibTeX inputs.
Requires Python 3.10+ and Pandoc. Source files are never modified.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = re.compile(r"\\(?:input|include)\s*\{([^{}]+)\}")
BIB = re.compile(r"\\bibliography\s*\{([^{}]+)\}")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def uncomment(text: str) -> str:
    return re.sub(r"(?<!\\)((?:\\\\)*)%[^\n]*", r"\1", text)


def balanced(text: str, start: int) -> int:
    """Position after a balanced brace group, respecting TeX escapes."""
    if text[start] != "{":
        raise ValueError("Expected an opening brace")
    depth, i = 1, start + 1
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("Unbalanced braces")


def bib_entries(text: str) -> dict[str, dict]:
    """Keep exact source entries for copying; parse fields separately.
    Unsupported string/crossref dependencies fail rather than producing partial citations.
    """
    result: dict[str, dict] = {}
    pos = 0
    pattern = re.compile(r"(?m)^[ \t]*@([A-Za-z]+)\s*\{")
    while match := pattern.search(text, pos):
        kind = match.group(1).lower()
        start = text.index("@", match.start())
        opening = match.end() - 1
        depth, quoted, i = 1, False, opening + 1
        while i < len(text) and depth:
            ch = text[i]
            if ch == "\\":
                i += 2
                continue
            if ch == '"' and depth == 1:
                quoted = not quoted
            elif not quoted:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                elif ch == "%" and depth == 1:
                    end = text.find("\n", i)
                    i = len(text) if end == -1 else end
            i += 1
        if depth:
            raise ValueError("Unterminated BibTeX entry")
        pos = i
        if kind == "comment":
            continue
        if kind in {"string", "preamble"}:
            raise ValueError(f"@{kind} needs explicit clipboard dependency support")
        inside = text[opening + 1:i - 1]
        key, sep, rest = inside.partition(",")
        key = key.strip()
        if not sep or not key:
            raise ValueError("Missing BibTeX key")
        if key in result:
            raise ValueError(f"Duplicate BibTeX key: {key}")
        fields, p = {}, 0
        while p < len(rest):
            m = re.match(r"[\s,]*(?:%[^\n]*\n\s*)*([A-Za-z][\w-]*)\s*=\s*", rest[p:])
            if not m:
                if rest[p:].strip(" \t\r\n,"):
                    raise ValueError(f"Cannot parse BibTeX fields in {key}: {rest[p:p+50]}")
                break
            field = m.group(1).lower()
            p += m.end()
            if p >= len(rest):
                raise ValueError(f"Missing {field} in {key}")
            if rest[p] == "{":
                end = balanced(rest, p)
                value = rest[p + 1:end - 1]
                p = end
            elif rest[p] == '"':
                end = p + 1
                while end < len(rest):
                    if rest[end] == "\\":
                        end += 2
                    elif rest[end] == '"':
                        break
                    else:
                        end += 1
                if end >= len(rest):
                    raise ValueError(f"Unterminated {field} in {key}")
                value, p = rest[p + 1:end], end + 1
            else:
                end = rest.find(",", p)
                end = len(rest) if end == -1 else end
                value, p = rest[p:end].strip(), end
                if not re.fullmatch(r"[0-9]+", value):
                    raise ValueError(f"Unresolved BibTeX string in {key}.{field}")
            if field in {"crossref", "xdata"}:
                raise ValueError(f"{key}: copy dependency {field} must be resolved explicitly")
            if rest[p:].lstrip().startswith("#"):
                raise ValueError(f"BibTeX concatenation in {key} needs explicit support")
            fields[field] = value
        result[key] = {"raw": text[start:i] + "\n", "fields": fields}
    if re.search(r"(?m)^\s*@\w+\s*\(", text):
        raise ValueError("Parenthesis-style BibTeX entries need explicit support")
    return result


def pandoc(text: str, source: str, target: str, *args: str) -> str:
    proc = subprocess.run(["pandoc", "-f", source, "-t", target, *args],
                          input=text, text=True, capture_output=True, cwd=ROOT)
    if proc.returncode:
        raise ValueError(proc.stderr.strip())
    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)
    return proc.stdout


def plain(node) -> str:
    if isinstance(node, list):
        return "".join(plain(x) for x in node)
    if not isinstance(node, dict):
        return ""
    t, c = node.get("t"), node.get("c")
    if t == "Str":
        return c
    if t in {"Space", "SoftBreak", "LineBreak"}:
        return " "
    if t in {"Math", "Code"}:
        return c[1]
    if t in {"Link", "Image", "Span", "Header"}:
        return plain(c[1] if t in {"Span", "Link", "Image"} else c[2])
    if t == "Cite":
        return " ".join(x["citationId"] for x in c[0])
    return plain(c)


def walk(node):
    if isinstance(node, dict):
        yield node
        yield from walk(node.get("c"))
    elif isinstance(node, list):
        for item in node:
            yield from walk(item)


def citations(blocks) -> list[str]:
    return [cite["citationId"] for node in walk(blocks) if node.get("t") == "Cite"
            for cite in node["c"][0]]


def resolve(path: str, suffix: str = ".tex") -> Path:
    file = (ROOT / path).resolve()
    if file.suffix != suffix:
        file = Path(str(file) + suffix)
    if not file.is_relative_to(ROOT) or not file.is_file():
        raise ValueError(f"Missing or unsafe input: {path}")
    return file


def load_sources():
    main = uncomment((ROOT / "main.tex").read_text())
    body = main.split(r"\begin{document}", 1)[1].split(r"\end{document}", 1)[0]
    bibfiles = [resolve(x.strip(), ".bib") for m in BIB.finditer(body) for x in m.group(1).split(",")]
    if not bibfiles:
        raise ValueError("No bibliography declared in main.tex")
    seen, paper_paths, section_paths = set(), {}, {}
    def expand(text: str) -> str:
        def sub(match):
            file = resolve(match.group(1))
            rel = file.relative_to(ROOT).as_posix()
            if rel in seen:
                raise ValueError(f"Duplicate/cyclic input: {rel}")
            seen.add(rel)
            src = uncomment(file.read_text())
            if rel.startswith("papers/"):
                command, marker, mapping = "subsection", "paper-" + file.stem, paper_paths
            elif rel.startswith("sections/"):
                command, marker, mapping = "section", "section-" + file.stem, section_paths
            else:
                return expand(src)
            found = list(re.finditer(r"\\" + command + r"\s*\{", src))
            if len(found) != 1:
                raise ValueError(f"Expected one \\{command} in {rel}")
            end = balanced(src, found[0].end() - 1)
            mapping[marker] = rel
            src = src[:end] + "\n\\label{" + marker + "}\n" + src[end:]
            return expand(src)
        return INCLUDE.sub(sub, text)
    body = expand(body)
    body = BIB.sub("", body)
    body = re.sub(r"\\bibliographystyle\{[^}]+\}", "", body)
    body = re.sub(r"\\(?:maketitle|tableofcontents|clearpage|newpage)\b", "", body)
    unlisted = {p.relative_to(ROOT).as_posix() for p in (ROOT / "papers").glob("*.tex")
                if not p.name.startswith("_")} - seen
    if unlisted:
        raise ValueError("Paper files not reachable from main.tex: " + ", ".join(sorted(unlisted)))
    ast = json.loads(pandoc(body, "latex+raw_tex", "json"))
    sections, paper = [], None
    for block in ast["blocks"]:
        if block["t"] == "Header" and block["c"][0] == 1:
            sid = block["c"][1][0]
            if sid not in section_paths:
                raise ValueError(f"Unknown section {sid}")
            sections.append({"id": sid, "title": block["c"][2], "papers": [], "intro": []})
            paper = None
        elif block["t"] == "Header" and block["c"][0] == 2:
            pid = block["c"][1][0]
            if pid not in paper_paths or not sections:
                raise ValueError(f"Unknown paper heading {pid}")
            paper = {"id": pid, "path": paper_paths[pid], "title": block["c"][2], "blocks": []}
            sections[-1]["papers"].append(paper)
        elif paper is not None:
            paper["blocks"].append(block)
        elif sections:
            sections[-1]["intro"].append(block)
        else:
            raise ValueError("Unexpected content outside sections")
    for node in walk(ast["blocks"]):
        if node.get("t") in {"RawInline", "RawBlock"} and node["c"][0] == "latex":
            if not node["c"][1].startswith("\\cite"):
                raise ValueError(f"Unconverted LaTeX: {node['c'][1]}")
    inputs = ["main.tex", *sorted(seen), *[p.relative_to(ROOT).as_posix() for p in bibfiles]]
    return ast, sections, bibfiles, inputs


def render_factory(ast, numbers):
    def replace(node):
        if isinstance(node, list):
            return [replace(x) for x in node]
        if not isinstance(node, dict):
            return node
        if node.get("t") == "Cite":
            elements = [{"t": "Str", "c": "["}]
            for n, cite in enumerate(node["c"][0]):
                key = cite["citationId"]
                if n:
                    elements.append({"t": "Str", "c": ", "})
                elements.extend(replace(cite["citationPrefix"]))
                elements.append({"t": "Link", "c": [["", ["citation"], []],
                    [{"t": "Str", "c": str(numbers[key])}], ["#ref-" + key, key]]})
                elements.extend(replace(cite["citationSuffix"]))
            elements.append({"t": "Str", "c": "]"})
            return {"t": "Span", "c": [["", ["citations"], []], elements]}
        out = copy.deepcopy(node)
        if "c" in out:
            out["c"] = replace(out["c"])
        return out
    def render(blocks) -> str:
        doc = {**ast, "blocks": replace(blocks), "meta": {}}
        return pandoc(json.dumps(doc), "json", "html5", "--mathjax", "--wrap=none").strip()
    def inline(inlines) -> str:
        return render([{"t": "Plain", "c": inlines}])
    return render, inline


def norm_arxiv(value: str) -> str:
    return re.sub(r"v\d+$", "", value.strip()).replace("/", "-").replace("_", "-").lower()


def primary_key(paper, entries):
    cited = list(dict.fromkeys(citations(paper["blocks"])))
    stem = Path(paper["path"]).stem
    matches = [key for key in cited if norm_arxiv(entries[key]["fields"].get("eprint", "")) == norm_arxiv(stem)]
    if len(matches) == 1:
        return matches[0]
    if not re.search(r"\d{4}\.\d{4,5}|(?:hep|astro|gr)-", stem) and cited:
        return cited[0]
    raise ValueError(f"Cannot uniquely match {paper['path']} to its own BibTeX entry: {cited}")


def buttons(key: str, entry: dict) -> str:
    parts = ['<div class="actions" aria-label="引用情報">']
    for mode, text, label in [("bib", "BibTeX をコピー", "BibTeX全文をコピー"),
                             ("key", "Key", "citation keyをコピー"),
                             ("cite", r"\cite{…}", "LaTeXのciteコマンドをコピー")]:
        parts.append(f'<button type="button" class="copy {mode}" data-key="{esc(key)}" data-copy="{mode}" aria-label="{label}: {esc(key)}" disabled>{esc(text)}</button>')
    fields = entry["fields"]
    if eprint := fields.get("eprint"):
        parts.append(f'<a class="external" href="https://arxiv.org/abs/{quote(eprint, safe="/.")}" target="_blank" rel="noopener noreferrer">arXiv ↗</a>')
    if doi := fields.get("doi"):
        parts.append(f'<a class="external" href="https://doi.org/{quote(doi, safe="/().:;-_")}" target="_blank" rel="noopener noreferrer">DOI ↗</a>')
    parts.append('</div>')
    return "".join(parts)


def bib_preview(entry) -> str:
    return '<details class="bib-preview"><summary>BibTeXを表示</summary><pre tabindex="0"><code>' + esc(entry["raw"]) + '</code></pre></details>'


def generate(output: Path, revision: str, source_date: str, pdf: Path | None):
    ast, sections, bibfiles, inputs = load_sources()
    entries = {}
    bibtext = "\n".join(p.read_text() for p in bibfiles)
    for file in bibfiles:
        parsed = bib_entries(file.read_text())
        duplicate = set(parsed) & set(entries)
        if duplicate:
            raise ValueError("Duplicate bibliography keys: " + ", ".join(sorted(duplicate)))
        entries.update(parsed)
    meta = {x["id"]: x for x in json.loads(pandoc(bibtext, "biblatex", "csljson"))}
    order = list(dict.fromkeys(citations(ast["blocks"])))
    missing = set(order) - entries.keys()
    if missing:
        raise ValueError("Citations absent from bibliography: " + ", ".join(sorted(missing)))
    numbers = {key: i + 1 for i, key in enumerate(order)}
    render, inline = render_factory(ast, numbers)
    cards, sidebar, options, manifest_papers = [], [], [], []
    for sn, section in enumerate(sections, 1):
        stitle = inline(section["title"])
        sid = section["id"]
        options.append(f'<option value="{esc(sid)}">{esc(plain(section["title"]))}</option>')
        sidebar.append(f'<a href="#{esc(sid)}"><span>{sn}. {stitle}</span><span class="count">{len(section["papers"])}</span></a>')
        cards.append(f'<section class="topic" id="{esc(sid)}"><h2><span class="section-number">{sn:02}</span> {stitle}</h2>')
        if section["intro"]:
            cards.append(render(section["intro"]))
        for pn, paper in enumerate(section["papers"], 1):
            key = primary_key(paper, entries)
            pid, blocks = paper["id"], paper["blocks"]
            if not blocks or "Authors:" not in plain(blocks[0]):
                raise ValueError(f"Missing Authors: {paper['path']}")
            labels = [plain(b["c"][2]) for b in blocks if b["t"] == "Header"]
            if labels[:3] != ["主な主張", "新規性", "位置付け"]:
                raise ValueError(f"Unexpected card fields in {paper['path']}: {labels}")
            title = inline(paper["title"])
            refs = list(dict.fromkeys(citations(blocks)))
            cards.append(f'<article class="paper" id="{esc(pid)}" data-section="{esc(sid)}" data-key="{esc(key)}" data-refs="{esc(json.dumps(refs))}">')
            cards.append(f'<div class="paper-heading"><span class="paper-number">{sn}.{pn}</span><h3><a href="#{esc(pid)}">{title}</a></h3></div>')
            cards.append('<div class="authors">' + render([blocks[0]]) + '</div>')
            cards.append(buttons(key, entries[key]))
            fields, current = [], None
            for block in blocks[1:]:
                if block["t"] == "Header":
                    current = {"title": block["c"][2], "body": []}
                    fields.append(current)
                elif current is not None:
                    current["body"].append(block)
                else:
                    raise ValueError(f"Unlabelled text after Authors: {paper['path']}")
            cards.append('<div class="paper-body">')
            for field in fields:
                cards.append('<div class="field"><h4>' + inline(field["title"]) + '</h4><div class="field-content">' + render(field["body"]) + '</div></div>')
            cards.extend(['</div>', bib_preview(entries[key]), '</article>'])
            manifest_papers.append({"id": pid, "path": paper["path"], "key": key, "section": sid, "citations": refs})
        cards.append('</section>')
    refs_html = []
    for key in order:
        entry, metadata = entries[key], meta[key]
        authors = ", ".join(a.get("literal") or " ".join(filter(None, [a.get("given"), a.get("non-dropping-particle"), a.get("family")])) for a in metadata.get("author", []))
        title_html = pandoc(entry["fields"].get("title", ""), "latex", "html5", "--mathjax", "--wrap=none").strip()
        title_html = re.sub(r"^<p>|</p>$", "", title_html)
        venue = " ".join(str(metadata[x]) for x in ["container-title", "volume", "issue", "page"] if x in metadata)
        year = metadata.get("issued", {}).get("date-parts", [[""]])[0][0]
        refs_html.append(f'<article class="reference" id="ref-{esc(key)}" data-key="{esc(key)}"><span class="ref-number">[{numbers[key]}]</span><div class="ref-content"><p>{esc(authors)}. <em>{title_html}</em>.</p><p class="ref-venue">{esc(venue)}{esc(" (" + str(year) + ")" if year else "")}</p>')
        refs_html.append(buttons(key, entry) + bib_preview(entry) + '</div></article>')
    output.mkdir(parents=True, exist_ok=True)
    assets = output / "assets"
    assets.mkdir(exist_ok=True)
    versions = {}
    for name in ["notes.css", "notes.js"]:
        data = (ROOT / "web" / name).read_bytes()
        hashed = f'{Path(name).stem}-{hashlib.sha256(data).hexdigest()[:12]}{Path(name).suffix}'
        (assets / hashed).write_bytes(data)
        versions[name] = "assets/" + hashed
    pdf_href, pdf_digest = "paper-reading-notes.pdf", None
    if pdf is not None:
        data = pdf.read_bytes()
        if not data.startswith(b"%PDF-"):
            raise ValueError("Invalid PDF input")
        pdf_digest = hashlib.sha256(data).hexdigest()
        pdf_href = f"paper-reading-notes-{pdf_digest[:16]}.pdf"
        (output / pdf_href).write_bytes(data)
        (output / "paper-reading-notes.pdf").write_bytes(data)
    digest = hashlib.sha256()
    for rel in inputs:
        digest.update(rel.encode() + b"\0" + (ROOT / rel).read_bytes() + b"\0")
    manifest = {"source_revision": revision, "source_date": source_date,
                "source_sha256": digest.hexdigest(), "pdf_sha256": pdf_digest,
                "pdf_file": pdf_href, "paper_count": len(manifest_papers),
                "section_count": len(sections), "reference_count": len(order),
                "papers": manifest_papers, "reference_keys": order, "inputs": inputs}
    (output / "build-info.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (output / "references.bib").write_text(bibtext)
    payload = json.dumps({key: entries[key]["raw"] for key in order}, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = (ROOT / "web" / "index.template.html").read_text()
    replacements = {"CSS": versions["notes.css"], "JS": versions["notes.js"], "PDF": pdf_href,
                    "REVISION": esc(revision), "SHORT_REVISION": esc(revision[:12]),
                    "SOURCE_DATE": esc(source_date), "PAPER_COUNT": str(len(manifest_papers)),
                    "SECTION_COUNT": str(len(sections)), "REFERENCE_COUNT": str(len(order)),
                    "NAV": "\n".join(sidebar), "OPTIONS": "\n".join(options),
                    "CARDS": "\n".join(cards), "REFERENCES": "\n".join(refs_html), "DATA": payload}
    template = re.sub(r"@@([A-Z_]+)@@", lambda m: replacements[m.group(1)], template)
    (output / "index.html").write_text(template)
    (output / ".nojekyll").touch()
    print(f'HTML: {len(manifest_papers)} papers, {len(sections)} sections, {len(order)} cited references')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    parser.add_argument("--revision", default="local-preview")
    parser.add_argument("--source-date", default="")
    parser.add_argument("--pdf", type=Path, default=ROOT / "paper-reading-notes.pdf")
    args = parser.parse_args()
    if shutil.which("pandoc") is None:
        parser.error("pandoc is required")
    try:
        generate(args.output, args.revision, args.source_date, args.pdf)
    except (ValueError, OSError, KeyError, IndexError) as exc:
        print(f"HTML build failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
