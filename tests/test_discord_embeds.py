"""The Discord link previews (scripts/build-discord-embeds.py), checked against Discord's rules:
one Container at the root, link buttons using only allowed keys, at most 40 components and
3,000 bytes at most. https://docs.discord.com/developers/link-previews/component-embeds

Run with: python -m unittest discover -s tests   (tests/run.sh runs it for you)

Copyright (c) Stux.Group. All Rights Reserved.
"""
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("build_discord_embeds", ROOT / "scripts" / "build-discord-embeds.py")
embeds = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(embeds)

OPEN = '<script id="discord:component-embed" type="application/json">'
TAG = re.compile(r'<script id="discord:component-embed" type="application/json">(.*?)</script>', re.S)


def payload(tag: str) -> dict:
    m = re.fullmatch(re.escape(OPEN) + r"(.*)</script>", tag, re.S)
    return json.loads(m.group(1)) if m else {}


def flatten(component: dict) -> list:
    """Every component in the tree, the root included."""
    found = [component]
    children = list(component.get("components", []))
    if "accessory" in component:
        children.append(component["accessory"])
    for child in children:
        found += flatten(child)
    return found


def headline(data: dict) -> str:
    """The text of the first section, where every preview puts its title and description."""
    return data["component"]["components"][0]["components"][0]["content"]


class DiscordEmbedTest(unittest.TestCase):
    def assertValidEmbed(self, tag: str, label: str) -> dict:
        self.assertTrue(tag.startswith(OPEN) and tag.endswith("</script>"), f"{label}: preview left out or malformed")
        body = tag[len(OPEN):-len("</script>")]
        self.assertLessEqual(len(body.encode("utf-8")), 3000, f"{label}: over 3,000 bytes")
        self.assertNotIn("</", body, f"{label}: could close the <script> early")
        data = json.loads(body)
        self.assertEqual(["component"], list(data), label)
        root = data["component"]
        self.assertEqual(17, root["type"], f"{label}: the root is one Container")
        self.assertEqual(0xD11010, root["accent_color"], f"{label}: the Stux.Group red")
        everything = flatten(root)
        self.assertLessEqual(len(everything), 40, label)
        for c in everything:
            self.assertIn(c["type"], [1, 2, 9, 10, 11, 12, 14, 17], label)
            if c["type"] == 17:
                self.assertIs(root, c, f"{label}: no nested Containers")
            if c["type"] == 2:
                self.assertEqual(5, c["style"], f"{label}: link buttons only")
                self.assertLessEqual(set(c), {"id", "type", "url", "style", "label", "emoji", "disabled"}, label)
                self.assertRegex(c["url"], r"^https?://", label)
        return data

    def test_every_page_carries_a_valid_committed_preview(self):
        for src, path, kind in embeds.PAGES:
            page = (ROOT / src).read_text(encoding="utf-8")
            head = page.split("</head>", 1)[0]
            tags = TAG.findall(head)
            self.assertEqual(1, len(tags), f"{src}: exactly one preview in <head>")
            data = self.assertValidEmbed(OPEN + tags[0] + "</script>", src)
            self.assertIn("(" + embeds.url(path) + ")", headline(data), f"{src}: links to its own page")

    def test_home_preview_says_what_the_page_is(self):
        data = payload(embeds.home_embed())
        self.assertIn("hasn't been set up yet", headline(data))
        labels = [b["label"] for b in data["component"]["components"][1]["components"]]
        self.assertEqual(["Stux.Group", "All services", "Bluesky"], labels)

    def test_legal_preview_links_all_six_pages(self):
        data = payload(embeds.legal_embed("Boring Legal Stuff", "d", embeds.url("/legal")))
        text = json.dumps(data)
        for _, slug in embeds.LEGAL_PAGES:
            self.assertIn(embeds.url("/legal/" + slug), text)

    def test_committed_previews_are_up_to_date(self):
        for src, path, kind in embeds.PAGES:
            page = (ROOT / src).read_text(encoding="utf-8")
            self.assertEqual(page, embeds.build(page, path, kind), f"{src}: run python scripts/build-discord-embeds.py")

    def test_error_page_gets_no_preview(self):
        self.assertNotIn("discord:component-embed", (ROOT / "404.html").read_text(encoding="utf-8"))
        self.assertNotIn("404.html", [src for src, _, _ in embeds.PAGES])

    def test_markdown_in_data_is_escaped(self):
        # One backslash before each special character, never a literal "$1" in its place.
        self.assertEqual(r"\*\*bold\*\* a\_b", embeds.discord_md("**bold** a_b"))
        self.assertEqual(r"\*\*bold\*\* \[x\](y) a\_b \~\~s\~\~ \`c\` \|\|p\|\| \\",
                         embeds.discord_md("**bold** [x](y) a_b ~~s~~ `c` ||p|| " + chr(92)))
        self.assertEqual(r"\# heading" + "\n" + r"\- list" + "\n" + r"\> quote" + "\nmid # - > stays",
                         embeds.discord_md("# heading\n- list\n> quote\nmid # - > stays"))
        self.assertNotIn("$1", embeds.discord_md("**bold** a_b"))

    def test_escaped_data_reaches_the_preview_intact(self):
        data = self.assertValidEmbed(embeds.page_embed("A_b *c*", "# not a heading", "https://example.com/x"), "escaped")
        self.assertIn(r"## [A\_b \*c\*](https://example.com/x)" + "\n" + r"\# not a heading", headline(data))
        self.assertNotIn("$1", headline(data))

    def test_script_cant_be_closed_early(self):
        tag = embeds.page_embed("</script><b>x", "d", "https://example.com/x")
        self.assertEqual(1, tag.count("</script>"), "only the tag's own closing")
        # JSON's <\/ decodes back to </, so Discord still shows the title as written
        self.assertIn("## [</script><b>x](", headline(payload(tag)))

    def test_over_the_limit_falls_back_to_the_plain_preview(self):
        tag = embeds.page_embed("T", "Long description. " * 300, "https://example.com/x")
        self.assertTrue(tag.startswith("<!-- discord:component-embed left out"))


if __name__ == "__main__":
    unittest.main()
