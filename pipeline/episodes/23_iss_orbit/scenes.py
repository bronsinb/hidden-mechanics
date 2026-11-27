"""Episode 23: Why doesn't the Space Station fall? (orbit = falling and missing)."""
from hm.core import *
from hm.props import *

DARK = "#0F172A"
OCEAN = "#1D4ED8"
LAND = "#16A34A"
ECX, ECY, ER = 540, 960, 290          # Earth on screen
R0 = ER + 70                          # launch radius (top of the tower)
GM = (300.0 ** 2) * R0                # so a circular orbit at R0 has speed 300 px/s


def sim_path(v_frac, tmax=12.0, dt=1 / 240):
    """Launch sideways from the top of the tower at v_frac * circular speed."""
    x, y = 0.0, -R0
    vx, vy = 300.0 * v_frac, 0.0
    pts = [(x, y)]
    t = 0.0
    ang0 = math.atan2(y, x)
    swept = 0.0
    while t < tmax:
        r = math.hypot(x, y)
        ax, ay = -GM * x / r ** 3, -GM * y / r ** 3
        vx += ax * dt; vy += ay * dt
        x += vx * dt; y += vy * dt
        t += dt
        pts.append((x, y))
        if math.hypot(x, y) <= ER:
            break
        a = math.atan2(y, x)
        swept = a - ang0
        if len(pts) > 200 and abs(math.hypot(x, y) - R0) < 3 and abs(x) < 6 and y < 0:
            break
    return pts


PATHS = {f: sim_path(f) for f in (0.42, 0.62, 0.8, 1.0)}


def earth(c, a, t, scale=1.0, cx=ECX, cy=ECY):
    if a <= 0: return
    r = ER * scale
    glow(c, cx, cy, r * 1.25, "#60A5FA", 0.35 * a)
    c.arc(cx, cy, r + 10 * scale, 0, 2 * math.pi); c.set_source_rgba(0.38, 0.65, 0.98, 0.25 * a); c.fill()
    c.arc(cx, cy, r, 0, 2 * math.pi); fill(c, OCEAN, a); c.fill()
    c.save(); c.arc(cx, cy, r, 0, 2 * math.pi); c.clip()
    rot = t * 0.08
    for k, (ang, dist, sz) in enumerate(((0.3, 0.3, 0.35), (2.1, 0.55, 0.3), (3.6, 0.2, 0.4), (4.9, 0.6, 0.25), (1.2, 0.75, 0.22))):
        x = cx + r * dist * math.cos(ang + rot); y = cy + r * dist * math.sin(ang + rot) * 0.9
        c.save(); c.translate(x, y); c.rotate(ang); c.scale(1, 0.6)
        c.arc(0, 0, r * sz, 0, 2 * math.pi); c.restore(); fill(c, LAND, a); c.fill()
    c.restore()


def iss(c, x, y, s, a, ang=0.0, thrust=0.0):
    if a <= 0: return
    c.save(); c.translate(x, y); c.rotate(ang); safe_scale(c, s, s)
    c.set_line_width(8); fill(c, "#CBD5E1", a); c.move_to(-90, 0); c.line_to(90, 0); c.stroke()
    for sx in (-80, -45, 45, 80):
        rr(c, sx - 14, -60, 28, 50, 3); fill(c, "#B45309", a); c.fill()
        rr(c, sx - 14, 10, 28, 50, 3); c.fill()
    rr(c, -30, -14, 60, 28, 10); fill(c, "#F8FAFC", a); c.fill()
    rr(c, -10, -22, 20, 44, 8); fill(c, "#E2E8F0", a); c.fill()
    if thrust > 0:
        fl = 0.8 + 0.2 * math.sin(time_noise(x) * 20)
        c.move_to(-30, -8); c.line_to(-30 - 70 * thrust * fl, 0); c.line_to(-30, 8); c.close_path(); fill(c, "#FB923C", a * thrust); c.fill()
    c.restore()


def time_noise(v):
    return (v * 12.9898) % 1


def arrow(c, x0, y0, x1, y1, col, a, w=10):
    if a <= 0: return
    c.set_line_width(w); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, col, a)
    c.move_to(x0, y0); c.line_to(x1, y1); c.stroke()
    ang = math.atan2(y1 - y0, x1 - x0)
    c.move_to(x1, y1); c.line_to(x1 - 26 * math.cos(ang - 0.45), y1 - 26 * math.sin(ang - 0.45))
    c.line_to(x1 - 26 * math.cos(ang + 0.45), y1 - 26 * math.sin(ang + 0.45)); c.close_path(); c.fill()


def draw_path(c, pts, p, col, a, ball=True):
    if a <= 0 or p <= 0: return
    m = max(2, int(len(pts) * p))
    c.set_line_width(5); c.set_dash([14, 10]); fill(c, col, a)
    c.move_to(ECX + pts[0][0], ECY + pts[0][1])
    for x, y in pts[1:m:4]: c.line_to(ECX + x, ECY + y)
    c.stroke(); c.set_dash([])
    if ball:
        x, y = pts[m - 1]
        glow(c, ECX + x, ECY + y, 26, col, 0.8 * a)
        c.arc(ECX + x, ECY + y, 11, 0, 2 * math.pi); fill(c, WHITE, a); c.fill()


def tower(c, a):
    if a <= 0: return
    c.move_to(ECX - 16, ECY - ER + 4); c.line_to(ECX - 8, ECY - R0); c.line_to(ECX + 8, ECY - R0); c.line_to(ECX + 16, ECY - ER + 4); c.close_path()
    fill(c, "#94A3B8", a); c.fill()


def astronaut(c, x, y, s, a, t):
    c.save(); c.translate(x, y + 6 * math.sin(t * 1.4)); c.rotate(0.3 * math.sin(t * 0.7)); safe_scale(c, s, s)
    rr(c, -30, -40, 60, 80, 22); fill(c, "#F8FAFC", a); c.fill()
    c.arc(0, -62, 30, 0, 2 * math.pi); c.fill()
    c.arc(0, -62, 20, 0, 2 * math.pi); fill(c, "#1E3A8A", a); c.fill()
    for sx in (-1, 1):
        rr(c, sx * 34 - 10, -30, 20, 56, 10); fill(c, "#F8FAFC", a); c.fill()
        rr(c, sx * 14 - 10, 36, 20, 50, 10); c.fill()
    c.restore()


def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "WHY DOESN'T THE", "SPACE STATION FALL?", S("falling"))

    wide_a = A * (ease(pr(t, 0.05, 0.5)) * (1 - ease(pr(t, S("throw") - 0.2, 0.4))))
    nw_a = A * ease(pr(t, S("throw") - 0.1, 0.5)) * (1 - ease(pr(t, S("float") - 0.2, 0.4)))
    fl_a = A * ease(pr(t, S("float") - 0.1, 0.5)) * (1 - ease(pr(t, S("drag") - 0.2, 0.4)))
    dr_a = A * ease(pr(t, S("drag") - 0.1, 0.5))

    if wide_a > 0:
        # big Earth limb with the station above
        earth(c, wide_a, t, scale=2.6, cx=540, cy=1900)
        ix, iy = 540 + 40 * math.sin(t * 0.4), 880
        iss(c, ix, iy, 1.3, wide_a)
        c.set_line_width(4); c.set_dash([12, 10]); fill(c, WHITE, 0.7 * wide_a * ease(pr(t, wt("hook", "250") - 0.3, 0.4)))
        c.move_to(860, 900); c.line_to(860, 1150); c.stroke(); c.set_dash([])
        text(c, "~250 MILES", 880, 1040, 30, WHITE, "black", align="left", a=wide_a * ease(pr(t, wt("hook", "250") - 0.3, 0.4)), stroke=6)
        g = pr(t, wt("hook", "90") - 0.3, 0.4)
        pill(c, "GRAVITY UP THERE: ~90%", 540, 470, 30, DARK, YEL, a=wide_a * ease(g) * (1 - ease(pr(t, S("falling") - 0.2, 0.3))), sc=back(g), pad=22, outline=YEL)
        fa = ease(pr(t, wt("falling", "falling") - 0.4, 0.4))
        arrow(c, ix, iy + 90, ix, iy + 90 + 160 * fa, RED, wide_a * fa, w=14)
        fp = pr(t, wt("falling", "does") - 0.2, 0.4)
        pill(c, "IT IS FALLING. ALL THE TIME.", 540, 470, 30, "#450A0A", RED, a=wide_a * ease(fp), sc=back(fp), pad=22, outline=RED)

    if nw_a > 0:
        earth(c, nw_a, t)
        tower(c, nw_a)
        if t < S("orbit"):
            p1 = eio(pr(t, wt("throw", "sideways") - 0.3, 1.1))
            draw_path(c, PATHS[0.42], p1, AMBER, nw_a)
            p2 = eio(pr(t, wt("throw", "faster") - 0.4, 1.3))
            draw_path(c, PATHS[0.62], p2, YEL, nw_a)
            p3 = eio(pr(t, wt("throw", "farther") - 0.4, 1.0))
            draw_path(c, PATHS[0.8], p3, "#FDE68A", nw_a)
            sw = pr(t, wt("throw", "sideways") - 0.2, 0.4) * (1 - ease(pr(t, wt("throw", "faster") - 0.3, 0.3)))
            pill(c, "THROW IT SIDEWAYS", 540, 470, 30, DARK, AMBER, a=nw_a * ease(sw), sc=back(sw), pad=22, outline=AMBER)
            ff = pr(t, wt("throw", "faster") - 0.2, 0.4)
            pill(c, "FASTER = LANDS FARTHER", 540, 470, 30, DARK, YEL, a=nw_a * ease(ff), sc=back(ff), pad=22, outline=YEL)
        else:
            for f, col in ((0.42, AMBER), (0.62, YEL), (0.8, "#FDE68A")):
                draw_path(c, PATHS[f], 1.0, col, nw_a * 0.35, ball=False)
            po = PATHS[1.0]
            n = len(po)
            u = ((t - (wt("orbit", "17500") - 0.4)) * 0.16) % 1 if t > wt("orbit", "17500") - 0.4 else 0
            m = max(2, int(n * (u if t < wt("orbit", "17500") + 5.8 else 1)))
            draw_path(c, po, 1.0 if t > wt("orbit", "17500") + 5.8 else m / n, CYAN, nw_a, ball=False)
            x, y = po[min(n - 1, m - 1)]
            sx, sy = ECX + x, ECY + y
            ang = math.atan2(y, x) + math.pi / 2
            iss(c, sx, sy, 0.45, nw_a, ang=ang)
            vv = ease(pr(t, wt("orbit", "ground") - 0.3, 0.4))
            r = math.hypot(x, y)
            arrow(c, sx, sy, sx + 120 * (-y / r), sy + 120 * (x / r), GREEN, nw_a * vv, w=8)
            arrow(c, sx, sy, sx - 90 * x / r, sy - 90 * y / r, RED, nw_a * vv, w=8)
            sp = pr(t, wt("orbit", "17500") - 0.3, 0.4) * (1 - ease(pr(t, wt("orbit", "ground") - 0.3, 0.3)))
            pill(c, "~17,500 MPH SIDEWAYS", 540, 470, 32, DARK, CYAN, a=nw_a * ease(sp), sc=back(sp), pad=22, outline=CYAN)
            ms = pr(t, wt("orbit", "ground") - 0.2, 0.4)
            pill(c, "FALLS · BUT KEEPS MISSING EARTH", 540, 470, 28, "#052E2B", GREEN, a=nw_a * ease(ms), sc=back(ms), pad=22, outline=GREEN)

    if fl_a > 0:
        # station module with a floating astronaut; both fall together
        rr(c, 170, 700, 740, 460, 60); fill(c, "#E2E8F0", fl_a); c.fill()
        rr(c, 200, 730, 680, 400, 46); fill(c, "#1E293B", fl_a); c.fill()
        for k in range(4):
            c.arc(270 + k * 180, 760, 16, 0, 2 * math.pi); fill(c, "#334155", fl_a); c.fill()
        astronaut(c, 540, 930, 1.3, fl_a, t)
        fa = ease(pr(t, wt("float", "falling") - 0.4, 0.4))
        arrow(c, 970, 760, 970, 1000, RED, fl_a * fa, w=14)
        arrow(c, 110, 760, 110, 1000, RED, fl_a * fa, w=14)
        text(c, "STATION", 970, 1200, 24, RED, "black", a=fl_a * fa, stroke=6)
        text(c, "ASTRONAUT", 540, 1200, 24, RED, "black", a=fl_a * fa, stroke=6)
        fp = pr(t, wt("float", "float") - 0.3, 0.4) * (1 - ease(pr(t, wt("float", "beyond") - 0.3, 0.3)))
        pill(c, "WHY ASTRONAUTS FLOAT", 540, 470, 30, DARK, WHITE, a=fl_a * ease(fp), sc=back(fp), pad=22, outline=MUTED)
        ng = pr(t, wt("float", "beyond") - 0.2, 0.4) * (1 - ease(pr(t, wt("float", "falling") - 0.4, 0.3)))
        pill(c, "NOT BEYOND GRAVITY", 540, 470, 30, "#450A0A", RED, a=fl_a * ease(ng), sc=back(ng), pad=22, outline=RED)
        tg = pr(t, wt("float", "falling") - 0.3, 0.4)
        pill(c, "FREE FALL · TOGETHER", 540, 470, 30, DARK, CYAN, a=fl_a * ease(tg), sc=back(tg), pad=22, outline=CYAN)

    if dr_a > 0:
        earth(c, dr_a, t)
        sink = ease(pr(t, wt("drag", "drags") - 0.5, 1.4)) * (1 - ease(pr(t, wt("drag", "climb") - 0.4, 1.0)))
        r = R0 - 28 * sink
        c.set_line_width(4); c.set_dash([14, 10]); fill(c, CYAN, 0.6 * dr_a)
        c.new_path(); c.arc(ECX, ECY, r, 0, 2 * math.pi); c.stroke(); c.set_dash([])
        ang = -math.pi / 2 + (t - S("drag")) * 0.7
        sx, sy = ECX + r * math.cos(ang), ECY + r * math.sin(ang)
        thr = ease(pr(t, wt("drag", "fires") - 0.3, 0.3)) * (1 - ease(pr(t, wt("drag", "back") + 0.3, 0.4)))
        iss(c, sx, sy, 0.6, dr_a, ang=ang + math.pi / 2, thrust=thr)
        wa = ease(pr(t, wt("drag", "air") - 0.3, 0.4))
        for k in range(14):
            ph = (t * 1.5 + k * 0.13) % 1
            da = ang + 0.5 - 0.6 * ph
            rr_ = r + (k % 5 - 2) * 12
            c.arc(ECX + rr_ * math.cos(da), ECY + rr_ * math.sin(da), 4, 0, 2 * math.pi); fill(c, "#BAE6FD", dr_a * wa * (1 - ph)); c.fill()
        ap = pr(t, wt("drag", "whisper") - 0.2, 0.4) * (1 - ease(pr(t, wt("drag", "once") - 0.3, 0.3)))
        pill(c, "THIN AIR DRAG · SLOWLY SINKS", 540, 470, 28, DARK, "#BAE6FD", a=dr_a * ease(ap), sc=back(ap), pad=22, outline="#BAE6FD")
        mp = pr(t, wt("drag", "once") - 0.2, 0.4)
        pill(c, "REBOOST ~ ONCE A MONTH", 540, 470, 30, DARK, "#FB923C", a=dr_a * ease(mp), sc=back(mp), pad=22, outline="#FB923C")

    for lid, s, col in (("falling", "THE TWIST", RED), ("throw", "THE THOUGHT EXPERIMENT", AMBER), ("orbit", "THE ORBIT", CYAN),
                        ("float", "THE FLOAT", WHITE), ("drag", "THE UPKEEP", "#FB923C")):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "250") - 0.3, "blip"), (wt("hook", "90") - 0.3, "ping"), (wt("hook", "fall") - 0.3, "pop"),
            (wt("falling", "falling") - 0.4, "low"), (wt("throw", "sideways") - 0.3, "rise"), (wt("throw", "faster") - 0.4, "rise"),
            (wt("orbit", "17500") - 0.3, "pop"), (wt("orbit", "missing") - 0.3, "success"),
            (wt("float", "float") - 0.3, "ping"), (wt("float", "falling") - 0.4, "low"),
            (wt("drag", "drags") - 0.4, "low"), (wt("drag", "fires") - 0.3, "rumble"), (wt("drag", "climb") - 0.3, "resolve")]
