"""Reusable props: car (top view), key fob, house, radio bubbles, devices, icons."""
from .core import *

# ---------- car ----------
ANT = {"dl": (-140, -10), "dr": (140, -10), "cab": (0, 45), "tr": (0, 268)}
ANT_LABEL = {"dl": "Door", "dr": "Door", "cab": "Cabin", "tr": "Trunk"}
BUB_R = 175

def car(c, cx, cy, s, xray=0.0, flash=0.0, lights=0.0, alpha=1.0):
    c.save(); c.translate(cx, cy); safe_scale(c, s, s)
    c.push_group()
    # shadow
    glow(c, 0, 20, 420, "#000000", 0.55)
    # wheels
    for wx in (-160, 122):
        for wy in (-238, 140):
            rr(c, wx, wy, 38, 100, 14); fill(c, "#0A0F1A"); c.fill()
    # mirrors
    for sx in (-1, 1):
        rr(c, sx * 158 - 16, -118, 32, 24, 9)
        fill(c, "#1D4ED8"); c.fill()
    # body
    rr(c, -145, -315, 290, 630, 105)
    g = cairo.LinearGradient(-145, 0, 145, 0)
    g.add_color_stop_rgb(0, *hexc("#1E40AF")[:3]); g.add_color_stop_rgb(0.5, *hexc("#3B82F6")[:3]); g.add_color_stop_rgb(1, *hexc("#1E40AF")[:3])
    c.set_source(g); c.fill_preserve()
    fill(c, "#93C5FD", 0.35); c.set_line_width(3); c.stroke()
    # hood creases
    c.set_line_width(3); fill(c, "#1E3A8A", 0.7)
    for sx in (-1, 1):
        c.move_to(sx * 62, -292); c.curve_to(sx * 70, -240, sx * 74, -200, sx * 78, -168); c.stroke()
    # interior (visible with x-ray)
    rr(c, -124, -78, 248, 258, 34); fill(c, "#0F172A"); c.fill()
    for sx in (-1, 1):
        rr(c, sx * 62 - 46, -52, 92, 104, 24); fill(c, "#334155"); c.fill()
        rr(c, sx * 62 - 30, 34, 60, 22, 10); fill(c, "#475569"); c.fill()
    rr(c, -108, 88, 216, 78, 24); fill(c, "#334155"); c.fill()
    rr(c, -92, 150, 184, 22, 10); fill(c, "#475569"); c.fill()
    c.set_line_width(7); fill(c, "#64748B"); c.arc(-62, -72, 26, math.pi * 1.05, math.pi * 1.95); c.stroke()
    # roof (fades with x-ray)
    ra = 1 - 0.86 * xray
    rr(c, -124, -78, 248, 258, 34)
    g = cairo.LinearGradient(-124, 0, 124, 0)
    g.add_color_stop_rgba(0, *hexc("#1E3A8A")[:3], ra); g.add_color_stop_rgba(.5, *hexc("#2563EB")[:3], ra); g.add_color_stop_rgba(1, *hexc("#1E3A8A")[:3], ra)
    c.set_source(g); c.fill()
    # windshield
    c.move_to(-112, -168); c.line_to(112, -168); c.line_to(126, -80); c.line_to(-126, -80); c.close_path()
    g = cairo.LinearGradient(0, -168, 0, -80)
    g.add_color_stop_rgb(0, *hexc("#1E293B")[:3]); g.add_color_stop_rgb(1, *hexc("#0B1220")[:3])
    c.set_source(g); c.fill()
    c.move_to(-80, -160); c.line_to(-30, -160); c.line_to(-60, -92); c.line_to(-100, -92); c.close_path()
    fill(c, "#FFFFFF", 0.07); c.fill()
    # rear window
    c.move_to(-122, 184); c.line_to(122, 184); c.line_to(108, 236); c.line_to(-108, 236); c.close_path()
    fill(c, "#0B1220"); c.fill()
    # trunk seam
    fill(c, "#1E3A8A", 0.8); c.set_line_width(3)
    c.move_to(-112, 252); c.line_to(112, 252); c.stroke()
    # lights
    hl = max(lights, flash)
    for sx in (-1, 1):
        if hl > 0: glow(c, sx * 92, -320, 150, "#FDE68A", 0.55 * hl)
        rr(c, sx * 92 - 34, -306, 68, 20, 10); fill(c, lerp_col("#CBD5E1", "#FEF9C3", hl)); c.fill()
        if flash > 0: glow(c, sx * 92, 300, 120, "#F59E0B", 0.6 * flash)
        rr(c, sx * 92 - 34, 287, 68, 16, 8); fill(c, lerp_col("#B91C1C", "#F59E0B", flash)); c.fill()
    c.pop_group_to_source(); c.paint_with_alpha(alpha)
    c.restore()

def lerp_col(a, b, x):
    A, B = hexc(a), hexc(b)
    return tuple(lerp(A[i], B[i], cl(x)) for i in range(4))

def to_screen(cam, p):
    cx, cy, s = cam
    return (cx + p[0] * s, cy + p[1] * s)

# ---------- key fob ----------
def keyfob(c, x, y, s, awake=0.0, t=0.0, alpha=1.0, col=AMBER, badge=None, badge_a=0):
    if alpha <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, s, s)
    if awake > 0: glow(c, 0, 0, 130, col, 0.45 * awake * alpha)
    c.set_line_width(7); fill(c, "#94A3B8", alpha); c.arc(0, -74, 17, 0, 2 * math.pi); c.stroke()
    rr(c, -36, -58, 72, 116, 26)
    g = cairo.LinearGradient(-36, 0, 36, 0)
    g.add_color_stop_rgba(0, *hexc("#111827")[:3], alpha); g.add_color_stop_rgba(.5, *hexc("#374151")[:3], alpha); g.add_color_stop_rgba(1, *hexc("#111827")[:3], alpha)
    c.set_source(g); c.fill_preserve()
    fill(c, lerp_col("#4B5563", col, awake), alpha); c.set_line_width(4 + 2 * awake); c.stroke()
    for i, yy in enumerate((-26, 4, 34)):
        rr(c, -18, yy - 10, 36, 20, 8); fill(c, "#1F2937", alpha); c.fill()
        fill(c, "#64748B", alpha); c.set_line_width(2.5); rr(c, -18, yy - 10, 36, 20, 8); c.stroke()
    led = awake * (0.6 + 0.4 * math.sin(t * 14))
    c.arc(0, -46, 5, 0, 2 * math.pi); fill(c, lerp_col("#334155", col, led), alpha); c.fill()
    if badge and badge_a > 0:
        pill(c, badge, 0, 92, 26, PURPLE, "#0B1220", a=badge_a * alpha, sc=back(badge_a), pad=14)
    c.restore()

def zzz(c, x, y, t, a):
    if a <= 0: return
    for i in range(3):
        ph = (t * 0.7 + i / 3) % 1
        text(c, "z", x + 20 + ph * 50, y - ph * 70, 30 + i * 6, MUTED, "xbold", a=a * (1 - ph) * 0.9)

# ---------- radio visuals ----------
def bubble(c, x, y, R, col, a, t, clip=None):
    if a <= 0 or R <= 1: return
    c.save()
    if clip: clip(c); c.clip()
    rgb = hexc(col)
    g = cairo.RadialGradient(x, y, 0, x, y, R)
    g.add_color_stop_rgba(0, rgb[0], rgb[1], rgb[2], 0.28 * a)
    g.add_color_stop_rgba(0.75, rgb[0], rgb[1], rgb[2], 0.12 * a)
    g.add_color_stop_rgba(1, rgb[0], rgb[1], rgb[2], 0.02 * a)
    c.set_source(g); c.arc(x, y, R, 0, 2 * math.pi); c.fill()
    c.set_line_width(3); c.set_dash([10, 10], t * 30)
    c.set_source_rgba(rgb[0], rgb[1], rgb[2], 0.75 * a); c.arc(x, y, R, 0, 2 * math.pi); c.stroke()
    c.set_dash([])
    for k in range(2):
        ph = (t * 0.8 + k * 0.5) % 1
        c.set_line_width(4 * (1 - ph) + 1)
        c.set_source_rgba(rgb[0], rgb[1], rgb[2], 0.6 * a * (1 - ph)); c.arc(x, y, R * ph, 0, 2 * math.pi); c.stroke()
    c.restore()

def antenna_dot(c, x, y, s, col=CYAN, a=1.0):
    if a <= 0 or s <= 0: return
    glow(c, x, y, 46 * s, col, 0.7 * a)
    c.arc(x, y, 13 * s, 0, 2 * math.pi); fill(c, "#0B1220", a); c.fill_preserve()
    fill(c, col, a); c.set_line_width(5 * s); c.stroke()
    c.arc(x, y, 5 * s, 0, 2 * math.pi); fill(c, col, a); c.fill()

def waves(c, x, y, ang, col, t, a, n=3, r0=40, r1=170, spread=0.55, speed=1.4):
    if a <= 0: return
    rgb = hexc(col)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(n):
        ph = (t * speed + k / n) % 1
        r = lerp(r0, r1, ph)
        c.set_line_width(9); c.set_source_rgba(rgb[0], rgb[1], rgb[2], a * (1 - ph) * 0.95)
        c.arc(x, y, r, ang - spread, ang + spread); c.stroke()

def dashed_beam(c, p, q, col, t, a, prog=1.0, lw=6):
    if a <= 0 or prog <= 0: return
    rgb = hexc(col)
    e = lp(p, q, prog)
    glow(c, e[0], e[1], 30, col, 0.8 * a)
    c.set_line_width(lw); c.set_dash([18, 14], -t * 90); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_source_rgba(rgb[0], rgb[1], rgb[2], a); c.move_to(*p); c.line_to(*e); c.stroke(); c.set_dash([])

def device(c, x, y, s, a, t, active=0.0):
    if a <= 0 or s <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, s, s)
    if active > 0: glow(c, 0, 0, 90, RED, 0.5 * active * a)
    fill(c, "#94A3B8", a); c.set_line_width(5); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(14, -30); c.line_to(22, -70); c.stroke()
    c.arc(22, -74, 6, 0, 2 * math.pi); fill(c, RED, a); c.fill()
    rr(c, -34, -32, 68, 64, 14); fill(c, "#1F2937", a); c.fill_preserve()
    fill(c, RED, a); c.set_line_width(4); c.stroke()
    blink = 0.5 + 0.5 * math.sin(t * 10)
    for i in range(3):
        c.arc(-14 + i * 14, 0, 5, 0, 2 * math.pi); fill(c, RED, a * (0.35 + 0.65 * blink * active)); c.fill()
    c.restore()

def house(c, x, y, s, a):
    if a <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, s, s)
    c.push_group()
    glow(c, 0, 60, 330, "#000000", 0.5)
    rr(c, -175, -40, 350, 260, 18); fill(c, "#1E293B"); c.fill_preserve()
    fill(c, "#475569"); c.set_line_width(5); c.stroke()
    c.move_to(-215, -30); c.line_to(0, -190); c.line_to(215, -30); c.close_path()
    fill(c, "#334155"); c.fill_preserve(); fill(c, "#64748B"); c.set_line_width(5); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
    rr(c, 70, 90, 70, 130, 8); fill(c, "#0F172A"); c.fill()
    c.arc(124, 160, 5, 0, 2 * math.pi); fill(c, "#94A3B8"); c.fill()
    rr(c, 70, 10, 70, 56, 6); fill(c, "#FDE68A", 0.25); c.fill()
    # table
    rr(c, -150, 150, 140, 12, 5); fill(c, "#64748B"); c.fill()
    for lx in (-140, -26): rr(c, lx, 160, 10, 58, 3); c.fill()
    c.pop_group_to_source(); c.paint_with_alpha(a)
    c.restore()

def bars(c, x, y, n, filled, col, a, w=22, gap=8, h0=14, step=9):
    for i in range(n):
        hh = h0 + step * i
        rr(c, x + i * (w + gap), y - hh, w, hh, 5)
        fill(c, col if i < filled else "#334155", a); c.fill()

def scale_bar(c, p, q, label, a):
    if a <= 0: return
    fill(c, WHITE, a); c.set_line_width(4)
    c.move_to(*p); c.line_to(*q); c.stroke()
    for e in (p, q):
        c.move_to(e[0], e[1] - 14); c.line_to(e[0], e[1] + 14); c.stroke()
    m = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
    pill(c, label, m[0], m[1] - 44, 30, "#0F172A", WHITE, a=a, pad=18, outline=CYAN)
