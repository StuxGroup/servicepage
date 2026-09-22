<p align="center">
  <img src="https://global.media.stux.group/logo.png" height="80" alt="Stux.Group Logo">
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

## Versioning and changelog

- The version lives in `VERSION.md` (a bare version string) — bump it on every release
- Every release gets a `CHANGELOG.md` entry using `### Added` / `### Changed` / `### Fixed` subsections — never a bare bullet list directly under a version heading
- `commit.sh` (bash) and `commit.bat` (Windows) read `VERSION.md` and handle the commit + `git tag` for a release — no need to edit them per release
