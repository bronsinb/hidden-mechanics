"""Episode 18: Why golf balls have dimples."""
from hm.core import *
from hm.props import *

DARK = "#0F172A"
GRASS = "#15803D"
AIR = "#7DD3FC"
WAKE = "#F87171"
BX, BY, BR = 400, 900, 115


def ball(c, x, y, r, a, dimples=1.0, rot=0.0, scuff=0.0):
    if a <= 0: return
    g = cairo.RadialGradient(x - r * 0.35, y - r * 0.35, r * 0.1, x, y, r)
    g.add_color_stop_rgba(0, 1, 1, 1, a); g.add_color_stop_rgba(1, *hexc("#CBD5E1")[:3], a)
    c.arc(x, y, r, 0, 2 * math.pi); c.set_source(g); c.fill()
    if dimples > 0:
        c.save(); c.arc(x, y, r * 0.98, 0, 2 * math.pi); c.clip()
        for i in range(-4, 5):
            for j in range(-4, 5):
                px = i * r * 0.24 + (r * 0.12 if j % 2 else 0) + math.cos(rot) * 0
                py = j * r * 0.21
                ang = rot
                qx = px * math.cos(ang) - py * math.sin(ang); qy = px * math.sin(ang) + py * math.cos(ang)
                d = math.hypot(qx, qy) / r
                if d > 0.95: continue
                rad = r * 0.075 * (1 - 0.45 * d * d)
                c.save(); c.translate(x + qx, y + qy); c.scale(1, max(0.25, math.sqrt(max(0.0, 1 - d * d))))
                c.arc(0, 0, rad, 0, 2 * math.pi); c.restore()
                fill(c, "#94A3B8", 0.55 * a * dimples); c.fill()
        c.restore()
    if scuff > 0:
        c.set_line_width(3); fill(c, "#78716C", a * scuff)
        for k in range(9):
            ang = k * 0.7 + 0.3
            sx, sy = x + r * 0.55 * math.cos(ang), y + r * 0.5 * math.sin(ang * 1.3)
            c.move_to(sx - 12, sy - 4); c.line_to(sx + 14, sy + 5); c.stroke()


def flow(c, a, t, sep_deg, wake_h, turb=0.0, ball_dimples=0.0, show_pressure=0.0):
    """Air flowing left->right around the ball, separating at sep_deg (90 = top), wake of half-height wake_h."""
    if a <= 0: return
    # streamlines
    for k in range(-5, 6):
        if k == 0: continue
        h = k * 62
        pts = []
        for i in range(0, 121):
            x = 60 + 960 * i / 120
            dx = x - BX
            ay = abs(h)
            yabs = ay + BR * BR * ay / (dx * dx + ay * ay + 0.6 * BR * BR)
            if abs(dx) < BR + 14:
                yabs = max(yabs, math.sqrt(max(0.0, (BR + 16) ** 2 - dx * dx)))
            if dx > -BR * 0.2:
                edge = lerp(BR * math.sin(math.radians(sep_deg)), wake_h, 1 - math.exp(-max(dx, 0) / 90)) + 14
                if ay < wake_h + 40:
                    yabs = max(yabs, edge + (ay - 62) * 0.5)
            y = BY + math.copysign(yabs, h)
            pts.append((x, y))
        c.set_line_width(3); fill(c, AIR, 0.35 * a)
        c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.stroke()
        for j in range(3):
            u = (t * 0.35 + j / 3 + k * 0.07) % 1
            p = pts[int(u * 120)]
            glow(c, p[0], p[1], 16, AIR, 0.7 * a); c.arc(p[0], p[1], 5, 0, 2 * math.pi); fill(c, WHITE, a); c.fill()
    # wake
    sep = math.radians(sep_deg)
    sx, sy = BX - BR * math.cos(sep), BY - BR * math.sin(sep)
    c.move_to(sx, sy)
    c.curve_to(sx + 140, BY - wake_h, 700, BY - wake_h, 1020, BY - wake_h * 1.1)
    c.line_to(1020, BY + wake_h * 1.1)
    c.curve_to(700, BY + wake_h, sx + 140, BY + wake_h, sx, 2 * BY - sy)
    c.arc_negative(BX, BY, BR, math.pi + sep, math.pi - sep) if False else c.line_to(sx, 2 * BY - sy)
    c.close_path()
    c.set_source_rgba(*hexc(WAKE)[:3], 0.18 * a); c.fill()
    for k in range(int(4 + wake_h / 30)):
        u = (t * 0.22 + k * 0.137) % 1
        x = lerp(BX + BR * 0.6, 1000, u)
        yy = BY + wake_h * 0.75 * math.sin(k * 2.3 + t * 2)
        rv = 18 + 22 * u
        c.set_line_width(4); fill(c, WAKE, a * 0.8 * (1 - u * 0.6))
        c.new_path(); c.arc(x, yy, rv, t * 5 + k, t * 5 + k + 4.5); c.stroke()
    # separation dots
    for sgn in (-1, 1):
        px, py = BX - BR * math.cos(sep), BY + sgn * BR * math.sin(sep)
        glow(c, px, py, 30, YEL, 0.8 * a); c.arc(px, py, 9, 0, 2 * math.pi); fill(c, YEL, a); c.fill()
    # turbulent skin layer
    if turb > 0:
        c.set_line_width(4); fill(c, CYAN, a * turb)
        for sgn in (-1, 1):
            c.new_path()
            n = 40
            for i in range(n + 1):
                th = math.radians(lerp(170, sep_deg, i / n))
                rr_ = BR + 10 + 6 * math.sin(i * 1.7 + t * 14)
                x = BX - rr_ * math.cos(th) if False else BX + rr_ * math.cos(math.pi - th)
                y = BY - sgn * rr_ * math.sin(th)
                (c.move_to if i == 0 else c.line_to)(x, y)
            c.stroke()
    ball(c, BX, BY, BR, a, dimples=ball_dimples)
    if show_pressure > 0:
        text(c, "LOW PRESSURE", 760, BY + 12, 30, WAKE, "black", a=a * show_pressure, stroke=6)
        c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, WAKE, a * show_pressure)
        c.move_to(BX - BR - 30, BY - BR - 50); c.line_to(BX - BR - 170, BY - BR - 50); c.stroke()
        c.move_to(BX - BR - 140, BY - BR - 74); c.line_to(BX - BR - 172, BY - BR - 50); c.line_to(BX - BR - 140, BY - BR - 26); c.stroke()
        text(c, "DRAG", BX - BR - 100, BY - BR - 84, 28, WAKE, "black", a=a * show_pressure, stroke=6)


def flight(c, a, t, p_smooth, p_dimpled, lift=0.0):
    if a <= 0: return
    gy = 1230
    c.rectangle(0, gy, 1080, 120); fill(c, GRASS, a); c.fill()
    c.rectangle(0, gy, 1080, 8); fill(c, "#22C55E", a); c.fill()
    # tee
    c.rectangle(96, gy - 22, 8, 22); fill(c, "#FBBF24", a); c.fill()
    for p, land, peak, dimp, col, lab in ((p_smooth, 480, 200, 0.0, MUTED, "SMOOTH"), (p_dimpled, 960, 400 + 80 * lift, 1.0, YEL, "DIMPLED")):
        if p <= 0: continue
        pts = []
        for i in range(0, 81):
            u = i / 80
            x = lerp(100, land, u)
            sk = 0.62 if dimp else 0.45                 # dimpled: peak later (lift); smooth: drops early
            y = gy - 20 - peak * (math.sin(math.pi * min(1.0, u / (2 * sk))) if u < sk * 2 else 0) if u <= sk else gy - 20 - peak * math.cos((u - sk) / (1 - sk) * math.pi / 2)
            pts.append((x, y))
        m = max(2, int(81 * p))
        c.set_line_width(5); c.set_dash([16, 12]); fill(c, col, 0.8 * a)
        c.move_to(*pts[0]); [c.line_to(*q) for q in pts[1:m]]; c.stroke(); c.set_dash([])
        bx, by = pts[m - 1]
        ball(c, bx, by, 22, a, dimples=dimp)
        if p >= 0.99:
            c.set_line_width(4); fill(c, col, a); c.move_to(land, gy + 10); c.line_to(land, gy + 50); c.stroke()
            text(c, lab, land, gy + 90, 28, col, "black", a=a)


def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "WHY GOLF BALLS", "HAVE DIMPLES", S("drag"))

    fl_a = A * (ease(pr(t, 0.05, 0.5)) * (1 - ease(pr(t, S("drag") - 0.2, 0.4)))
                + ease(pr(t, S("spin") - 0.1, 0.5)) * (1 - ease(pr(t, S("history") - 0.2, 0.4))))
    air_a = A * ease(pr(t, S("drag") - 0.1, 0.5)) * (1 - ease(pr(t, S("spin") - 0.2, 0.4)))
    his_a = A * ease(pr(t, S("history") - 0.1, 0.5))

    if fl_a > 0:
        if t < S("drag"):
            ps = eio(pr(t, wt("hook", "smooth") - 0.6, 1.4))
            pd = eio(pr(t, wt("hook", "twice") - 0.6, 1.8))
            flight(c, fl_a, t, ps, pd)
            tw = pr(t, wt("hook", "far") - 0.2, 0.4)
            pill(c, "NEARLY 2× THE DISTANCE", 540, 470, 32, DARK, YEL, a=fl_a * ease(tw), sc=back(tw), pad=22, outline=YEL)
        else:
            # spin + lift close-up
            rot = -t * 6
            ball(c, 540, 860, 170, fl_a, dimples=1.0, rot=rot)
            c.set_line_width(9); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, AMBER, fl_a)
            c.new_path(); c.arc_negative(540, 860, 215, -0.4, -2.6); c.stroke()
            ex, ey = 540 + 215 * math.cos(-2.6), 860 + 215 * math.sin(-2.6)
            c.move_to(ex + 10, ey - 30); c.line_to(ex, ey); c.line_to(ex + 32, ey + 8); c.stroke()
            text(c, "BACKSPIN", 540, 1130, 30, AMBER, "black", a=fl_a * ease(pr(t, wt("spin", "backspin") - 0.3, 0.4)), stroke=6)
            lf = ease(pr(t, wt("spin", "lift") - 0.3, 0.4))
            if lf > 0:
                c.set_line_width(16); fill(c, GREEN, fl_a * lf)
                c.move_to(540, 640); c.line_to(540, 640 - 90 * back(pr(t, wt("spin", "lift") - 0.3, 0.5))); c.stroke()
                c.move_to(505, 590 - 20); c.line_to(540, 545 - 20); c.line_to(575, 590 - 20); c.stroke()
            lp_ = pr(t, wt("spin", "lift") - 0.2, 0.4)
            pill(c, "BACKSPIN + DIMPLES = LIFT", 540, 470, 30, "#052E2B", GREEN, a=fl_a * ease(lp_), sc=back(lp_), pad=22, outline=GREEN)
            la = pr(t, wt("spin", "longer") - 0.3, 0.4)
            text(c, "STAYS UP LONGER", 540, 1200, 34, GREEN, "black", a=fl_a * ease(la), stroke=6)

    if air_a > 0:
        if t < S("smooth"):
            flow(c, air_a, t, 95, 125, show_pressure=ease(pr(t, wt("drag", "pulls") - 0.3, 0.4)))
            pl = pr(t, wt("drag", "peels") - 0.2, 0.4) * (1 - ease(pr(t, wt("drag", "low") - 0.3, 0.3)))
            pill(c, "AIR PEELS OFF THE BACK", 540, 470, 30, DARK, AIR, a=air_a * ease(pl), sc=back(pl), pad=22, outline=AIR)
            wk = pr(t, wt("drag", "low") - 0.2, 0.4)
            pill(c, "THE WAKE = DRAG", 540, 470, 32, "#450A0A", WAKE, a=air_a * ease(wk), sc=back(wk), pad=22, outline=WAKE)
        elif t < S("dimples"):
            g = ease(pr(t, wt("smooth", "early") - 0.3, 0.6))
            flow(c, air_a, t, lerp(95, 80, g), lerp(125, 190, g))
            sm = pr(t, wt("smooth", "smooth") - 0.2, 0.4)
            pill(c, "NO DIMPLES", 540, 470, 32, DARK, MUTED, a=air_a * ease(sm) * (1 - ease(pr(t, wt("smooth", "huge") - 0.3, 0.3))), sc=back(sm), pad=22, outline=MUTED)
            hg = pr(t, wt("smooth", "huge") - 0.2, 0.4)
            pill(c, "EARLY SEPARATION · HUGE WAKE", 540, 470, 28, "#450A0A", WAKE, a=air_a * ease(hg), sc=back(hg), pad=22, outline=WAKE)
        else:
            d = ease(pr(t, S("dimples") - 0.1, 0.5))
            tb = ease(pr(t, wt("dimples", "turbulent") - 0.3, 0.5))
            lv = ease(pr(t, wt("wake", "leaves") - 0.4, 0.8))
            flow(c, air_a, t, lerp(80, 118, lv), lerp(190, 70, lv), turb=tb, ball_dimples=d)
            dp = pr(t, S("dimples") - 0.1, 0.4) * (1 - ease(pr(t, wt("dimples", "turbulent") - 0.3, 0.3)))
            pill(c, "ADD DIMPLES", 540, 470, 32, DARK, WHITE, a=air_a * ease(dp), sc=back(dp), pad=22, outline=MUTED)
            tl = pr(t, wt("dimples", "turbulent") - 0.2, 0.4) * (1 - ease(pr(t, wt("dimples", "clings") - 0.3, 0.3)))
            pill(c, "THIN TURBULENT LAYER", 540, 470, 32, DARK, CYAN, a=air_a * ease(tl), sc=back(tl), pad=22, outline=CYAN)
            cl_ = pr(t, wt("dimples", "clings") - 0.2, 0.4) * (1 - ease(pr(t, S("wake") - 0.1, 0.3)))
            pill(c, "AIR CLINGS LONGER", 540, 470, 32, DARK, CYAN, a=air_a * ease(cl_), sc=back(cl_), pad=22, outline=CYAN)
            sh = pr(t, wt("wake", "shrinks") - 0.3, 0.4) * (1 - ease(pr(t, wt("wake", "drag") - 0.3, 0.3)))
            pill(c, "SMALLER WAKE", 540, 470, 32, "#052E2B", GREEN, a=air_a * ease(sh), sc=back(sh), pad=22, outline=GREEN)
            dd = pr(t, wt("wake", "drag") - 0.2, 0.4)
            pill(c, "LESS DRAG", 540, 470, 34, "#052E2B", GREEN, a=air_a * ease(dd), sc=back(dd), pad=24, outline=GREEN)

    if his_a > 0:
        n = ease(pr(t, wt("history", "old") - 0.4, 0.4))
        ball(c, 320, 860, 130, his_a * n, dimples=0.0, scuff=1.0)
        text(c, "OLD + SCUFFED", 320, 1060, 30, AMBER, "black", a=his_a * n, stroke=6)
        s2 = ease(pr(t, wt("history", "new") - 0.4, 0.4))
        ball(c, 760, 860, 130, his_a * s2, dimples=0.0)
        text(c, "NEW + SMOOTH", 760, 1060, 30, MUTED, "black", a=his_a * s2, stroke=6)
        ff = pr(t, wt("history", "farther") - 0.3, 0.4)
        pill(c, "SCUFFED FLEW FARTHER", 540, 1200, 30, DARK, AMBER, a=his_a * ease(ff), sc=back(ff), pad=22, outline=AMBER)
        ac = pr(t, wt("history", "accident") - 0.3, 0.4)
        pill(c, "DISCOVERED BY ACCIDENT", 540, 470, 32, DARK, YEL, a=his_a * ease(ac), sc=back(ac), pad=22, outline=YEL)

    for lid, s, col in (("drag", "THE ENEMY", WAKE), ("smooth", "SMOOTH BALL", MUTED), ("dimples", "THE DIMPLES", CYAN),
                        ("wake", "THE PAYOFF", GREEN), ("spin", "THE BONUS", GREEN), ("history", "THE ORIGIN", YEL)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "smooth") - 0.6, "pop"), (wt("hook", "twice") - 0.6, "rise"), (wt("hook", "far") - 0.2, "success"),
            (wt("drag", "peels") - 0.2, "blip"), (wt("drag", "low") - 0.2, "low"), (wt("drag", "pulls") - 0.3, "warn"),
            (wt("smooth", "huge") - 0.2, "low"), (S("dimples") - 0.1, "pop"), (wt("dimples", "turbulent") - 0.2, "ping"),
            (wt("wake", "shrinks") - 0.3, "resolve"), (wt("spin", "lift") - 0.2, "rise"),
            (wt("history", "accident") - 0.3, "tick"), (wt("history", "farther") - 0.3, "ok")]
