<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://global.media.stux.group/logo-light.png"><source media="(prefers-color-scheme: light)" srcset="https://global.media.stux.group/logo-dark.png"><img src="https://global.media.stux.group/logo-dark.png" height="80" alt="Stux.Group Logo"></picture>
</p>

# Contributing to Servicepage

Servicepage is a [Stux.Group](https://stux.group) project — the repository is not
open to public pull requests. This document exists for anyone with write
access to the repo who wants to work on it consistently.

## Local setup

Just clone the repo and run `./dev-server.sh [port]` (or `dev-server.bat [port]`
on Windows) — starts PHP's built-in server pointed at the directory, since it's
a static site with no build step. Then open `http://127.0.0.1:8000`.

## Project conventions

- **Plain static HTML.** No framework, no build step. Barlow and Font Awesome
  are self-hosted under `assets/` (not loaded from a CDN) — if you bump the
  Font Awesome version or add font weights, update `assets/` and re-check
  which files each page actually references.
- Deployed via GitHub Pages to [servicepage.stux.group](https://servicepage.stux.group)
  (see `CNAME`) — pushing to `main` deploys automatically.
- This is a single page, not a soonpage/maintenancepage pair — a service
  either has been set up or it hasn't; there's no separate "under
  maintenance" state to design for.
- The sitemap (`sitemap.xml`, `sitemap/index.html`, `robots.txt`) is generated: after adding or removing a page, edit the `PAGES` list in `scripts/build-sitemap.py` and run `python scripts/build-sitemap.py`, then commit the result

## Branches

- Work on `test`, or on a feature branch off it. Never push to `main`
- Changes reach `main` only through a pull request from `test` into `main`, which needs CI to pass and is reviewed and merged by Leo
- Merging into `main` deploys the site to GitHub Pages; release commits and tags are made on `test` (`git push origin test --tags`) and go live when the pull request is merged

## Versioning and changelog

- Servicepage uses [Date Versioning](https://datevers.ing) (since v26.10.23; semver before that): the version is the UTC date of the release as `YY.MM.DD` (e.g. `26.10.23`), and a second release on the same UTC day is `26.10.23-1`, then `-2` and so on. Never a future date, and a released version is never reused
- The version lives in `VERSION.md` (the bare version, no `v`) — set it on every release. The `v` only appears in git tags, changelog headings and footers
- Every release gets a `CHANGELOG.md` entry using `### Added` / `### Changed` / `### Fixed` subsections — never a bare bullet list directly under a version heading
- `commit.sh` (bash) and `commit.bat` (Windows) read `VERSION.md`, refuse anything that isn't a valid Date Version, and handle the commit + `git tag` for a release — no need to edit them per release. `bash tests/run.sh` checks the version, icons, Discord previews and pages
