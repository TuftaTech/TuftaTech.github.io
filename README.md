# tuftatech.github.io

The download page for [YukariBox](https://github.com/TuftaTech/YukariBox), a sing-box
client for Android. Published by GitHub Pages from this repository's default branch at
<https://tuftatech.github.io/>.

Three pages, no build step, no dependencies. Pages serves the files as they are.

## Releasing a new version of the app changes nothing here

The download button is a static link to
`releases/latest/download/YukariBox-arm64.apk`. GitHub resolves `latest` at request
time and the asset name never carries a version, so the address is a constant. Cut a
release in the app repository, attach the APK under exactly that name, and this site is
already pointing at it.

The version, size and SHA-256 beside the button come from one call to the GitHub API and
are not written into the HTML. Nothing here is edited per release; there is no stale
number to forget.

That call is unauthenticated, so it lands under GitHub's limit of **60 requests an hour per
IP address**, shared with everything else on that address. A visitor over the limit gets a
403, and the page then shows the button, `ARM64 · ANDROID 9+` and nothing else: no version,
no size, no checksum, and no error either. That is the designed outcome rather than a fault
— the download is a static link that never touches the API, so it keeps working — but it
means a missing checksum is not evidence of a broken page. Check
<https://api.github.com/rate_limit> from the same address before concluding anything. Seen
for real on 2026-08-27: the limit was exhausted on the development machine, the block was
correctly absent, and it came back the moment the window rolled over.

## Editing

| File | What it owns |
|---|---|
| `index.html` | the download page and why this client rather than another |
| `help.html` | the documentation: ten sections with a table of contents |
| `legal.html` | what is collected (nothing), the permissions and why, the licences |
| `assets/tokens.css` | **every colour value in the project**, light and dark |
| `assets/site.css` | layout and components — `var(--…)` only, never a literal |
| `assets/site.js` | the language switch and the release lookup |
| `assets/img/` | the map, the mascot, three screenshots, the touch icon |
| `favicon.ico` | the tab icon: 16, 32 and 48 in one file, at the root on purpose |
| `tools/check.py` | the structural checks below |
| `tools/make_web_map.py` | regenerates `assets/img/worldmap.webp` — never hand-edit it |
| `tools/make_favicon.py` | regenerates `favicon.ico` and `assets/img/icon-180.png` — likewise |

Both languages ship in the HTML as text, one hidden by CSS on `<html lang>`. A string is
added as a pair:

```html
<span lang="en" data-lang="en" data-key="some.key">English</span>
<span lang="ru" data-lang="ru" data-key="some.key">Русский</span>
```

That is what keeps the page whole with JavaScript switched off, and `check.py` fails the
build if one half of a pair is missing.

## The map

`assets/img/worldmap.webp` is generated, not drawn: `tools/make_web_map.py` reuses the app's
own `design/tools/make_wireframe_map.py` — same Natural Earth coastlines, same Miller
projection, same Douglas-Peucker outline and Delaunay interior — and re-renders it against a
wide design width. That last part is the whole reason a second render exists: every
proportion in the app's generator is relative to a 407 dp phone panel, so displayed at
desktop width the mesh cells and coastlines are enlarged threefold and the map reads as a
coarse zoomed fragment. Run the tool from the app's repo root; it needs numpy, scipy and
Pillow, which are design-time only — the committed `.webp` is what ships.

It is a pure alpha mask, tinted from `--dot`, so one file serves both themes. It is sized to
`--stage-h` — the same height the hero's copy block claims — so it sits behind the heading and
the lede rather than only behind the button, and its width follows the 2.03 aspect, which is
what keeps the whole world in frame at any viewport. Its side edges are faded by
`--mask-edge-fade` so it dissolves into the page instead of ending in a cut through a
continent. Below roughly 760 px the page width wins and the map covers the lower part of the
stage only: on a phone the copy needs the contrast more than the picture needs the room.

Its `opacity` is measured, not chosen. The lede is the smallest text on the page that has to
stay readable, and it now sits over the map; sampling the rendered pixels behind that
paragraph with the text hidden gives a worst-pixel contrast of 4.88:1 at 0.55 against 4.60:1
at 0.65 — the WCAG floor is 4.5, and a threshold with no margin is not a pass worth keeping.
Change the opacity and re-measure.

## The tab icon

`favicon.ico` and `assets/img/icon-180.png` are the app's launcher icon, downscaled by
`tools/make_favicon.py` from `app/src/main/ic_launcher-playstore.png` in the app repository, so
the tab, the bookmark and the home-screen shortcut all show the same thing. Regenerate them;
never hand-edit them.

They are the one place on this site that carries colour, and deliberately so. The rule
`check.py` enforces is about the page, and the launcher icon these are cut from has always been
in colour for the same reason: a tab strip and a home screen are the browser's and the
operating system's surfaces, not this site's. The checker reads only `.css`, `.html` and `.js`,
so nothing here is being smuggled past it.

Three details are load-bearing. The near-white background is kept rather than keyed out — it is
`#FEFEFE`, which is the page's own `--page`, so the icon dissolves into a light tab strip and
reads as a white tile in a dark one; made transparent, the dark hair would vanish against a
dark tab. The corners are left square, because Android masks the adaptive icon to the
launcher's shape and iOS masks `apple-touch-icon` itself, while desktop browsers mask nothing —
rounding here would pre-empt exactly one of the three, wrongly. And `favicon.ico` sits at the
root rather than in `assets/`, because a browser asks for `/favicon.ico` whether or not the
HTML says to: that unanswered request was the only 404 the console showed on the live site.

## Checking

```bash
py -3 -m unittest discover -s tools    # the checker's own tests
py -3 tools/check.py                   # the site
py -3 -m http.server 8080              # then open http://localhost:8080/
```

The theme follows the operating system until the visitor clicks the control in the bar,
which then toggles light and dark. **Two states, not three** — a `system` state was tried
and removed: whichever of light and dark matched the visitor's OS rendered identically to
it, so one click in every cycle changed nothing on screen, which reads as a broken button.
The trade is that the choice cannot be handed back to the OS once made.

The choice is applied by a small inline script in the `<head>` before first paint, so the
page never flashes the wrong theme and then corrects itself; `assets/tokens.css` therefore
carries the dark values twice — once under the media query for visitors who never touch
the control, once under `[data-theme="dark"]` for those who do.

`check.py` asserts four things, none of which are matters of taste:

- every colour value has `R == G == B` — the app is monochrome by construction;
- no colour value lives outside `tokens.css`;
- no `border-radius: 999px`, and `50%` only on a real circle — the design system measures
  radii of 5, 10 and 11 px and has no pills;
- every `data-key` exists in both languages.
