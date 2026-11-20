"""Story illustrations, part A. Full-bleed flat-vector editorial scenes.

Each fn(w, h) returns an inline <svg>. Content is drawn in a fixed design box
(lead 1: 770x300, other leads: 400x300, small cards: 330x150). The viewBox is
widened/heightened to match the requested aspect and the design box is centred,
so xMidYMid slice cropping stays safe. Backgrounds over-bleed the design box.
The bottom ~15% sits under the page's caption band: nothing essential there.
"""
import math

INK = "#14121a"
BARLOW = 'font-family="Barlow Condensed" font-weight="700"'
SERIF = 'font-family="DM Serif Display"'


# ---------------------------------------------------------------- frame
def _svg(pid, w, h, dw, dh, defs, body):
    """Centre a dw x dh design box in a viewBox with the aspect of w x h."""
    ar = float(w) / float(h)
    if ar >= float(dw) / dh:
        vw, vh = dh * ar, float(dh)
    else:
        vw, vh = float(dw), dw / ar
    ox, oy = (vw - dw) / 2.0, (vh - dh) / 2.0
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="%.2f %.2f %.2f %.2f" '
            'preserveAspectRatio="xMidYMid slice"><defs>%s</defs>%s</svg>'
            % (w, h, -ox, -oy, vw, vh, defs, body))


def _lg(gid, stops, x2=0, y2=1):
    s = "".join('<stop offset="%s" stop-color="%s"/>' % (o, c) for o, c in stops)
    return '<linearGradient id="%s" x1="0" y1="0" x2="%s" y2="%s">%s</linearGradient>' % (gid, x2, y2, s)


def _rg(gid, stops):
    s = "".join('<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (o, c, op) for o, c, op in stops)
    return '<radialGradient id="%s">%s</radialGradient>' % (gid, s)


def _bg(fill, y=-400, hgt=1200):
    return '<rect x="-600" y="%s" width="2000" height="%s" fill="%s"/>' % (y, hgt, fill)


def _txt(x, y, s, size, fill="#fff", anchor="middle", font=BARLOW, extra=""):
    return ('<text x="%s" y="%s" text-anchor="%s" %s font-size="%s" fill="%s" %s>%s</text>'
            % (x, y, anchor, font, size, fill, extra, s))


def _badge(x, y, s, size, bg, fg="#fff", pad=None, anchor="middle"):
    """Bold label pill. (x, y) = centre (anchor middle) or left edge; y = vertical centre."""
    pad = pad if pad is not None else size * 0.38
    tw = len(s) * size * 0.47 + pad * 2
    hh = size * 1.18
    x0 = x - tw / 2 if anchor == "middle" else x
    return ('<g><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="#000" opacity=".28"/>'
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s"/>%s</g>'
            % (x0 + 2, y - hh / 2 + 2.5, tw, hh, hh * 0.18,
               x0, y - hh / 2, tw, hh, hh * 0.18, bg,
               _txt(x0 + tw / 2, y + size * 0.35, s, size, fg)))


def _star(cx, cy, r, fill, inner=0.38, rot=0):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * inner
        a = -math.pi / 2 + rot + i * math.pi / 5
        pts.append("%.2f,%.2f" % (cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return '<polygon points="%s" fill="%s"/>' % (" ".join(pts), fill)


# ---------------------------------------------------------------- flags (x, y top-left)
def _flag_us(x, y, w, h):
    s = ['<rect x="%s" y="%s" width="%s" height="%s" fill="#fff"/>' % (x, y, w, h)]
    for i in range(0, 13, 2):
        s.append('<rect x="%s" y="%.2f" width="%s" height="%.2f" fill="#b22234"/>' % (x, y + i * h / 13.0, w, h / 13.0))
    cw, ch = w * 0.4, h * 7 / 13.0
    s.append('<rect x="%s" y="%s" width="%.2f" height="%.2f" fill="#3c3b6e"/>' % (x, y, cw, ch))
    for r in range(4):
        for c in range(5):
            s.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="#fff"/>'
                     % (x + cw * (c + 0.5) / 5, y + ch * (r + 0.5) / 4, h * 0.022))
    return "".join(s)


def _flag_cn(x, y, w, h):
    s = '<rect x="%s" y="%s" width="%s" height="%s" fill="#de2910"/>' % (x, y, w, h)
    s += _star(x + w * 5 / 30, y + h * 5 / 20, h * 3 / 20, "#ffde00")
    for sx, sy in ((10, 2), (12, 4), (12, 7), (10, 9)):
        s += _star(x + w * sx / 30, y + h * sy / 20, h / 20, "#ffde00")
    return s


def _tri_h(x, y, w, h, cols):
    return "".join('<rect x="%s" y="%.2f" width="%s" height="%.2f" fill="%s"/>'
                   % (x, y + i * h / 3.0, w, h / 3.0 + 0.1, c) for i, c in enumerate(cols))


def _flag_ru(x, y, w, h):
    return _tri_h(x, y, w, h, ["#fff", "#0039a6", "#d52b1e"])


def _flag_nl(x, y, w, h):
    return _tri_h(x, y, w, h, ["#ae1c28", "#fff", "#21468b"])


def _flag_at(x, y, w, h):
    return _tri_h(x, y, w, h, ["#c8102e", "#fff", "#c8102e"])


def _flag_mm(x, y, w, h):
    return _tri_h(x, y, w, h, ["#fecb00", "#34b233", "#ea2839"]) + _star(x + w / 2, y + h * 0.55, h * 0.45, "#fff")


def _flag_ir(x, y, w, h):
    return (_tri_h(x, y, w, h, ["#239f40", "#fff", "#da0000"])
            + '<circle cx="%.1f" cy="%.1f" r="%.2f" fill="none" stroke="#da0000" stroke-width="%.2f"/>'
            % (x + w / 2, y + h / 2, h * 0.1, h * 0.04))


def _pole(px, py, pole_h, fw, fh, flag, wave=True, pole_col="#d9d2c0"):
    """Flagpole at px from py down pole_h; flag hung top-right with a soft wave shade."""
    s = '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % (px - fw * 0.02, py, fw * 0.04 + 0.6, pole_h, pole_col)
    s += '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#e8c35a"/>' % (px + 0.3, py, fw * 0.05 + 0.6)
    s += flag(px + fw * 0.03, py + 1, fw, fh)
    if wave:
        s += ('<path d="M%.1f,%.1f h%.1f v%.1f h-%.1f Z" fill="#000" opacity=".12"/>'
              % (px + fw * 0.45, py + 1, fw * 0.2, fh, fw * 0.2))
    return s


# ---------------------------------------------------------------- figures
def _figure(cx, base, s, suit, tie="#b8312f", hair="#2b2622", skin="#e7b995", shirt="#fff",
            hair_style="short", arm=None):
    """Simple suited figure, head-and-torso, scale s (s=1: ~70 tall)."""
    o = []
    sh = 26 * s  # shoulder half-width
    top = base - 44 * s
    o.append('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f L%.1f,%.1f Q%.1f,%.1f %.1f,%.1f Z" fill="%s"/>'
             % (cx - sh, base, cx - sh, top, cx - 8 * s, top - 2 * s, cx + 8 * s, top - 2 * s,
                cx + sh, top, cx + sh, base, suit))
    o.append('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f Z" fill="#000" opacity=".18"/>'
             % (cx + 6 * s, top - 1 * s, cx + sh, top, cx + sh, base))
    o.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (cx - 8 * s, top - 2 * s, cx + 8 * s, top - 2 * s, cx, top + 20 * s, shirt))
    o.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (cx - 2.6 * s, top + 1 * s, cx + 2.6 * s, top + 1 * s, cx + 3.2 * s, top + 19 * s, cx - 3.2 * s, top + 19 * s, tie))
    # lapels
    o.append('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="#000" opacity=".22"/>'
             % (cx - 8 * s, top - 2 * s, cx - 1 * s, top + 22 * s, cx - 12 * s, top + 8 * s,
                cx + 8 * s, top - 2 * s, cx + 1 * s, top + 22 * s, cx + 12 * s, top + 8 * s))
    # neck + head
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % (cx - 5 * s, top - 9 * s, 10 * s, 9 * s, skin))
    o.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>' % (cx, top - 19 * s, 11.5 * s, 13.5 * s, skin))
    o.append('<path d="M%.1f,%.1f a%.1f,%.1f 0 0 0 0,%.1f Z" fill="#000" opacity=".08"/>'
             % (cx + 2 * s, top - 32.5 * s, 9.5 * s, 13.5 * s, 27 * s))
    hy = top - 19 * s
    if hair_style == "swoop":  # full blonde swept
        o.append('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f Q%.1f,%.1f %.1f,%.1f Q%.1f,%.1f %.1f,%.1f Z" fill="%s"/>'
                 % (cx - 12.5 * s, hy - 1 * s, cx - 14 * s, hy - 18 * s, cx + 1 * s, hy - 16 * s,
                    cx + 15 * s, hy - 15 * s, cx + 13 * s, hy - 2 * s, cx + 2 * s, hy - 12 * s, cx - 12.5 * s, hy - 1 * s, hair))
    elif hair_style == "thin":  # receding, light
        o.append('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f L%.1f,%.1f Q%.1f,%.1f %.1f,%.1f Z" fill="%s"/>'
                 % (cx - 12 * s, hy + 1 * s, cx - 13 * s, hy - 10 * s, cx - 7 * s, hy - 11 * s,
                    cx - 8 * s, hy - 4 * s, cx - 11 * s, hy - 3 * s, cx - 12 * s, hy + 1 * s, hair))
        o.append('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f L%.1f,%.1f Q%.1f,%.1f %.1f,%.1f Z" fill="%s"/>'
                 % (cx + 12 * s, hy + 1 * s, cx + 13 * s, hy - 10 * s, cx + 7 * s, hy - 11 * s,
                    cx + 8 * s, hy - 4 * s, cx + 11 * s, hy - 3 * s, cx + 12 * s, hy + 1 * s, hair))
    else:  # short dark, neat
        o.append('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f Q%.1f,%.1f %.1f,%.1f Q%.1f,%.1f %.1f,%.1f Z" fill="%s"/>'
                 % (cx - 12 * s, hy - 1 * s, cx - 13 * s, hy - 17 * s, cx, hy - 15 * s,
                    cx + 13 * s, hy - 17 * s, cx + 12 * s, hy - 1 * s, cx, hy - 11 * s, cx - 12 * s, hy - 1 * s, hair))
    return "".join(o)


def _robe(cx, base, s, robe="#1b1b22", band="#fff", skin="#d9a982", hair="#3a332e"):
    """Judge in robe, seated behind a bench (torso only)."""
    top = base - 30 * s
    return ('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f L%.1f,%.1f Q%.1f,%.1f %.1f,%.1f Z" fill="%s"/>'
            % (cx - 16 * s, base, cx - 16 * s, top, cx - 4 * s, top - 2 * s, cx + 4 * s, top - 2 * s,
               cx + 16 * s, top, cx + 16 * s, base, robe)
            + '<path d="M%.1f,%.1f l%.1f,%.1f l%.1f,%.1f Z" fill="%s"/>' % (cx - 3 * s, top - 1 * s, 3 * s, 10 * s, 3 * s, -10 * s, band)
            + '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, top - 9 * s, 7.5 * s, skin)
            + '<path d="M%.1f,%.1f a%.1f,%.1f 0 0 1 %.1f,0 Z" fill="%s"/>' % (cx - 7.8 * s, top - 10 * s, 7.8 * s, 7.8 * s, 15.6 * s, hair))


# ---------------------------------------------------------------- props
def _flame(cx, base, wd, ht, pid, k):
    """Layered flame shape."""
    o = []
    for f, col in ((1.0, "#e2401c"), (0.72, "#f59a1d"), (0.42, "#ffe066")):
        ww, hh = wd * f, ht * f
        o.append('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f Q%.1f,%.1f %.1f,%.1f Q%.1f,%.1f %.1f,%.1f '
                 'Q%.1f,%.1f %.1f,%.1f Z" fill="%s"/>'
                 % (cx - ww / 2, base,
                    cx - ww * 0.62, base - hh * 0.5, cx - ww * 0.2, base - hh * 0.72,
                    cx - ww * 0.1, base - hh * 0.95, cx + ww * 0.05, base - hh,
                    cx + ww * 0.12, base - hh * 0.6, cx + ww * 0.3, base - hh * 0.7,
                    cx + ww * 0.62, base - hh * 0.45, cx + ww / 2, base, col))
    return "".join(o)


def _smoke(pts, col="#2a2630", op=0.85):
    """Smoke plume from list of (cx, cy, r)."""
    return '<g fill="%s" opacity="%s">%s</g>' % (col, op, "".join(
        '<circle cx="%.1f" cy="%.1f" r="%.1f"/>' % p for p in pts))


def _tanker(x, wl, L, hull="#3b2d2a", deck="#8c2f27", s=1.0, flip=False):
    """Oil tanker at waterline wl, bow to the right (flip: bow left). Length L."""
    hgt = L * 0.13
    g = []
    g.append('<path d="M0,%.1f L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="%s"/>'
             % (-hgt, L * 0.94, -hgt, L, -hgt * 1.25, L * 0.93, hgt * 0.35, L * 0.03, hgt * 0.35, hull))
    g.append('<rect x="0" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % (-hgt * 0.15, L * 0.95, hgt * 0.5, "#8a2a24"))
    g.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % (L * 0.03, -hgt * 1.18, L * 0.9, hgt * 0.2, deck))
    # pipes on deck
    for i in range(5):
        g.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#c9b48a"/>' % (L * (0.3 + i * 0.12), -hgt * 1.5, L * 0.015, hgt * 0.33))
    g.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#c9b48a"/>' % (L * 0.28, -hgt * 1.45, L * 0.6, hgt * 0.06))
    # superstructure (aft)
    g.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eae4d8"/>' % (L * 0.04, -hgt * 2.6, L * 0.17, hgt * 1.45))
    g.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#d2cabb"/>' % (L * 0.15, -hgt * 2.6, L * 0.06, hgt * 1.45))
    g.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#263446"/>' % (L * 0.06, -hgt * 2.35, L * 0.13, hgt * 0.22))
    g.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#2a2a2a"/>' % (L * 0.06, -hgt * 3.25, L * 0.05, hgt * 0.65))
    tr = "translate(%.1f %.1f)" % (x, wl)
    if flip:
        tr += " translate(%.1f 0) scale(-1 1)" % L
    return '<g transform="%s">%s</g>' % (tr, "".join(g))


def _waves(x0, x1, y, col, step=22, amp=2.2, op=0.5, sw=1.4):
    d = "M%.1f,%.1f" % (x0, y)
    x = x0
    while x < x1:
        d += " q%.1f,%.1f %.1f,0" % (step / 2.0, -amp, step)
        x += step
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%s" opacity="%s" stroke-linecap="round"/>' % (d, col, sw, op)


# ================================================================ LEADS
def trump_xi_putin_shenzhen(w, h):
    p = "trump-xi-putin-shenzhen"
    DW, DH = 770, 300
    d = (_lg(p + "-sky", [(0, "#1d1b4a"), (0.45, "#6a3a7c"), (0.78, "#e2706a"), (1, "#f7b267")])
         + _lg(p + "-sea", [(0, "#f0a070"), (0.3, "#7a4a7e"), (1, "#22204a")])
         + _lg(p + "-stage", [(0, "#7c1d22"), (1, "#4a0f14")])
         + _lg(p + "-tbl", [(0, "#f3efe6"), (1, "#cfc6b4")])
         + _rg(p + "-sun", [(0, "#ffd27a", 0.9), (1, "#ffd27a", 0)]))
    b = [_bg("url(#%s-sky)" % p, -300, 520)]
    b.append('<circle cx="385" cy="150" r="170" fill="url(#%s-sun)"/>' % p)
    # far skyline (lilac) and near skyline (deep purple) with Ping An-style spire
    far = [(-200, 60), (-150, 90), (-110, 70), (-60, 110), (-10, 80), (40, 120), (90, 75), (130, 100),
           (600, 95), (650, 125), (700, 80), (740, 115), (790, 70), (840, 105), (890, 85), (940, 60)]
    for x, bh in far:
        b.append('<rect x="%d" y="%d" width="44" height="%d" fill="#8a5d93" opacity=".75"/>' % (x, 180 - bh, bh))
    near = [(-180, 70, 40), (-130, 105, 34), (-90, 80, 30), (-50, 128, 36), (0, 96, 30), (40, 150, 28), (80, 112, 34),
            (128, 82, 26), (610, 88, 30), (650, 140, 32), (690, 100, 28), (725, 160, 26), (760, 118, 34), (800, 92, 30),
            (840, 136, 34), (885, 98, 30), (925, 74, 40)]
    for x, bh, bw in near:
        b.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#3b2550"/>' % (x, 182 - bh, bw, bh))
        for wy in range(182 - bh + 8, 176, 10):
            b.append('<rect x="%d" y="%d" width="%d" height="2.2" fill="#ffcf7a" opacity=".55"/>' % (x + 4, wy, bw - 8))
    # Ping An Finance Centre-like spire (left) and a twin tower (right)
    b.append('<polygon points="168,182 172,34 180,6 188,34 192,182" fill="#2d1c42"/>'
             '<polygon points="180,6 188,34 192,182 182,182" fill="#000" opacity=".2"/>'
             '<line x1="180" y1="6" x2="180" y2="-14" stroke="#2d1c42" stroke-width="2.4"/>'
             '<circle cx="180" cy="-14" r="2.4" fill="#ff5a5a"/>')
    b.append('<polygon points="580,182 584,62 596,52 608,62 612,182" fill="#2d1c42"/>')
    for y in range(44, 180, 14):
        b.append('<rect x="174" y="%d" width="13" height="2" fill="#ffcf7a" opacity=".5"/>' % y)
    # bay water with reflections
    b.append('<rect x="-600" y="182" width="2000" height="40" fill="url(#%s-sea)"/>' % p)
    for i, x in enumerate(range(-120, 900, 46)):
        b.append('<rect x="%d" y="%d" width="%d" height="2" fill="#ffd8a0" opacity=".35"/>' % (x + (i % 3) * 7, 188 + (i % 4) * 7, 18 + (i % 3) * 6))
    # stage floor + red backdrop banner behind leaders
    b.append('<rect x="-600" y="214" width="2000" height="200" fill="url(#%s-stage)"/>' % p)
    b.append('<rect x="-600" y="214" width="2000" height="4" fill="#d8a24a"/>')
    # three flags on tall poles behind leaders
    for fx, flag in ((258, _flag_us), (368, _flag_cn), (478, _flag_ru)):
        b.append('<rect x="%d" y="20" width="3" height="200" fill="#e6c36a"/>' % fx)
        b.append('<circle cx="%d" cy="19" r="4" fill="#f0d27a"/>' % (fx + 1.5))
        b.append(flag(fx + 3, 24, 72, 46))
        b.append('<path d="M%d,24 h18 v46 h-18 Z" fill="#000" opacity=".13"/>' % (fx + 42))
        b.append('<rect x="%d" y="24" width="72" height="46" fill="none" stroke="#000" stroke-opacity=".25" stroke-width=".8"/>' % (fx + 3))
    # leaders (left -> right: Trump, Xi, Putin), standing behind a draped table
    b.append(_figure(292, 222, 1.75, "#1f2a44", tie="#c3282f", hair="#e9c46a", skin="#efb48a", hair_style="swoop"))
    b.append(_figure(385, 222, 1.75, "#22232b", tie="#8f1d22", hair="#16141a", skin="#e6bd92"))
    b.append(_figure(478, 222, 1.75, "#3b414b", tie="#3a5f9a", hair="#b9ab92", skin="#ecc4a2", hair_style="thin"))
    # table with cloth, signed declaration & pens
    b.append('<ellipse cx="385" cy="262" rx="190" ry="10" fill="#000" opacity=".35"/>')
    b.append('<rect x="195" y="206" width="380" height="56" rx="3" fill="url(#%s-tbl)"/>' % p)
    b.append('<rect x="195" y="206" width="380" height="7" fill="#fff"/>')
    b.append('<rect x="195" y="230" width="380" height="5" fill="#c8a24a"/>')
    # document folders in leaders' colours
    for dx, col in ((268, "#1f3f7a"), (361, "#a61e22"), (454, "#1f3f7a")):
        b.append('<path d="M%d,209 l48,0 l6,-9 l-48,0 Z" fill="%s"/>' % (dx, col))
        b.append('<path d="M%d,208 l46,0 l5,-7 l-46,0 Z" fill="#fbf7ee"/>' % (dx + 3))
        b.append('<path d="M%d,204 q6,-4 12,0 t12,0" fill="none" stroke="#1a2f6a" stroke-width="1.2"/>' % (dx + 14))
    # badges
    b.append(_badge(120, 46, "3-WAY SUMMIT", 26, "#c3282f"))
    b.append(_txt(120, 92, "SHENZHEN", 22, "#ffe0b0", extra='letter-spacing="3"'))
    return _svg(p, w, h, DW, DH, d, "".join(b))


def icj_myanmar_genocide(w, h):
    p = "icj-myanmar-genocide"
    DW, DH = 400, 300
    d = (_lg(p + "-wall", [(0, "#3a2418"), (1, "#5e3b25")])
         + _lg(p + "-glass", [(0, "#2a5fa8"), (0.5, "#5fa0d8"), (1, "#e8c66a")])
         + _lg(p + "-bench", [(0, "#8a5a33"), (1, "#5a361c")])
         + _rg(p + "-glow", [(0, "#ffe2a0", 0.55), (1, "#ffe2a0", 0)]))
    b = [_bg("url(#%s-wall)" % p)]
    # wood panelling verticals
    for x in range(-200, 620, 34):
        b.append('<rect x="%d" y="-100" width="3" height="400" fill="#2a1810" opacity=".6"/>' % x)
    # three tall stained glass windows (Great Hall of Justice)
    for cx in (80, 200, 320):
        b.append('<path d="M%d,150 V40 a30,30 0 0 1 60,0 V150 Z" fill="#2a1a10"/>' % (cx - 30))
        b.append('<path d="M%d,146 V42 a26,26 0 0 1 52,0 V146 Z" fill="url(#%s-glass)"/>' % (cx - 26, p))
        for gx in (-9, 9):
            b.append('<rect x="%d" y="20" width="2" height="128" fill="#2a1a10"/>' % (cx + gx - 1))
        for gy in (60, 92, 122):
            b.append('<rect x="%d" y="%d" width="52" height="2" fill="#2a1a10"/>' % (cx - 26, gy))
        b.append('<circle cx="%d" cy="40" r="9" fill="#e9c35a" opacity=".85"/>' % cx)
    b.append('<ellipse cx="200" cy="90" rx="220" ry="90" fill="url(#%s-glow)"/>' % p)
    # big scales of justice in gold, centred above
    g = ('<g stroke="#f2cf6a" stroke-width="3" fill="none" stroke-linecap="round">'
         '<line x1="200" y1="56" x2="200" y2="128"/><line x1="160" y1="66" x2="240" y2="66"/>'
         '<line x1="160" y1="66" x2="148" y2="96"/><line x1="160" y1="66" x2="172" y2="96"/>'
         '<line x1="240" y1="66" x2="228" y2="88"/><line x1="240" y1="66" x2="252" y2="88"/></g>'
         '<path d="M144,96 Q160,110 176,96 Z" fill="#f2cf6a"/><path d="M224,88 Q240,102 256,88 Z" fill="#f2cf6a"/>'
         '<circle cx="200" cy="56" r="5" fill="#f2cf6a"/><rect x="186" y="126" width="28" height="6" rx="2" fill="#f2cf6a"/>')
    b.append(g)
    # 15 judges behind the bench: 9 (blue: majority) + 6 (grey) hint via collar colour stripe
    xs = [22 + i * 25.4 for i in range(15)]
    for i, x in enumerate(xs):
        b.append(_robe(x, 188, 0.78, robe="#14141c", skin=("#d9a982", "#b98462", "#e8c4a0", "#8d5a3c")[i % 4],
                       hair=("#3a332e", "#d8d2c8", "#1c1a18", "#6b5a4a")[i % 4]))
    # bench
    b.append('<rect x="-600" y="182" width="2000" height="200" fill="url(#%s-bench)"/>' % p)
    b.append('<rect x="-600" y="182" width="2000" height="7" fill="#b07a48"/>')
    for x in range(-200, 620, 50):
        b.append('<rect x="%d" y="196" width="40" height="50" rx="2" fill="none" stroke="#3e2412" stroke-width="2" opacity=".6"/>' % x)
    # Myanmar flag on a pole, left
    b.append(_pole(26, 108, 80, 40, 26, _flag_mm))
    # vote tally board
    b.append('<rect x="146" y="196" width="108" height="46" rx="5" fill="#000" opacity=".3"/>')
    b.append('<rect x="143" y="193" width="108" height="46" rx="5" fill="#f6efe0"/>')
    b.append(_txt(197, 233, "9–6", 46, "#123a7a", font=SERIF))
    b.append(_badge(330, 216, "GENOCIDE", 24, "#b3261e"))
    return _svg(p, w, h, DW, DH, d, "".join(b))


def iea_gulf_oil_loss(w, h):
    p = "iea-gulf-oil-loss"
    DW, DH = 400, 300
    d = (_lg(p + "-sky", [(0, "#3b1d3e"), (0.5, "#c4473a"), (1, "#f6a64a")])
         + _lg(p + "-sea", [(0, "#1d4a6a"), (1, "#0b2236")])
         + _lg(p + "-brl", [(0, "#1a1a1a"), (0.35, "#3b3b3b"), (0.7, "#1d1d1d"), (1, "#0d0d0d")], x2=1, y2=0)
         + _rg(p + "-sun", [(0, "#ffe08a", 1), (0.5, "#ffb45a", 0.5), (1, "#ffb45a", 0)]))
    b = [_bg("url(#%s-sky)" % p, -300, 470)]
    b.append('<circle cx="300" cy="150" r="80" fill="url(#%s-sun)"/>' % p)
    # desert coast + refinery silhouette
    b.append('<path d="M-600,160 L40,160 Q90,140 150,152 Q220,162 300,150 Q360,142 1000,156 L1000,175 L-600,175 Z" fill="#6b2f2a"/>')
    for x, hh, ww in ((20, 34, 16), (42, 22, 26), (250, 30, 22), (276, 46, 10), (292, 26, 30), (330, 38, 14), (350, 20, 26)):
        b.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#3a1820"/>' % (x, 160 - hh, ww, hh))
    # flare stack with fire
    b.append('<rect x="372" y="96" width="5" height="64" fill="#3a1820"/>')
    b.append(_flame(374.5, 98, 12, 26, p, 0))
    b.append(_smoke([(380, 64, 10), (392, 52, 13), (408, 40, 16), (428, 30, 18)], "#3a1f2a", 0.55))
    # storage tanks
    for x in (70, 104, 210):
        b.append('<rect x="%d" y="140" width="28" height="20" fill="#4a2228"/><ellipse cx="%d" cy="140" rx="14" ry="3.5" fill="#5e2e32"/>' % (x, x + 14))
    # sea
    b.append('<rect x="-600" y="172" width="2000" height="300" fill="url(#%s-sea)"/>' % p)
    for i, y in enumerate((182, 196, 212, 230)):
        b.append(_waves(-200 + i * 9, 640, y, "#7fb3d5", step=26, op=0.35))
    b.append('<rect x="270" y="176" width="60" height="3" fill="#ffc46a" opacity=".5"/><rect x="284" y="186" width="34" height="3" fill="#ffc46a" opacity=".35"/>')
    # oil platform
    b.append('<g fill="#2a1b22"><rect x="300" y="128" width="58" height="8"/><rect x="306" y="136" width="5" height="50"/>'
             '<rect x="346" y="136" width="5" height="50"/><rect x="326" y="136" width="5" height="50"/>'
             '<polygon points="314,128 322,92 330,128"/><rect x="336" y="114" width="18" height="14"/></g>')
    # falling chart line across the sky
    b.append('<polyline points="20,48 70,58 110,52 150,84 190,96 230,126" fill="none" stroke="#fff" stroke-width="4" '
             'stroke-linejoin="round" stroke-linecap="round" opacity=".95"/>')
    b.append('<polygon points="230,126 214,124 228,112" fill="#fff" transform="rotate(10 230 126)"/>')
    # giant leaking oil barrel (focal)
    bx, by, bw, bh = 104, 112, 92, 112
    b.append('<ellipse cx="%d" cy="%d" rx="64" ry="9" fill="#000" opacity=".45"/>' % (bx + 46, by + bh + 6))
    b.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="url(#%s-brl)"/>' % (bx, by, bw, bh, p))
    for ry in (by + 26, by + bh - 26):
        b.append('<rect x="%d" y="%d" width="%d" height="5" fill="#5a5a5a"/>' % (bx, ry, bw))
    b.append('<ellipse cx="%d" cy="%d" rx="46" ry="9" fill="#2e2e2e" stroke="#555" stroke-width="2"/>' % (bx + 46, by))
    b.append('<rect x="%d" y="%d" width="%d" height="22" fill="#e8b23a"/>' % (bx, by + 44, bw))
    b.append(_txt(bx + 46, by + 62, "IEA", 20, "#1a1a1a"))
    # leak: crack + oil pooling
    b.append('<path d="M%d,%d l6,4 l-4,5 l7,5" fill="none" stroke="#000" stroke-width="2"/>' % (bx + 78, by + 76))
    b.append('<path d="M%d,%d q10,6 16,20 q4,12 -2,16 q-6,2 -6,-10 Z" fill="#050505"/>' % (bx + 84, by + 90))
    b.append('<ellipse cx="%d" cy="%d" rx="58" ry="7" fill="#050505" opacity=".9"/>' % (bx + 110, by + bh + 6))
    b.append(_badge(300, 34, "2.8BN BBL LOST", 24, "#d9481c"))
    return _svg(p, w, h, DW, DH, d, "".join(b))


def anthropic_ipo_debut(w, h):
    p = "anthropic-ipo-debut"
    DW, DH = 400, 300
    d = (_lg(p + "-sky", [(0, "#0a1030"), (1, "#26306a")])
         + _lg(p + "-scr", [(0, "#0a2a6a"), (1, "#1257c8")], x2=1, y2=0)
         + _lg(p + "-st", [(0, "#22263a"), (1, "#0e1020")])
         + _rg(p + "-glow", [(0, "#3aa0ff", 0.55), (1, "#3aa0ff", 0)]))
    b = [_bg("url(#%s-sky)" % p)]
    # Times Square towers in background with lit windows
    for x, bw, bh, col in ((-120, 60, 200, "#1a1f44"), (-60, 50, 240, "#151a3a"), (-10, 44, 210, "#1d2350"),
                           (300, 46, 230, "#1d2350"), (346, 56, 200, "#151a3a"), (402, 60, 250, "#1a1f44"), (462, 60, 190, "#151a3a")):
        b.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (x, 240 - bh, bw, bh, col))
        for wy in range(240 - bh + 10, 236, 12):
            for wx in range(x + 6, x + bw - 6, 10):
                if (wx * 7 + wy * 3) % 5 < 3:
                    b.append('<rect x="%d" y="%d" width="4" height="5" fill="#ffd57a" opacity=".55"/>' % (wx, wy))
    # side billboards (coloured)
    b.append('<rect x="-4" y="60" width="38" height="56" fill="#e0457b"/><rect x="2" y="66" width="26" height="12" fill="#ffd3e3"/>')
    b.append('<rect x="306" y="78" width="36" height="46" fill="#f2b632"/><rect x="312" y="86" width="24" height="8" fill="#fff6d6"/>')
    b.append('<rect x="352" y="50" width="44" height="40" fill="#22c58b"/>')
    # Nasdaq-style curved cylindrical tower screen (focal)
    b.append('<ellipse cx="170" cy="130" rx="150" ry="130" fill="url(#%s-glow)"/>' % p)
    b.append('<path d="M68,24 Q170,6 272,24 L272,236 Q170,220 68,236 Z" fill="url(#%s-scr)"/>' % p)
    for y in range(36, 230, 9):
        b.append('<path d="M68,%d Q170,%d 272,%d" fill="none" stroke="#5aa8ff" stroke-width=".7" opacity=".35"/>' % (y, y - 18, y))
    b.append('<path d="M240,22 Q258,24 272,24 L272,236 Q258,235 240,232 Z" fill="#000" opacity=".25"/>')
    # ticker panel
    b.append('<path d="M80,38 Q170,24 260,38 L260,82 Q170,70 80,82 Z" fill="#06143a"/>')
    b.append(_txt(126, 72, "ANT", 34, "#fff", extra='transform="skewY(-3)"'))
    b.append(_txt(214, 68, "▲ $97.17", 24, "#3ef08a", extra='transform="skewY(-3)"'))
    # rising chart on screen
    b.append('<polyline points="88,196 116,186 140,192 164,168 190,158 214,132 240,104" fill="none" stroke="#3ef08a" '
             'stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>')
    b.append('<polygon points="250,92 234,100 246,112" fill="#3ef08a"/>')
    b.append('<polyline points="88,196 116,186 140,192 164,168 190,158 214,132 240,104 240,214 88,214" fill="#3ef08a" opacity=".14"/>')
    b.append('<line x1="88" y1="190" x2="248" y2="190" stroke="#fff" stroke-width="1.2" stroke-dasharray="4 4" opacity=".7"/>')
    b.append(_txt(250, 186, "IPO $83", 13, "#cfe0ff", anchor="end"))
    # street + crowd silhouettes
    b.append('<rect x="-600" y="236" width="2000" height="200" fill="url(#%s-st)"/>' % p)
    for i, x in enumerate(range(-40, 440, 22)):
        hh = 22 + (i * 5) % 9
        b.append('<path d="M%d,262 v-%d a8,8 0 0 1 16,0 v%d Z" fill="#0a0b16"/><circle cx="%d" cy="%d" r="6" fill="#0a0b16"/>'
                 % (x, hh - 8, hh - 8, x + 8, 262 - hh - 2))
    # confetti
    cols = ("#ff5a8a", "#ffd23a", "#3ef08a", "#5ac8ff", "#fff")
    for i in range(34):
        cx, cy = (i * 53) % 400, 20 + (i * 37) % 200
        b.append('<rect x="%d" y="%d" width="5" height="2.6" fill="%s" transform="rotate(%d %d %d)"/>'
                 % (cx, cy, cols[i % 5], (i * 47) % 180, cx, cy))
    b.append(_badge(334, 150, "+17%", 40, "#16a35a"))
    return _svg(p, w, h, DW, DH, d, "".join(b))


# ================================================================ SMALL CARDS (330x150)
def putin_no_truce(w, h):
    p = "putin-no-truce"
    DW, DH = 330, 150
    d = (_lg(p + "-sky", [(0, "#41506e"), (0.6, "#c98a6a"), (1, "#e7b38a")])
         + _lg(p + "-sea", [(0, "#2d5a7a"), (1, "#163448")]))
    b = [_bg("url(#%s-sky)" % p, -300, 400)]
    # sea
    b.append('<rect x="-600" y="96" width="2000" height="200" fill="url(#%s-sea)"/>' % p)
    b.append(_waves(-100, 440, 110, "#9cc6e2", step=20, op=0.35))
    b.append(_waves(-90, 440, 122, "#9cc6e2", step=20, op=0.3))
    # Crimean (Kerch) bridge: road deck + railway arch, strike smoke on the span
    b.append('<rect x="-600" y="84" width="2000" height="5" fill="#2b2f3a"/>')
    for x in range(-200, 640, 26):
        b.append('<rect x="%d" y="89" width="4" height="12" fill="#2b2f3a"/>' % x)
    b.append('<path d="M150,86 Q210,40 270,86" fill="none" stroke="#2b2f3a" stroke-width="5"/>')
    for x in range(160, 268, 12):
        yy = 86 - (1 - ((x - 210) / 60.0) ** 2) * 46
        b.append('<line x1="%d" y1="%.1f" x2="%d" y2="86" stroke="#2b2f3a" stroke-width="1.4"/>' % (x, yy, x))
    b.append(_smoke([(238, 70, 10), (250, 56, 14), (264, 42, 17), (284, 28, 20), (308, 18, 22)], "#2a2630", 0.8))
    b.append(_flame(236, 86, 22, 22, p, 0))
    # Putin at a podium, left, with Russian flag
    b.append(_pole(14, 8, 120, 46, 30, _flag_ru))
    b.append(_figure(100, 128, 1.45, "#30343e", tie="#1f3f7a", hair="#b9ab92", skin="#ecc4a2", hair_style="thin"))
    b.append('<path d="M70,108 L130,108 L124,160 L76,160 Z" fill="#6b3a24"/><rect x="66" y="104" width="68" height="7" fill="#8a4e30"/>')
    b.append('<path d="M94,104 q3,-10 8,-12" fill="none" stroke="#111" stroke-width="1.8"/><circle cx="103" cy="91" r="2.8" fill="#111"/>')
    b.append('<circle cx="100" cy="122" r="6" fill="#e3c06a"/>')
    # quote badge
    b.append(_badge(246, 82, "“NO TRUCE”", 22, "#b3261e"))
    b.append(_badge(306, 14, "CLAIM", 13, "#d98a12", pad=4))
    return _svg(p, w, h, DW, DH, d, "".join(b))


def kyiv_embassies(w, h):
    p = "kyiv-embassies"
    DW, DH = 330, 150
    d = (_lg(p + "-sky", [(0, "#0e1530"), (1, "#3c3a62")])
         + _rg(p + "-fire", [(0, "#ff8a3a", 0.8), (1, "#ff8a3a", 0)]))
    b = [_bg("url(#%s-sky)" % p)]
    # distant Kyiv skyline: golden domes (Lavra-like) & blocks
    b.append('<g fill="#232650">')
    for x, bh in ((-80, 40), (-40, 54), (0, 36), (200, 46), (238, 30), (272, 52), (310, 40), (350, 56)):
        b.append('<rect x="%d" y="%d" width="34" height="%d"/>' % (x, 100 - bh, bh))
    b.append('</g>')
    for cx, r in ((160, 9), (146, 6), (174, 6)):
        b.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#2c2f5a"/>' % (cx - r, 66 - r, 2 * r, 40))
        b.append('<path d="M%d,%d q%d,-%d %d,0 Z" fill="#e2b33a"/><rect x="%d" y="%d" width="1.4" height="7" fill="#e2b33a"/>'
                 % (cx - r, 66 - r, r, r * 2, 2 * r, cx - 0.7, 66 - 3 * r - 4))
    b.append('<ellipse cx="165" cy="70" rx="160" ry="60" fill="url(#%s-fire)"/>' % p)
    # two embassy buildings with flags, damaged windows
    def bldg(x, wd, flag, label):
        o = ['<rect x="%d" y="44" width="%d" height="90" fill="#d6cfc0"/>' % (x, wd),
             '<rect x="%d" y="44" width="%d" height="90" fill="#000" opacity=".14"/>' % (x + wd - 14, 14),
             '<rect x="%d" y="40" width="%d" height="6" fill="#bdb5a4"/>' % (x - 3, wd + 6)]
        for r in range(4):
            for c in range(4):
                wx, wy = x + 8 + c * (wd - 16) / 4.0, 52 + r * 18
                broken = (r + c + x) % 3 == 0
                o.append('<rect x="%.1f" y="%d" width="%.1f" height="11" fill="%s"/>'
                         % (wx, wy, (wd - 16) / 4.0 - 5, "#1a1820" if broken else "#ffd88a"))
                if broken:
                    o.append('<path d="M%.1f,%d l4,5 l-3,3 l5,3" fill="none" stroke="#d6cfc0" stroke-width="1"/>' % (wx + 1, wy))
        o.append(_pole(x + wd / 2.0, 12, 30, 30, 20, flag))
        return "".join(o)
    b.append(bldg(46, 96, _flag_nl, "NL"))
    b.append(bldg(188, 96, _flag_at, "AT"))
    # blast damage: scorch, smoke and debris
    b.append('<path d="M126,80 l12,-8 l8,10 l10,-6 l-4,16 l-14,4 Z" fill="#14121a"/>')
    b.append(_smoke([(150, 44, 14), (164, 30, 18), (184, 18, 20), (210, 8, 22)], "#3a3640", 0.75))
    b.append(_flame(144, 84, 18, 18, p, 0))
    b.append('<rect x="-600" y="134" width="2000" height="100" fill="#1a1a26"/>')
    for i, x in enumerate((40, 70, 130, 158, 200, 262, 290)):
        b.append('<polygon points="%d,134 %d,%d %d,134" fill="#8a8478"/>' % (x, x + 4, 128 - (i % 3) * 2, x + 9))
    b.append(_badge(165, 96, "2 EMBASSIES HIT", 17, "#b3261e"))
    return _svg(p, w, h, DW, DH, d, "".join(b))


def senate_iran_war_powers(w, h):
    p = "senate-iran-war-powers"
    DW, DH = 330, 150
    d = (_lg(p + "-sky", [(0, "#1d3a6e"), (0.7, "#e0886a"), (1, "#f3c08a")])
         + _lg(p + "-dome", [(0, "#ffffff"), (1, "#cfc8bb")], x2=1, y2=0))
    b = [_bg("url(#%s-sky)" % p)]
    # Capitol: dome, drum, wings
    cx = 112
    b.append('<rect x="-600" y="112" width="2000" height="200" fill="#3d5a3a"/>')
    b.append('<rect x="%d" y="88" width="190" height="28" fill="#ece6da"/>' % (cx - 95))
    for x in range(cx - 92, cx + 94, 9):
        b.append('<rect x="%d" y="92" width="3.6" height="22" fill="#c9c1b2"/>' % x)
    b.append('<polygon points="%d,88 %d,76 %d,88" fill="#ece6da"/>' % (cx - 30, cx, cx + 30))
    b.append('<rect x="%d" y="54" width="56" height="26" fill="#ece6da"/>' % (cx - 28))
    for x in range(cx - 26, cx + 28, 7):
        b.append('<rect x="%d" y="58" width="3" height="20" fill="#c9c1b2"/>' % x)
    b.append('<path d="M%d,56 Q%d,8 %d,56 Z" fill="url(#%s-dome)"/>' % (cx - 34, cx, cx + 34, p))
    for k in (-18, 0, 18):
        b.append('<path d="M%d,55 Q%d,20 %d,24" fill="none" stroke="#bdb5a4" stroke-width="1.2"/>' % (cx + k, cx + k * 0.6, cx))
    b.append('<rect x="%d" y="18" width="10" height="10" fill="#ece6da"/><path d="M%d,18 l5,-10 l5,10 Z" fill="#ece6da"/>' % (cx - 5, cx - 5))
    b.append('<path d="M%d,8 l1,-3 l1,3 Z" fill="#ece6da"/>' % (cx - 1))
    b.append('<rect x="-600" y="114" width="2000" height="6" fill="#d7cfbd"/>')
    # US flag on a pole
    b.append(_pole(18, 24, 92, 40, 21, _flag_us))
    # vote board (focal)
    bx = 214
    b.append('<rect x="%d" y="16" width="108" height="96" rx="5" fill="#000" opacity=".35"/>' % (bx + 3))
    b.append('<rect x="%d" y="12" width="108" height="96" rx="5" fill="#101626"/>' % bx)
    b.append(_txt(bx + 31, 30, "YEA", 13, "#7fe0a0"))
    b.append(_txt(bx + 79, 30, "NAY", 13, "#ff8a7a"))
    b.append(_txt(bx + 54, 70, "48–51", 40, "#fff", font=SERIF))
    b.append('<rect x="%d" y="80" width="96" height="20" rx="3" fill="#c3282f"/>' % (bx + 6))
    b.append(_txt(bx + 54, 95, "FAILS", 17, "#fff", extra='letter-spacing="2"'))
    # bar split
    b.append('<rect x="%d" y="36" width="%.1f" height="5" fill="#3ec46d"/>' % (bx + 6, 96 * 48 / 99.0))
    b.append('<rect x="%.1f" y="36" width="%.1f" height="5" fill="#e0483a"/>' % (bx + 6 + 96 * 48 / 99.0, 96 * 51 / 99.0))
    return _svg(p, w, h, DW, DH, d, "".join(b))


def hormuz_mine_claim(w, h):
    p = "hormuz-mine-claim"
    DW, DH = 330, 150
    d = (_lg(p + "-sky", [(0, "#4a2a3a"), (0.6, "#c4583a"), (1, "#eb9a52")])
         + _lg(p + "-sea", [(0, "#24506e"), (1, "#0e2a40")])
         + _rg(p + "-glow", [(0, "#ff9a3a", 0.75), (1, "#ff9a3a", 0)]))
    b = [_bg("url(#%s-sky)" % p, -300, 400)]
    # Musandam mountains on the horizon
    b.append('<path d="M-600,86 L-20,86 L20,60 L50,72 L84,50 L120,74 L160,66 L200,80 L240,58 L280,70 L320,56 L360,76 L1000,86 Z" fill="#5a2e36"/>')
    b.append('<path d="M-600,86 L40,86 L70,72 L100,80 L150,74 L210,84 L270,74 L330,82 L1000,86 Z" fill="#3e1f2a"/>')
    # sea
    b.append('<rect x="-600" y="86" width="2000" height="200" fill="url(#%s-sea)"/>' % p)
    for i, y in enumerate((96, 108, 122, 136)):
        b.append(_waves(-100 + i * 7, 440, y, "#8cc0de", step=18, op=0.3))
    # smoke plumes
    b.append(_smoke([(96, 60, 12), (104, 44, 16), (118, 28, 20), (136, 12, 24), (160, 0, 28)], "#221c24", 0.85))
    b.append(_smoke([(232, 66, 10), (240, 52, 14), (252, 38, 18), (270, 24, 22), (292, 12, 26)], "#221c24", 0.8))
    b.append('<ellipse cx="100" cy="88" rx="60" ry="22" fill="url(#%s-glow)"/>' % p)
    b.append('<ellipse cx="236" cy="92" rx="50" ry="18" fill="url(#%s-glow)"/>' % p)
    # two tankers, listing slightly, both burning
    b.append('<g transform="rotate(-3 90 96)">' + _tanker(14, 100, 150) + '</g>')
    b.append(_flame(98, 86, 22, 30, p, 0) + _flame(118, 86, 14, 18, p, 1))
    b.append('<g transform="rotate(2.5 240 100)">' + _tanker(196, 104, 124, hull="#2f3540", deck="#7a2a24", flip=True) + '</g>')
    b.append(_flame(236, 91, 18, 26, p, 0))
    # sea mine (spiked sphere) in foreground
    mx, my, r = 168, 112, 11
    spikes = "".join('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
                     % (mx + r * 0.8 * math.cos(a), my + r * 0.8 * math.sin(a), mx + (r + 6) * math.cos(a), my + (r + 6) * math.sin(a))
                     for a in [k * math.pi / 4 + 0.2 for k in range(8)])
    b.append('<g stroke="#111" stroke-width="2.6" stroke-linecap="round">%s</g>' % spikes)
    b.append('<circle cx="%d" cy="%d" r="%d" fill="#1b1b1f"/><circle cx="%d" cy="%d" r="3.4" fill="#5a5a66"/>' % (mx, my, r, mx - 4, my - 4))
    b.append('<path d="M%d,%d q%d,6 %d,0 v12 h-%d Z" fill="url(#%s-sea)"/>' % (mx - 20, my + 4, 20, 40, 40, p))
    b.append(_waves(mx - 22, mx + 22, my + 5, "#cfe6f5", step=11, amp=1.6, op=0.8, sw=1.6))
    b.append(_badge(300, 18, "CLAIM", 18, "#d98a12", pad=5))
    b.append(_badge(48, 18, "2 TANKERS", 16, "#14121a"))
    return _svg(p, w, h, DW, DH, d, "".join(b))


ILLUS_PART = {
    "trump-xi-putin-shenzhen": trump_xi_putin_shenzhen,
    "icj-myanmar-genocide": icj_myanmar_genocide,
    "iea-gulf-oil-loss": iea_gulf_oil_loss,
    "anthropic-ipo-debut": anthropic_ipo_debut,
    "putin-no-truce": putin_no_truce,
    "kyiv-embassies": kyiv_embassies,
    "senate-iran-war-powers": senate_iran_war_powers,
    "hormuz-mine-claim": hormuz_mine_claim,
}
