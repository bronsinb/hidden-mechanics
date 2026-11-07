"""Channel mark (gear + keyhole), logo, banner, watermark."""
import cairo, math, sys, os
from .core import hexc, glow, rr, text, font, tw, fill, CYAN, YEL, WHITE, MUTED

OUT = os.environ.get("HM_BRAND_OUT", "brand")

def gear_path(c, cx, cy, ro, ri, teeth, tooth=0.42):
    c.new_sub_path()
    step = 2 * math.pi / teeth
    for i in range(teeth):
        a = i * step - math.pi / 2
        pts = [(ri, a - step * 0.5 + 0.02), (ri, a - step * tooth / 2 - 0.05),
               (ro, a - step * tooth / 2 + 0.03), (ro, a + step * tooth / 2 - 0.03),
               (ri, a + step * tooth / 2 + 0.05)]
        for k, (r, ang) in enumerate(pts):
            x, y = cx + r * math.cos(ang), cy + r * math.sin(ang)
            (c.move_to if (i == 0 and k == 0) else c.line_to)(x, y)
    c.close_path()

def keyhole(c, cx, cy, s, col):
    c.new_sub_path(); c.arc(cx, cy - 30 * s, 50 * s, 0, 2 * math.pi)
    fill(c, col); c.fill()
    c.move_to(cx - 26 * s, cy - 10 * s); c.line_to(cx + 26 * s, cy - 10 * s)
    c.line_to(cx + 46 * s, cy + 92 * s); c.line_to(cx - 46 * s, cy + 92 * s); c.close_path()
    c.fill()

def mark(c, cx, cy, s):
    """Gear with a keyhole: the channel mark."""
    glow(c, cx, cy, 380 * s, "#38BDF8", 0.30)
    gear_path(c, cx, cy, 290 * s, 238 * s, 10)
    c.new_sub_path(); c.arc_negative(cx, cy, 158 * s, 2 * math.pi, 0)
    g = cairo.LinearGradient(cx - 290 * s, cy - 290 * s, cx + 290 * s, cy + 290 * s)
    g.add_color_stop_rgb(0, *hexc("#7DD3FC")[:3]); g.add_color_stop_rgb(0.55, *hexc("#38BDF8")[:3]); g.add_color_stop_rgb(1, *hexc("#2563EB")[:3])
    c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); c.set_source(g); c.fill()
    c.set_fill_rule(cairo.FILL_RULE_WINDING)
    # inner disc
    c.arc(cx, cy, 150 * s, 0, 2 * math.pi); fill(c, "#0B1222"); c.fill()
    glow(c, cx, cy, 150 * s, YEL, 0.22)
    keyhole(c, cx, cy - 4 * s, 1.18 * s, YEL)

def bg(c, w, h, dots=True, glow_xy=None):
    g = cairo.LinearGradient(0, 0, 0, h)
    g.add_color_stop_rgb(0, *hexc("#0B1222")[:3]); g.add_color_stop_rgb(1, *hexc("#070B16")[:3])
    c.set_source(g); c.paint()
    if glow_xy: glow(c, glow_xy[0], glow_xy[1], max(w, h) * 0.45, "#1E3A8A", 0.40)
    if dots:
        for yy in range(30, h, 54):
            for xx in range(27, w, 54):
                c.new_sub_path(); c.arc(xx, yy, 1.8, 0, 2 * math.pi)
        c.set_source_rgba(1, 1, 1, 0.06); c.fill()

def logo(size=800):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size); c = cairo.Context(s)
    bg(c, size, size, dots=False, glow_xy=(size / 2, size / 2))
    mark(c, size / 2, size / 2, size / 800)
    s.write_to_png(f"{OUT}/logo_800.png")

def banner():
    W, H = 2560, 1440
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    bg(c, W, H, glow_xy=(W / 2, H / 2))
    # decorative radio bubbles + small gears outside the safe zone
    for (x, y, r, col, a) in ((260, 300, 220, CYAN, .35), (2330, 1150, 260, CYAN, .3), (2250, 260, 150, "#A78BFA", .3), (330, 1170, 170, "#FBBF24", .25)):
        rgb = hexc(col)
        c.set_line_width(4); c.set_dash([16, 16]); c.set_source_rgba(rgb[0], rgb[1], rgb[2], a)
        c.arc(x, y, r, 0, 2 * math.pi); c.stroke(); c.set_dash([])
        c.set_line_width(3); c.set_source_rgba(rgb[0], rgb[1], rgb[2], a * 0.6); c.arc(x, y, r * 0.55, 0, 2 * math.pi); c.stroke()
    for (x, y, sc_, a) in ((560, 230, .22, .18), (2000, 1240, .26, .18), (120, 720, .18, .14), (2450, 700, .2, .14)):
        gear_path(c, x, y, 290 * sc_, 238 * sc_, 10); c.new_sub_path(); c.arc_negative(x, y, 150 * sc_, 2 * math.pi, 0)
        c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); c.set_source_rgba(*hexc("#38BDF8")[:3], a); c.fill(); c.set_fill_rule(cairo.FILL_RULE_WINDING)
    # safe area 1546x423 centred: x 507..2053, y 508..931
    title = "HIDDEN MECHANICS"
    safe_w = 1546 - 90
    mark_d, gap = 270, 44
    fs = 150
    font(c, fs, "black"); tw_ = tw(c, title)
    fs = fs * (safe_w - mark_d - gap) / tw_
    font(c, fs, "black"); tw_ = tw(c, title)
    total = mark_d + gap + tw_
    x0 = (W - total) / 2
    mark(c, x0 + mark_d / 2, H / 2, mark_d / 640)
    tx = x0 + mark_d + gap
    text(c, title, tx, H / 2 + 6, fs, WHITE, "black", "left")
    tag = "How everyday things actually work, in under a minute"
    ts = 46
    font(c, ts, "xbold")
    while tw(c, tag) > tw_ and ts > 30: ts -= 1; font(c, ts, "xbold")
    text(c, tag, tx + 4, H / 2 + 6 + ts * 1.8, ts, YEL, "xbold", "left")
    s.write_to_png(f"{OUT}/banner_2560x1440.png")
    # preview with safe-area guides (for checking only)
    c.set_source_rgba(1, 0.2, 0.2, 0.8); c.set_line_width(3)
    c.rectangle(507, 508, 1546, 423); c.stroke()
    s.write_to_png(f"{OUT}/_banner_guides.png")

def watermark():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 150, 150); c = cairo.Context(s)
    mark(c, 75, 75, 150 / 640)
    s.write_to_png(f"{OUT}/watermark_150.png")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    logo(); banner(); watermark()
    print("ok")
