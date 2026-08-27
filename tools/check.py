"""Structural checks for the YukariBox download site.

Stdlib only, no dependencies -- the site has none and this must not be the
first. Every check returns a list of violations; empty means clean.
"""
import re
import sys
from pathlib import Path

HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RGB = re.compile(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)")
RADIUS = re.compile(r"border-radius\s*:\s*([^;}]+)")
URL = re.compile(r"https?://[^\s\"'()<>]+")
TAG = re.compile(r"<[^>]*data-lang=\"(en|ru)\"[^>]*>")
KEY = re.compile(r"data-key=\"([^\"]+)\"")

ALLOWED_RADII = {"0", "2px", "3px", "5px", "10px", "11px", "inherit", "0px"}
ALLOWED_HOSTS = {"github.com", "api.github.com", "objects.githubusercontent.com"}


def colour_literals(text):
    """Every hex colour literal in `text`, in source order."""
    return HEX.findall(text)


def _channels(literal):
    body = literal.lstrip("#")
    if len(body) in (3, 4):
        body = "".join(c * 2 for c in body[:3])
    return [int(body[i:i + 2], 16) for i in (0, 2, 4)]


def bad_greys(text):
    """Colour literals whose channels are not all equal -- i.e. that carry hue."""
    out = []
    for literal in colour_literals(text):
        r, g, b = _channels(literal)
        if not (r == g == b):
            out.append(literal)
    for match in RGB.finditer(text):
        r, g, b = (int(v) for v in match.groups())
        if not (r == g == b):
            out.append(match.group(0) + ")")
    return out


def bad_radii(text):
    """Radii outside the allowed set. `50%` is allowed only in a `.circle` rule."""
    out = []
    for match in RADIUS.finditer(text):
        value = match.group(1).strip()
        if value == "50%":
            head = text[max(0, match.start() - 200):match.start()]
            if ".circle" not in head.split("}")[-1]:
                out.append(value)
            continue
        for part in value.split():
            if part not in ALLOWED_RADII and not part.startswith("var("):
                out.append(part)
    return out


def foreign_hosts(text):
    """Absolute URLs pointing anywhere but GitHub."""
    out = []
    for url in URL.findall(text):
        host = url.split("//", 1)[1].split("/", 1)[0].split(":")[0]
        if host not in ALLOWED_HOSTS:
            out.append(url)
    return out


def lang_parity(html):
    """Every data-key must appear once for `en` and once for `ru`."""
    seen = {}
    for tag in TAG.finditer(html):
        lang = tag.group(1)
        key = KEY.search(tag.group(0))
        if not key:
            seen.setdefault("(no data-key)", set()).add(lang)
            continue
        seen.setdefault(key.group(1), set()).add(lang)
    out = []
    for key in sorted(seen):
        langs = seen[key]
        if langs == {"en"}:
            out.append(key + ": en without ru")
        elif langs == {"ru"}:
            out.append(key + ": ru without en")
    return out


def main(root):
    root = Path(root)
    failures = []

    tokens = root / "assets" / "tokens.css"
    if tokens.exists():
        for literal in bad_greys(tokens.read_text(encoding="utf-8")):
            failures.append("tokens.css: %s carries hue" % literal)

    for path in sorted(root.rglob("*")):
        if path.is_dir() or path.suffix not in (".css", ".html", ".js"):
            continue
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        if rel != "assets/tokens.css":
            for literal in colour_literals(text):
                failures.append("%s: colour literal %s outside tokens.css" % (rel, literal))
            for literal in bad_greys(text):
                failures.append("%s: %s carries hue" % (rel, literal))
        for radius in bad_radii(text):
            failures.append("%s: radius %s not allowed" % (rel, radius))
        for url in foreign_hosts(text):
            failures.append("%s: third-party host %s" % (rel, url))
        if path.suffix == ".html":
            for problem in lang_parity(text):
                failures.append("%s: %s" % (rel, problem))

    for line in failures:
        print("FAIL " + line)
    print("%d violation(s)" % len(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(Path(__file__).resolve().parent.parent))
