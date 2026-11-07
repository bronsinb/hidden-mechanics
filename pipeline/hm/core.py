"""Hidden Mechanics engine: timing, easing, drawing primitives, captions, outro, render loop."""
import cairo, math, json, re, sys, subprocess, os

W, H, FPS = 1080, 1920, 30
TL = {"total": 1.0, "lines": []}
L = {}
IDS = []
TOTAL = 1.0

def load_timeline(path):
    """Load an episode's timeline.json (written by hm.voice) into the engine."""
    global TL, L, IDS, TOTAL, CHUNKS
    TL = json.load(open(path))
    L = {l["id"]: l for l in TL["lines"]}
    IDS = [l["id"] for l in TL["lines"]]
    TOTAL = TL["total"]
    CHUNKS = caption_chunks()

# ---------- timing helpers ----------
def S(lid): return 0.0 if lid == IDS[0] else L[lid]["s"]
def E(lid):
    i = IDS.index(lid)
    return L[IDS[i + 1]]["s"] if i + 1 < len(IDS) else TOTAL
def norm(w): return re.sub(r"[^\w']", "", w).lower()
def wt(lid, word, nth=0, end=False):
    c = 0
    for w in L[lid]["words"]:
        if norm(w["w"]) == word.lower():
            if c == nth: return w["e"] if end else w["s"]
            c += 1
    raise KeyError((lid, word))

# ---------- easing ----------
def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def pr(t, a, d): return cl((t - a) / d) if d > 0 else (1.0 if t >= a else 0.0)
def ease(x): x = cl(x); return x * x * (3 - 2 * x)
def eout(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def back(x):
    x = cl(x); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def lerp(a, b, x): return a + (b - a) * x
def lp(p, q, x): return (lerp(p[0], q[0], x), lerp(p[1], q[1], x))

def hexc(h, a=1.0):
    h = h.lstrip("#"); return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)

CYAN, AMBER, GREEN, RED, PURPLE = "#38BDF8", "#FBBF24", "#34D399", "#F87171", "#A78BFA"
WHITE, MUTED, YEL = "#F8FAFC", "#94A3B8", "#FDE047"

# ---------- drawing primitives ----------
def safe_scale(c, sx, sy):
    c.scale(sx if abs(sx) > 1e-3 else 1e-3, sy if abs(sy) > 1e-3 else 1e-3)

def rr(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()

def fill(c, col, a=1.0):
    r, g, b, a0 = hexc(col) if isinstance(col, str) else col
    c.set_source_rgba(r, g, b, a0 * a)

def font(c, size, weight="bold", family="Inter"):
    fam = {"black": "Inter Black", "xbold": "Inter ExtraBold", "bold": "Inter", "semi": "Inter SemiBold", "mono": "DejaVu Sans Mono"}[weight]
    c.select_font_face(fam, cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD if weight in ("bold", "mono") else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)

def tw(c, s): return c.text_extents(s).x_advance

def text(c, s, x, y, size, col=WHITE, weight="bold", align="center", a=1.0, stroke=0, scol="#020617"):
    if a <= 0.001: return
    font(c, size, weight)
    w = tw(c, s)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    c.move_to(x0, y)
    c.text_path(s)
    if stroke:
        fill(c, scol, a * 0.9); c.set_line_width(stroke); c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.stroke_preserve()
    fill(c, col, a); c.fill()
    return w

def pill(c, s, x, y, size, bg, fg=WHITE, a=1.0, sc=1.0, pad=26, weight="xbold", outline=None):
    if a <= 0.001 or sc <= 0.001: return
    c.save(); c.translate(x, y); safe_scale(c, sc, sc)
    font(c, size, weight); w = tw(c, s)
    h = size * 1.75
    rr(c, -w / 2 - pad, -h / 2, w + pad * 2, h, h / 2)
    fill(c, bg, a); c.fill_preserve()
    if outline:
        fill(c, outline, a); c.set_line_width(3); c.stroke()
    else:
        c.new_path()
    text(c, s, 0, size * 0.36, size, fg, weight, a=a)
    c.restore()

def glow(c, x, y, r, col, a):
    if a <= 0: return
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    rgb = hexc(col)
    g.add_color_stop_rgba(0, rgb[0], rgb[1], rgb[2], a)
    g.add_color_stop_rgba(1, rgb[0], rgb[1], rgb[2], 0)
    c.set_source(g); c.arc(x, y, r, 0, 2 * math.pi); c.fill()

def check(c, x, y, s, col, a=1, lw=10, p=1.0):
    c.save(); fill(c, col, a); c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    pts = [(x - s * .5, y), (x - s * .12, y + s * .38), (x + s * .55, y - s * .4)]
    c.move_to(*pts[0])
    if p < .4: c.line_to(*lp(pts[0], pts[1], p / .4))
    else: c.line_to(*pts[1]); c.line_to(*lp(pts[1], pts[2], (p - .4) / .6))
    c.stroke(); c.restore()

def cross(c, x, y, s, col, a=1, lw=10):
    c.save(); fill(c, col, a); c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(x - s / 2, y - s / 2); c.line_to(x + s / 2, y + s / 2)
    c.move_to(x + s / 2, y - s / 2); c.line_to(x - s / 2, y + s / 2); c.stroke(); c.restore()

def lock_icon(c, x, y, s, open_, col, a=1.0):
    if a <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, s, s)
    # shackle
    c.save(); c.translate(0, -14 - 26 * open_)
    if open_ > 0: c.translate(-22, 0); c.rotate(-0.5 * open_); c.translate(22, 0)
    fill(c, col, a); c.set_line_width(13); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(-22, 0); c.arc(0, -8, 22, math.pi, 0); c.line_to(22, 0); c.stroke()
    c.restore()
    rr(c, -38, -16, 76, 62, 14); fill(c, col, a); c.fill()
    c.arc(0, 10, 8, 0, 2 * math.pi); fill(c, "#0B1220", a); c.fill()
    rr(c, -3.5, 12, 7, 18, 3); c.fill()
    c.restore()

# ---------- background ----------
_BG = None
def background(c):
    global _BG
    if _BG is None:
        _BG = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        b = cairo.Context(_BG)
        g = cairo.LinearGradient(0, 0, 0, H)
        g.add_color_stop_rgb(0, *hexc("#0B1222")[:3]); g.add_color_stop_rgb(1, *hexc("#070B16")[:3])
        b.set_source(g); b.paint()
        glow(b, 540, 820, 760, "#1E3A8A", 0.32)
        for yy in range(30, H, 54):
            for xx in range(27, W, 54):
                b.new_sub_path(); b.arc(xx, yy, 1.8, 0, 2 * math.pi)
        b.set_source_rgba(1, 1, 1, 0.055); b.fill()
    c.set_source_surface(_BG, 0, 0); c.paint()

# ---------- captions ----------
def caption_chunks():
    chunks = []
    for ln in TL["lines"]:
        cur = []
        for w in ln["words"]:
            cur.append(w)
            if len(cur) >= 3 or re.search(r"[,.?!]$", w["w"]):
                chunks.append(cur); cur = []
        if cur: chunks.append(cur)
    out = []
    for i, ch in enumerate(chunks):
        s = ch[0]["s"] - 0.05
        nxt = chunks[i + 1][0]["s"] - 0.05 if i + 1 < len(chunks) else TOTAL
        e = min(nxt, ch[-1]["e"] + 0.45)
        out.append((s, e, ch))
    return out

CHUNKS = []

def captions(c, t):
    for s, e, ch in CHUNKS:
        if s <= t < e:
            size = 84
            font(c, size, "black")
            words = [w["w"].upper() for w in ch]
            sp = tw(c, " ")
            total = sum(tw(c, w) for w in words) + sp * (len(words) - 1)
            if total > 960:
                size = size * 960 / total; font(c, size, "black")
                sp = tw(c, " "); total = sum(tw(c, w) for w in words) + sp * (len(words) - 1)
            pop = back(pr(t, s, 0.16))
            fade = 1 - pr(t, e - 0.08, 0.08)
            c.save(); c.translate(540, 1470); safe_scale(c, 0.85 + 0.15 * pop, 0.85 + 0.15 * pop)
            x = -total / 2
            for w, wd in zip(ch, words):
                active = w["s"] - 0.03 <= t
                cur = w["s"] - 0.03 <= t < w["e"] + 0.02
                col = YEL if cur else (WHITE if active else "#CBD5E1")
                text(c, wd, x, size * 0.36, size, col, "black", "left", a=fade, stroke=16)
                x += tw(c, wd) + sp
                font(c, size, "black")
            c.restore()
            break


# ---------- shared scene helpers ----------
def scene_label(c, t, lid, label, col):
    """Pill at the top naming the current beat; shows while line `lid` is spoken."""
    a = ease(pr(t, S(lid), 0.35)) * (1 - ease(pr(t, E(lid) - 0.15, 0.3)))
    if a > 0:
        pill(c, label, 540, 200, 38, "#0F172A", col, a=a, sc=0.9 + 0.1 * back(pr(t, S(lid), 0.35)), pad=30, outline=col)

def hook_title(c, t, line1, line2, end_t):
    """Two-line title card for the hook (white line, yellow line), fades out at end_t."""
    ha = 1 - ease(pr(t, end_t - 0.1, 0.4))
    if ha <= 0: return
    t1 = back(pr(t, 0.05, 0.45)); t2 = back(pr(t, 0.25, 0.45))
    c.save(); c.translate(540, 250); safe_scale(c, t1, t1)
    text(c, line1, 0, 0, 74, WHITE, "black", a=ha); c.restore()
    c.save(); c.translate(540, 345); safe_scale(c, t2, t2)
    text(c, line2, 0, 0, 66, YEL, "black", a=ha); c.restore()

def cta_amount(t):
    """0..1 fade toward the branded outro (the line with id 'cta'). Scenes multiply their alpha by 1 - this."""
    return ease(pr(t, S("cta") - 0.1, 0.6)) if "cta" in L else 0.0

def outro(c, t):
    cta = cta_amount(t)
    if cta <= 0: return
    from .branding import mark
    s_ = back(pr(t, S("cta"), 0.5))
    c.save(); c.translate(540, 700); safe_scale(c, s_, s_)
    c.push_group(); mark(c, 0, 0, 0.62); c.pop_group_to_source(); c.paint_with_alpha(cta)
    c.restore()
    text(c, "HIDDEN MECHANICS", 540, 1060, 92, WHITE, "black", a=cta)
    text(c, "Follow for more", 540, 1140, 46, YEL, "xbold", a=cta)

def frame(c, t, scene_draw):
    background(c)
    scene_draw(c, t)
    outro(c, t)
    captions(c, t)
