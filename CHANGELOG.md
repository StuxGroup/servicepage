# Changelog

All notable changes to Servicepage are documented here.

This project uses [Date Versioning](https://datevers.ing): each version is the UTC date it was released, as `YY.MM.DD`, with `-1`, `-2` and so on for later releases the same day. Versions up to v1.1.5 used Semantic Versioning.

## v26.11.06-1

### Changed

- `README.md` is titled with the page's full name, Stux.Group Servicepage, as on services.stux.group, and lists what
  the page has now: the Boring Legal Stuff hub, the changelog page, the sitemap, the Discord link preview and the
  site banners
- `README.md`'s License section and footer come last again (the Local preview section had ended up after the
  footer), and its licence wording is corrected to say all rights are reserved: it said the project was open source
- The README's site links use https

## v26.11.06

### Added

- A `test` branch: work goes there and reaches `main` only through a reviewed pull request, and merging is what deploys the site. CI now runs on `test` too

### Fixed

- **Short, wide windows:** the logo, the `{No Service Here}` heading, the message and the footer no longer crowd into or overlap each other in short, wide windows (around 2:1, such as 1600x800). They now stack in one column with gaps that can't collapse, the logo and heading are sized by the window's height as well as its width, and a window too short for everything scrolls instead of overlapping

## v26.10.26

### Security

- CI runs on Node.js 24 instead of the end-of-life Node.js 20, which has no fix for the Brotli decoder vulnerability CVE-2026-111497

## v26.10.23

### Added

- Discord link previews: every page except the 404 page carries a `discord:component-embed` block in its `<head>`, in the Stux.Group red with the Stux.Group icon. The home page shows what this placeholder is with links to Stux.Group, all services and Bluesky; the changelog, the legal hub and the other pages get their own preview. The blocks are pre-built and committed by `python scripts/build-discord-embeds.py` (which `build-sitemap.py` now runs too), page text is escaped so it shows as plain text, a preview over Discord's 3,000-byte limit is left out, and the page title and description stay as the fallback
- A full favicon set: `favicon.ico` (16, 32 and 48px), `apple-touch-icon.png` (on a white background, so iOS doesn't fill it with black) and `site.webmanifest` with 192px, 512px and maskable 512px icons, linked from every page, the 404 page included; the dev server serves the manifest as `application/manifest+json` like GitHub Pages does
- A test suite, `tests/run.sh`, run by CI: the version and changelog, the Discord previews, the favicon set, the changelog page's parser and, when PHP is installed, a smoke test of every page through the dev server

### Changed

- Switched from Semantic Versioning (last version v1.1.5) to [Date Versioning](https://datevers.ing): versions are now the UTC release date as `YY.MM.DD`, plus `-1`, `-2`... for later releases the same day
- `commit.sh` and `commit.bat` refuse a `VERSION.md` that isn't a real Date Version or is dated in the future (UTC), and warn when it's dated before today; they also name the project as Servicepage rather than Soonpage in tag messages

## v1.1.5

### Changed

- The favicon follows the browser's light or dark theme: the deep icon (`icon-dark.png`) on light and the bright one (`icon-light.png`) on dark, straight from the brand's media host, so a brand colour change is just a new file there
- The logos and icons in the Markdown docs (README and the like) follow GitHub's light or dark theme, using each brand's `logo-light`/`logo-dark` and `icon-light`/`icon-dark` files

## v1.1.4

### Fixed

- The footer's copyright line had a second, hidden copy of the © icon inside its screen-reader text; it's gone, leaving the visible icon and a plain "©" for screen readers. Nothing changes on screen

## v1.1.3

### Fixed

- The animated "{No Service Here}" heading is no longer cut off at the sides: it's wider than the other pages' headings, so its drawing area is now wide enough to fit it, braces included, at every screen size

## v1.1.2

### Changed

- The footer's copyright year is worked out automatically: the start year alone in the first year, then START–CURRENT

## v1.1.1

### Fixed

- The footer's Created-with icons are optically sized, so the heart no longer looks bigger than the code and coffee icons

## v1.1.0

### Added

- A dev-mode banner, the shared Stux site banner, shown on every page while `dev-server.sh`/`.bat` runs; `?banner=soon,maintenance,site` previews the other banner types locally, and production never shows one (`assets/site-banner.css`, `assets/site-banner.js`, `assets/site-banners.js`, `assets/dev-mode.js`)
- A "Created with love / code / coffee by Stux.Group" line in the footer of every page
- The footer brand line on every page: the Stux.Group mark and "A Stux.Group Service" (linking to services.stux.group), both muted until hovered or focused
- `/sitemap` (an HTML page in the site's layout listing every page) and `sitemap.xml`, committed as static files and regenerated with `python scripts/build-sitemap.py` (`lastmod` comes from each page's last git commit); `robots.txt` points at it and the footer links to it

### Changed

- `dev-server.sh`/`.bat` serve the site the way GitHub Pages does (`/changelog` for `changelog.html`, the 404 page for missing paths) through `.github/dev-router.php`, turn DEV_MODE on by default (`--no-dev-mode` to preview production), and run on PHP 7.4 like the other Stux projects (`PHP_BIN`, `php74`, or `%LOCALAPPDATA%\Programs\PHP\7.4`, with a warning otherwise)
- The copyright symbol in the footers is an icon, with a visually hidden "©" so screen readers still read it

## v1.0.3

### Changed
- `changelog.html` now sorts each release's `###` sections into a fixed order — Added, Changed, Fixed, Removed, Security, Deprecated — at render time, rather than trusting the order `CHANGELOG.md` lists them in; unknown section types go last
- Changelog type badges now use the fixed family palette — Added `#2ecc71`, Changed `#3ba7ff`, Fixed `#ffa64d`, Removed `#ff4d4d`, Security `#b06bff`, Deprecated `#8a8a94` — as tinted badges (coloured text on a light tint of the same hue), with darker variants of each for the light theme

## v1.0.2

### Added
- GitHub Actions CI (`.github/workflows/ci.yml`): validates `index.html` and lints all Markdown on every push and pull request against `main`. Added `.markdownlint.json` and `.htmlvalidate.json` matching this org's established doc/markup style.

### Fixed
- GitHub Pages was using the legacy branch-deploy build system, which can silently stop auto-deploying with no error recorded anywhere. Switched to GitHub Actions-based Pages deployment (`.github/workflows/pages.yml`), making every deploy an ordinary, observable CI run instead.

## v1.0.1

### Fixed
- The footer's changelog/version link (and other footer links) turned accent-purple once visited — `a:visited` carries a pseudo-class, giving it higher CSS specificity than the plain `footer a` selector meant to keep footer links muted, so it kept winning regardless of source order. Every affected footer link now also styles `footer a:visited` explicitly.

## v1.0.0

### Added

- Initial release: a placeholder page shown when a Stux.Group service hasn't
  been set up yet, with self-hosted Barlow font and Font Awesome (brands), a
  "Boring Legal Stuff" legal hub (`legal.html` + `legal/`), `changelog.html`
  that fetches and renders `CHANGELOG.md` at runtime, a version indicator
  fetched live from `VERSION.md`, cross-origin `postMessage` title sync, a
  custom `404.html` error page, and `dev-server.sh` / `dev-server.bat` for
  local previewing
