"""Small-card illustrations (part B). Each fn(w, h) -> inline <svg> string.

Full-bleed flat-vector editorial scenes. Every drawing is designed on a
163x74 canvas (the small-card display size, so text sizes are true pixels).
The viewBox is fitted to the requested w:h aspect, centred on that canvas,
and backgrounds overdraw far past the edges, so "xMidYMid slice" cropping is
safe. The bottom ~15% (y > 63) sits under the page's caption band and holds
only ground/background.
"""
import math

INK = "#1d1a16"
FONT = "Barlow Condensed"
CW, CH = 163.0, 74.0          # design canvas
SAFE_B = 62                    # essential content stays above this y


# --- core helpers ---------------------------------------------------------------
def _svg(w, h, sid, body, defs=""):
    w, h = max(1.0, float(w)), max(1.0, float(h))
    asp = w / h
    if asp >= CW / CH:
        vw, vh = CW, CW / asp
    else:
        vw, vh = CH * asp, CH
    vx, vy = (CW - vw) / 2, (CH - vh) / 2
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="%.2f %.2f %.2f %.2f" '
            'preserveAspectRatio="xMidYMid slice" role="img" aria-label="%s">'
            '<defs>%s</defs>%s</svg>' % (round(w), round(h), vx, vy, vw, vh, sid, defs, body))


def _lin(id_, stops, x2=0, y2=1):
    s = "".join('<stop offset="%s" stop-color="%s"/>' % (o, c) for o, c in stops)
    return ('<linearGradient id="%s" x1="0" y1="0" x2="%s" y2="%s">%s</linearGradient>'
            % (id_, x2, y2, s))


def _rad(id_, stops, cx=0.5, cy=0.5, r=0.5):
    s = "".join('<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (o, c, op) for o, c, op in stops)
    return '<radialGradient id="%s" cx="%s" cy="%s" r="%s">%s</radialGradient>' % (id_, cx, cy, r, s)


def _bg(fill):
    return '<rect x="-200" y="-200" width="563" height="474" fill="%s"/>' % fill


def _band(y, fill, h=300):
    return '<rect x="-200" y="%.1f" width="563" height="%d" fill="%s"/>' % (y, h, fill)


def _text(x, y, s, size=10, fill=INK, weight=700, anchor="middle", extra=""):
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-weight="%d" font-size="%.1f" '
            'fill="%s" text-anchor="%s" %s>%s</text>' % (x, y, FONT, weight, size, fill, anchor, extra, s))


def _badge(x, y, w, h, label, bg="#c0392b", fg="#ffffff", size=11):
    """Bold label chip, centred on x; y is the top."""
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="#000" opacity="0.25" '
            'transform="translate(1 1)"/>'
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s"/>'
            % (x - w / 2, y, w, h, x - w / 2, y, w, h, bg)
            + _text(x, y + h / 2 + size * 0.36, label, size, fg, 700, "middle", 'letter-spacing="0.4"'))


def _star(cx, cy, r, fill, rot=-90):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.4
        a = math.radians(rot + i * 36)
        pts.append("%.2f,%.2f" % (cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return '<polygon points="%s" fill="%s"/>' % (" ".join(pts), fill)


def _person(x, y, s=1.0, suit="#2b2f3a", skin="#8a5a3c", tie=None, legs=None, cap=None, walk=0):
    """Simple standing figure; (x, y) = feet centre, about 22*s tall."""
    legs = legs or suit
    st = 1.2 * walk
    g = ('<g transform="translate(%.1f %.1f) scale(%.2f)">'
         '<ellipse cx="0" cy="0.4" rx="5" ry="1.1" fill="#000" opacity="0.22"/>'
         '<path d="M-2.6 -9 L%.1f 0 h2.2 L0 -7 L%.1f 0 h2.2 L2.6 -9 Z" fill="%s"/>'
         '<path d="M-3.6 -16.5 Q0 -18 3.6 -16.5 L3.3 -8.6 H-3.3 Z" fill="%s"/>'
         '<path d="M-3.6 -16 L-4.6 -9.5 M3.6 -16 L4.6 -9.5" stroke="%s" stroke-width="1.7" stroke-linecap="round"/>'
         '<circle cx="0" cy="-19.6" r="2.6" fill="%s"/>'
         % (x, y, s, -2.8 - st, 0.6 + st, legs, suit, suit, skin))
    if tie:
        g += ('<path d="M-0.9 -16.9 L0.9 -16.9 L0 -15.8 Z" fill="#fff"/>'
              '<path d="M0 -16.2 L0.7 -14.4 L0 -11.6 L-0.7 -14.4 Z" fill="%s"/>' % tie)
    if cap:
        g += '<path d="M-2.8 -20.4 Q0 -23.6 2.8 -20.4 Z" fill="%s"/>' % cap
    return g + '</g>'


# --- flags (x, y = top-left) ---------------------------------------------------
def _frame(x, y, w, h):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" '
            'stroke-opacity="0.35" stroke-width="0.5"/>' % (x, y, w, h))


def flag_somalia(x, y, w, h):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#4189dd"/>' % (x, y, w, h)
            + _star(x + w / 2, y + h / 2 + h * 0.03, h * 0.34, "#fff") + _frame(x, y, w, h))


def flag_senegal(x, y, w, h):
    t = w / 3
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#00853f"/>'
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdef42"/>'
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#e31b23"/>'
            % (x, y, t, h, x + t, y, t, h, x + 2 * t, y, t, h)
            + _star(x + w / 2, y + h / 2 + h * 0.03, h * 0.24, "#00853f") + _frame(x, y, w, h))


def flag_bangladesh(x, y, w, h):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#006a4e"/>'
            '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#f42a41"/>'
            % (x, y, w, h, x + w * 0.45, y + h / 2, h * 0.32) + _frame(x, y, w, h))


def flag_el_salvador(x, y, w, h):
    t = h / 3
    cx, cy = x + w / 2, y + h / 2
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#0f47af"/>'
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff"/>'
            '<circle cx="%.1f" cy="%.1f" r="%.2f" fill="none" stroke="#c9a227" stroke-width="0.5"/>'
            '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#2e8b4a"/>'
            % (x, y, w, h, x, y + t, w, t, cx, cy, t * 0.45,
               cx, cy - t * 0.3, cx - t * 0.3, cy + t * 0.22, cx + t * 0.3, cy + t * 0.22)
            + _frame(x, y, w, h))


def flag_tonga(x, y, w, h):
    cw, ch = w * 0.42, h * 0.5
    a = ch * 0.17
    cx, cy = x + cw / 2, y + ch / 2
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#c10000"/>'
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff"/>'
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#c10000"/>'
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#c10000"/>'
            % (x, y, w, h, x, y, cw, ch, cx - a / 2, cy - a * 1.6, a, a * 3.2, cx - a * 1.6, cy - a / 2, a * 3.2, a)
            + _frame(x, y, w, h))


def _flagpole(fn, x, top, w, h, bottom, pole="#d9d4c8"):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.3" stroke-linecap="round"/>'
            '<circle cx="%.1f" cy="%.1f" r="1" fill="#e0b84a"/>'
            % (x, top - 1.5, x, bottom, pole, x, top - 2) + fn(x + 0.7, top, w, h))


# --- scenes ---------------------------------------------------------------------
def somalia_uae_envoy(w, h):
    sid = "somalia-uae-envoy"
    d = (_lin(sid + "-sky", [(0, "#f6a65a"), (0.55, "#f9d38c"), (1, "#fbe7b8")])
         + _lin(sid + "-sea", [(0, "#2f7fb8"), (1, "#1d5f91")])
         + _lin(sid + "-tar", [(0, "#5c5f66"), (1, "#3c3f45")]))
    b = _bg("url(#%s-sky)" % sid)
    b += '<circle cx="128" cy="20" r="9" fill="#fff4d6" opacity="0.9"/>'
    b += _band(37, "url(#%s-sea)" % sid)
    b += '<path d="M90 41 h26 M120 44 h20 M100 47 h14" stroke="#9cd0f0" stroke-width="0.7" opacity="0.7"/>'
    # Mogadishu whitewashed skyline, far left
    b += ('<g fill="#efe6d6">'
          '<rect x="-40" y="22" width="20" height="18"/><rect x="-22" y="16" width="14" height="24"/>'
          '<rect x="-10" y="24" width="18" height="16"/><rect x="6" y="19" width="12" height="21"/>'
          '<rect x="16" y="26" width="22" height="14"/><rect x="36" y="22" width="12" height="18"/>'
          '<rect x="46" y="28" width="22" height="12"/>'
          '<path d="M10 19 q2 -6 4 0 z M-17 16 v-6 h1 v6"/></g>'
          '<g fill="#c9b99c">'
          + "".join('<rect x="%d" y="%d" width="2" height="3"/>' % (x, y)
                    for x, y in ((-36, 27), (-31, 27), (-18, 21), (-14, 21), (-6, 28), (0, 28),
                                 (9, 24), (21, 30), (27, 30), (39, 26), (50, 32), (58, 32)))
          + '</g>')
    # tarmac
    b += _band(46, "url(#%s-tar)" % sid)
    b += '<path d="M-60 55 H220" stroke="#e8d36a" stroke-width="0.9" stroke-dasharray="6 5"/>'
    # airliner on the apron, right
    b += ('<g transform="translate(104 34)">'
          '<path d="M0 6 Q2 2 8 2 H44 Q49 2 50 5 L52 -6 H56 L55 6 Q54 10 48 10 H6 Q1 10 0 6 Z" fill="#f4f4f2"/>'
          '<path d="M2 7 H50" stroke="#c0392b" stroke-width="1.1"/>'
          '<path d="M18 9 L30 16 H35 L28 9 Z" fill="#d7d9dc"/>'
          + "".join('<rect x="%d" y="4" width="1.6" height="1.6" rx="0.4" fill="#5a6b7c"/>' % x for x in range(10, 46, 4))
          + '<rect x="27" y="10" width="6" height="2.6" rx="1.2" fill="#9aa0a8"/>'
          '<line x1="9" y1="10" x2="9" y2="13" stroke="#333" stroke-width="0.8"/><circle cx="9" cy="13.4" r="1" fill="#222"/>'
          '<line x1="36" y1="10" x2="36" y2="13" stroke="#333" stroke-width="0.8"/><circle cx="36" cy="13.4" r="1" fill="#222"/>'
          '</g>')
    # stairs
    b += '<path d="M101 47 L108 40 H111 L111 47 Z" fill="#b7bcc3"/>'
    # Somali flag
    b += _flagpole(flag_somalia, 8, 9, 28, 18, 54)
    # envoy walking to the plane with suitcase
    b += _person(83, 55, 1.15, suit="#1f2430", skin="#c99a72", tie="#c0392b", walk=1)
    b += ('<rect x="89" y="45.5" width="8" height="7.5" rx="1" fill="#7a4b26"/>'
          '<path d="M91.5 45.5 v-1.4 h3 v1.4" fill="none" stroke="#3a2412" stroke-width="0.8"/>')
    b += '<path d="M58 50 h12 l-3 -2.4 M70 50 l-3 2.4" fill="none" stroke="#fff" stroke-width="1.3" stroke-linecap="round" opacity="0.85"/>'
    # 72-hour clock + badge
    b += ('<g transform="translate(55 17)">'
          '<circle r="10.5" fill="#fff" stroke="%s" stroke-width="1.6"/>'
          '<path d="M0 0 L0 -10.5 A10.5 10.5 0 1 1 -9.1 5.25 Z" fill="#f0a29a"/>'
          '<circle r="10.5" fill="none" stroke="%s" stroke-width="1.6"/>'
          '<path d="M0 0 V-7 M0 0 l4.4 2.6" stroke="%s" stroke-width="1.5" stroke-linecap="round"/>'
          '<circle r="1.2" fill="%s"/></g>' % (INK, INK, INK, INK))
    b += _badge(55, 29.5, 30, 11, "72 HRS", "#c0392b", size=10.5)
    return _svg(w, h, sid, b, d)


def senegal_budget_decree(w, h):
    sid = "senegal-budget-decree"
    d = (_lin(sid + "-wall", [(0, "#e7d2a8"), (1, "#cfae7a")])
         + _lin(sid + "-desk", [(0, "#7a4523"), (1, "#4f2a14")])
         + _rad(sid + "-lamp", [(0, "#fff6d8", 0.75), (1, "#fff6d8", 0)], 0.5, 0.5, 0.5))
    b = _bg("url(#%s-wall)" % sid)
    # wood panelling
    b += "".join('<rect x="%d" y="-20" width="1" height="70" fill="#b8925c" opacity="0.6"/>' % x
                 for x in range(-30, 200, 22))
    # window with Dakar view (sea + skyline) behind
    b += ('<rect x="96" y="4" width="46" height="32" fill="#7ec3e6"/>'
          '<rect x="96" y="26" width="46" height="10" fill="#2a83b8"/>'
          '<path d="M96 26 h6 v-6 h4 v-3 h5 v9 h6 v-5 h7 v5 h5 v-9 h4 v9 h5 V26 Z" fill="#f3efe6"/>'
          '<rect x="95" y="3" width="48" height="34" fill="none" stroke="#5d3a1c" stroke-width="2"/>'
          '<line x1="119" y1="4" x2="119" y2="36" stroke="#5d3a1c" stroke-width="1.4"/>')
    b += '<ellipse cx="70" cy="34" rx="50" ry="26" fill="url(#%s-lamp)"/>' % sid
    # Senegal flag on stand
    b += _flagpole(flag_senegal, 12, 7, 30, 20, 46, pole="#8a6a3a")
    b += '<path d="M8 47 h8 l-1 -2 h-6 z" fill="#8a6a3a"/>'
    # desk
    b += _band(44, "url(#%s-desk)" % sid)
    b += '<rect x="-200" y="44" width="563" height="1.6" fill="#9a6235"/>'
    # decree document (focal)
    b += ('<g transform="rotate(-4 70 44)">'
          '<rect x="49" y="12" width="40" height="44" fill="#000" opacity="0.25" transform="translate(1.6 1.6)"/>'
          '<rect x="49" y="12" width="40" height="44" fill="#fffdf6"/>'
          '<rect x="49" y="12" width="40" height="3" fill="#00853f"/>'
          '<rect x="62.3" y="12" width="13.4" height="3" fill="#fdef42"/>'
          '<rect x="75.7" y="12" width="13.3" height="3" fill="#e31b23"/>'
          + _text(69, 23.5, "DECREE", 8.5, INK, 700, "middle", 'letter-spacing="1"')
          + "".join('<rect x="54" y="%d" width="30" height="1.3" fill="#b9b2a4"/>' % yy for yy in (27, 30.5, 34, 37.5))
          + '<path d="M54 49 q3 -5 5 0 t5 -1 t6 -2" fill="none" stroke="#1d3f8a" stroke-width="1.2" stroke-linecap="round"/>'
          '<circle cx="80" cy="48" r="4.6" fill="#c0392b"/>'
          '<circle cx="80" cy="48" r="2.8" fill="none" stroke="#f3c1b8" stroke-width="0.7"/>'
          '</g>')
    # hand with pen
    b += ('<g transform="rotate(-38 76 44)">'
          '<rect x="70" y="42" width="24" height="3.4" rx="1.4" fill="#1d1a16"/>'
          '<polygon points="70,42 66,43.7 70,45.4" fill="#c9a227"/>'
          '<rect x="88" y="42" width="1.6" height="3.4" fill="#c9a227"/></g>'
          '<path d="M84 36 q6 -3 12 2 l18 10 l-4 8 l-20 -8 q-6 -3 -6 -12 z" fill="#5a3a26"/>'
          '<path d="M110 48 l20 6 l-3 10 l-21 -8 z" fill="#1f2430"/>')
    # $2.2bn IMF badge
    b += _badge(140, 38.5, 38, 11.5, "$2.2bn IMF", "#00853f", size=10)
    return _svg(w, h, sid, b, d)


def odisha_akvan_evac(w, h):
    sid = "odisha-akvan-evac"
    d = (_lin(sid + "-sky", [(0, "#3a3f5c"), (0.6, "#6b6f8f"), (1, "#9aa0b4")])
         + _lin(sid + "-sea", [(0, "#3f6c80"), (1, "#24485a")])
         + _lin(sid + "-land", [(0, "#6f9a4a"), (1, "#4c7432")]))
    b = _bg("url(#%s-sky)" % sid)
    # cyclone spiral cloud mass, right
    b += ('<g transform="translate(140 14)">'
          '<circle r="26" fill="#d9dce8" opacity="0.25"/>'
          '<path d="M0 0 C0 -9 12 -12 18 -4 C23 5 16 17 5 19 M0 0 C0 9 -12 12 -18 4 C-23 -5 -16 -17 -5 -19" '
          'fill="none" stroke="#eef0f6" stroke-width="5" stroke-linecap="round" opacity="0.9"/>'
          '<circle r="3.4" fill="#3a3f5c"/></g>')
    # rain streaks
    b += "".join('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#c9d3e6" stroke-width="0.6" opacity="0.6"/>'
                 % (x, y, x - 3, y + 8) for x, y in ((104, 22), (112, 28), (122, 24), (130, 32), (146, 34),
                                                    (156, 26), (98, 32), (138, 38), (118, 36)))
    # sea, right, with big waves
    b += '<path d="M96 40 C 110 38 130 38 260 38 V200 H80 Z" fill="url(#%s-sea)"/>' % sid
    b += ('<path d="M100 44 q5 -4 10 0 q5 -4 10 0 q5 -4 10 0 q5 -4 10 0 q5 -4 10 0 q5 -4 10 0 q5 -4 10 0" '
          'fill="none" stroke="#cfe6ee" stroke-width="1.2"/>'
          '<path d="M94 51 q5 -4 10 0 q5 -4 10 0 q5 -4 10 0 q5 -4 10 0 q5 -4 10 0 q5 -4 10 0 q5 -4 10 0" '
          'fill="none" stroke="#cfe6ee" stroke-width="1.2" opacity="0.7"/>')
    # bent palms on the coast
    for (x, lean) in ((94, 1), (86, 1)):
        b += ('<path d="M%d 44 q2 -9 %d -15" fill="none" stroke="#3b2a1a" stroke-width="1.5"/>'
              '<path d="M%d 29 q-6 0 -9 4 M%d 29 q-7 -3 -11 -1 M%d 29 q-4 -4 -8 -5" fill="none" '
              'stroke="#2e4d22" stroke-width="1.6" stroke-linecap="round"/>'
              % (x, -5 * lean, x - 5, x - 5, x - 5))
    # land
    b += '<path d="M-200 40 H70 C 84 40 92 42 100 46 L104 200 H-200 Z" fill="url(#%s-land)"/>' % sid
    # cyclone shelter, left (raised on pillars)
    b += ('<rect x="2" y="28" width="30" height="12" fill="#f2ede1"/>'
          '<path d="M0 28 h34 l-3 -4 h-28 z" fill="#c0392b"/>'
          + "".join('<rect x="%d" y="31" width="3" height="3" fill="#5a6b7c"/>' % x for x in (6, 12, 18, 24))
          + '<rect x="4" y="40" width="2" height="6" fill="#d8d0bf"/><rect x="28" y="40" width="2" height="6" fill="#d8d0bf"/>'
          '<rect x="16" y="40" width="2" height="6" fill="#d8d0bf"/>')
    # road
    b += '<path d="M-200 50 H98 L96 58 H-200 Z" fill="#4a4a4f"/>'
    b += '<path d="M-60 54 H96" stroke="#e9e2cf" stroke-width="0.7" stroke-dasharray="4 4"/>'

    def bus(x, y, col):
        return ('<g transform="translate(%.1f %.1f)">'
                '<rect x="0" y="0" width="24" height="9.5" rx="1.8" fill="%s"/>'
                '<rect x="0" y="6.6" width="24" height="1.2" fill="#fff" opacity="0.7"/>' % (x, y, col)
                + "".join('<rect x="%.1f" y="1.6" width="3.4" height="3" fill="#cfe2ee"/>' % xx
                          for xx in (5, 9.5, 14, 18.5))
                + '<rect x="0.8" y="1.6" width="3" height="4.4" fill="#cfe2ee"/>'
                '<circle cx="5" cy="9.8" r="1.8" fill="#151515"/><circle cx="19" cy="9.8" r="1.8" fill="#151515"/></g>')
    b += bus(40, 43, "#e8a317") + bus(68, 43, "#d9822b")
    # people walking inland (left)
    for i, x in enumerate((20, 27, 34)):
        b += _person(x, 60, 0.55, suit=("#3b6ea5", "#a5412e", "#6a5a8a")[i], skin="#7a4b2e", walk=1)
    b += '<path d="M62 37 h-18 l3 -2.6 M44 37 l3 2.6" fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>'
    b += _badge(130, 37, 58, 11.5, "298,000 MOVED", "#7b4fa0", size=9.5)
    b += _text(80, 9, "CYCLONE AKVAN", 8.5, "#ffffff", 700, "middle", 'letter-spacing="0.6" opacity="0.92"')
    return _svg(w, h, sid, b, d)


def bangladesh_protests(w, h):
    sid = "bangladesh-protests"
    d = (_lin(sid + "-sky", [(0, "#f0b27a"), (1, "#f7dcb4")])
         + _lin(sid + "-road", [(0, "#6c6862"), (1, "#4a4743")]))
    b = _bg("url(#%s-sky)" % sid)
    # far Dhaka skyline
    b += ('<g fill="#c9a88a">'
          '<rect x="-30" y="6" width="16" height="30"/><rect x="-12" y="12" width="12" height="24"/>'
          '<rect x="2" y="2" width="14" height="34"/><rect x="18" y="10" width="18" height="26"/>'
          '<rect x="38" y="4" width="12" height="32"/><rect x="52" y="14" width="16" height="22"/>'
          '<rect x="70" y="0" width="14" height="36"/><rect x="86" y="9" width="18" height="27"/>'
          '<rect x="106" y="3" width="12" height="33"/><rect x="120" y="12" width="16" height="24"/>'
          '<rect x="138" y="6" width="14" height="30"/><rect x="154" y="11" width="22" height="25"/></g>')
    # shuttered shopfronts (shutdown)
    cols = ("#2f7d68", "#b5473a", "#3f6aa0", "#c58a2a", "#6b4f8a", "#2f7d68", "#b5473a", "#3f6aa0")
    for i, x in enumerate(range(-24, 190, 22)):
        b += ('<rect x="%d" y="18" width="21" height="24" fill="#e9e2d3"/>'
              '<rect x="%d" y="18" width="21" height="5" fill="%s"/>'
              '<rect x="%d" y="24" width="17" height="18" fill="#a9a59d"/>'
              % (x, x, cols[i % len(cols)], x + 2))
        for yy in range(26, 42, 2):
            b += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#827e76" stroke-width="0.6"/>' % (x + 2, yy, x + 19, yy)
        b += '<rect x="%d" y="40" width="3" height="2" fill="#3a3530"/>' % (x + 9)
    b += _band(42, "url(#%s-road)" % sid)
    b += '<path d="M-60 52 H220" stroke="#efe6d0" stroke-width="0.8" stroke-dasharray="6 5"/>'
    # empty parked rickshaw, left
    b += ('<g transform="translate(6 42)">'
          '<path d="M2 -2 q6 -9 13 0 z" fill="#1f7a6a"/>'
          '<rect x="3" y="-2" width="11" height="3" fill="#d34a6a"/>'
          '<circle cx="5" cy="4" r="3" fill="none" stroke="#222" stroke-width="0.9"/>'
          '<circle cx="13" cy="4" r="3" fill="none" stroke="#222" stroke-width="0.9"/>'
          '<path d="M14 1 L22 1 L24 4" fill="none" stroke="#222" stroke-width="0.9"/>'
          '<circle cx="24" cy="4" r="3" fill="none" stroke="#222" stroke-width="0.9"/></g>')

    def truck(x, y):
        return ('<g transform="translate(%.1f %.1f)">'
                '<rect x="0" y="0" width="28" height="13" rx="1.2" fill="#56603a"/>'
                '<path d="M0 0 h28 v3 h-28 z" fill="#3f4728"/>'
                '<path d="M28 4 h7 l4.5 4.5 v4.5 h-11.5 z" fill="#454e2c"/>'
                '<rect x="30" y="5.5" width="4.4" height="3.2" fill="#cfe0e8"/>'
                '<circle cx="7" cy="14" r="3" fill="#151515"/><circle cx="33" cy="14" r="3" fill="#151515"/>'
                '<circle cx="7" cy="14" r="1" fill="#888"/><circle cx="33" cy="14" r="1" fill="#888"/></g>'
                % (x, y))
    b += truck(98, 34)
    # border guards in a line (olive uniforms, helmets), shields
    for x in (40, 50, 60, 70, 80):
        b += _person(x, 58, 1.0, suit="#5d6b3a", skin="#7a4b2e", legs="#4a5530", cap="#3f4728")
        b += '<rect x="%.1f" y="44" width="4" height="9" rx="1" fill="#a9c0cc" opacity="0.85"/>' % (x + 2.4)
    # flag on a pole
    b += _flagpole(flag_bangladesh, 142, 8, 20, 12, 40, pole="#8b8680")
    b += _badge(56, 3.5, 54, 11.5, "97 PLATOONS", "#006a4e", size=10)
    return _svg(w, h, sid, b, d)


def bukele_third_term(w, h):
    sid = "bukele-third-term"
    d = (_lin(sid + "-sky", [(0, "#4aa3df"), (1, "#bfe3f5")])
         + _lin(sid + "-volc", [(0, "#5f8f5a"), (1, "#3e6b42")])
         + _lin(sid + "-plaza", [(0, "#d6cbb4"), (1, "#b9ad95")]))
    b = _bg("url(#%s-sky)" % sid)
    b += '<circle cx="18" cy="10" r="6" fill="#fff3c4"/>'
    b += '<path d="M40 14 q4 -4 9 -1 q4 -3 7 1 z M120 9 q3 -3 7 -1 q3 -2 6 1 z" fill="#fff" opacity="0.85"/>'
    # San Salvador volcano behind
    b += '<path d="M-20 40 L40 12 Q48 8 56 12 L74 20 L120 40 Z" fill="url(#%s-volc)"/>' % sid
    b += '<path d="M40 12 Q48 8 56 12 L50 14 Z" fill="#2f5233"/>'
    # electoral tribunal building
    b += ('<rect x="76" y="16" width="80" height="28" fill="#f3efe6"/>'
          '<path d="M72 16 L116 4 L160 16 Z" fill="#e4ddcf"/>'
          '<rect x="72" y="15" width="88" height="2.4" fill="#d6ceba"/>'
          + "".join('<rect x="%d" y="19" width="3.4" height="24" fill="#ddd5c4"/>' % x for x in range(80, 156, 9))
          + '<rect x="109" y="28" width="14" height="16" fill="#0f47af"/>'
          '<rect x="74" y="43" width="84" height="2" fill="#cfc6b2"/>')
    b += _band(45, "url(#%s-plaza)" % sid)
    b += '<path d="M66 45 L60 52 H170 L164 45 Z" fill="#c9bea6"/>'
    # flags flanking the entrance
    b += _flagpole(flag_el_salvador, 101, 22, 11, 7, 44, pole="#8b8680")
    b += _flagpole(flag_el_salvador, 128, 22, 11, 7, 44, pole="#8b8680")
    # candidate with folder walking to the tribunal + aides
    b += _person(60, 58, 1.25, suit="#20232b", skin="#c99a72", tie="#0f47af", walk=1)
    b += '<rect x="64.5" y="41" width="6" height="8" rx="0.6" fill="#0f47af" stroke="#fff" stroke-width="0.6"/>'
    b += _person(44, 58, 1.05, suit="#3a3f4a", skin="#a87a56", walk=1)
    b += _person(33, 58, 1.0, suit="#2d3440", skin="#8a5a3c")
    # press cameras
    b += ('<g fill="#1d1a16"><rect x="8" y="46" width="7" height="5" rx="1"/><rect x="15" y="47.5" width="3" height="2"/>'
          '<rect x="10.5" y="51" width="1.2" height="9"/></g>')
    b += _badge(28, 20, 40, 12, "3RD TERM", "#0f47af", size=10.5)
    return _svg(w, h, sid, b, d)


def tonga_drought(w, h):
    sid = "tonga-drought"
    d = (_lin(sid + "-sky", [(0, "#f08a3c"), (0.6, "#f8c46a"), (1, "#fbe2a6")])
         + _lin(sid + "-sea", [(0, "#3fa0b8"), (1, "#2a7f96")])
         + _lin(sid + "-soil", [(0, "#d39a5c"), (1, "#a8693a")])
         + _rad(sid + "-sun", [(0, "#fff6c8", 1), (0.35, "#ffe08a", 0.9), (1, "#ffb84a", 0)]))
    b = _bg("url(#%s-sky)" % sid)
    b += '<circle cx="80" cy="12" r="26" fill="url(#%s-sun)"/>' % sid
    b += '<circle cx="80" cy="12" r="8" fill="#fff8dc"/>'
    # sea at horizon
    b += _band(28, "url(#%s-sea)" % sid)
    b += '<path d="M40 30 h20 M90 31 h26 M128 30 h16" stroke="#bfe6ee" stroke-width="0.6"/>'
    # parched ground
    b += '<path d="M-200 36 Q 0 32 80 34 T 363 34 V300 H-200 Z" fill="url(#%s-soil)"/>' % sid
    b += ('<path d="M-5 48 L14 51 L24 46 L40 54 L58 49 L72 53 L90 47 L104 54 L122 49 L170 52 '
          'M24 46 L28 60 M58 49 L52 62 M90 47 L96 62 M122 49 L118 62 M40 54 L44 62 M104 54 L108 62 M14 51 L8 62 '
          'M72 53 L70 62 M140 50 L146 62" fill="none" stroke="#6b3f1f" stroke-width="1" stroke-linejoin="round"/>')
    # drooping, brown palm
    b += '<path d="M58 50 C 58 38 62 28 70 20" fill="none" stroke="#6a4526" stroke-width="2.6" stroke-linecap="round"/>'
    for dd in ("M70 20 C 62 18 56 22 53 30", "M70 20 C 66 24 64 30 64 36", "M70 20 C 78 18 84 24 85 32",
               "M70 20 C 74 24 76 30 74 36", "M70 20 C 68 13 62 11 56 13"):
        b += '<path d="%s" fill="none" stroke="#9c7a3a" stroke-width="2" stroke-linecap="round"/>' % dd
    b += '<ellipse cx="58" cy="50.5" rx="8" ry="1.6" fill="#000" opacity="0.2"/>'
    # village fale (hut) left
    b += ('<path d="M-6 34 L12 22 L30 34 Z" fill="#8a5a2b"/>'
          '<rect x="-2" y="34" width="28" height="12" fill="#e9d4ae"/>'
          '<rect x="9" y="37" width="6" height="9" fill="#5c3d1e"/>')
    # empty water tank with near-empty gauge
    b += ('<rect x="102" y="22" width="24" height="26" rx="2" fill="#dfe3e4"/>'
          + "".join('<line x1="102" y1="%d" x2="126" y2="%d" stroke="#b9c0c2" stroke-width="0.7"/>' % (y, y)
                    for y in (27, 32, 37, 42))
          + '<ellipse cx="114" cy="22" rx="12" ry="2.8" fill="#c8ced0"/>'
          '<rect x="105" y="25" width="4" height="20" fill="#fff" stroke="#556" stroke-width="0.5"/>'
          '<rect x="105" y="43" width="4" height="2" fill="#2f86c1"/>'
          '<path d="M126 44 h5 v4" fill="none" stroke="#556" stroke-width="1.2"/>'
          '<ellipse cx="114" cy="48.5" rx="14" ry="2" fill="#000" opacity="0.2"/>')
    b += _flagpole(flag_tonga, 142, 8, 18, 11, 46, pole="#8b8680")
    b += _badge(140, 38, 36, 12, "27 DAYS", "#c10000", size=10.5)
    return _svg(w, h, sid, b, d)


def cop31_draft_fossils(w, h):
    sid = "cop31-draft-fossils"
    d = (_lin(sid + "-hall", [(0, "#1d3550"), (1, "#2c4e6e")])
         + _lin(sid + "-scr", [(0, "#f7f9fb"), (1, "#dfe7ee")])
         + _lin(sid + "-floor", [(0, "#2a3b4c"), (1, "#18242f")]))
    b = _bg("url(#%s-hall)" % sid)
    # ceiling spotlights
    b += "".join('<path d="M%d -4 L%d 46 L%d 46 Z" fill="#ffffff" opacity="0.05"/>' % (x, x - 14, x + 14)
                 for x in (20, 82, 144))
    # COP31 stage banner strips (green/teal)
    b += '<rect x="-200" y="40" width="563" height="4" fill="#1f9e8a"/>'
    # big screen with the draft text (focal)
    b += ('<rect x="33" y="3" width="98" height="36" rx="1.5" fill="#000" opacity="0.35" transform="translate(1.5 1.5)"/>'
          '<rect x="33" y="3" width="98" height="36" rx="1.5" fill="url(#%s-scr)"/>' % sid
          + '<rect x="33" y="3" width="98" height="8" fill="#1f9e8a"/>'
          + _text(82, 9.6, "COP31 DRAFT", 7, "#ffffff", 700, "middle", 'letter-spacing="0.8"')
          + '<rect x="40" y="14" width="84" height="1.4" fill="#b7c3cf"/>'
          + _text(82, 28, "FOSSIL FUELS", 13, "#1d1a16")
          + '<line x1="40" y1="24.4" x2="124" y2="24.4" stroke="#d6342a" stroke-width="2.4" stroke-linecap="round"/>'
          + '<rect x="40" y="32" width="60" height="1.4" fill="#b7c3cf"/>'
          '<rect x="104" y="32" width="20" height="1.4" fill="#b7c3cf"/>')
    # globe logo left of screen
    b += ('<defs><clipPath id="%s-g"><circle cx="16" cy="20" r="11"/></clipPath></defs>'
          '<circle cx="16" cy="20" r="11" fill="#3f8fc8"/>'
          '<g clip-path="url(#%s-g)" fill="#5bae6a">'
          '<path d="M6 12 C 10 8 16 9 17 14 C 18 18 13 19 12 23 C 11 27 7 27 5 24 Z"/>'
          '<path d="M19 9 C 24 9 28 13 28 17 C 25 18 23 16 20 17 C 18 15 18 11 19 9 Z"/>'
          '<path d="M18 24 C 22 23 25 25 24 30 C 21 33 18 32 18 28 Z"/></g>'
          '<circle cx="16" cy="20" r="11" fill="none" stroke="#cfe3f1" stroke-width="0.8"/>' % (sid, sid))
    # floor
    b += _band(44, "url(#%s-floor)" % sid)
    # delegates' long table and seated silhouettes facing screen (backs)
    for i, x in enumerate(range(6, 166, 16)):
        col = ("#3a2f2a", "#2b2b33", "#4a3a2a", "#23272f")[i % 4]
        b += ('<circle cx="%d" cy="45" r="3.2" fill="%s"/>'
              '<path d="M%d 49 q6 -3.4 12 0 v8 h-12 z" fill="%s"/>' % (x + 6, col, x, ("#2f3e52", "#46424a", "#2c4a5a", "#3b3550")[i % 4]))
    b += '<rect x="-200" y="55" width="563" height="4" fill="#d7dde3"/>'
    b += '<rect x="-200" y="59" width="563" height="10" fill="#9aa6b1"/>'
    # nameplates/flags on table
    b += "".join('<rect x="%d" y="52.5" width="5" height="2.6" fill="#ffffff"/>' % (x + 9) for x in range(6, 166, 32))
    # bold label
    b += _person(148, 40, 1.0, suit="#2b2f3a", skin="#b07a55", tie="#1f9e8a")
    b += ('<path d="M140 30 h16 l-2 14 h-12 z" fill="#d7dde3"/><rect x="140" y="30" width="16" height="3" fill="#1f9e8a"/>'
          '<path d="M146 30 l2 -5" stroke="#222" stroke-width="0.7"/><circle cx="148.2" cy="24.6" r="0.9" fill="#222"/>')
    return _svg(w, h, sid, b, d)


def voyager_signal(w, h):
    sid = "voyager-signal"
    d = (_lin(sid + "-sp", [(0, "#070a1c"), (0.6, "#121a3a"), (1, "#1c1438")], 1, 1)
         + _lin(sid + "-mw", [(0, "#6a5aa8"), (0.5, "#9fb3e8"), (1, "#6a5aa8")], 1, 0)
         + _rad(sid + "-sun", [(0, "#fff3c4", 1), (0.25, "#ffd27a", 0.7), (1, "#ff9a3c", 0)])
         + _rad(sid + "-dot", [(0, "#bfe8ff", 1), (1, "#5ab4ff", 0)]))
    b = _bg("url(#%s-sp)" % sid)
    # milky way band
    b += ('<path d="M-30 70 C 30 40 100 30 200 -10 L200 10 C 110 46 40 56 -30 86 Z" fill="url(#%s-mw)" opacity="0.22"/>'
          % sid)
    stars = ((60, 8, 0.7), (84, 52, 0.6), (100, 6, 0.8), (40, 56, 0.6), (150, 44, 0.7), (6, 10, 0.6),
             (72, 28, 0.5), (112, 22, 0.5), (24, 48, 0.5), (90, 18, 0.4), (128, 8, 0.6), (48, 14, 0.4),
             (118, 54, 0.5), (66, 60, 0.4), (14, 30, 0.4), (156, 14, 0.5), (138, 30, 0.4), (96, 40, 0.5))
    b += "".join('<circle cx="%d" cy="%d" r="%.1f" fill="#f0ecff"/>' % s for s in stars)
    # distant Sun with tiny Earth beside it (right)
    b += '<circle cx="150" cy="25" r="16" fill="url(#%s-sun)"/>' % sid
    b += '<circle cx="150" cy="25" r="2.2" fill="#fff8dc"/>'
    b += '<circle cx="138" cy="31" r="5" fill="url(#%s-dot)"/><circle cx="138" cy="31" r="1.5" fill="#cfefff"/>' % sid
    b += _text(138, 42, "EARTH", 7.5, "#b9cce0", 600, "middle", 'letter-spacing="0.8"')
    # signal arcs travelling to Earth
    for i, x in enumerate((50, 64, 78, 92, 106, 120)):
        b += ('<path d="M%d 22 Q %d 30 %d 38" fill="none" stroke="#7fd0ff" stroke-width="1.6" '
              'stroke-linecap="round" opacity="%.2f"/>' % (x, x + 5, x, 0.95 - i * 0.12))
    # Voyager 1 (focal), left
    b += ('<g transform="translate(26 30)">'
          '<line x1="-2" y1="2" x2="-22" y2="-16" stroke="#cfc8b8" stroke-width="0.9"/>'
          '<line x1="-2" y1="4" x2="-18" y2="18" stroke="#cfc8b8" stroke-width="1.4"/>'
          '<rect x="-23" y="16" width="8" height="5" rx="1" fill="#8f8a80"/>'
          '<line x1="2" y1="6" x2="2" y2="20" stroke="#cfc8b8" stroke-width="0.7"/>'
          '<polygon points="-6,-5 4,-5 6,0 4,5 -6,5 -8,0" fill="#c9a227"/>'
          '<polygon points="-6,-5 4,-5 6,0 -8,0" fill="#e0bf4a"/>'
          '<ellipse cx="9" cy="0" rx="5.2" ry="15" fill="#f4efe4"/>'
          '<ellipse cx="10" cy="0" rx="3.4" ry="12" fill="#d9d3c4"/>'
          '<line x1="10" y1="0" x2="17" y2="0" stroke="#f4efe4" stroke-width="1"/>'
          '<circle cx="17" cy="0" r="1.2" fill="#f4efe4"/></g>')
    b += _text(24, 9, "VOYAGER 1", 7.5, "#d9d3c4", 600, "middle", 'letter-spacing="0.8"')
    b += _badge(86, 37, 52, 12.5, "1 LIGHT-DAY", "#2f6fbf", size=11)
    return _svg(w, h, sid, b, d)


ILLUS_PART = {
    "somalia-uae-envoy": somalia_uae_envoy,
    "senegal-budget-decree": senegal_budget_decree,
    "odisha-akvan-evac": odisha_akvan_evac,
    "bangladesh-protests": bangladesh_protests,
    "bukele-third-term": bukele_third_term,
    "tonga-drought": tonga_drought,
    "cop31-draft-fossils": cop31_draft_fossils,
    "voyager-signal": voyager_signal,
}
