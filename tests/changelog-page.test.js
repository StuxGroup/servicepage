// The changelog page's Markdown renderer (the inline script in changelog.html), run against
// stand-in browser objects: Date Version headings, section order and the badge palette.
// Run with: node tests/changelog-page.test.js   (tests/run.sh runs it for you)
// Copyright (c) Stux.Group. All Rights Reserved.
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const ROOT = path.join(__dirname, '..');
const page = fs.readFileSync(path.join(ROOT, 'changelog.html'), 'utf8');
const script = [...page.matchAll(/<script>([\s\S]*?)<\/script>/g)]
    .map((m) => m[1]).find((s) => s.includes('renderChangelog'));

/** Renders a changelog through the page's own script and resolves with the HTML it writes. */
function render(markdown) {
    const target = { innerHTML: '' };
    let done;
    const finished = new Promise((resolve) => { done = resolve; });
    const context = {
        document: { getElementById: () => target },
        fetch: () => Promise.resolve({ ok: true, text: () => Promise.resolve(markdown) }),
    };
    vm.runInNewContext(script, context);
    setTimeout(function wait() { target.innerHTML.includes('Loading') || target.innerHTML === '' ? setTimeout(wait, 5) : done(target.innerHTML); }, 5);
    return finished;
}

const versions = (html) => [...html.matchAll(/<h3 class="changelog-version">([^<]*)<\/h3>/g)].map((m) => m[1]);
const badges = (html) => [...html.matchAll(/changelog-label changelog-label-([a-z]+)"/g)].map((m) => m[1]);

test('renders Date Version headings, same-day releases included', async () => {
    const html = await render('# Changelog\n\nIntro.\n\n## v26.10.23-1\n\n### Fixed\n\n- b\n\n## v26.10.23\n\n### Added\n\n- a\n\n## v1.1.5\n\n### Changed\n\n- c\n');
    assert.deepStrictEqual(versions(html), ['v26.10.23-1', 'v26.10.23', 'v1.1.5']);
});

test('sorts sections into Added, Changed, Fixed, Removed, Security, Deprecated, unknown last', async () => {
    const html = await render('## v26.10.23\n\n### Deprecated\n\n- f\n\n### Notes\n\n- g\n\n### Security\n\n- e\n\n### Removed\n\n- d\n\n### Fixed\n\n- c\n\n### Changed\n\n- b\n\n### Added\n\n- a\n');
    assert.deepStrictEqual(badges(html), ['added', 'changed', 'fixed', 'removed', 'security', 'deprecated']);
    assert.ok(html.indexOf('changelog-label-deprecated') < html.indexOf('<h4 class="changelog-section">Notes</h4>'));
});

test('renders the real CHANGELOG.md, newest entry being VERSION.md', async () => {
    const html = await render(fs.readFileSync(path.join(ROOT, 'CHANGELOG.md'), 'utf8'));
    const version = fs.readFileSync(path.join(ROOT, 'VERSION.md'), 'utf8').trim();
    assert.strictEqual(versions(html)[0], 'v' + version);
});

test('badge colours match the house palette', () => {
    const want = { added: '#2ecc71', changed: '#3ba7ff', fixed: '#ffa64d', removed: '#ff4d4d', security: '#b06bff', deprecated: '#8a8a94' };
    for (const [type, colour] of Object.entries(want)) {
        assert.match(page, new RegExp(String.raw`\n\s*\.changelog-label-` + type + String.raw`\s*\{ --cl: ` + colour + String.raw`; \}`), type);
    }
    assert.match(script, /\['Added', 'Changed', 'Fixed', 'Removed', 'Security', 'Deprecated'\]/);
});
