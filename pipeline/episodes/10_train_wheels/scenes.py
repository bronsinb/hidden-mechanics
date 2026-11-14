"""Episode 10: How trains turn without steering (conical wheels)."""
from hm.core import *
from hm.props import *

STEEL = "#94A3B8"
WHEEL = "#64748B"
DARK = "#0F172A"

# ---------- front view: wheelset on two rails ----------
FCX, FCY = 540, 860          # axle centre
RAIL_X = (300, 780)          # rail centres (fixed)
W_IN, W_OUT = 70, 210        # wheel tread spans from |x-540| = 170..300 -> local offsets
R_MAX, TAPER = 170, 0.45     # radius at the flange side, slope (exaggerated)


def wheel_r(local, k):
    """Radius at distance `local` from the wheel's inner face (0 = flange side)."""
    return R_MAX - TAPER * k * local


def front_view(c, a, t, k, dx, spin=True, contacts=0.0, radii=0.0, lock=0.0):
    if a <= 0: return
    # sleepers + rails
    for xr in RAIL_X:
        pass
    rr(c, 150, 1060, 780, 46, 10); fill(c, "#57534E", a); c.fill()
    inner_x = (FCX - 170 + dx, FCX + 170 + dx)   # inner faces of the left/right wheels
    contact_y = []
    for side, xr in zip((-1, 1), RAIL_X):
        xi = inner_x[0 if side < 0 else 1]
        local = (xr - xi) * side                  # distance from flange side to the rail
        ry = FCY + wheel_r(local, k)
        contact_y.append(ry)
    # axle
    c.set_line_width(26); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, STEEL, a)
    c.move_to(FCX - 330 + dx, FCY); c.line_to(FCX + 330 + dx, FCY); c.stroke()
    for side in (-1, 1):
        xi = inner_x[0 if side < 0 else 1]
        xo = xi + side * 130
        r_in, r_out = wheel_r(0, k), wheel_r(130, k)
        # flange lip on the inner side
        c.move_to(xi, FCY - r_in - 26); c.line_to(xi - side * 18, FCY - r_in - 26)
        c.line_to(xi - side * 18, FCY + r_in + 26); c.line_to(xi, FCY + r_in + 26); c.close_path()
        fill(c, "#475569", a); c.fill()
        # cone body
        c.move_to(xi, FCY - r_in); c.line_to(xo, FCY - r_out); c.line_to(xo, FCY + r_out); c.line_to(xi, FCY + r_in); c.close_path()
        g = cairo.LinearGradient(0, FCY - R_MAX, 0, FCY + R_MAX)
        g.add_color_stop_rgba(0, *hexc("#94A3B8")[:3], a); g.add_color_stop_rgba(0.5, *hexc("#CBD5E1")[:3], a)
        g.add_color_stop_rgba(1, *hexc("#475569")[:3], a)
        c.set_source(g); c.fill()
        # spin stripes (moving bands across the face)
        if spin:
            c.save()
            c.move_to(xi, FCY - r_in); c.line_to(xo, FCY - r_out); c.line_to(xo, FCY + r_out); c.line_to(xi, FCY + r_in); c.close_path(); c.clip()
            for j in range(4):
                ph = ((t * 0.9 + j / 4) % 1)
                yy = FCY - R_MAX + 2 * R_MAX * ph
                c.rectangle(min(xi, xo), yy - 8, 130, 16); fill(c, DARK, 0.28 * a); c.fill()
            c.restore()
        c.arc(lerp(xi, xo, 0.5), FCY, 16, 0, 2 * math.pi); fill(c, "#334155", a); c.fill()
    # rails, under each wheel's contact point
    for i, xr in enumerate(RAIL_X):
        ry = contact_y[i]
        rr(c, xr - 26, ry, 52, 26, 8); fill(c, "#CBD5E1", a); c.fill()
        c.rectangle(xr - 9, ry + 24, 18, 1060 - ry - 24); fill(c, "#94A3B8", a); c.fill()
        rr(c, xr - 40, 1046, 80, 16, 4); fill(c, "#94A3B8", a); c.fill()
        if contacts > 0:
            glow(c, xr, ry, 34, YEL, 0.8 * a * contacts)
            c.arc(xr, ry, 9, 0, 2 * math.pi); fill(c, YEL, a * contacts); c.fill()
    if radii > 0:
        for i, xr in enumerate(RAIL_X):
            col = CYAN if i == 0 else AMBER
            ry = contact_y[i]
            c.set_line_width(7); fill(c, col, a * radii)
            c.move_to(xr, FCY); c.line_to(xr, lerp(FCY, ry, eout(radii))); c.stroke()
            c.arc(xr, FCY, 9, 0, 2 * math.pi); c.fill()
    if lock > 0:
        c.save(); c.translate(FCX + dx, FCY - 4); safe_scale(c, back(lock), back(lock))
        rr(c, -46, -46, 92, 92, 22); fill(c, DARK, a * ease(lock)); c.fill()
        c.restore()
        lock_icon(c, FCX + dx, FCY - 4, 0.9 * back(lock), False, YEL, a * ease(lock))
    return contact_y


# ---------- top view: curved track ----------
TCX, TCY, R_IN, R_OUT = 540, 1560, 430, 610
A0, A1 = math.radians(-152), math.radians(-28)


def arc_path(c, r, a0, a1):
    c.new_path(); c.arc(TCX, TCY, r, a0, a1)


def top_track(c, a):
    if a <= 0: return
    for k in range(26):
        ang = lerp(A0, A1, k / 25)
        c.set_line_width(16); fill(c, "#57534E", a)
        c.move_to(TCX + (R_IN - 40) * math.cos(ang), TCY + (R_IN - 40) * math.sin(ang))
        c.line_to(TCX + (R_OUT + 40) * math.cos(ang), TCY + (R_OUT + 40) * math.sin(ang)); c.stroke()
    for r in (R_IN, R_OUT):
        c.set_line_width(12); fill(c, "#CBD5E1", a); arc_path(c, r, A0, A1); c.stroke()


def top_wheelset(c, ang, a, col=STEEL):
    if a <= 0: return
    ca, sa = math.cos(ang), math.sin(ang)
    p = lambda r: (TCX + r * ca, TCY + r * sa)
    c.set_line_width(14); fill(c, col, a); c.move_to(*p(R_IN - 30)); c.line_to(*p(R_OUT + 30)); c.stroke()
    for r in (R_IN, R_OUT):
        x, y = p(r)
        c.save(); c.translate(x, y); c.rotate(ang + math.pi / 2)
        rr(c, -50, -20, 100, 40, 10); fill(c, "#E2E8F0", a); c.fill()
        c.restore()


def straight_track(c, a, y0=560, y1=1280):
    if a <= 0: return
    for k in range(13):
        y = lerp(y0, y1, k / 12)
        rr(c, 300, y - 9, 480, 18, 4); fill(c, "#57534E", a); c.fill()
    for x in (380, 700):
        c.rectangle(x - 7, y0 - 20, 14, y1 - y0 + 40); fill(c, "#CBD5E1", a); c.fill()


def rolling(c, a, t, t0):
    """A big and a small wheel roll exactly one turn each: big one goes farther."""
    if a <= 0: return
    for i, (r, col, y, lab) in enumerate(((95, AMBER, 760, "WIDE PART"), (60, CYAN, 1110, "NARROW PART"))):
        p = eio(pr(t, t0 + 0.2, 1.8))
        x0 = 150
        x = x0 + 2 * math.pi * r * p
        c.set_line_width(6); fill(c, "#475569", a); c.move_to(110, y + r); c.line_to(980, y + r); c.stroke()
        c.set_line_width(10); fill(c, col, a); c.move_to(x0, y + r); c.line_to(x, y + r); c.stroke()
        glow(c, x, y, r * 1.3, col, 0.3 * a)
        c.arc(x, y, r, 0, 2 * math.pi); fill(c, "#334155", a); c.fill_preserve(); c.set_line_width(8); fill(c, col, a); c.stroke()
        ang = -2 * math.pi * p
        c.move_to(x, y); c.line_to(x + r * math.sin(-ang), y + r * math.cos(-ang)); c.set_line_width(6); fill(c, WHITE, a); c.stroke()
        text(c, lab, x0 - 40, y - r - 26, 26, col, "black", align="left", a=a)
        if p >= 1:
            text(c, "1 TURN", x, y + r + 50, 28, WHITE, "black", a=a * ease(pr(t, t0 + 2.0, 0.3)))


def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "A TRAIN HAS NO STEERING.", "SO HOW DOES IT TURN?", S("problem"))

    # which view is on screen
    front_a = A * (ease(pr(t, 0.05, 0.5)) * (1 - ease(pr(t, wt("hook", "how") - 0.2, 0.4)))
                   + ease(pr(t, S("cone") - 0.2, 0.5)) * (1 - ease(pr(t, S("distance") - 0.1, 0.4)))
                   + ease(pr(t, S("center") - 0.2, 0.5)) * (1 - ease(pr(t, S("hunting") - 0.1, 0.4))))
    top_a = A * (ease(pr(t, wt("hook", "how") - 0.1, 0.5)) * (1 - ease(pr(t, S("cone") - 0.3, 0.4)))
                 + ease(pr(t, wt("distance", "steers") - 0.5, 0.5)) * (1 - ease(pr(t, S("center") - 0.3, 0.4))))
    roll_a = A * ease(pr(t, S("distance") + 0.1, 0.4)) * (1 - ease(pr(t, wt("distance", "steers") - 0.6, 0.4)))
    hunt_a = A * ease(pr(t, S("hunting") - 0.1, 0.5))

    # ---- front view ----
    if front_a > 0:
        k = ease(pr(t, wt("cone", "cones") - 0.2, 0.7))
        dx = 0.0
        if S("shift") - 0.5 < t < S("distance") + 0.5:
            dx = 55 * eio(pr(t, wt("shift", "outward") - 0.3, 0.7))
        if t > S("center") - 0.5:
            u = max(0.0, t - wt("center", "nudging") + 0.4)
            dx = -60 * math.exp(-0.9 * u) * math.cos(3.2 * u) if t > wt("center", "nudging") - 0.4 else -60 * ease(pr(t, S("center") - 0.3, 0.6))
        contacts = ease(pr(t, wt("shift", "rolls") - 0.2, 0.4)) * (1 - ease(pr(t, S("distance"), 0.3))) if t < S("center") else 0
        radii = ease(pr(t, wt("shift", "wide") - 0.2, 0.5)) * (1 - ease(pr(t, S("distance"), 0.3))) if t < S("center") else 0
        lock = ease(pr(t, wt("hook", "locked") - 0.2, 0.4)) if t < S("problem") else 0
        front_view(c, front_a, t, k, dx, contacts=contacts, radii=radii, lock=lock)
        if t < S("problem"):
            sp = pr(t, wt("hook", "together") - 0.3, 0.4)
            pill(c, "ONE AXLE · SAME SPIN", 540, 470, 30, DARK, YEL, a=front_a * ease(sp), sc=back(sp), pad=22, outline=YEL)
        elif t < S("shift"):
            fl = pr(t, wt("cone", "flat") - 0.2, 0.4) * (1 - ease(pr(t, wt("cone", "cones") - 0.2, 0.3)))
            pill(c, "FLAT?", 540, 470, 34, "#450A0A", RED, a=front_a * ease(fl), sc=back(fl), pad=24, outline=RED)
            wd = pr(t, wt("cone", "wider") - 0.2, 0.4)
            pill(c, "CONES · WIDER ON THE INSIDE", 540, 470, 30, DARK, CYAN, a=front_a * ease(wd), sc=back(wd), pad=22, outline=CYAN)
            text(c, "taper exaggerated", 540, 1180, 24, MUTED, "bold", a=front_a * ease(wd))
        elif t < S("center"):
            ou = pr(t, wt("shift", "outward") - 0.2, 0.4)
            pill(c, "CURVE → WHEELS SLIDE OUTWARD", 540, 470, 28, DARK, WHITE, a=front_a * ease(ou), sc=back(ou), pad=22, outline=MUTED)
            # outward arrow
            aa = front_a * ease(ou) * (1 - ease(pr(t, wt("shift", "wide") - 0.3, 0.3)))
            c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, WHITE, aa)
            c.move_to(420, 600); c.line_to(660, 600); c.stroke(); c.move_to(630, 575); c.line_to(662, 600); c.line_to(630, 625); c.stroke()
            w = pr(t, wt("shift", "wide") - 0.2, 0.4)
            pill(c, "OUTER: BIG", 780, 600, 28, DARK, AMBER, a=front_a * ease(w), sc=back(w), pad=20, outline=AMBER)
            n = pr(t, wt("shift", "narrow") - 0.2, 0.4)
            pill(c, "INNER: SMALL", 300, 600, 28, DARK, CYAN, a=front_a * ease(n), sc=back(n), pad=20, outline=CYAN)
        else:
            ce = pr(t, wt("center", "nudging") - 0.3, 0.4)
            pill(c, "SELF-CENTERING", 540, 470, 30, "#052E2B", GREEN, a=front_a * ease(ce), sc=back(ce), pad=22, outline=GREEN)
            md = pr(t, wt("center", "middle") - 0.1, 0.4)
            c.set_line_width(4); c.set_dash([14, 10]); fill(c, GREEN, 0.7 * front_a * ease(ce))
            c.move_to(540, 640); c.line_to(540, 1110); c.stroke(); c.set_dash([])
            check(c, 540, 1200, 50, GREEN, a=front_a * ease(md), p=ease(md))

    # ---- top view ----
    if top_a > 0:
        top_track(c, top_a)
        if t < S("cone"):
            ln = eio(pr(t, wt("problem", "outer") - 0.3, 1.2))
            if ln > 0:
                for r, col in ((R_OUT, AMBER), (R_IN, CYAN)):
                    c.set_line_width(16); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, col, top_a)
                    arc_path(c, r, A0, lerp(A0, A1, ln)); c.stroke()
                o = pr(t, wt("problem", "longer") - 0.2, 0.4)
                pill(c, "OUTER RAIL: LONGER", 540, 470, 30, DARK, AMBER, a=top_a * ease(o) * (1 - ease(pr(t, wt("problem", "skid") - 0.3, 0.2))), sc=back(o), pad=22, outline=AMBER)
                text(c, "INNER: SHORTER", 540, 1250, 28, CYAN, "black", a=top_a * ease(o))
            ang = lerp(A0 + 0.15, -math.pi / 2, eio(pr(t, wt("hook", "how") - 0.1, 1.2)))
            top_wheelset(c, ang, top_a)
            q = pr(t, wt("hook", "corner") - 0.2, 0.4) * (1 - ease(pr(t, S("problem"), 0.3)))
            text(c, "?", 540, 830, 150, YEL, "black", a=top_a * ease(q), stroke=10)
            sk = pr(t, wt("problem", "skid") - 0.2, 0.4)
            if sk > 0:
                x, y = TCX + R_IN * math.cos(-math.pi / 2), TCY + R_IN * math.sin(-math.pi / 2)
                for j in range(4):
                    c.set_line_width(6); fill(c, RED, top_a * ease(sk))
                    c.move_to(x - 70 + j * 12, y + 30 + j * 4); c.line_to(x - 140 + j * 12, y + 40 + j * 4); c.stroke()
                pill(c, "FLAT WHEELS WOULD SKID", 540, 470, 28, "#450A0A", RED, a=top_a * ease(sk), sc=back(sk), pad=20, outline=RED)
        else:
            u = (t - wt("distance", "steers") + 0.5) * 0.35
            for j in range(3):
                ang = A0 + 0.12 + ((u + j * 0.33) % 1) * (A1 - A0 - 0.24)
                top_wheelset(c, ang, top_a, GREEN)
            st = pr(t, wt("distance", "steers") - 0.2, 0.4)
            pill(c, "IT STEERS ITSELF", 540, 470, 32, "#052E2B", GREEN, a=top_a * ease(st), sc=back(st), pad=22, outline=GREEN)

    # ---- rolling comparison ----
    if roll_a > 0:
        rolling(c, roll_a, t, S("distance"))
        mo = pr(t, wt("distance", "farther") - 0.2, 0.4)
        pill(c, "SAME TURN · MORE DISTANCE", 540, 470, 30, DARK, AMBER, a=roll_a * ease(mo), sc=back(mo), pad=22, outline=AMBER)

    # ---- hunting ----
    if hunt_a > 0:
        straight_track(c, hunt_a)
        grow = ease(pr(t, wt("hunting", "overshoot") - 0.3, 2.5))
        amp = lambda y: (14 + 110 * grow) * (1 - (y - 560) / 720) * 0.4 + (14 + 110 * grow) * 0.6
        # snake trail
        c.set_line_width(8); c.set_line_cap(cairo.LINE_CAP_ROUND)
        pts = []
        for i in range(80):
            y = 1280 - i * 9
            x = 540 + amp(y) * math.sin(i * 0.19 - t * 5)
            pts.append((x, y))
        fill(c, RED if grow > 0.5 else AMBER, 0.6 * hunt_a)
        c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.stroke()
        hx = 540 + amp(1000) * math.sin(-t * 5 + 280 * 0.19 / 9 * 0 )
        hx = 540 + amp(1000) * math.sin(((1280 - 1000) / 9) * 0.19 - t * 5)
        c.save(); c.translate(hx, 1000); c.rotate(0.25 * grow * math.cos(((1280 - 1000) / 9) * 0.19 - t * 5))
        c.set_line_width(14); fill(c, STEEL, hunt_a); c.move_to(-200, 0); c.line_to(200, 0); c.stroke()
        for sx in (-160, 160):
            rr(c, sx - 20, -50, 40, 100, 10); fill(c, "#E2E8F0", hunt_a); c.fill()
        c.restore()
        if grow > 0.6 and abs(hx - 540) > 0.85 * amp(1000):
            glow(c, 380 if hx < 540 else 700, 1000, 70, RED, 0.8 * hunt_a)
        hp = pr(t, wt("hunting", "hunting") - 0.2, 0.4)
        pill(c, "HUNTING OSCILLATION", 540, 470, 32, "#450A0A", RED, a=hunt_a * ease(hp), sc=back(hp), pad=22, outline=RED)
        hs = pr(t, wt("hunting", "high") - 0.2, 0.4) * (1 - ease(pr(t, wt("hunting", "hunting") - 0.2, 0.3)))
        pill(c, "HIGH SPEED", 540, 470, 32, DARK, AMBER, a=hunt_a * ease(hs), sc=back(hs), pad=22, outline=AMBER)

    for lid, s, col in (("problem", "THE PROBLEM", RED), ("cone", "THE TRICK", CYAN), ("shift", "IN A CURVE", AMBER),
                        ("distance", "THE STEERING", GREEN), ("center", "ON THE STRAIGHT", GREEN), ("hunting", "THE CATCH", RED)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "locked") - 0.2, "tick"), (wt("hook", "corner") - 0.2, "blip"),
            (wt("problem", "outer") - 0.3, "rise"), (wt("problem", "skid") - 0.2, "warn"),
            (wt("cone", "flat") - 0.2, "low"), (wt("cone", "cones") - 0.2, "pop"),
            (wt("shift", "outward") - 0.3, "blip"), (wt("shift", "wide") - 0.2, "ping"), (wt("shift", "narrow") - 0.2, "ping"),
            (S("distance") + 0.3, "rise"), (wt("distance", "steers") - 0.2, "success"),
            (wt("center", "nudging") - 0.3, "blip"), (wt("center", "middle") - 0.1, "ok"),
            (wt("hunting", "overshoot") - 0.3, "rumble"), (wt("hunting", "hunting") - 0.2, "warn")]
