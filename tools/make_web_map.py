"""The site's world map: the app's wireframe treatment, re-rendered for a web canvas.

Why a second render rather than the app's file. Every proportion in
`design/tools/make_wireframe_map.py` is expressed in dp relative to a 407 dp phone panel --
the 15 dp mesh grid is 27 cells across the world, the coastline is 0.7 dp. Blown up to
1265 CSS px on a desktop that is a 3x enlargement: the cells become 46 px and the drawing
reads as a coarse zoomed fragment rather than as a map. Rendering the same geometry against
a wide design width restores the grain: the same 15 units of grid become 80 cells, and the
coastline stays a hairline.

Nothing about the technique changes -- same Natural Earth 1:110m land, same Miller
projection over lat +84..-56, same Douglas-Peucker outline, same Delaunay interior, same dot
on every other corner. Output is one file, `site/assets/img/worldmap.webp`, a pure alpha
mask so the CSS tints it from `--dot` and one file serves both themes.

Run from the repo root of the app (the geometry and the generator it reuses live
there): py -3 site/tools/make_web_map.py

Needs numpy, scipy and Pillow. Those are design-time only -- nothing the site
serves depends on them, and the committed .webp is what ships.
"""
import importlib.util
import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
GEN = REPO / "design" / "tools" / "make_wireframe_map.py"
OUT = REPO / "site" / "assets" / "img" / "worldmap.webp"

# The design width the dp proportions are read against, and the factor the file is
# rasterised at on top of it. The map is displayed at most ~800 CSS px wide (its height is
# capped, and the width follows the 2.03 aspect), so 1600 px is exactly 2x for a retina
# display. Measured: 1600 costs 151 KiB, 2000 costs 199 and 2400 costs 246, for pixels no
# screen will ever ask for.
DESIGN_WIDTH = 1200.0
SCALE = 1.333

spec = importlib.util.spec_from_file_location("wireframe", GEN)
wf = importlib.util.module_from_spec(spec)
sys.modules["wireframe"] = wf
spec.loader.exec_module(wf)

wf.PANEL_DP = DESIGN_WIDTH

alpha = wf.render(SCALE)
out = Image.merge("LA", (Image.new("L", alpha.size, 255), alpha)).convert("RGBA")
OUT.parent.mkdir(parents=True, exist_ok=True)
out.save(OUT, quality=90, method=6)
print("%s  %dx%d  %.0f KiB  (design width %.0f, scale %.1f, aspect %.3f)"
      % (OUT.name, out.width, out.height, OUT.stat().st_size / 1024,
         DESIGN_WIDTH, SCALE, wf.ASPECT))
