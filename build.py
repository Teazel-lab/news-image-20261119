#!/usr/bin/env python3
"""Build the one-page news image: data/stories.json -> render.html -> entry.png (1024x1024).

Usage: python3 build.py [path/to/stories.json]
Standard library only. Rendering uses headless google-chrome with locally installed fonts.
"""
import base64
import fcntl
import html
import json
import math
import os
import re
import select
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024

PAPER, INK, RULE = "#F4EFE4", "#1d1a16", "#b9b0a0"
REGIONS = [
    ("Europe", "#2f5fa8"),
    ("Americas", "#c0392b"),
    ("Asia", "#7b4fa0"),
    ("Africa", "#2e8b4a"),
    ("Middle East", "#b8862b"),
    ("Oceania", "#178a8a"),
    ("World/Space", "#6b6b6b"),
]
COLOR = dict(REGIONS)
OK_COL, CLAIM_COL = "#1f7a45", "#a85f00"

try:
    from illus import ILLUS  # id -> function(w, h) -> "<svg ...>"
except Exception:  # illus.py is written later; fall back to placeholders
    ILLUS = {}


def esc(s):
    return html.escape(str(s), quote=True)


def region_of(name):
    """Normalise a region label to one of the seven palette keys."""
    n = (name or "").strip().lower()
    for key, _ in REGIONS[:-1]:
        if n == key.lower():
            return key
    aliases = {
        "america": "Americas", "north america": "Americas", "south america": "Americas",
        "latin america": "Americas", "mideast": "Middle East", "pacific": "Oceania",
        "asia-pacific": "Asia",
    }
    return aliases.get(n, "World/Space")


# ----------------------------------------------------------------------------
# World map: hand-made coarse polygons, (lon, lat) pairs, equirectangular.
# ----------------------------------------------------------------------------
LAND = [
    # North + Central America
    [(-168, 66), (-156, 71), (-125, 70), (-105, 68), (-95, 69), (-85, 66), (-93, 59), (-82, 53),
     (-79, 58), (-77, 62), (-65, 60), (-56, 52), (-66, 48), (-70, 43), (-76, 35), (-81, 31),
     (-80, 25), (-83, 29), (-90, 29), (-97, 27), (-97, 21), (-91, 19), (-87, 21), (-87, 16),
     (-83, 10), (-78, 8), (-82, 8), (-87, 13), (-95, 16), (-105, 20), (-110, 24), (-114, 31),
     (-117, 33), (-124, 40), (-124, 48), (-130, 55), (-140, 60), (-152, 59), (-165, 55),
     (-160, 59), (-166, 62)],
    # Canadian Arctic islands (one blob)
    [(-120, 72), (-95, 74), (-80, 73), (-68, 68), (-75, 64), (-88, 70), (-110, 70)],
    # South America
    [(-78, 8), (-72, 12), (-62, 10), (-52, 5), (-50, 0), (-35, -6), (-39, -15), (-41, -22),
     (-48, -26), (-53, -34), (-58, -38), (-65, -42), (-68, -52), (-72, -53), (-75, -45),
     (-72, -30), (-70, -18), (-76, -14), (-81, -5), (-80, 1)],
    # Greenland
    [(-55, 82), (-30, 83), (-18, 76), (-22, 70), (-40, 64), (-45, 60), (-52, 65), (-58, 75),
     (-70, 77)],
    # Iceland
    [(-24, 65), (-18, 66.5), (-14, 65), (-19, 63.5)],
    # Great Britain, Ireland
    [(-5, 50), (1, 51), (1.5, 53), (-2, 56), (-2, 58.5), (-5, 58.5), (-6, 56), (-3, 54), (-5, 53)],
    [(-10, 52), (-6, 52), (-6, 55), (-9, 54.5)],
    # Scandinavia + Finland
    [(5, 58), (5, 62), (13, 67), (20, 70), (28, 71), (31, 69), (30, 61), (23, 60), (21, 63),
     (24, 65.5), (21, 65.5), (17, 61), (18, 59), (15, 56), (12, 56), (11, 59), (8, 58)],
    # Eurasia
    [(-9, 37), (-9, 43), (-1, 44), (-4, 48), (2, 51), (8, 54), (9, 57), (11, 56), (13, 54),
     (20, 55), (23, 59), (29, 60), (33, 66), (40, 66), (44, 68), (60, 69), (68, 72), (80, 73),
     (100, 77), (112, 74), (130, 71), (150, 71), (170, 69), (180, 68), (180, 65), (172, 61),
     (163, 58), (162, 54), (156, 51), (156, 57), (143, 59), (135, 54), (141, 48), (133, 43),
     (128, 40), (129, 35), (126, 34), (126, 38), (122, 40), (118, 39), (122, 37), (120, 32),
     (122, 30), (119, 25), (114, 22), (109, 21), (106, 19), (109, 13), (105, 9), (100, 13),
     (103, 6), (104, 1), (100, 5), (98, 9), (97, 16), (94, 17), (92, 22), (88, 22), (85, 19),
     (80, 15), (80, 10), (77, 8), (73, 17), (72, 21), (67, 24), (62, 25), (57, 26), (56, 27),
     (51, 28), (48, 30), (51, 25), (56, 24), (59, 22), (55, 17), (45, 13), (43, 13), (39, 21),
     (35, 28), (34, 31), (36, 36), (30, 36), (26, 38), (26, 40), (29, 41), (23, 40), (23, 37),
     (21, 38), (19, 42), (14, 45), (12, 44), (18, 40), (16, 38), (12, 42), (8, 44), (3, 43),
     (0, 39), (-2, 37), (-5, 36)],
    # Africa
    [(-17, 15), (-17, 21), (-13, 27), (-10, 30), (-6, 35), (0, 36), (10, 37), (11, 33), (20, 31),
     (25, 32), (32, 31), (34, 28), (37, 21), (39, 15), (43, 12), (51, 12), (48, 5), (41, -2),
     (39, -8), (40, -16), (35, -24), (32, -29), (26, -34), (19, -35), (15, -27), (12, -17),
     (14, -10), (9, -1), (9, 4), (4, 6), (-4, 5), (-8, 4), (-13, 8)],
    # Madagascar
    [(44, -16), (49, -12), (50, -16), (47, -25), (44, -23)],
    # Sri Lanka, Taiwan
    [(80, 9.5), (82, 7.5), (80.5, 6), (79.7, 8)],
    [(120, 22), (121.5, 25), (122, 24), (121, 22)],
    # Japan
    [(130, 31), (132, 34), (136, 34), (140, 35), (142, 40), (141, 42), (145, 44), (142, 45),
     (140, 42), (139, 38), (135, 36), (131, 34)],
    # Philippines
    [(120, 18), (122, 18), (124, 13), (126, 7), (122, 7), (120, 14)],
    # Indonesia: Sumatra, Java, Borneo, Sulawesi, New Guinea
    [(95, 5), (99, 3), (104, -3), (106, -6), (102, -4), (97, 1)],
    [(106, -6), (114, -7), (114, -8.6), (106, -7.6)],
    [(109, 1), (113, 3), (117, 7), (119, 1), (116, -4), (111, -3)],
    [(119, 1), (124, 1), (121, -1), (123, -5), (120, -5)],
    [(131, -1), (138, -2), (145, -4), (150, -10), (143, -9), (138, -8), (133, -4)],
    # Australia, Tasmania
    [(114, -22), (122, -17), (129, -15), (131, -12), (136, -12), (137, -16), (141, -17),
     (142, -11), (146, -19), (153, -26), (151, -34), (147, -38), (141, -38), (136, -35),
     (131, -32), (124, -33), (116, -35), (114, -28)],
    [(145, -41), (148, -41), (147, -43.5), (146, -43.5)],
    # New Zealand
    [(173, -35), (178, -38), (175, -41), (173, -39)],
    [(172, -41), (174, -42), (169, -46.5), (167, -45)],
    # Cuba, Hispaniola
    [(-84, 22), (-80, 23), (-75, 20), (-78, 20.5)],
    [(-74, 19.5), (-69, 19.5), (-69, 18), (-74, 18)],
]
WATER = [  # inland seas cut out of the Eurasia blob
    [(28, 42), (31, 46), (37, 45.5), (41, 42), (36, 41)],          # Black Sea
    [(48, 46), (53, 45), (54, 38), (50, 37), (49, 41)],            # Caspian
    [(-92, 58), (-80, 63), (-78, 56), (-82, 52), (-88, 56)],       # Hudson Bay
]
LAT_TOP, LAT_BOT = 75.0, -50.0
MAP_H = 166      # box height; longitude span is cropped to fit (seam in the Pacific)
LON0 = -133.0    # western edge of the map


def _miller(lat):
    return 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * math.radians(lat)))


def map_height(w):
    return MAP_H


def world_map(stories, w, h):
    """Miller-projection world map. Returns (svg, unplaced stories). Pins nudged apart."""
    k = h / (_miller(LAT_TOP) - _miller(LAT_BOT))
    W = 2 * math.pi * k  # width of the full 360 degrees at this scale
    top = _miller(LAT_TOP)

    def xy(lon, lat, wrap=True):
        d = lon - LON0
        if wrap:
            d %= 360.0
        return d / 360.0 * W, (top - _miller(lat)) * k

    def poly(pts, fill, extra=""):
        res = []
        for sh in (-W, 0.0, W):
            d = " ".join("%.1f,%.1f" % (x + sh, y) for x, y in (xy(lo, la, False) for lo, la in pts))
            res.append('<polygon points="%s" fill="%s"%s/>' % (d, fill, extra))
        return "".join(res)

    sea, land = "#e1e7e5", "#cbc0a6"
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (w, h, w, h),
           '<rect width="%d" height="%d" fill="%s"/>' % (w, h, sea)]
    for lat in (60, 30, 0, -30):
        y = xy(0, lat)[1]
        out.append('<line x1="0" y1="%.1f" x2="%d" y2="%.1f" stroke="#cfd6d3" stroke-width="%s"/>'
                   % (y, w, y, "0.9" if lat == 0 else "0.5"))
    out += [poly(p, land, ' stroke="#9a8d70" stroke-width="0.6" stroke-linejoin="round"') for p in LAND]
    out += [poly(p, sea) for p in WATER]

    R = 7.5
    pins, unplaced = [], []
    for s in stories:
        lon, lat = s.get("lon"), s.get("lat")
        if lon is None or lat is None:
            unplaced.append(s)
            continue
        x, y = xy(float(lon), float(lat))
        pins.append({"n": s["n"], "c": COLOR[region_of(s.get("region"))], "ox": x, "oy": y, "x": x, "y": y})
    for _ in range(400):
        moved = False
        for i in range(len(pins)):
            for j in range(i + 1, len(pins)):
                a, b = pins[i], pins[j]
                dx, dy = b["x"] - a["x"], b["y"] - a["y"]
                d = math.hypot(dx, dy)
                need = 2 * R + 1.0
                if d < need:
                    if d < 0.01:
                        ang = 2.4 * (i + 1)
                        dx, dy, d = math.cos(ang), math.sin(ang), 1.0
                    push = (need - d) / 2.0 + 0.05
                    a["x"] -= dx / d * push
                    a["y"] -= dy / d * push
                    b["x"] += dx / d * push
                    b["y"] += dy / d * push
                    moved = True
        for p in pins:
            p["x"] = min(max(p["x"], R + 1), w - R - 1)
            p["y"] = min(max(p["y"], R + 1), h - R - 1)
        if not moved:
            break
    for p in pins:
        if math.hypot(p["x"] - p["ox"], p["y"] - p["oy"]) > 3.0:
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>'
                       % (p["ox"], p["oy"], p["x"], p["y"], INK))
            out.append('<circle cx="%.1f" cy="%.1f" r="1.8" fill="%s"/>' % (p["ox"], p["oy"], INK))
    for p in pins:
        out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="#fff" stroke-width="1.2"/>'
                   % (p["x"], p["y"], R, p["c"]))
        out.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-family="Barlow Condensed" '
                   'font-weight="700" font-size="11" fill="#fff">%s</text>' % (p["x"], p["y"] + 3.8, esc(p["n"])))
    out.append("</svg>")
    return "".join(out), unplaced


# ----------------------------------------------------------------------------
# Page pieces
# ----------------------------------------------------------------------------
def illustration(story, w, h):
    fn = ILLUS.get(story.get("id"))
    svg = None
    if fn:
        try:
            svg = fn(w, h)
        except Exception as e:
            print("WARN illustration %s failed: %s" % (story.get("id"), e), file=sys.stderr)
    if not svg:
        print("WARN no illustration for id=%r (placeholder used)" % story.get("id"), file=sys.stderr)
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
               '<rect width="%d" height="%d" fill="#e9e2d2"/></svg>' % (w, h, w, h, w, h))
    # make sure the art fills (and is cropped to) the box whatever size it declares
    head, rest = svg.split(">", 1) if svg.lstrip().startswith("<svg") else ("<svg", svg)
    head = re.sub(r'\s(width|height|preserveAspectRatio)="[^"]*"', "", head)
    head += ' width="%d" height="%d" preserveAspectRatio="xMidYMid slice"' % (w, h)
    return head + ">" + rest


def status_tag(story):
    claim = str(story.get("status", "")).lower().startswith("claim")
    word = "CLAIM" if claim else "CONFIRMED"
    return '<div class="tag %s fit"><b>%s</b> · %s</div>' % ("claim" if claim else "ok", word, esc(story.get("tag", "")))


def card(story, x, y, w, h, kind):
    """kind: 'big' (lead 1), 'lead' (leads 2-4) or 'small'."""
    reg = region_of(story.get("region"))
    c = COLOR[reg]
    iw = int(round(w - 2))
    ih = {"big": 136, "lead": 136, "small": 71}[kind]
    sub = story.get("subhead") if kind != "small" else None
    cap = story.get("cap") or str(story.get("place", "")).upper()
    regl = "WORLD" if reg == "World/Space" else reg.upper()
    return (
        '<div class="card %s" style="left:%.1fpx;top:%dpx;width:%.1fpx;height:%dpx">'
        '<div class="ill" style="width:%dpx;height:%dpx">%s<div class="cap fit" data-fit="cap">%s</div></div>'
        '<div class="body fitbox" style="top:%dpx;bottom:%dpx">'
        '<div class="kick" style="color:%s"><span class="badge" style="background:%s">%s</span>'
        '<span class="fit kt" data-fit="kt">%s · %s</span></div>'
        '<div class="hl">%s</div>%s</div>%s</div>'
        % (kind, x, y, w, h, iw, ih, illustration(story, iw, ih), esc(cap),
           ih + 3, 20 if kind != "small" else 17,
           c, c, esc(story["n"]), esc(regl), esc(str(story.get("beat", "")).upper()),
           esc(story.get("headline", "")),
           '<div class="sub">%s</div>' % esc(sub) if sub else "",
           status_tag(story)))


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1024px;height:1024px;overflow:hidden;background:%(paper)s;color:%(ink)s;
 font-family:'Barlow',sans-serif;-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}
.abs,.card,.ill,.body,.tag,.cap{position:absolute}
svg{display:block}
/* masthead */
.kr{top:7px;font:700 11px/13px 'Barlow Condensed';letter-spacing:1.4px;white-space:nowrap}
#date{left:12px;top:14px;width:1000px;height:64px;text-align:center;font:400 66px/64px 'DM Serif Display';
 white-space:nowrap;letter-spacing:-.5px}
.rule{left:12px;width:1000px;background:%(ink)s}
#tag{left:12px;top:83px;width:1000px;height:17px;text-align:center;font:italic 400 15px/17px 'DM Serif Display';
 color:#8a3a26;white-space:nowrap}
#bar{left:12px;top:104px;width:1000px;height:16px;display:flex}
#bar div{height:16px;color:#fff;font:700 11.5px/16px 'Barlow Condensed';letter-spacing:.8px;text-align:center;
 white-space:nowrap;overflow:hidden}
/* stats */
#stats{left:12px;top:123px;width:1000px;height:36px;display:flex;gap:6px}
#stats .st{flex:1;min-width:0;border-left:3px solid;padding-left:7px;background:#fbf8f1}
#stats .v{font:400 22px/23px 'DM Serif Display';white-space:nowrap}
#stats .l{font:600 10px/12px 'Barlow Condensed';letter-spacing:.3px;color:#3d372f;white-space:nowrap;text-transform:uppercase}
/* timeline */
#tl{left:12px;top:162px;width:1000px;height:18px}
#tl .lab{position:absolute;left:0;top:2px;font:700 11.5px/14px 'Barlow Condensed';letter-spacing:.8px;white-space:nowrap}
#tl .line{position:absolute;left:96px;right:0;top:9px;height:1.5px;background:%(ink)s}
#tl .ev{position:absolute;top:2px;font:500 11.5px/14px 'Barlow Condensed';white-space:nowrap;background:%(paper)s;
 padding:0 6px 0 3px;display:flex;align-items:center}
#tl .ev i{display:inline-block;width:9px;height:9px;border-radius:50%%;background:%(paper)s;border:2.2px solid %(ink)s;
 margin-right:4px}
#tl .ev b{font-weight:700;margin-right:3px}
/* cards */
.card{background:#fdfbf6;border:1px solid %(rule)s;overflow:hidden}
.ill{left:0;top:0;overflow:hidden}
.cap{left:0;right:0;bottom:0;background:rgba(29,26,22,.85);color:#fff;font-family:'Barlow Condensed';font-weight:700;
 white-space:nowrap;text-transform:uppercase;overflow:hidden}
.body{left:7px;right:7px;overflow:hidden}
.kick{display:flex;align-items:center;gap:5px;font-family:'Barlow Condensed';font-weight:700;white-space:nowrap}
.kt{display:block;flex:1;min-width:0}
.badge{flex:none;display:inline-block;border-radius:50%%;color:#fff;text-align:center;font-family:'Barlow Condensed';
 font-weight:700}
.hl{font-family:'DM Serif Display',serif}
.tag{left:7px;font-family:'Barlow Condensed';font-weight:500;white-space:nowrap;border-radius:2px;
 letter-spacing:.3px;max-width:calc(100%% - 14px)}
.tag.ok{color:%(ok)s;border:1px solid %(ok)s;background:#eef5ee}
.tag.claim{color:%(claim)s;border:1px solid %(claim)s;background:#fbefd6}
.big .cap,.lead .cap{height:18px;font-size:12px;line-height:18px;letter-spacing:1px;padding:0 8px}
.big .kick,.lead .kick{font-size:12px;line-height:17px;letter-spacing:.7px;height:17px}
.big .badge,.lead .badge{width:17px;height:17px;font-size:12px;line-height:17px}
.big .hl{font-size:25px;line-height:26px;margin-top:4px}
.lead .hl{font-size:17px;line-height:18px;margin-top:3px}
.big .sub,.lead .sub{font:500 12px/14px 'Barlow';margin-top:3px;color:#37322b}
.big .sub{font-size:13.5px;line-height:16px;margin-top:5px}
.big .tag,.lead .tag{bottom:4px;font-size:11px;line-height:13px;padding:0 5px}
.small .cap{height:15px;font-size:10px;line-height:15px;letter-spacing:.7px;padding:0 6px}
.small .kick{font-size:10.5px;line-height:14px;letter-spacing:.4px;height:14px;gap:4px}
.small .badge{width:14px;height:14px;font-size:10px;line-height:14px}
.small .hl{font-size:13.5px;line-height:14px;margin-top:2px}
.small .tag{bottom:3px;font-size:9.5px;line-height:11.5px;padding:0 3px}
/* bottom band */
.h{font:700 12.5px/14px 'Barlow Condensed';letter-spacing:1px;text-transform:uppercase;white-space:nowrap}
.h span{font-weight:500;letter-spacing:.2px;text-transform:none;color:#4a443b}
#map{border:1px solid %(rule)s;overflow:hidden}
#legend{font:500 10.5px/12px 'Barlow Condensed';color:#3d372f;white-space:nowrap}
#legend i{display:inline-block;width:11px;height:11px;border-radius:50%%;vertical-align:-2px;margin:0 3px 0 0}
#briefs{display:flex;gap:14px}
#briefs .col{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:space-between}
.br{font:500 11.5px/12px 'Barlow Condensed';height:13px;flex:none;box-sizing:border-box;white-space:nowrap;display:flex;align-items:center;
 border-bottom:1px dotted %(rule)s;padding-bottom:0}
.br .n{flex:none;width:18px;font-weight:700;text-align:right;padding-right:5px}
.br .t{min-width:0;flex:1;overflow:hidden}
.br b{font-weight:700}
.br em{color:#7a7266;font-size:.9em}
#dc{left:12px;width:1000px;border:1.5px solid %(ink)s;background:#fbf8f1;display:flex;overflow:hidden}
#dc .lb{flex:none;width:96px;background:%(ink)s;color:#fff;font:700 14px/16px 'Barlow Condensed';letter-spacing:1px;
 display:flex;align-items:center;justify-content:center;text-align:center}
#dc .lb span{color:#7fd39a}
#dc .tx{flex:1;min-width:0;padding:2px 9px;font:500 11px/13px 'Barlow';overflow:hidden}
#dc .tx .a{font-weight:700}
#dc .tx .k{font-family:'Barlow Condensed';font-weight:700;letter-spacing:.5px}
#foot{left:12px;width:1000px;text-align:center;font:500 10.5px/13px 'Barlow Condensed';
 letter-spacing:.25px;white-space:nowrap;color:#2c2822}
"""

# Shrinks overflowing ".fit" one-liners and ".fitbox" card bodies (down to legibility floors),
# then reports anything still overflowing so build.py can print it.
FIT_JS = """
window.__fit=function(){
 if(window.__fitres)return window.__fitres;
 var floor={cap:9.5,tag:9.5,kt:9.5,t:9.5,foot:9.5,dt:40,stl:9.5,dc:9.5,tl:9.5};
 var bad=[];
 function shrink(e,min){var cs=getComputedStyle(e),fs=parseFloat(cs.fontSize),lh=parseFloat(cs.lineHeight)/fs;
  if(fs-0.25<min)return false;fs-=0.25;e.style.fontSize=fs+'px';e.style.lineHeight=(fs*lh)+'px';return true;}
 document.querySelectorAll('.fit').forEach(function(e){
  var min=floor[e.dataset.fit]||9.5;
  if(e.dataset.mh){while(e.scrollHeight>e.clientHeight+0.5&&shrink(e,min));
   if(e.scrollHeight>e.clientHeight+0.5)bad.push('box '+e.id);return;}
  while(e.scrollWidth>e.clientWidth+0.5&&shrink(e,min));
  if(e.scrollWidth>e.clientWidth+0.5)bad.push((e.dataset.fit||'')+': '+e.textContent.trim().slice(0,60));
 });
 document.querySelectorAll('.fitbox').forEach(function(b){
  var hl=b.querySelector('.hl'),sub=b.querySelector('.sub');
  var hmin=b.parentNode.classList.contains('small')?11.5:14;
  for(var i=0;i<80&&b.scrollHeight>b.clientHeight+0.5;i++){
   var a=sub&&shrink(sub,10.5),c=shrink(hl,hmin);if(!a&&!c)break;}
  if(b.scrollHeight>b.clientHeight+0.5)bad.push('card: '+hl.textContent.slice(0,50));
 });
 return window.__fitres=JSON.stringify(bad);
};
window.__fit();
"""


def build_html(data):
    pictured = sorted(data["pictured"], key=lambda s: s["n"])
    briefs = sorted(data.get("briefs", []), key=lambda s: s["n"])
    leads = [s for s in pictured if s.get("lead")] or pictured[:4]
    smalls = [s for s in pictured if s not in leads]
    date_label = data.get("date_label", "Thursday 19 November 2026")
    day_short = " ".join(date_label.split()[:3])

    counts = {k: 0 for k, _ in REGIONS}
    for s in pictured + briefs:
        counts[region_of(s.get("region"))] += 1
    total = len(pictured) + len(briefs)

    p = []
    # ---- masthead
    p.append('<div class="abs kr" style="left:12px">THE WORLD IN ONE DAY</div>')
    p.append('<div class="abs kr" style="right:12px">%d STORIES · EVERY INHABITED CONTINENT · ALL FROM THIS ONE DAY</div>' % total)
    p.append('<div class="abs fit" id="date" data-fit="dt">%s</div>' % esc(date_label))
    p.append('<div class="abs rule" style="top:79px;height:2.5px"></div>')
    p.append('<div class="abs fit" id="tag" data-fit="tl">%s</div>' % esc(data.get("tagline", "")))

    # ---- region bar
    shown = [(k, c, counts[k]) for k, c in REGIONS if counts[k]]
    floor_w = 96.0
    spare = 1000.0 - floor_w * len(shown)
    tot = float(sum(n for _, _, n in shown)) or 1.0
    p.append('<div class="abs" id="bar">')
    for k, c, n in shown:
        p.append('<div style="width:%.2fpx;background:%s">%s %d</div>'
                 % (floor_w + spare * n / tot, c, esc(k.upper()), n))
    p.append('</div>')

    # ---- stat strip
    p.append('<div class="abs" id="stats">')
    for st in data.get("stats", [])[:6]:
        c = COLOR[region_of(st.get("region"))]
        p.append('<div class="st" style="border-color:%s"><div class="v" style="color:%s">%s</div>'
                 '<div class="l fit" data-fit="stl">%s</div></div>' % (c, c, esc(st["v"]), esc(st["l"])))
    p.append('</div>')

    # ---- timeline: one line
    tl = data.get("timeline", [])
    p.append('<div class="abs" id="tl"><div class="lab">THE DAY IN UTC</div><div class="line"></div>')
    if tl:
        x0, x1 = 100.0, 1000.0
        slot = (x1 - x0) / len(tl)
        for i, ev in enumerate(tl):
            t = str(ev.get("t", "")).replace(" UTC", "")
            p.append('<div class="ev" style="left:%.1fpx"><i></i><b>%s</b>%s</div>'
                     % (x0 + slot * i, esc(t), esc(ev.get("label", ""))))
    p.append('</div>')

    # ---- lead row
    ly, lh, gap = 184, 256, 8.0
    bw = 385.0
    ow = (1000.0 - bw - 3 * gap) / 3
    x = 12.0
    for i, s in enumerate(leads[:4]):
        w = bw if i == 0 else ow
        p.append(card(s, x, ly, w, lh, "big" if i == 0 else "lead"))
        x += w + gap

    # ---- two rows of 6 small cards
    sy, sh, sgap = ly + lh + 5, 144, 5.6
    sw = (1000.0 - sgap * 5) / 6
    for i, s in enumerate(smalls[:12]):
        r, c = divmod(i, 6)
        p.append(card(s, 12 + c * (sw + sgap), sy + r * (sh + 5), sw, sh, "small"))
    band = sy + 2 * sh + 5 + 6  # top of bottom band

    # ---- bottom band, left: map
    map_w = 356
    map_h = map_height(map_w)
    svg, unplaced = world_map(pictured, map_w, map_h)
    p.append('<div class="abs h" style="left:12px;top:%dpx">Where it happened</div>' % band)
    p.append('<div class="abs" id="map" style="left:12px;top:%dpx;width:%dpx;height:%dpx">%s</div>'
             % (band + 16, map_w + 2, map_h + 2, svg))
    off = "".join(' · <b>%s</b> %s: off the map' % (esc(s["n"]), esc(str(s.get("place", "")).lower()))
                  for s in unplaced)
    leg_top = band + 16 + map_h + 4
    p.append('<div class="abs" id="legend" style="left:12px;top:%dpx;width:%dpx">'
             '<i style="background:%s"></i>numbers match the stories%s</div>'
             % (leg_top, map_w + 2, COLOR["Europe"], off))
    n_rows = (len(briefs) + 1) // 2
    bottom = max(leg_top + 13, band + 17 + int(math.ceil(n_rows * 13.4)))

    # ---- bottom band, right: briefs
    bx = 12 + map_w + 2 + 16
    bwid = 1012 - bx
    p.append('<div class="abs h" style="left:%dpx;top:%dpx">Also on %s <span>· %d more stories, one line each</span></div>'
             % (bx, band, esc(day_short), len(briefs)))
    half = (len(briefs) + 1) // 2
    p.append('<div class="abs" id="briefs" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">'
             % (bx, band + 17, bwid, bottom - band - 17))
    for col in (briefs[:half], briefs[half:]):
        p.append('<div class="col">')
        for b in col:
            c = COLOR[region_of(b.get("region"))]
            src = ' <em>· %s</em>' % esc(b["src"]) if b.get("src") else ""
            p.append('<div class="br"><span class="n" style="color:%s">%s</span>'
                     '<span class="t fit" data-fit="t"><b>%s</b> %s%s</span></div>'
                     % (c, esc(b["n"]), esc(b.get("place", "")), esc(b.get("fact", "")), src))
        p.append('</div>')
    p.append('</div>')

    # ---- date check
    dc = data.get("date_check", {})
    dc_top = bottom + 5
    dc_h = 1024 - 20 - dc_top - 3
    later = "; ".join(dc.get("later", [])) or "none"
    before = "; ".join(dc.get("before", [])) or "none"
    p.append('<div class="abs" id="dc" style="top:%dpx;height:%dpx"><div class="lb">DATE<br>CHECK <span>✓</span></div>'
             '<div class="tx fit" id="dct" data-fit="dc" data-mh="%d"><span class="a">Every story on this page happened, or was first reported, on %s.</span> '
             '<span class="k">LEFT OUT AS OTHER DAYS\' NEWS:</span> <b>earlier</b> — %s. <b>Later</b> — %s.</div></div>'
             % (dc_top, dc_h, dc_h - 3, esc(date_label), esc(before), esc(later)))

    # ---- footer
    p.append('<div class="abs rule" style="top:%dpx;height:1px"></div>' % (1024 - 19))
    p.append('<div class="abs fit" id="foot" data-fit="foot" style="top:%dpx">Claims by parties are attributed, not stated as fact'
             ' · Pictures and map drawn in code · Sources: %s</div>'
             % (1024 - 16, esc(", ".join(data.get("sources", [])))))

    css = CSS % {"paper": PAPER, "ink": INK, "rule": RULE, "ok": OK_COL, "claim": CLAIM_COL}
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>%s</title><style>%s</style></head>'
            '<body>%s<script>%s</script></body></html>' % (esc(date_label), css, "\n".join(p), FIT_JS))



# ----------------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------------
CHROME_FLAGS = ["--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                "--window-size=%d,%d" % (W, H), "--default-background-color=00000000", "--no-first-run"]


def chrome_exe():
    return shutil.which("google-chrome") or shutil.which("chromium") or "google-chrome"


def render_cli(url, png_path, profile, timeout=40):
    """Plain one-shot: google-chrome --headless=new ... --screenshot=<png> <url>."""
    cmd = [chrome_exe()] + CHROME_FLAGS + ["--user-data-dir=" + profile, "--screenshot=" + png_path, url]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
    return None


def render_pipe(url, png_path, profile, timeout=40):
    """Same Chrome, same flags, but the screenshot is requested over --remote-debugging-pipe.

    The one-shot --screenshot mode never exits on machines where policy force-installs
    extensions; the pipe (fd 3 = commands in, fd 4 = replies out, NUL-separated JSON) does not
    depend on Chrome deciding when to quit. Returns the page's list of overflowing texts.
    """
    a, b = os.pipe(), os.pipe()
    r_in, w_in, r_out, w_out = [fcntl.fcntl(f, fcntl.F_DUPFD, 20) for f in (a[0], a[1], b[0], b[1])]
    for f in a + b:
        os.close(f)

    def pre():
        os.dup2(r_in, 3)
        os.dup2(w_out, 4)

    cmd = [chrome_exe()] + CHROME_FLAGS + ["--user-data-dir=" + profile, "--remote-debugging-pipe", "about:blank"]
    proc = subprocess.Popen(cmd, preexec_fn=pre, pass_fds=(3, 4), stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, start_new_session=True)
    os.close(r_in)
    os.close(w_out)
    state = {"buf": b"", "id": 0}
    deadline = time.time() + timeout

    def send(method, params=None, sid=None):
        state["id"] += 1
        msg = {"id": state["id"], "method": method, "params": params or {}}
        if sid:
            msg["sessionId"] = sid
        os.write(w_in, json.dumps(msg).encode() + b"\0")
        return state["id"]

    def wait(pred):
        while True:
            while b"\0" in state["buf"]:
                raw, state["buf"] = state["buf"].split(b"\0", 1)
                msg = json.loads(raw)
                if pred(msg):
                    return msg
            if time.time() > deadline:
                raise TimeoutError("chrome did not answer in time")
            if select.select([r_out], [], [], 0.5)[0]:
                chunk = os.read(r_out, 1 << 20)
                if not chunk:
                    raise EOFError("chrome closed the debugging pipe")
                state["buf"] += chunk

    def call(method, params=None, sid=None):
        i = send(method, params, sid)
        res = wait(lambda m: m.get("id") == i)
        if "error" in res:
            raise RuntimeError("%s: %s" % (method, res["error"]))
        return res["result"]

    try:
        tid = call("Target.createTarget", {"url": "about:blank", "width": W, "height": H})["targetId"]
        sid = call("Target.attachToTarget", {"targetId": tid, "flatten": True})["sessionId"]
        call("Page.enable", None, sid)
        call("Emulation.setDeviceMetricsOverride", {"width": W, "height": H, "deviceScaleFactor": 1, "mobile": False}, sid)
        send("Page.navigate", {"url": url}, sid)
        wait(lambda m: m.get("method") == "Page.loadEventFired")
        call("Runtime.evaluate", {"expression": "document.fonts.ready.then(()=>1)", "awaitPromise": True}, sid)
        ovf = call("Runtime.evaluate", {"expression": "window.__fit()", "returnByValue": True}, sid)
        shot = call("Page.captureScreenshot", {"format": "png", "clip": {"x": 0, "y": 0, "width": W, "height": H, "scale": 1}}, sid)
        with open(png_path, "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        try:
            call("Browser.close")
        except Exception:
            pass
        return json.loads(ovf.get("result", {}).get("value") or "[]")
    finally:
        try:
            proc.wait(5)
        except Exception:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except Exception:
                pass
        os.close(w_in)
        os.close(r_out)


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        raise ValueError("not a PNG: " + path)
    return struct.unpack(">II", head[16:24])


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "data", "stories.json")
    with open(src, encoding="utf-8") as f:
        data = json.load(f)
    html_path = os.path.join(HERE, "render.html")
    png_path = os.path.join(HERE, "entry.png")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build_html(data))
    url = "file://" + html_path
    profile = tempfile.mkdtemp(prefix="newsimg-chrome-", dir="/tmp")
    try:
        if os.path.exists(png_path):
            os.remove(png_path)
        try:
            overflow = render_pipe(url, png_path, profile)
        except Exception as e:
            print("WARN debugging-pipe render failed (%s); trying plain --screenshot" % e, file=sys.stderr)
            overflow = None
            try:
                render_cli(url, png_path, profile)
            except subprocess.TimeoutExpired:
                pass
        if not os.path.isfile(png_path):
            sys.exit("chrome did not write a screenshot")
        if overflow is None:
            print("WARN overflow check did not run", file=sys.stderr)
        for item in overflow or []:
            print("OVERFLOW " + item, file=sys.stderr)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    w, h = png_size(png_path)
    size = os.path.getsize(png_path)
    print("%s  %dx%d  %d bytes" % (png_path, w, h, size))
    if (w, h) != (W, H):
        sys.exit("ERROR: expected %dx%d" % (W, H))
    if size > 1048576:
        sys.exit("ERROR: PNG is over 1 MiB")


if __name__ == "__main__":
    main()
