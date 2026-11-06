#!/bin/bash
# Stux.Group Servicepage - checks and smoke tests
# Usage: ./tests/run.sh   (needs bash, Python 3 and Node; the smoke tests also need PHP and curl,
#                          and are skipped when PHP isn't found. PHP=/path/to/php picks a binary.)
#
# 1. VERSION.md is a valid Date Version (https://datevers.ing), a real calendar date, not in the
#    future, and matches the newest "## v..." heading in CHANGELOG.md.
# 2. Every page carries the four icon tags, and the icon files are what the tags promise.
# 3. The Discord link previews (tests/test_discord_embeds.py).
# 4. The changelog page's renderer (tests/changelog-page.test.js).
# 5. Every page and icon is served by the dev server's router with the right status and type.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-$(command -v python3 || command -v python)}"
FAILS=0
PASSES=0

pass() { PASSES=$((PASSES + 1)); }
fail() { FAILS=$((FAILS + 1)); echo "FAIL: $*" >&2; }
check() { if [ "$1" = "$2" ]; then pass; else fail "$3 (expected '$2', got '$1')"; fi; }

# Reads a big-endian 32-bit integer at byte offset $2 of file $1.
u32be() { od -A n -t u1 -j "$2" -N 4 "$1" | awk '{ print $1 * 16777216 + $2 * 65536 + $3 * 256 + $4 }'; }
# Prints "WIDTHxHEIGHT colourtype" for a PNG file, or nothing if it isn't one.
png_info() {
    [ "$(od -A n -t x1 -N 8 "$1" | tr -d ' \n')" = "89504e470d0a1a0a" ] || return
    echo "$(u32be "$1" 16)x$(u32be "$1" 20) $(od -A n -t u1 -j 25 -N 1 "$1" | tr -d ' ')"
}

# --- 1. Version -------------------------------------------------------------------------------
DATEVER='^[0-9]{2}\.(0[1-9]|1[0-2])\.(0[1-9]|[12][0-9]|3[01])(-[1-9][0-9]*)?$'
VERSION="$(tr -d '[:space:]' < "$DIR/VERSION.md")"
if [[ "$VERSION" =~ $DATEVER ]]; then pass; else fail "VERSION.md holds '$VERSION', which isn't a Date Version"; fi
DATE="${VERSION%%-*}"
if [ "$(date -u -d "20${DATE//./-}" +%y.%m.%d 2>/dev/null)" = "$DATE" ]; then pass; else fail "$VERSION isn't a real calendar date"; fi
if [[ "$DATE" > "$(date -u +%y.%m.%d)" ]]; then fail "$VERSION is dated in the future (UTC)"; else pass; fi
NEWEST="$(grep -m 1 -E '^## v' "$DIR/CHANGELOG.md" | sed -E 's/^## v([^ ]+).*/\1/' | tr -d '\r')"
check "$NEWEST" "$VERSION" "the newest CHANGELOG.md entry should be the version in VERSION.md"

# The checks themselves: the Date Version pattern accepts and rejects what the spec says it should.
for v in 26.10.23 26.10.23-1 26.10.23-12 99.12.31; do
    if [[ "$v" =~ $DATEVER ]]; then pass; else fail "pattern should accept $v"; fi
done
for v in 3.15.0 26.10.23-0 26.13.01 26.10.32 v26.10.23 26.1.5 26.10.23-01; do
    if [[ "$v" =~ $DATEVER ]]; then fail "pattern should reject $v"; else pass; fi
done
if [ "$(date -u -d "2026-02-30" +%y.%m.%d 2>/dev/null)" = "26.02.30" ]; then fail "26.02.30 should not be a calendar date"; else pass; fi

# --- 2. Icon tags and files -------------------------------------------------------------------
TAGS=(
    '<link rel="icon" href="/favicon.ico" sizes="48x48">'
    '<link rel="icon" type="image/png" sizes="512x512" href="https://global.media.stux.group/icon-dark.png" media="(prefers-color-scheme: light)">'
    '<link rel="icon" type="image/png" sizes="512x512" href="https://global.media.stux.group/icon-light.png" media="(prefers-color-scheme: dark)">'
    '<link rel="apple-touch-icon" href="/apple-touch-icon.png">'
    '<link rel="manifest" href="/site.webmanifest">'
)
PAGE_LIST=()
while IFS= read -r f; do
    rel="${f#"$DIR"/}"
    PAGE_LIST+=("$rel")
    head="$(sed -n '/<head>/,/<\/head>/p' "$f")"
    for tag in "${TAGS[@]}"; do
        if grep -qF "$tag" <<< "$head"; then pass; else fail "$rel is missing $tag"; fi
    done
done < <(grep -rl --include='*.html' '<head' "$DIR" | grep -v -e '/node_modules/' -e '/\.git/' | sort)
[ "${#PAGE_LIST[@]}" -ge 11 ] && pass || fail "expected at least 11 pages, found ${#PAGE_LIST[@]}"

# favicon.ico: an ICO holding 16, 32 and 48px PNG images.
ICO="$DIR/favicon.ico"
check "$(od -A n -t u1 -N 6 "$ICO" | tr -s ' ' | sed 's/^ //;s/ $//')" "0 0 1 0 3 0" "favicon.ico should be an icon with 3 images"
SIZES=""
for i in 0 1 2; do
    entry=$((6 + i * 16))
    w="$(od -A n -t u1 -j "$entry" -N 1 "$ICO" | tr -d ' ')"
    offset="$(od -A n -t u4 -j $((entry + 12)) -N 4 --endian=little "$ICO" | tr -d ' ')"
    SIZES="$SIZES $w"
    check "$(od -A n -t x1 -j "$offset" -N 4 "$ICO" | tr -d ' \n')" "89504e47" "favicon.ico's ${w}px image should be a PNG"
done
check "$(tr ' ' '\n' <<< "$SIZES" | grep . | sort -n | tr '\n' ' ')" "16 32 48 " "favicon.ico sizes"

# PNGs: sizes, and the ones a platform puts on its own background are opaque (colour type 2, RGB).
check "$(png_info "$DIR/apple-touch-icon.png")" "180x180 2" "apple-touch-icon.png should be 180px and opaque"
check "$(png_info "$DIR/assets/img/icon-maskable-512.png")" "512x512 2" "icon-maskable-512.png should be 512px and opaque"
check "$(png_info "$DIR/assets/img/icon-512.png" | cut -d' ' -f1)" "512x512" "icon-512.png size"
check "$(png_info "$DIR/assets/img/icon-192.png" | cut -d' ' -f1)" "192x192" "icon-192.png size"

# site.webmanifest: valid JSON with the fields and icons browsers look for, all of which exist.
MANIFEST_CHECK="$("$PYTHON" - "$DIR" <<'PY'
import json, os, sys
root = sys.argv[1]
try:
    m = json.load(open(os.path.join(root, "site.webmanifest"), encoding="utf-8"))
except ValueError:
    print("not valid JSON"); sys.exit()
for k in ["name", "short_name", "start_url", "display", "theme_color", "background_color", "icons"]:
    if not m.get(k):
        print("missing " + k); sys.exit()
if m["start_url"] != "/":
    print("start_url should be /"); sys.exit()
if m["display"] != "browser":
    print("display should be browser"); sys.exit()
have = []
for i in m["icons"]:
    if not i["src"].startswith("/") or not os.path.isfile(os.path.join(root, i["src"].lstrip("/"))):
        print("missing icon " + i["src"]); sys.exit()
    have.append(i["sizes"] + (" " + i["purpose"] if "purpose" in i else ""))
for want in ["192x192", "512x512", "512x512 maskable"]:
    if want not in have:
        print("no " + want + " icon"); sys.exit()
print("ok")
PY
)"
check "$(tr -d '\r' <<< "$MANIFEST_CHECK")" "ok" "site.webmanifest"

# --- 3. Discord link previews -----------------------------------------------------------------
if "$PYTHON" -W error -m unittest discover -s "$DIR/tests" -t "$DIR/tests" -p 'test_*.py' 2>&1 | tail -n 3 | grep -q '^OK'; then
    pass
else
    "$PYTHON" -m unittest discover -s "$DIR/tests" -t "$DIR/tests" -p 'test_*.py' >&2
    fail "tests/test_discord_embeds.py"
fi

# --- 4. Changelog page renderer ---------------------------------------------------------------
if node --test "$DIR/tests/changelog-page.test.js" >/dev/null 2>&1; then
    pass
else
    node --test "$DIR/tests/changelog-page.test.js" >&2
    fail "tests/changelog-page.test.js"
fi

# --- 5. Smoke tests through the dev server's router -------------------------------------------
PHP="${PHP:-}"
if [ -z "$PHP" ]; then
    for candidate in php74 php7.4 "${LOCALAPPDATA:-/nonexistent}/Programs/PHP/7.4/php.exe" php; do
        if command -v "$candidate" >/dev/null 2>&1 || [ -x "$candidate" ]; then PHP="$candidate"; break; fi
    done
fi
if [ -z "$PHP" ]; then
    echo "PHP not found: skipping the smoke tests." >&2
else
    PORT="${TEST_PORT:-8098}"
    DEV_MODE=0 "$PHP" -S "127.0.0.1:$PORT" -t "$DIR" "$DIR/.github/dev-router.php" >/dev/null 2>&1 &
    SERVER=$!
    trap 'kill $SERVER 2>/dev/null' EXIT
    for _ in $(seq 1 50); do
        curl -s -o /dev/null "http://127.0.0.1:$PORT/" && break
        sleep 0.1
    done

    # Prints "STATUS CONTENT-TYPE" for a path (without any ;charset=...).
    fetch() { curl -s -o /dev/null -w '%{http_code} %{content_type}' "http://127.0.0.1:$PORT$1" | sed 's/;.*//'; }

    for url in / /changelog /legal /legal/privacy /legal/terms /legal/cookies /legal/imprint \
        /legal/disclaimer /legal/opt-out /sitemap/; do
        check "$(fetch "$url")" "200 text/html" "GET $url"
    done
    check "$(fetch /no-such-page | cut -d' ' -f1)" "404" "GET a missing page"
    # PHP's built-in server says image/x-icon on Windows and image/vnd.microsoft.icon on Linux (CI); both are fine.
    check "$(fetch /favicon.ico | sed 's#image/vnd\.microsoft\.icon#image/x-icon#')" "200 image/x-icon" "GET /favicon.ico"
    check "$(fetch /apple-touch-icon.png)" "200 image/png" "GET /apple-touch-icon.png"
    check "$(fetch /site.webmanifest)" "200 application/manifest+json" "GET /site.webmanifest"
    for img in icon-192.png icon-512.png icon-maskable-512.png; do
        check "$(fetch "/assets/img/$img")" "200 image/png" "GET /assets/img/$img"
    done
    check "$(fetch /CHANGELOG.md | cut -d' ' -f1)" "200" "GET /CHANGELOG.md (the changelog page reads it)"
fi

echo "$PASSES passed, $FAILS failed."
[ "$FAILS" -eq 0 ]
