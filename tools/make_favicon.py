"""Cut the browser-tab icons out of the app's launcher icon.

The tab icon has to be the app's icon, or the bookmark and the home-screen
shortcut disagree about what this thing looks like. The source is the one square
rendering of it that exists, `app/src/main/ic_launcher-playstore.png` -- 512x512,
opaque, the figure filling 502 of the 512 rows -- so this is a downscale and
nothing more: no crop, no recolour, no rounding.

Three decisions in it, each with a reason:

- **The colour stays.** Every pixel the *page* draws is neutral by construction and
  `check.py` enforces it, but that rule is about the interface; the launcher icon is
  already in colour for the same reason this is -- a tab strip and a home screen are
  the browser's and the OS's surfaces, not the site's. `check.py` reads only .css,
  .html and .js, so nothing here is being smuggled past it.
- **The near-white background stays, and is not made transparent.** It is #FEFEFE,
  which happens to be the page's own `--page`, so the icon dissolves into a light
  tab strip and reads as a white tile in a dark one. Keyed out instead, the dark hair
  would sit on a dark tab with nothing behind it and disappear.
- **The corners stay square.** Android masks the adaptive icon to whatever shape the
  launcher uses and iOS masks `apple-touch-icon` itself; desktop browsers mask
  nothing. Rounding here would only pre-empt one of the three, wrongly.

Outputs, and why each exists:

  favicon.ico             16 + 32 + 48 in one file, at the site root, because a
                          browser asks for `/favicon.ico` whether or not the HTML
                          says to -- that unanswered request was a 404 in the console
  assets/img/icon-180.png the `apple-touch-icon`: iOS ignores .ico entirely and this
                          is the size it wants for a home-screen bookmark

Run from either repo root: python site/tools/make_favicon.py
Needs Pillow, which is design-time only, like `make_web_map.py`. The committed
outputs are what ships -- never hand-edit them, re-run this.
"""

import sys
from pathlib import Path

from PIL import Image, ImageFilter

SITE = Path(__file__).resolve().parents[1]
SOURCE = SITE.parent / "app" / "src" / "main" / "ic_launcher-playstore.png"
ICO_SIZES = (16, 32, 48)
TOUCH = 180
# Small sizes lose the tank outline on the shirt to the resampler; a light unsharp
# pass holds it. Above 64 px there is nothing to recover, so it is not applied.
SHARPEN_UPTO = 64


def scaled(src, size):
    out = src.resize((size, size), Image.LANCZOS)
    if size <= SHARPEN_UPTO:
        out = out.filter(ImageFilter.UnsharpMask(radius=0.6, percent=60, threshold=2))
    return out


def main():
    if not SOURCE.exists():
        print("source not found: %s" % SOURCE, file=sys.stderr)
        print("It lives in the app repository; this site repo ships the outputs only.",
              file=sys.stderr)
        return 1
    src = Image.open(SOURCE).convert("RGB")
    if src.size != (512, 512):
        print("unexpected source size %sx%s" % src.size, file=sys.stderr)
        return 1

    # Each frame is built here rather than left to the ICO writer, which resamples
    # from whatever base image it is handed and would skip the unsharp pass above.
    # Pillow matches an appended image to a requested size exactly, so the base is
    # the largest frame and the rest are appended.
    frames = {size: scaled(src, size) for size in ICO_SIZES}
    base = frames[max(ICO_SIZES)]
    ico = SITE / "favicon.ico"
    base.save(ico, format="ICO", sizes=[(s, s) for s in ICO_SIZES],
              append_images=[frames[s] for s in ICO_SIZES if s != max(ICO_SIZES)])
    print("wrote %s (%s, %d bytes)" % (ico.name, "+".join(map(str, ICO_SIZES)),
                                       ico.stat().st_size))

    touch = SITE / "assets" / "img" / ("icon-%d.png" % TOUCH)
    scaled(src, TOUCH).save(touch, format="PNG", optimize=True)
    print("wrote %s (%dx%d, %d bytes)" % (touch.name, TOUCH, TOUCH, touch.stat().st_size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
