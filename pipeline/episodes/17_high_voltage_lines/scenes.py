"""Episode 17: Why power lines run at 100,000+ volts."""
from hm.core import *
from hm.props import *

DARK = "#0F172A"
HEAT = "#F97316"
COPPER = "#D97706"


def bolt(c, x, y, s, col, a):
    if a <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, s, s)
    c.move_to(10, -60); c.line_to(-30, 8); c.line_to(-2, 8); c.line_to(-14, 60); c.line_to(32, -12); c.line_to(4, -12); c.close_path()
    fill(c, col, a); c.fill(); c.restore()


def outlet(c, x, y, a):
    if a <= 0: return
    rr(c, x - 90, y - 130, 180, 260, 26); fill(c, "#E2E8F0", a); c.fill()
    for yy in (y - 55, y + 55):
        rr(c, x - 60, yy - 42, 120, 84, 30); fill(c, "#CBD5E1", a); c.fill()
        c.rectangle(x - 30, yy - 22, 12, 34); c.rectangle(x + 18, yy - 22, 12, 34); fill(c, "#1E293B", a); c.fill()
        c.arc(x, yy + 24, 9, math.pi, 2 * math.pi); c.close_path(); c.fill()


def tower(c, x, y, s, a, insul=0.0, gap=0.0, wires=1.0):
    """Lattice tower with base at (x,y)."""
    if a <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, s, s)
    if wires > 0:
        reach = (1080 / s) + 200
        c.set_line_width(4 / s * 1.6); fill(c, "#CBD5E1", 0.85 * a * wires)
        for ix, iy in ((-170, -330), (170, -330), (-120, -420), (120, -420)):
            yb = iy + 12 + 6 * 12
            side = -1 if ix < 0 else 1
            c.move_to(ix, yb); c.curve_to(ix + side * reach * 0.3, yb + 60, ix + side * reach * 0.7, yb + 60, ix + side * reach, yb); c.stroke()
    c.set_line_width(7); c.set_line_join(cairo.LINE_JOIN_ROUND); fill(c, "#94A3B8", a)
    c.move_to(-90, 0); c.line_to(-26, -420); c.line_to(26, -420); c.line_to(90, 0); c.stroke()
    for k in range(6):
        y0 = -k * 70; y1 = -(k + 1) * 70
        w0 = 90 - 64 * k / 6; w1 = 90 - 64 * (k + 1) / 6
        c.move_to(-w0, y0); c.line_to(w1, y1); c.move_to(w0, y0); c.line_to(-w1, y1); c.stroke()
    for arm_y, arm_w in ((-330, 190), (-420, 140)):
        c.move_to(-arm_w, arm_y); c.line_to(arm_w, arm_y); c.stroke()
        c.move_to(-arm_w, arm_y); c.line_to(-26, arm_y - 40); c.move_to(arm_w, arm_y); c.line_to(26, arm_y - 40); c.stroke()
    # insulator strings
    for ix, iy in ((-170, -330), (170, -330), (-120, -420), (120, -420)):
        for d in range(6):
            c.save(); c.translate(ix, iy + 12 + d * 12); c.scale(1, 0.4)
            c.arc(0, 0, 14, 0, 2 * math.pi); c.restore()
            fill(c, lerp_col("#E2E8F0", CYAN, insul), a); c.fill()
    c.restore()


def wire_heat(c, a, t, current, label=True):
    """A thick wire with flowing current and heat shimmer."""
    if a <= 0: return
    y = 880
    hot = cl(current)
    glow(c, 540, y, 380 * (0.5 + hot), HEAT, 0.45 * hot * a)
    rr(c, 90, y - 30, 900, 60, 30); fill(c, lerp_col(COPPER, "#FDBA74", hot * 0.7), a); c.fill()
    n = int(6 + 18 * current)
    for k in range(n):
        u = (t * (0.25 + 0.3 * current) + k / n) % 1
        x = 110 + 860 * u
        c.arc(x, y, 9, 0, 2 * math.pi); fill(c, YEL, a); c.fill()
    # heat waves
    c.set_line_width(5)
    for k in range(5):
        x0 = 200 + k * 170
        for j in range(3):
            ph = (t * 0.8 + j / 3 + k * 0.2) % 1
            yy = y - 60 - 180 * ph
            fill(c, HEAT, a * hot * (1 - ph))
            c.move_to(x0, yy)
            for s in range(1, 9):
                c.line_to(x0 + 10 * math.sin(s * 1.3 + t * 4), yy - s * 8)
            c.stroke()


def loss_grid(c, x, y, n, a, p, col, lab, sub):
    if a <= 0: return
    s = 70
    tot = n * n
    shown = int(tot * p + 0.999) if p > 0 else 0
    for i in range(tot):
        if i >= shown: break
        r, cc = divmod(i, n)
        bx = x - n * s / 2 + cc * s; by = y - n * s + r * s
        rr(c, bx + 4, by + 4, s - 8, s - 8, 10); fill(c, col, a); c.fill()
        glow(c, bx + s / 2, by + s / 2, 40, col, 0.25 * a)
    text(c, lab, x, y + 60, 34, WHITE, "black", a=a)
    text(c, sub, x, y + 105, 28, col, "black", a=a)


def power_rect(c, a, t, v, i_, col_v=CYAN, col_i=YEL):
    """Rectangle with width = current, height = voltage: area = power."""
    if a <= 0: return
    area = 300 * 300
    h = v; w = area / max(h, 1)
    bx, by = 540 - w / 2 + 60, 1200
    c.rectangle(bx, by - h, w, h); c.set_source_rgba(*hexc(GREEN)[:3], 0.25 * a); c.fill_preserve()
    c.set_line_width(5); fill(c, GREEN, a); c.stroke()
    text(c, "POWER", bx + w / 2, by - h / 2 + 12, 30, GREEN, "black", a=a)
    # voltage axis
    c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, col_v, a)
    c.move_to(bx - 30, by); c.line_to(bx - 30, by - h); c.stroke()
    text(c, "VOLTAGE", bx - 50, by - h / 2, 26, col_v, "black", align="right", a=a)
    fill(c, col_i, a); c.move_to(bx, by + 30); c.line_to(bx + w, by + 30); c.stroke()
    text(c, "CURRENT", bx + w / 2, by + 80, 26, col_i, "black", a=a)


def chain(c, a, t, p, step_dn=0.0):
    """Plant -> step-up -> line -> step-down -> house."""
    if a <= 0: return
    y = 1000
    # plant
    rr(c, 70, y - 90, 130, 140, 12); fill(c, "#475569", a); c.fill()
    for k in range(2):
        rr(c, 95 + k * 55, y - 190, 32, 110, 6); fill(c, "#64748B", a); c.fill()
        c.arc(111 + k * 55, y - 210 - 20 * ((t + k * 0.4) % 1), 18 + 10 * ((t + k * 0.4) % 1), 0, 2 * math.pi)
        fill(c, "#CBD5E1", 0.4 * a * (1 - (t + k * 0.4) % 1)); c.fill()
    # transformer boxes
    def xf(x, lab, col, on):
        rr(c, x - 55, y - 70, 110, 120, 14); fill(c, "#1E293B", a); c.fill_preserve(); c.set_line_width(4); fill(c, col, a * (0.4 + 0.6 * on)); c.stroke()
        for k in range(3):
            c.arc(x - 20, y - 38 + k * 28, 12, -math.pi / 2, math.pi / 2); c.stroke()
            c.arc(x + 20, y - 38 + k * 28, 12, math.pi / 2, 3 * math.pi / 2); c.stroke()
        text(c, lab, x, y + 95, 24, col, "black", a=a * on)
    up_on = ease(cl(p * 3))
    xf(290, "STEP UP", CYAN, up_on)
    xf(790, "STEP DOWN", GREEN, step_dn)
    # line between
    c.set_line_width(8); fill(c, "#94A3B8", a)
    c.move_to(345, y - 40); c.curve_to(480, y + 10, 600, y + 10, 735, y - 40); c.stroke()
    if up_on > 0:
        for k in range(6):
            u = (t * 0.5 + k / 6) % 1
            x = lerp(345, 735, u); yy = y - 40 + 50 * 4 * u * (1 - u) * 0.75
            glow(c, x, yy, 22, CYAN, 0.8 * a * up_on); c.arc(x, yy, 7, 0, 2 * math.pi); fill(c, WHITE, a * up_on); c.fill()
        text(c, "100,000+ V · LOW CURRENT", 540, y - 120, 28, CYAN, "black", a=a * up_on, stroke=6)
    # house
    hx = 960
    c.move_to(hx - 70, y - 30); c.line_to(hx, y - 100); c.line_to(hx + 70, y - 30); c.close_path(); fill(c, AMBER, a); c.fill()
    rr(c, hx - 55, y - 30, 110, 80, 6); fill(c, "#E2E8F0", a); c.fill()
    rr(c, hx - 15, y + 5, 30, 45, 4); fill(c, "#78350F", a); c.fill()
    text(c, "~120 V", hx, y + 95, 24, AMBER, "black", a=a * step_dn)


def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "WHY POWER LINES USE", "100,000+ VOLTS", S("loss"))

    hook_a = A * ease(pr(t, 0.05, 0.5)) * (1 - ease(pr(t, S("loss") - 0.2, 0.4)))
    wire_a = A * ease(pr(t, S("loss") - 0.1, 0.5)) * (1 - ease(pr(t, S("square") - 0.2, 0.4)))
    sq_a = A * ease(pr(t, S("square") - 0.1, 0.5)) * (1 - ease(pr(t, S("trade") - 0.2, 0.4)))
    tr_a = A * ease(pr(t, S("trade") - 0.1, 0.5)) * (1 - ease(pr(t, S("xfmr") - 0.2, 0.4)))
    ch_a = A * ease(pr(t, S("xfmr") - 0.1, 0.5)) * (1 - ease(pr(t, S("air") - 0.2, 0.4)))
    air_a = A * ease(pr(t, S("air") - 0.1, 0.5)) * (1 - ease(pr(t, S("result") - 0.2, 0.4)))
    res_a = A * ease(pr(t, S("result") - 0.1, 0.5))

    if hook_a > 0:
        o = ease(pr(t, wt("hook", "outlet") - 0.3, 0.4))
        outlet(c, 260, 900, hook_a * o)
        text(c, "~120 V", 260, 1110, 44, AMBER, "black", a=hook_a * ease(pr(t, wt("hook", "volts") - 0.4, 0.4)), stroke=8)
        tw = ease(pr(t, wt("hook", "lines") - 0.3, 0.5))
        tower(c, 780, 1190, 0.85, hook_a * tw, wires=0)
        v = int(lerp(120, 100000, eio(pr(t, wt("hook", "hundred") - 0.3, 0.8))))
        text(c, f"{v:,}+ V" if v > 99000 else f"{v:,} V", 780, 1270, 44, CYAN, "black", a=hook_a * ease(pr(t, wt("hook", "above") - 0.3, 0.4)), stroke=8)
        bolt(c, 780, 660, 0.9, YEL, hook_a * ease(pr(t, wt("hook", "extreme") - 0.3, 0.4)))

    if wire_a > 0:
        cur = 0.3 + 0.6 * ease(pr(t, wt("loss", "current") - 0.3, 0.6))
        wire_heat(c, wire_a, t, cur)
        wh = pr(t, wt("loss", "heat") - 0.3, 0.4) * (1 - ease(pr(t, wt("loss", "depends") - 0.3, 0.3)))
        pill(c, "WIRES WASTE ENERGY AS HEAT", 540, 470, 30, "#431407", HEAT, a=wire_a * ease(wh), sc=back(wh), pad=22, outline=HEAT)
        dp = pr(t, wt("loss", "depends") - 0.2, 0.4)
        pill(c, "MORE CURRENT = MORE HEAT", 540, 470, 30, "#431407", HEAT, a=wire_a * ease(dp), sc=back(dp), pad=22, outline=HEAT)

    if sq_a > 0:
        p1 = ease(pr(t, wt("square", "double") - 0.3, 0.4))
        loss_grid(c, 300, 1050, 1, sq_a * p1, 1.0, HEAT, "1× CURRENT", "1× LOSS")
        p2 = eio(pr(t, wt("square", "quadruples") - 0.4, 0.6))
        loss_grid(c, 760, 1050, 2, sq_a * ease(pr(t, wt("square", "loss") - 0.3, 0.4)), p2, RED, "2× CURRENT", "4× LOSS" if p2 > 0.9 else "")
        q = pr(t, wt("square", "quadruples") - 0.2, 0.4)
        pill(c, "LOSS GROWS WITH CURRENT²", 540, 470, 30, "#450A0A", RED, a=sq_a * ease(q), sc=back(q), pad=22, outline=RED)

    if tr_a > 0:
        hv = lerp(300, 560, eio(pr(t, wt("trade", "crank") - 0.2, 1.0)))
        power_rect(c, tr_a, t, hv, 0)
        f = pr(t, wt("trade", "power") - 0.2, 0.4) * (1 - ease(pr(t, wt("trade", "crank") - 0.3, 0.3)))
        pill(c, "POWER = VOLTAGE × CURRENT", 540, 470, 30, DARK, GREEN, a=tr_a * ease(f), sc=back(f), pad=22, outline=GREEN)
        sp = pr(t, wt("trade", "same") - 0.2, 0.4)
        pill(c, "SAME POWER · TINY CURRENT", 540, 470, 30, "#052E2B", GREEN, a=tr_a * ease(sp), sc=back(sp), pad=22, outline=GREEN)

    if ch_a > 0:
        p = ease(pr(t, wt("xfmr", "boost") - 0.4, 0.6)) / 3 * 3
        chain(c, ch_a, t, cl(p), step_dn=ease(pr(t, wt("xfmr", "step") - 0.3, 0.4)))
        tp = pr(t, wt("xfmr", "transformers") - 0.2, 0.4)
        pill(c, "TRANSFORMERS", 540, 470, 32, DARK, CYAN, a=ch_a * ease(tp), sc=back(tp), pad=22, outline=CYAN)

    if air_a > 0:
        ins = ease(pr(t, wt("air", "insulation") - 0.3, 0.4))
        tower(c, 540, 1300, 1.45, air_a, insul=ins)
        bm = pr(t, wt("air", "bare") - 0.2, 0.4) * (1 - ease(pr(t, wt("air", "insulation") - 0.3, 0.3)))
        pill(c, "BARE METAL WIRES", 540, 470, 32, DARK, WHITE, a=air_a * ease(bm), sc=back(bm), pad=22, outline=MUTED)
        ai = pr(t, wt("air", "air") - 0.3, 0.4)
        pill(c, "THE INSULATION IS AIR", 540, 470, 32, DARK, CYAN, a=air_a * ease(ai), sc=back(ai), pad=22, outline=CYAN)
        # spacing arrows between the conductors
        sp = ease(pr(t, wt("air", "spaced") - 0.3, 0.4))
        if sp > 0:
            y = 1300 - 330 * 1.45 + 95
            c.set_line_width(6); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, YEL, air_a * sp)
            x0, x1 = 540 - 170 * 1.45, 540 + 170 * 1.45
            c.move_to(x0 + 20, y); c.line_to(x1 - 20, y); c.stroke()
            for xx, d in ((x0 + 20, 1), (x1 - 20, -1)):
                c.move_to(xx + d * 22, y - 16); c.line_to(xx, y); c.line_to(xx + d * 22, y + 16); c.stroke()
            text(c, "KEEP YOUR DISTANCE", 540, y + 60, 28, YEL, "black", a=air_a * sp, stroke=6)
        tl = ease(pr(t, wt("air", "tall") - 0.3, 0.4))
        if tl > 0:
            c.set_line_width(6); fill(c, YEL, air_a * tl)
            c.move_to(960, 1300); c.line_to(960, 1300 - 420 * 1.45 * tl); c.stroke()
            text(c, "TALL", 960, 1300 - 420 * 1.45 * tl - 24, 28, YEL, "black", a=air_a * tl, stroke=6)

    if res_a > 0:
        p = eio(pr(t, wt("result", "percent") - 0.4, 0.8))
        x, y, w, hh = 120, 860, 840, 110
        rr(c, x, y, w, hh, 30); fill(c, "#1E293B", res_a); c.fill()
        rr(c, x + 6, y + 6, (w - 12) * (1 - 0.05 * p), hh - 12, 24); fill(c, YEL, res_a); c.fill()
        if p > 0:
            rr(c, x + 6 + (w - 12) * 0.95, y + 6, (w - 12) * 0.05, hh - 12, 12); fill(c, RED, res_a * p); c.fill()
            glow(c, x + w - 20, y + hh / 2, 80, RED, 0.6 * res_a * p)
        text(c, "DELIVERED", x + 40, y + hh / 2 + 12, 32, DARK, "black", align="left", a=res_a)
        f = pr(t, wt("result", "five") - 0.3, 0.4)
        c.save(); c.translate(540, 760); safe_scale(c, back(f), back(f))
        text(c, "~5% LOST", 0, 30, 110, RED, "black", a=res_a * ease(f), stroke=12)
        c.restore()
        text(c, "U.S. AVERAGE, 2018–2022 (EIA)", 540, 1040, 28, MUTED, "black", a=res_a * ease(pr(t, wt("result", "america's") - 0.3, 0.4)))

    for lid, s, col in (("loss", "THE PROBLEM", HEAT), ("square", "THE SQUARE LAW", RED), ("trade", "THE TRADE", GREEN),
                        ("xfmr", "THE TRANSFORMERS", CYAN), ("air", "THE SAFETY GAP", YEL), ("result", "THE COST", RED)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "volts") - 0.4, "pop"), (wt("hook", "hundred") - 0.3, "rise"), (wt("hook", "extreme") - 0.3, "rumble"),
            (wt("loss", "heat") - 0.3, "low"), (wt("loss", "current") - 0.3, "blip"),
            (wt("square", "double") - 0.3, "pop"), (wt("square", "quadruples") - 0.4, "warn"),
            (wt("trade", "power") - 0.2, "ping"), (wt("trade", "crank") - 0.2, "rise"), (wt("trade", "same") - 0.2, "success"),
            (wt("xfmr", "boost") - 0.4, "rise"), (wt("xfmr", "step") - 0.3, "resolve"),
            (wt("air", "bare") - 0.2, "tick"), (wt("air", "air") - 0.3, "ping"),
            (wt("result", "percent") - 0.4, "low")]
