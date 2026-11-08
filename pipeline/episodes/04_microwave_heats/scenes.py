"""Episode 04: How a microwave oven heats food."""
import numpy as np
from hm.core import *
from hm.props import *

O_COL, H_COL = "#FB7185", "#F1F5F9"
WAVE = "#F472B6"


# ---------- props for this episode ----------
def microwave(c, cx, cy, s, a, on, t, shake=0.0):
    if a <= 0: return
    c.save(); c.translate(cx, cy); safe_scale(c, s, s)
    c.push_group()
    glow(c, 0, 30, 520, "#000000", 0.5)
    rr(c, -380, -230, 760, 460, 40); fill(c, "#CBD5E1"); c.fill()
    rr(c, -370, -220, 740, 440, 34)
    g = cairo.LinearGradient(0, -220, 0, 220)
    g.add_color_stop_rgb(0, *hexc("#E2E8F0")[:3]); g.add_color_stop_rgb(1, *hexc("#94A3B8")[:3])
    c.set_source(g); c.fill()
    # window
    rr(c, -330, -180, 470, 360, 22); fill(c, "#0B1220"); c.fill()
    if on > 0:
        rr(c, -330, -180, 470, 360, 22)
        gg = cairo.RadialGradient(-95, 40, 20, -95, 0, 300)
        gg.add_color_stop_rgba(0, *hexc("#FDE68A")[:3], 0.75 * on); gg.add_color_stop_rgba(1, *hexc("#F59E0B")[:3], 0.15 * on)
        c.set_source(gg); c.fill()
    # bowl on plate
    c.save(); c.translate(-95, 90)
    c.save(); safe_scale(c, 1, 0.22); c.arc(0, 0, 170, 0, 2 * math.pi); fill(c, "#475569"); c.fill(); c.restore()
    c.move_to(-110, -60); c.curve_to(-100, 20, 100, 20, 110, -60); c.close_path(); fill(c, "#F8FAFC"); c.fill()
    c.save(); safe_scale(c, 1, 0.25); c.arc(0, -240, 110, 0, 2 * math.pi); fill(c, "#FB923C"); c.fill(); c.restore()
    c.restore()
    # mesh dots
    for yy in range(-170, 180, 18):
        for xx in range(-320, 140, 18):
            c.new_sub_path(); c.arc(xx, yy, 3.2, 0, 2 * math.pi)
    fill(c, "#020617", 0.35); c.fill()
    # control panel
    rr(c, 190, -180, 150, 70, 12); fill(c, "#0F172A"); c.fill()
    text(c, "0:30" if on > 0 else "12:00", 265, -132, 40, "#4ADE80" if on > 0 else "#64748B", "mono")
    for i in range(3):
        for j in range(3):
            c.arc(225 + j * 40, -50 + i * 44, 13, 0, 2 * math.pi); fill(c, "#64748B"); c.fill()
    rr(c, 210, 110, 110, 46, 23); fill(c, "#334155"); c.fill()
    c.pop_group_to_source(); c.paint_with_alpha(a)
    c.restore()


def no_icon(c, x, y, kind, a, cross):
    if a <= 0: return
    c.save(); c.translate(x, y)
    c.arc(0, 0, 70, 0, 2 * math.pi); fill(c, "#0F172A", 0.9 * a); c.fill_preserve(); fill(c, "#475569", a); c.set_line_width(4); c.stroke()
    if kind == "flame":
        c.move_to(0, -44); c.curve_to(40, -10, 34, 40, 0, 42); c.curve_to(-34, 40, -40, -10, 0, -44); fill(c, AMBER, a); c.fill()
        c.move_to(0, -6); c.curve_to(16, 8, 14, 30, 0, 32); c.curve_to(-14, 30, -16, 8, 0, -6); fill(c, YEL, a); c.fill()
    else:
        c.set_line_width(7); fill(c, "#F97316", a)
        for i in range(4):
            c.move_to(-40, -30 + i * 20); c.curve_to(-15, -44 + i * 20, 15, -16 + i * 20, 40, -30 + i * 20)
        c.stroke()
    if cross > 0:
        c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, RED, a)
        e = -50 + 100 * cross
        c.move_to(-50, -50); c.line_to(e, e); c.stroke()
    c.restore()


def water(c, x, y, s, ang, a, charges=0.0):
    """Water molecule: O with two H at ~104.5 degrees. ang = direction the O->H side points (radians)."""
    if a <= 0: return
    c.save(); c.translate(x, y); c.rotate(ang); safe_scale(c, s, s)
    half = math.radians(104.5) / 2
    for sgn in (-1, 1):
        hx, hy = 70 * math.cos(sgn * half), 70 * math.sin(sgn * half)
        c.set_line_width(10); fill(c, "#CBD5E1", a); c.move_to(0, 0); c.line_to(hx, hy); c.stroke()
        c.arc(hx, hy, 28, 0, 2 * math.pi); fill(c, H_COL, a); c.fill()
    c.arc(0, 0, 48, 0, 2 * math.pi)
    g = cairo.RadialGradient(-14, -14, 4, 0, 0, 48)
    g.add_color_stop_rgba(0, *hexc("#FECDD3")[:3], a); g.add_color_stop_rgba(1, *hexc(O_COL)[:3], a)
    c.set_source(g); c.fill()
    if charges > 0:
        c.save(); c.rotate(-ang)
        ox, oy = -60 * math.cos(ang), -60 * math.sin(ang)
        hx, hy = 92 * math.cos(ang), 92 * math.sin(ang)
        text(c, "−", ox, oy + 18, 64, RED, "black", a=a * charges, stroke=8)
        text(c, "+", hx, hy + 18, 60, CYAN, "black", a=a * charges, stroke=8)
        c.restore()
    c.restore()


def sine(c, x0, x1, y, amp, wl, phase, col, a, lw=7):
    if a <= 0 or x1 <= x0: return
    c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, col, a)
    n = max(2, int((x1 - x0) / 4))
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        yy = y + amp * math.sin(2 * math.pi * (x - x0) / wl - phase)
        (c.move_to if i == 0 else c.line_to)(x, yy)
    c.stroke()


def cavity(c, a, t, waves, ruler):
    """Side cutaway: magnetron box on the right sending waves into the cooking chamber."""
    if a <= 0: return
    rr(c, 90, 560, 900, 560, 30); fill(c, "#0F172A", 0.95 * a); c.fill_preserve()
    fill(c, "#94A3B8", a); c.set_line_width(8); c.stroke()
    # magnetron
    rr(c, 800, 600, 160, 150, 18); fill(c, "#475569", a); c.fill()
    for i in range(5):
        rr(c, 815, 615 + i * 26, 130, 12, 6); fill(c, "#64748B", a); c.fill()
    glow(c, 800, 675, 90, WAVE, 0.5 * a * waves)
    text(c, "MAGNETRON", 880, 790, 24, WHITE, "xbold", a=a)
    # waveguide
    rr(c, 640, 650, 160, 50, 6); fill(c, "#334155", a); c.fill()
    # plate + food
    c.save(); c.translate(500, 1040); safe_scale(c, 1, 0.22); c.arc(0, 0, 250, 0, 2 * math.pi); fill(c, "#475569", a); c.fill(); c.restore()
    rr(c, 400, 960, 200, 70, 30); fill(c, "#FB923C", a); c.fill()
    if waves > 0:
        front = 640 - 560 * waves
        for k, yy in enumerate((675, 800, 920)):
            sine(c, max(120, front), 640 if k == 0 else 760, yy, 26, 150, t * 9 + k, WAVE, a * (0.95 if k == 0 else 0.55))
    if ruler > 0:
        y = 600
        x0, x1 = 300, 450
        fill(c, YEL, a * ruler); c.set_line_width(4)
        c.move_to(x0, y); c.line_to(x1, y); c.stroke()
        for xx in (x0, x1):
            c.move_to(xx, y - 14); c.line_to(xx, y + 14); c.stroke()
        pill(c, "≈ 12 CM", 375, y - 50, 30, "#0F172A", YEL, a=a * ruler, sc=back(ruler), pad=18, outline=YEL)


def food_section(c, cx, cy, R, a, outer, middle, t):
    """Cross-section of a piece of food: outer ~1 cm layer heats first, middle warms by conduction."""
    if a <= 0: return
    c.arc(cx, cy, R, 0, 2 * math.pi)
    fill(c, "#FDBA74", a); c.fill()
    # heat layers
    if outer > 0:
        rin = R - 70
        g = cairo.RadialGradient(cx, cy, rin * (1 - 0.9 * middle), cx, cy, R)
        g.add_color_stop_rgba(0, *hexc("#FDBA74")[:3], 0)
        g.add_color_stop_rgba(0.55, *hexc(RED)[:3], 0.55 * outer * a)
        g.add_color_stop_rgba(1, *hexc("#DC2626")[:3], 0.9 * outer * a)
        c.set_source(g); c.arc(cx, cy, R, 0, 2 * math.pi); c.fill()
        c.set_dash([10, 10]); c.set_line_width(3); fill(c, WHITE, 0.6 * outer * a)
        c.arc(cx, cy, rin, 0, 2 * math.pi); c.stroke(); c.set_dash([])
    if middle > 0:
        for i in range(8):
            ang = i * math.pi / 4 + 0.2
            ph = (t * 0.8 + i * 0.12) % 1
            r0 = R - 80 - 120 * ph
            x0, y0 = cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)
            x1, y1 = cx + (r0 - 50) * math.cos(ang), cy + (r0 - 50) * math.sin(ang)
            c.set_line_width(7); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, "#B91C1C", middle * a * math.sin(ph * math.pi))
            c.move_to(x0, y0); c.line_to(x1, y1); c.stroke()
            for sd in (-1, 1):
                c.move_to(x1, y1); c.line_to(x1 + 18 * math.cos(ang + sd * 0.6), y1 + 18 * math.sin(ang + sd * 0.6)); c.stroke()
    c.set_line_width(5); fill(c, "#9A3412", a); c.arc(cx, cy, R, 0, 2 * math.pi); c.stroke()


def heatmap(c, cx, cy, size, a, hm, plate_ang, t):
    if a <= 0: return
    x0, y0 = cx - size / 2, cy - size / 2
    rr(c, x0 - 14, y0 - 14, size + 28, size + 28, 24); fill(c, "#94A3B8", a); c.fill()
    rr(c, x0, y0, size, size, 16); fill(c, "#0F172A", a); c.fill()
    if hm > 0:
        n = 18
        cell_ = size / n
        for i in range(n):
            for j in range(n):
                u = (i + 0.5) / n; v = (j + 0.5) / n
                val = (math.sin(3 * math.pi * u) * math.sin(3 * math.pi * v)) ** 2
                col = lerp_col("#1E3A8A", "#EF4444", val)
                c.rectangle(x0 + i * cell_, y0 + j * cell_, cell_ + 0.6, cell_ + 0.6)
                c.set_source_rgba(col[0], col[1], col[2], 0.85 * hm * a); c.fill()
    # turntable plate with food bits
    c.save(); c.translate(cx, cy); c.rotate(plate_ang)
    c.arc(0, 0, size * 0.36, 0, 2 * math.pi); fill(c, "#E2E8F0", 0.35 * a); c.fill_preserve()
    fill(c, "#F8FAFC", 0.8 * a); c.set_line_width(4); c.stroke()
    for k in range(5):
        ang = k * 2 * math.pi / 5
        c.arc(size * 0.22 * math.cos(ang), size * 0.22 * math.sin(ang), 22, 0, 2 * math.pi); fill(c, "#FB923C", a); c.fill()
    c.restore()


def eye(c, x, y, s, a):
    if a <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, s, s)
    c.move_to(-60, 0); c.curve_to(-30, -40, 30, -40, 60, 0); c.curve_to(30, 40, -30, 40, -60, 0); c.close_path()
    fill(c, WHITE, a); c.fill()
    c.arc(0, 0, 22, 0, 2 * math.pi); fill(c, "#0EA5E9", a); c.fill()
    c.arc(0, 0, 10, 0, 2 * math.pi); fill(c, "#020617", a); c.fill()
    c.restore()


# ---------- the episode ----------
def draw(c, t):
    A = 1 - cta_amount(t)

    # ---- hook ----
    hook_title(c, t, "HOW DOES A MICROWAVE", "HEAT YOUR FOOD?", S("magnetron"))
    ha = (1 - ease(pr(t, S("magnetron") - 0.1, 0.45))) * A
    if ha > 0:
        k = back(pr(t, 0.05, 0.6))
        on = ease(pr(t, wt("hook", "heats") - 0.1, 0.4))
        microwave(c, 540, 820, 0.95 * k, ha, on, t)
        no_icon(c, 300, 1200, "flame", ha * ease(pr(t, wt("hook", "flame") - 0.2, 0.3)), pr(t, wt("hook", "flame") + 0.1, 0.3))
        no_icon(c, 520, 1200, "coil", ha * ease(pr(t, wt("hook", "coil") - 0.4, 0.3)), pr(t, wt("hook", "coil"), 0.3))
        sh = ease(pr(t, wt("hook", "shakes") - 0.1, 0.4))
        if sh > 0:
            c.save(); c.translate(800, 1210); safe_scale(c, back(sh), back(sh))
            c.arc(0, 0, 90, 0, 2 * math.pi); fill(c, "#0F172A", 0.95 * ha); c.fill_preserve(); fill(c, CYAN, ha); c.set_line_width(4); c.stroke()
            water(c, 0, 0, 0.6, 0.6 * math.sin(t * 22), ha)
            c.restore()

    # ---- magnetron ----
    ma = ease(pr(t, S("magnetron") - 0.1, 0.5)) * (1 - ease(pr(t, S("dipole") - 0.1, 0.4))) * A
    if ma > 0:
        waves = eout(pr(t, wt("magnetron", "microwaves") - 0.2, 1.4))
        ruler = pr(t, wt("magnetron", "twelve") - 0.2, 0.4)
        cavity(c, ma, t, waves, ruler)
        mp = pr(t, wt("magnetron", "magnetron") - 0.1, 0.4)
        pill(c, "MAGNETRON → MICROWAVES", 540, 470, 30, "#0F172A", WAVE, a=ma * ease(mp), sc=back(mp), pad=22, outline=WAVE)
        rw = pr(t, wt("magnetron", "radio"), 0.4)
        pill(c, "A KIND OF RADIO WAVE", 540, 1215, 30, "#0F172A", CYAN, a=ma * ease(rw), sc=back(rw), pad=22, outline=CYAN)

    # ---- dipole ----
    da = ease(pr(t, S("dipole") - 0.1, 0.5)) * (1 - ease(pr(t, S("flip") - 0.1, 0.4))) * A
    if da > 0:
        k = back(pr(t, wt("dipole", "water") - 0.1, 0.5))
        ch = ease(pr(t, wt("dipole", "positive") - 0.1, 0.4))
        water(c, 540, 820, 2.0 * k, -math.pi / 2 + 0.08 * math.sin(t * 2), da, charges=ch)
        text(c, "H₂O", 540, 1190, 60, WHITE, "black", a=da * ease(k))
        p1 = pr(t, wt("dipole", "positive") - 0.1, 0.4); p2 = pr(t, wt("dipole", "negative") - 0.1, 0.4)
        pill(c, "SLIGHTLY +", 800, 520, 30, "#0F172A", CYAN, a=da * ease(p1), sc=back(p1), pad=20, outline=CYAN)
        pill(c, "SLIGHTLY −", 800, 1080, 30, "#0F172A", RED, a=da * ease(p2), sc=back(p2), pad=20, outline=RED)

    # ---- flip: field swings, molecules follow ----
    fa = ease(pr(t, S("flip") - 0.1, 0.5)) * (1 - ease(pr(t, S("heat") - 0.1, 0.4))) * A
    if fa > 0:
        fon = ease(pr(t, wt("flip", "field") - 0.1, 0.4))
        f = math.sin(t * 2 * math.pi * 0.9)          # slowed-down field for the eye
        for i in range(5):
            x = 150 + i * 195
            for y in (610, 1170):
                L = 70 * f
                c.set_line_width(8); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, AMBER, fa * fon * (0.3 + 0.7 * abs(f)))
                c.move_to(x, y); c.line_to(x, y - L); c.stroke()
                if abs(L) > 10:
                    sd = -1 if L > 0 else 1
                    c.move_to(x, y - L); c.line_to(x - 16, y - L - 16 * sd); c.move_to(x, y - L); c.line_to(x + 16, y - L - 16 * sd); c.stroke()
        tw = ease(pr(t, wt("flip", "twist") - 0.3, 0.4))
        follow = max(fon * 0.6, tw)
        for i in range(4):
            for j in range(2):
                x = 200 + i * 227; y = 760 + j * 230
                target = -math.pi / 2 * (1 if f >= 0 else -1) * min(1, abs(f) * 2)
                ang = lerp(0.9 * (i + j), target + 0.2 * math.sin(t * 7 + i), follow)
                water(c, x, y, 0.75, ang, fa * ease(pr(t, S("flip") + 0.1 * (i + j), 0.4)))
        cnt = pr(t, wt("flip", "two") - 0.1, 0.4)
        if cnt > 0:
            c.save(); c.translate(540, 460); safe_scale(c, back(cnt), back(cnt))
            rr(c, -330, -48, 660, 96, 48); fill(c, "#0F172A", 0.95 * fa); c.fill_preserve(); fill(c, AMBER, fa); c.set_line_width(3); c.stroke()
            text(c, "2.45 BILLION SWINGS / SECOND", 0, 14, 38, AMBER, "black", a=fa)
            c.restore()

    # ---- heat: only the outer ~1 cm heats directly ----
    ea = ease(pr(t, S("heat") - 0.1, 0.5)) * (1 - ease(pr(t, S("spots") - 0.1, 0.4))) * A
    if ea > 0:
        outer = ease(pr(t, wt("heat", "heat") - 0.3, 0.8))
        middle = ease(pr(t, wt("heat", "middle") - 0.1, 0.8))
        food_section(c, 540, 840, 330, ea, outer, middle, t)
        cm = pr(t, wt("heat", "centimeter") - 0.2, 0.4)
        if cm > 0:
            fill(c, WHITE, ea * ease(cm)); c.set_line_width(4)
            c.move_to(870, 840); c.line_to(800, 840); c.stroke()
            pill(c, "~1 CM", 940, 840, 30, "#0F172A", WHITE, a=ea * ease(cm), sc=back(cm), pad=16, outline=WHITE)
        md = pr(t, wt("heat", "middle"), 0.4)
        pill(c, "MIDDLE: HEATED BY CONDUCTION", 540, 1255, 30, "#0F172A", AMBER, a=ea * ease(md), sc=back(md), pad=22, outline=AMBER)
        my = pr(t, wt("heat", "only") - 0.2, 0.4) * (1 - ease(pr(t, wt("heat", "middle") - 0.2, 0.3)))
        pill(c, "NOT INSIDE-OUT", 540, 460, 32, "#450A0A", RED, a=ea * ease(my), pad=24, outline=RED)

    # ---- spots: standing waves + turntable ----
    sa = ease(pr(t, S("spots") - 0.1, 0.5)) * (1 - ease(pr(t, S("door") - 0.1, 0.4))) * A
    if sa > 0:
        hm = ease(pr(t, wt("spots", "hot") - 0.4, 0.6))
        spin = ease(pr(t, wt("spots", "plate") - 0.3, 0.4))
        heatmap(c, 540, 830, 640, sa, hm, (t - wt("spots", "plate")) * 2.2 * spin, t)
        h1 = pr(t, wt("spots", "hot") - 0.1, 0.4)
        pill(c, "HOT", 290, 1215, 30, "#450A0A", RED, a=sa * ease(h1), sc=back(h1), pad=18, outline=RED)
        pill(c, "COLD", 790, 1215, 30, "#0F172A", "#60A5FA", a=sa * ease(pr(t, wt("spots", "cold") - 0.1, 0.4)), pad=18, outline="#60A5FA")
        sp = pr(t, wt("spots", "spins") - 0.2, 0.4)
        pill(c, "SPINNING EVENS IT OUT", 540, 460, 32, "#052E2B", GREEN, a=sa * ease(sp), sc=back(sp), pad=24, outline=GREEN)

    # ---- door: mesh blocks long waves, light gets through ----
    oa = ease(pr(t, S("door") - 0.1, 0.5)) * A
    if oa > 0:
        mx = 560
        rr(c, mx - 18, 520, 36, 700, 10); fill(c, "#94A3B8", oa); c.fill()
        for y in range(540, 1210, 34):
            rr(c, mx - 8, y, 16, 14, 4); fill(c, "#0B1220", oa); c.fill()
        text(c, "DOOR MESH", mx, 1262, 28, WHITE, "xbold", a=oa * ease(pr(t, wt("door", "mesh") - 0.2, 0.4)))
        text(c, "INSIDE", 250, 1262, 26, MUTED, "xbold", a=oa)
        text(c, "YOU", 870, 1262, 26, MUTED, "xbold", a=oa)
        bounce = pr(t, wt("door", "bounce") - 0.6, 1.0)
        if t > wt("door", "holes") - 0.3:
            go = ease(pr(t, wt("door", "holes") - 0.3, 0.8))
            front = lerp(110, mx - 24, go)
            back_x = mx - 24 - 420 * ease(bounce)
            sine(c, 110, front, 760, 60, 300, t * 6, WAVE, oa)
            if bounce > 0:
                sine(c, back_x, mx - 24, 900, 50, 300, -t * 6, WAVE, oa * 0.8)
                c.set_line_width(6); fill(c, WAVE, oa * 0.8)
                c.move_to(back_x, 900); c.line_to(back_x + 26, 880); c.move_to(back_x, 900); c.line_to(back_x + 26, 920); c.stroke()
        lt = ease(pr(t, wt("door", "light") - 0.2, 0.6))
        if lt > 0:
            for k, y in enumerate((1040, 1100)):
                sine(c, 140, lerp(140, 760, lt), y, 9, 26, t * 14 + k, YEL, oa, lw=5)
            eye(c, 860, 1070, 0.9, oa * lt)
        sm = pr(t, wt("door", "smaller") - 0.1, 0.4)
        pill(c, "HOLES MUCH SMALLER THAN THE WAVES", 540, 455, 30, "#0F172A", CYAN, a=oa * ease(sm), sc=back(sm), pad=22, outline=CYAN)

    for lid, s, col in (("magnetron", "THE SOURCE", WAVE), ("dipole", "WATER", CYAN), ("flip", "THE SHAKE", AMBER),
                        ("heat", "THE HEAT", RED), ("spots", "WHY IT SPINS", GREEN), ("door", "BONUS: THE DOOR", PURPLE)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "heats") - 0.1, "rumble"), (wt("hook", "flame") + 0.1, "low"), (wt("hook", "coil"), "low"),
            (wt("hook", "shakes") - 0.1, "pop"), (wt("magnetron", "magnetron") - 0.1, "pop"),
            (wt("magnetron", "microwaves") - 0.2, "ping"), (wt("magnetron", "twelve") - 0.2, "blip"),
            (wt("dipole", "water") - 0.1, "pop"), (wt("dipole", "positive") - 0.1, "blip"), (wt("dipole", "negative") - 0.1, "blip"),
            (wt("flip", "field") - 0.1, "rise"), (wt("flip", "two") - 0.1, "pop"), (wt("flip", "twist") - 0.3, "wake"),
            (wt("heat", "heat") - 0.3, "rise"), (wt("heat", "centimeter") - 0.2, "blip"), (wt("heat", "middle") - 0.1, "ping"),
            (wt("spots", "hot") - 0.4, "low"), (wt("spots", "spins") - 0.2, "success"),
            (wt("door", "mesh") - 0.2, "pop"), (wt("door", "bounce") - 0.6, "ping"), (wt("door", "light") - 0.2, "resolve")]
