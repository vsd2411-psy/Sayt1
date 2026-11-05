#!/usr/bin/env python3
"""Dependency-free checks for the PSYxAXIS static site."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = sorted(ROOT.rglob("*.html"))
SKIP_DIRS = {".git"}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.resources = []
        self.lang = None
        self.title = False
        self.description = False
        self.h1 = 0

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "html": self.lang = data.get("lang")
        if tag == "title": self.title = True
        if tag == "meta" and data.get("name") == "description": self.description = True
        if tag == "h1": self.h1 += 1
        if data.get("id"): self.ids.add(data["id"])
        if tag == "a" and data.get("href"): self.links.append(data["href"])
        if tag in {"img", "script", "link"}:
            value = data.get("src") or (data.get("href") if tag == "link" and data.get("rel") == "stylesheet" else None)
            if value: self.resources.append(value)


def local_target(page, raw):
    value = urlsplit(raw).path
    if not value or value.startswith(("mailto:", "tel:")):
        return None
    target = ROOT / value.lstrip("/") if value.startswith("/") else page.parent / value
    if value.endswith("/"): target /= "index.html"
    return target.resolve()


errors = []
pages = {}
for page in HTML_FILES:
    if any(part in SKIP_DIRS for part in page.parts): continue
    parser = PageParser()
    parser.feed(page.read_text(encoding="utf-8"))
    pages[page.resolve()] = parser
    rel = page.relative_to(ROOT)
    expected_lang = "uk" if rel.parts[0] == "ua" else "ru"
    if parser.lang != expected_lang: errors.append(f"{rel}: lang must be {expected_lang}")
    if not parser.title: errors.append(f"{rel}: title missing")
    if (rel.name == "index.html" or "spaces" in rel.parts) and not parser.description:
        errors.append(f"{rel}: description missing")
    if parser.h1 != 1: errors.append(f"{rel}: expected one h1, found {parser.h1}")

for page, parser in pages.items():
    for raw in parser.links + parser.resources:
        if urlsplit(raw).scheme or raw.startswith(("//", "#", "mailto:", "tel:")): continue
        target = local_target(page, raw)
        if target and not target.exists(): errors.append(f"{page.relative_to(ROOT)}: missing {raw}")
        fragment = urlsplit(raw).fragment
        if fragment and target in pages and fragment not in pages[target].ids:
            errors.append(f"{page.relative_to(ROOT)}: missing fragment #{fragment} in {target.relative_to(ROOT)}")

css = (ROOT / "styles.css").read_text(encoding="utf-8")
if css.count("{") != css.count("}"): errors.append("styles.css: unbalanced braces")
if re.search(r"styles\.css\?v=(?!20261105-1)", "\n".join(p.read_text(encoding="utf-8") for p in HTML_FILES)):
    errors.append("HTML: inconsistent styles.css cache version")

if errors:
    print("\n".join(f"ERROR: {error}" for error in sorted(set(errors))))
    sys.exit(1)
print(f"OK: checked {len(pages)} HTML pages, local links, resources, metadata and CSS structure")
