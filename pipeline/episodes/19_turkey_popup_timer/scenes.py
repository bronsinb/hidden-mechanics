"""Episode 19: How a turkey pop-up timer knows the bird is done."""
from hm.core import *
from hm.props import *

DARK = "#0F172A"
ROAST = "#B45309"
ROAST_D = "#7C2D12"
MEAT = "#9A3412"
STICK = "#EF4444"
METAL = "#94A3B8"
HOT = "#F97316"


# ---------- turkey + oven ----------
def turkey(c, x, y, s, a, timer_pop=0.0, probe=0.0, probe_read=""):
    if a <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, s, s)
    # platter
    c.save(); c.scale(1, 0.28); c.arc(0, 560, 340, 0, 2 * math.pi); c.restore(); fill(c, "#E2E8F0", a); c.fill()
    # drumsticks
    for sx in (-1, 1):
        c.save(); c.translate(sx * 210, 60); c.rotate(sx * 0.5)
        c.save(); c.scale(1, 0.6); c.arc(0, 0, 95, 0, 2 * math.pi); c.restore(); fill(c, ROAST_D, a); c.fill()
        rr(c, sx * 60 - 16, -18, 70 if sx > 0 else 70, 36, 18); c.restore()
        c.save(); c.translate(sx * 210, 60); c.rotate(sx * 0.5)
        rr(c, (40 if sx > 0 else -110), -14, 70, 28, 14); fill(c, "#F5F5F4", a); c.fill()
        c.arc(110 if sx > 0 else -110, -10, 16, 0, 2 * math.pi); c.arc(110 if sx > 0 else -110, 10, 16, 0, 2 * math.pi); c.fill()
        c.restore()
    # body
    g = cairo.RadialGradient(-60, -80, 30, 0, 0, 280)
    g.add_color_stop_rgba(0, *hexc("#F59E0B")[:3], a); g.add_color_stop_rgba(1, *hexc(ROAST_D)[:3], a)
    c.save(); c.scale(1, 0.72); c.arc(0, 0, 260, 0, 2 * math.pi); c.restore(); c.set_source(g); c.fill()
    # pop-up timer in the breast
    c.save(); c.translate(-40, -150)
    rr(c, -18, -12, 36, 20, 8); fill(c, "#E0F2FE", a); c.fill()
    if timer_pop > 0:
        rr(c, -8, -12 - 46 * timer_pop, 16, 46 * timer_pop + 4, 6); fill(c, STICK, a); c.fill()
    c.restore()
    # probe thermometer
    if probe > 0:
        c.save(); c.translate(150, -40)
        c.set_line_width(8); fill(c, "#CBD5E1", a * probe); c.move_to(0, 0); c.line_to(120, -160); c.stroke()
        rr(c, 90, -300, 170, 120, 22); fill(c, "#1E293B", a * probe); c.fill()
        rr(c, 104, -286, 142, 70, 12); fill(c, "#052E2B", a * probe); c.fill()
        text(c, probe_read, 175, -236, 40, GREEN, "black", a=a * probe)
        c.restore()
    c.restore()


def oven(c, a, t):
    if a <= 0: return
    rr(c, 90, 560, 900, 760, 40); fill(c, "#1E293B", a); c.fill()
    rr(c, 140, 610, 800, 620, 26); g = cairo.LinearGradient(0, 610, 0, 1230)
    g.add_color_stop_rgba(0, *hexc("#7C2D12")[:3], a); g.add_color_stop_rgba(1, *hexc("#F97316")[:3], 0.8 * a)
    c.set_source(g); c.fill()
    for k in range(3):
        c.set_line_width(10); fill(c, "#FDBA74", (0.5 + 0.4 * math.sin(t * 4 + k)) * a)
        c.move_to(200, 1190 - k * 6); c.line_to(880, 1190 - k * 6); c.stroke()
    c.set_line_width(6); fill(c, "#64748B", a)
    for yy in (900,):
        c.move_to(150, yy); c.line_to(930, yy); c.stroke()


def battery_crossed(c, x, y, a, cross):
    if a <= 0: return
    rr(c, x - 70, y - 34, 130, 68, 12); fill(c, DARK, a); c.fill_preserve(); c.set_line_width(6); fill(c, WHITE, a); c.stroke()
    rr(c, x + 60, y - 14, 14, 28, 4); fill(c, WHITE, a); c.fill()
    rr(c, x - 60, y - 24, 40, 48, 6); fill(c, GREEN, a); c.fill()
    if cross > 0:
        c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, RED, a)
        c.move_to(x - 100, y - 60); c.line_to(lerp(x - 100, x + 110, cross), lerp(y - 60, y + 60, cross)); c.stroke()


# ---------- the timer cutaway ----------
TX = 540


def timer_cutaway(c, a, t, heat=0.0, melt=0.0, pop=0.0, labels=0.0):
    if a <= 0: return
    top, tip = 640, 1250
    # meat around
    c.rectangle(80, 820, 920, 520); fill(c, lerp_col(MEAT, "#C2410C", heat), a); c.fill()
    for k in range(14):
        xx = 120 + (k * 67) % 860; yy = 860 + (k * 131) % 440
        c.set_line_width(5); fill(c, ROAST_D, 0.4 * a)
        c.move_to(xx, yy); c.curve_to(xx + 30, yy + 10, xx + 50, yy - 10, xx + 80, yy); c.stroke()
    if heat > 0:
        for k in range(6):
            ph = (t * 0.6 + k / 6) % 1
            xx = 150 + k * 150; yy = 1300 - 420 * ph
            c.set_line_width(5); fill(c, HOT, a * heat * (1 - ph))
            c.move_to(xx, yy)
            for s in range(1, 8): c.line_to(xx + 10 * math.sin(s + t * 5), yy - s * 10)
            c.stroke()
    # casing
    rr(c, TX - 120, top + 10, 240, 40, 16); fill(c, "#E0F2FE", a); c.fill()          # flange
    rr(c, TX - 60, top + 40, 120, tip - top - 40, 20); fill(c, "#BAE6FD", 0.55 * a); c.fill()
    c.set_line_width(5); fill(c, "#E0F2FE", a)
    rr(c, TX - 60, top + 40, 120, tip - top - 40, 20); c.stroke()
    # tip point
    c.move_to(TX - 60, tip - 20); c.line_to(TX, tip + 40); c.line_to(TX + 60, tip - 20); c.close_path(); fill(c, "#E0F2FE", a); c.fill()
    lift = 160 * back(pop) if pop > 0 else 0
    # spring between collar and the casing floor ring
    floor_y = 1020
    collar_y = 880 - lift
    n = 9
    c.set_line_width(7); fill(c, "#CBD5E1", a)
    c.move_to(TX - 40, floor_y)
    for i in range(1, n * 2 + 1):
        yy = lerp(floor_y, collar_y, i / (n * 2))
        c.line_to(TX + (40 if i % 2 else -40), yy)
    c.stroke()
    rr(c, TX - 58, floor_y, 116, 14, 6); fill(c, "#7DD3FC", a); c.fill()           # spring seat
    # stick
    rr(c, TX - 16, top - 30 - lift, 32, 1180 - top + 30, 14); fill(c, STICK, a); c.fill()
    rr(c, TX - 46, collar_y - 14, 92, 18, 8); fill(c, "#DC2626", a); c.fill()        # collar
    # metal blob holding the bottom of the stick
    if melt < 1:
        bx, by = TX, 1190
        glow(c, bx, by, 80, HOT, 0.7 * a * heat)
        c.save(); c.translate(bx, by); c.scale(1, 1 - 0.5 * melt)
        c.arc(0, 0, 44, 0, 2 * math.pi); c.restore()
        fill(c, lerp_col(METAL, HOT, heat), a); c.fill()
    if melt > 0:
        # liquid puddle
        c.save(); c.translate(TX, 1228); c.scale(1, 0.35); c.arc(0, 0, 40 + 10 * melt, 0, 2 * math.pi); c.restore()
        fill(c, "#FDBA74", a * melt); c.fill()
    if labels > 0:
        for txt, lx, ly, px, py, col in (("RED STICK", 840, 700 - 0, TX + 18, 760 - lift, STICK),
                                         ("SPRING", 840, 950, TX + 42, 950 - lift * 0.5, "#CBD5E1"),
                                         ("METAL BLOB", 840, 1190, TX + 46, 1190, METAL)):
            c.set_line_width(3); fill(c, col, 0.8 * a * labels); c.move_to(lx - 110, ly - 10); c.line_to(px, py); c.stroke()
            text(c, txt, lx, ly, 30, col, "black", a=a * labels, stroke=6)


def sprinkler(c, x, y, a, t, melt):
    if a <= 0: return
    c.rectangle(0, y - 160, 1080, 40); fill(c, "#334155", a); c.fill()
    c.rectangle(x - 18, y - 125, 36, 70); fill(c, "#94A3B8", a); c.fill()
    rr(c, x - 50, y - 60, 100, 40, 10); fill(c, "#CBD5E1", a); c.fill()
    c.move_to(x - 40, y - 20); c.line_to(x - 40, y + 40); c.line_to(x + 40, y + 40); c.line_to(x + 40, y - 20); c.set_line_width(8); fill(c, "#CBD5E1", a); c.stroke()
    rr(c, x - 70, y + 40, 140, 14, 6); fill(c, "#CBD5E1", a); c.fill()                      # deflector
    if melt < 1:
        glow(c, x, y + 10, 50, HOT, 0.6 * a * melt)
        rr(c, x - 16, y - 20, 32, 50, 8); fill(c, lerp_col(METAL, HOT, melt), a * (1 - melt * 0.8)); c.fill()
    if melt >= 1:
        for k in range(22):
            ang = math.pi * (0.1 + 0.8 * k / 21)
            for j in range(4):
                ph = (t * 1.6 + j / 4 + k * 0.05) % 1
                r0 = 60 + 360 * ph
                px, py = x + r0 * math.cos(ang), y + 50 + r0 * math.sin(ang) * 0.9
                c.arc(px, py, 6, 0, 2 * math.pi); fill(c, "#7DD3FC", a * (1 - ph)); c.fill()


def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "HOW THE TURKEY TIMER", "KNOWS IT'S DONE", S("parts"))

    hook_a = A * ease(pr(t, 0.05, 0.5)) * (1 - ease(pr(t, S("parts") - 0.2, 0.4)))
    cut_a = A * ease(pr(t, S("parts") - 0.1, 0.5)) * (1 - ease(pr(t, S("idea") - 0.2, 0.4)))
    idea_a = A * ease(pr(t, S("idea") - 0.1, 0.5)) * (1 - ease(pr(t, S("warn") - 0.3, 0.4)))
    warn_a = A * ease(pr(t, S("warn") - 0.2, 0.5))

    if hook_a > 0:
        oven(c, hook_a, t)
        turkey(c, 540, 960, 0.95, hook_a)
        b = ease(pr(t, wt("hook", "battery") - 0.3, 0.4))
        battery_crossed(c, 820, 680, hook_a * b, ease(pr(t, wt("hook", "electronics") - 0.3, 0.4)))

    if cut_a > 0:
        heat = ease(pr(t, wt("pop", "hot") - 0.6, 1.2))
        melt = eio(pr(t, wt("pop", "liquid") - 0.5, 0.7))
        pop = pr(t, wt("pop", "shoots") - 0.2, 0.5)
        timer_cutaway(c, cut_a, t, heat=heat, melt=melt, pop=pop,
                      labels=ease(pr(t, wt("parts", "red") - 0.3, 0.4)) * (1 - ease(pr(t, S("melt") + 0.6, 0.4))))
        sl = pr(t, wt("parts", "solder") - 0.3, 0.4) * (1 - ease(pr(t, S("melt") - 0.1, 0.3)))
        pill(c, "METAL SIMILAR TO SOLDER", 540, 470, 30, DARK, METAL, a=cut_a * ease(sl), sc=back(sl), pad=22, outline=METAL)
        mt = pr(t, wt("melt", "melt") - 0.2, 0.4) * (1 - ease(pr(t, S("pop") - 0.1, 0.3)))
        pill(c, "MELTS AT ABOUT TURKEY-DONE TEMP", 540, 470, 28, "#431407", HOT, a=cut_a * ease(mt), sc=back(mt), pad=22, outline=HOT)
        lq = pr(t, wt("pop", "liquid") - 0.2, 0.4) * (1 - ease(pr(t, wt("pop", "shoots") - 0.2, 0.3)))
        pill(c, "METAL MELTS · STICK RELEASED", 540, 470, 28, "#431407", HOT, a=cut_a * ease(lq), sc=back(lq), pad=22, outline=HOT)
        pp = pr(t, wt("pop", "pop") - 0.4, 0.3)
        if pp > 0:
            c.save(); c.translate(780, 640); safe_scale(c, back(pp), back(pp)); c.rotate(-0.15)
            text(c, "POP!", 0, 30, 110, YEL, "black", a=cut_a * ease(pp), stroke=12)
            c.restore()

    if idea_a > 0:
        mt = ease(pr(t, wt("idea", "melting") - 0.3, 0.6))
        rel = 1.0 if t > wt("idea", "release") - 0.2 else mt * 0.99
        sprinkler(c, 540, 820, idea_a, t, rel)
        fa = pr(t, wt("idea", "farmer") - 0.2, 0.4) * (1 - ease(pr(t, wt("idea", "sprinklers") - 0.3, 0.3)))
        pill(c, "A TURKEY FARMER'S IDEA", 540, 470, 30, DARK, AMBER, a=idea_a * ease(fa), sc=back(fa), pad=22, outline=AMBER)
        sp = pr(t, wt("idea", "sprinklers") - 0.2, 0.4) * (1 - ease(pr(t, S("patent") - 0.2, 0.3)))
        pill(c, "BORROWED FROM FIRE SPRINKLERS", 540, 470, 28, DARK, CYAN, a=idea_a * ease(sp), sc=back(sp), pad=22, outline=CYAN)
        y = pr(t, wt("patent", "1961") - 0.4, 0.5)
        if y > 0:
            c.save(); c.translate(540, 1210); safe_scale(c, back(y), back(y))
            text(c, "PATENTED 1961", 0, 20, 70, WHITE, "black", a=idea_a * ease(y), stroke=10)
            c.restore()

    if warn_a > 0:
        rd = ease(pr(t, wt("warn", "165") - 0.3, 0.4))
        turkey(c, 540, 1010, 0.95, warn_a, timer_pop=1.0, probe=ease(pr(t, wt("warn", "thermometer") - 0.4, 0.4)),
               probe_read="165°F" if rd > 0.5 else str(int(lerp(120, 165, rd))))
        ep = pr(t, wt("warn", "early") - 0.3, 0.4) * (1 - ease(pr(t, wt("warn", "thermometer") - 0.4, 0.3)))
        pill(c, "TIMERS CAN POP EARLY", 540, 470, 30, "#431407", AMBER, a=warn_a * ease(ep), sc=back(ep), pad=22, outline=AMBER)
        th = pr(t, wt("warn", "thermometer") - 0.2, 0.4)
        pill(c, "CHECK: 165°F, THICKEST PARTS", 540, 470, 28, "#052E2B", GREEN, a=warn_a * ease(th), sc=back(th), pad=22, outline=GREEN)

    for lid, s, col in (("parts", "THE PARTS", STICK), ("melt", "THE TRIGGER", HOT), ("pop", "THE POP", YEL),
                        ("idea", "THE ORIGIN", CYAN), ("warn", "THE CATCH", AMBER)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "battery") - 0.3, "blip"), (wt("hook", "electronics") - 0.3, "warn"),
            (wt("parts", "spring") - 0.3, "tick"), (wt("parts", "red") - 0.3, "pop"), (wt("parts", "metal") - 0.3, "ping"),
            (wt("melt", "melt") - 0.2, "rise"), (wt("pop", "hot") - 0.6, "rumble"), (wt("pop", "liquid") - 0.4, "low"),
            (wt("pop", "shoots") - 0.2, "pop"), (wt("pop", "pop") - 0.4, "success"),
            (wt("idea", "sprinklers") - 0.2, "ping"), (wt("idea", "release") - 0.2, "rise"), (wt("patent", "1961") - 0.4, "pop"),
            (wt("warn", "early") - 0.3, "warn"), (wt("warn", "165") - 0.3, "ok")]
