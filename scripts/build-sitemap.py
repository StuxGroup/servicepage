#!/usr/bin/env python3
"""Regenerate sitemap.xml and sitemap/index.html for this static site.

Run from anywhere: python scripts/build-sitemap.py
The page list is PAGES below; each page's <lastmod> is the date of the last git commit that
touched its source file (left out if the file has no history yet). URLs always use BASE_URL,
the site's production address.

Copyright (c) Stux.Group. All Rights Reserved.
"""
import html
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://" + (ROOT / "CNAME").read_text(encoding="utf-8").strip()

# (path, source file, label, description, priority, changefreq)
PAGES = [
    ("/", "index.html", "Home", "{title}", "1.0", "monthly"),
    ("/changelog", "changelog.html", "Changelog", "What's changed on this page, release by release.", "0.4", "monthly"),
    ("/legal", "legal.html", "Boring Legal Stuff", "Privacy, terms, cookies, imprint, disclaimer and opt-out preferences, in one place.", "0.3", "yearly"),
    ("/legal/privacy", "legal/privacy.html", "Privacy Policy", "What's collected (almost nothing) and why.", "0.2", "yearly"),
    ("/legal/terms", "legal/terms.html", "Terms and Ethics", "The simple rules for using this page.", "0.2", "yearly"),
    ("/legal/cookies", "legal/cookies.html", "Cookies Policy", "localStorage only, with no tracking cookies.", "0.2", "yearly"),
    ("/legal/imprint", "legal/imprint.html", "Imprint", "Who runs this page, and how to reach them.", "0.2", "yearly"),
    ("/legal/disclaimer", "legal/disclaimer.html", "Disclaimer", "Copyright, accuracy, and third-party links.", "0.2", "yearly"),
    ("/legal/opt-out", "legal/opt-out.html", "Opt-Out Preferences", "There's nothing sold, so nothing to opt out of.", "0.2", "yearly"),
    ("/sitemap/", "sitemap/index.html", "Sitemap", "Every page on this site, with a link to the XML version.", "0.1", "monthly"),
]


def lastmod(rel: str) -> str:
    out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    return out


def page_title() -> str:
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    start = text.index("<title>") + len("<title>")
    return html.unescape(text[start:text.index("</title>", start)])


def build_xml(title: str) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, src, _label, _desc, priority, freq in PAGES:
        lines.append("  <url>")
        lines.append(f"    <loc>{html.escape(BASE_URL + loc)}</loc>")
        mod = lastmod(src)
        if mod:
            lines.append(f"    <lastmod>{mod}</lastmod>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build_html(title: str) -> str:
    """The sitemap page, in the legal page's layout (header, theme, footer, banner)."""
    legal = (ROOT / "legal.html").read_text(encoding="utf-8")
    head_end = legal.index("<main")
    main_end = legal.index("</main>") + len("</main>")
    shell_head, shell_foot = legal[:head_end], legal[main_end:]

    def up(m: "re.Match") -> str:
        # The sitemap lives one folder down, so relative links in the shared shell need "../".
        attr, url = m.group(1), m.group(2)
        if url.startswith(("http:", "https:", "/", "#", "mailto:", "data:", "//")):
            return m.group(0)
        return f'{attr}="../{url[2:] if url.startswith("./") else url}"'

    rel = re.compile(r'(href|src)="([^"]*)"')
    shell_head = rel.sub(up, shell_head)
    shell_foot = rel.sub(up, shell_foot)
    shell_head = re.sub(r"<title>Legal(.*?)</title>", lambda m: "<title>Sitemap" + m.group(1) + "</title>", shell_head, count=1)
    desc_start = shell_head.index('<meta name="description" content="') + len('<meta name="description" content="')
    desc_end = shell_head.index('">', desc_start)
    shell_head = shell_head[:desc_start] + "Every page on this site, with a link to the XML sitemap." + shell_head[desc_end:]
    accent = "var(--accent)" if "--accent:" in shell_head else "var(--red)"
    css = "        .legal-card .url { display: block; margin: 0 0 6px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.04em; color: " + accent + "; overflow-wrap: anywhere; }"
    shell_head = shell_head.replace("    </style>", css + "\n    </style>", 1)
    cards = []
    for loc, _src, label, desc, _p, _f in PAGES:
        desc = desc.format(title=title)
        href = ".." + loc if loc != "/" else "../"
        cards.append(f"""        <a href="{html.escape(href)}" class="legal-card">
            <span class="url">{html.escape(BASE_URL + loc)}</span>
            <h3>{html.escape(label)}</h3>
            <p>{html.escape(desc)}</p>
        </a>""")
    main = f"""<main>
    <h1>Sitemap</h1>
    <p class="subtitle">Every page on this site. Looking for the XML version? <a href="../sitemap.xml">sitemap.xml</a></p>

    <div class="legal-grid">
{chr(10).join(cards)}
    </div>
</main>"""
    notice = "<!-- Generated by scripts/build-sitemap.py; edit the PAGES list there, then re-run it. -->\n"
    return shell_head.replace("<body>\n", "<body>\n" + notice, 1) + main + shell_foot


def main() -> None:
    title = page_title()
    (ROOT / "sitemap").mkdir(exist_ok=True)
    (ROOT / "sitemap" / "index.html").write_text(build_html(title), encoding="utf-8", newline="\n")
    (ROOT / "sitemap.xml").write_text(build_xml(title), encoding="utf-8", newline="\n")
    robots = ROOT / "robots.txt"
    line = f"Sitemap: {BASE_URL}/sitemap.xml"
    text = robots.read_text(encoding="utf-8") if robots.exists() else "User-agent: *\nAllow: /\n"
    if line not in text:
        text = text.rstrip("\n") + "\n\n" + line + "\n"
    robots.write_text(text, encoding="utf-8", newline="\n")
    print(f"Wrote sitemap.xml, sitemap/index.html and robots.txt for {BASE_URL} ({len(PAGES)} pages)")


if __name__ == "__main__":
    main()
