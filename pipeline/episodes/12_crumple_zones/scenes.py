"""Episode 12 (GTA 6 week #2): Why real cars are built to crumple."""
from hm.core import *
from hm.props import *

DARK = "#0F172A"
PINK = "#F472B6"
GROUND = 1130


# ---------- side-view car ----------
def side_car(c, x, a, crush=0.0, col="#3B82F6", zone_hi=0.0, cell_hi=0.0, dummy=True, belt=0.0, bag=0.0, lean=0.0, wheel_t=0.0, rear_crush=0.0):
    """Car from rear x to front; returns front x. Body length 560 when not crushed."""
    if a <= 0: return x
    rear_len = 130 * (1 - 0.45 * rear_crush)
    cab_len = 240
    front_len = 190 * (1 - 0.62 * crush)
    x0 = x
    x1 = x0 + rear_len          # rear of cabin
    x2 = x1 + cab_len           # front of cabin (windshield base)
    x3 = x2 + front_len         # front bumper
    yb = GROUND - 40            # body bottom
    # wheels
    for wx in (x0 + 80 * (1 - 0.3 * rear_crush), x2 + min(70, front_len * 0.45)):
        c.arc(wx, GROUND - 42, 42, 0, 2 * math.pi); fill(c, "#0B1220", a); c.fill()
        c.arc(wx, GROUND - 42, 18, 0, 2 * math.pi); fill(c, "#64748B", a); c.fill()
        c.save(); c.translate(wx, GROUND - 42); c.rotate(wheel_t)
        c.set_line_width(5); fill(c, "#0B1220", a); c.move_to(-16, 0); c.line_to(16, 0); c.stroke(); c.restore()
    # rear section
    def zig(xa, xb, top, n, amp):
        pts = []
        for i in range(n + 1):
            pts.append((lerp(xa, xb, i / n), top + (amp if i % 2 else 0)))
        return pts
    c.new_path()
    if rear_crush > 0:
        pts = zig(x0, x1, yb - 95, 6, -22 * rear_crush)
        c.move_to(x0, yb); [c.line_to(px, py) for px, py in pts]; c.line_to(x1, yb); c.close_path()
    else:
        c.move_to(x0, yb); c.line_to(x0, yb - 90); c.line_to(x1, yb - 100); c.line_to(x1, yb); c.close_path()
    fill(c, col, a); c.fill()
    # front section (hood)
    c.new_path()
    if crush > 0:
        pts = zig(x2, x3, yb - 95, 8, -26 * crush)
        c.move_to(x2, yb); [c.line_to(px, py) for px, py in pts]; c.line_to(x3, yb - 20); c.line_to(x3, yb); c.close_path()
    else:
        c.move_to(x2, yb); c.line_to(x2, yb - 100); c.line_to(x3 - 20, yb - 80); c.line_to(x3, yb - 55); c.line_to(x3, yb); c.close_path()
    fill(c, col, a); c.fill()
    if crush > 0:
        c.set_line_width(4); fill(c, "#1E3A8A", a)
        for i in range(1, 8):
            px = lerp(x2, x3, i / 8)
            c.move_to(px, yb - 95 + (-26 * crush if i % 2 else 0)); c.line_to(px + (8 if i % 2 else -8) * crush, yb - 6); c.stroke()
    # zone highlight
    if zone_hi > 0:
        for xa, xb in ((x2, x3), (x0, x1)):
            rr(c, xa - 4, yb - 130, xb - xa + 8, 136, 14)
            c.set_source_rgba(*hexc(AMBER)[:3], 0.28 * zone_hi * a); c.fill_preserve()
            c.set_line_width(5); c.set_dash([16, 10]); fill(c, AMBER, zone_hi * a); c.stroke(); c.set_dash([])
    # cabin
    c.new_path()
    c.move_to(x1, yb); c.line_to(x1, yb - 100); c.line_to(x1 + 40, yb - 190); c.line_to(x2 - 70, yb - 190); c.line_to(x2, yb - 100); c.line_to(x2, yb); c.close_path()
    fill(c, col, a); c.fill()
    # windows
    c.move_to(x1 + 22, yb - 105); c.line_to(x1 + 52, yb - 176); c.line_to(x1 + cab_len / 2 - 6, yb - 176); c.line_to(x1 + cab_len / 2 - 6, yb - 105); c.close_path()
    fill(c, "#BAE6FD", 0.85 * a); c.fill()
    c.move_to(x1 + cab_len / 2 + 6, yb - 105); c.line_to(x1 + cab_len / 2 + 6, yb - 176); c.line_to(x2 - 76, yb - 176); c.line_to(x2 - 14, yb - 105); c.close_path()
    fill(c, "#BAE6FD", 0.85 * a); c.fill()
    # dummy (driver, front seat)
    if dummy:
        hx = x1 + cab_len / 2 + 40 + lean * 40
        c.arc(hx, yb - 140, 20, 0, 2 * math.pi); fill(c, YEL, a); c.fill()
        c.set_line_width(4); fill(c, "#0B1220", a); c.move_to(hx - 8, yb - 140); c.line_to(hx + 8, yb - 140); c.stroke()
        c.arc(hx, yb - 140, 6, 0, 2 * math.pi); fill(c, "#0B1220", a); c.fill()
    if bag > 0:
        bx = x2 - 30
        glow(c, bx, yb - 130, 60 * bag, WHITE, 0.3 * a)
        c.arc(bx - 10 * bag, yb - 130, 40 * back(bag), 0, 2 * math.pi); fill(c, "#F8FAFC", a * ease(bag)); c.fill()
    if belt > 0:
        hx = x1 + cab_len / 2 + 40 + lean * 40
        c.set_line_width(9); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, GREEN, a * belt)
        c.move_to(hx - 30, yb - 168); c.line_to(lerp(hx - 30, hx + 30, belt), lerp(yb - 168, yb - 100, belt)); c.stroke()
    # safety cell outline
    if cell_hi > 0:
        glow(c, (x1 + x2) / 2, yb - 100, 200, CYAN, 0.25 * cell_hi * a)
        c.set_line_width(12); c.set_line_join(cairo.LINE_JOIN_ROUND); fill(c, CYAN, cell_hi * a)
        c.move_to(x1, yb); c.line_to(x1, yb - 100); c.line_to(x1 + 40, yb - 190); c.line_to(x2 - 70, yb - 190); c.line_to(x2, yb - 100); c.line_to(x2, yb); c.close_path(); c.stroke()
        c.move_to(x1 + cab_len / 2, yb - 190); c.line_to(x1 + cab_len / 2, yb); c.stroke()
    return x3


def wall(c, x, a, hit=0.0):
    if a <= 0: return
    rr(c, x, 560, 130, GROUND - 560, 8); fill(c, "#57534E", a); c.fill()
    for i in range(10):
        for j in range(2):
            off = 32 if i % 2 else 0
            c.rectangle(x + 6 + j * 64 - off * (j == 0) * 0 + (off if j == 0 else 0) * 0, 566 + i * 57, 58, 50)
            fill(c, "#78716C", a); c.fill()
    if hit > 0:
        glow(c, x, GROUND - 120, 140, RED, 0.7 * a * (1 - hit))


def ground(c, a):
    c.rectangle(0, GROUND, 1080, 210); fill(c, "#1E293B", a); c.fill()
    c.set_line_width(5); c.set_dash([40, 30]); fill(c, "#475569", a); c.move_to(0, GROUND + 60); c.line_to(1080, GROUND + 60); c.stroke(); c.set_dash([])


def gauge(c, x, y, r, val, a):
    if a <= 0: return
    c.set_line_width(26); fill(c, "#1E293B", a); c.arc(x, y, r, math.pi * 0.75, math.pi * 2.25); c.stroke()
    c.set_line_width(26); fill(c, lerp_col(RED, GREEN, 1 - val), a); c.arc(x, y, r, math.pi * 0.75, math.pi * 0.75 + 1.5 * math.pi * max(val, 0.001)); c.stroke()
    ang = math.pi * 0.75 + 1.5 * math.pi * val
    c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, WHITE, a)
    c.move_to(x, y); c.line_to(x + (r - 40) * math.cos(ang), y + (r - 40) * math.sin(ang)); c.stroke()
    c.arc(x, y, 20, 0, 2 * math.pi); c.fill()


def force_graph(c, a, t, p1, p2):
    if a <= 0: return
    ox, oy, w, h = 170, 1170, 780, 560
    c.set_line_width(5); fill(c, MUTED, a)
    c.move_to(ox, oy - h); c.line_to(ox, oy); c.line_to(ox + w, oy); c.stroke()
    text(c, "FORCE ON YOU", ox - 10, oy - h - 24, 26, MUTED, "black", align="left", a=a)
    text(c, "TIME →", ox + w, oy + 46, 26, MUTED, "black", align="right", a=a)

    def curve(cx, width, height, col, p):
        if p <= 0: return
        c.new_path()
        n = 60
        pts = []
        for i in range(n + 1):
            u = -2.6 + 5.2 * i / n
            pts.append((cx + u * width / 2.6 * 1.0, oy - height * math.exp(-u * u)))
        cut = max(1, int((n + 1) * p))
        c.move_to(pts[0][0], oy)
        for px, py in pts[:cut]: c.line_to(px, py)
        c.line_to(pts[cut - 1][0], oy); c.close_path()
        c.set_source_rgba(*hexc(col)[:3], 0.3 * a); c.fill_preserve(); c.set_line_width(7); fill(c, col, a)
        c.new_path(); c.move_to(*pts[0])
        for px, py in pts[:cut]: c.line_to(px, py)
        c.stroke()

    curve(ox + 150, 40, 520, RED, p1)
    curve(ox + 500, 190, 110, GREEN, p2)


def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "WHY REAL CARS", "CRUMPLE ON PURPOSE", S("stop"))

    car_a = A * (ease(pr(t, 0.05, 0.4)) * (1 - ease(pr(t, S("stop") + 0.2, 0.4)))
                 + ease(pr(t, S("crumple") - 0.2, 0.5)) * (1 - ease(pr(t, S("history") - 0.2, 0.4))))
    stop_a = A * ease(pr(t, S("stop") + 0.2, 0.5)) * (1 - ease(pr(t, S("time") - 0.2, 0.4)))
    graph_a = A * ease(pr(t, S("time") - 0.1, 0.5)) * (1 - ease(pr(t, S("crumple") - 0.3, 0.4)))
    hist_a = A * ease(pr(t, S("history") - 0.1, 0.5))
    WALL = 870

    if car_a > 0:
        ground(c, car_a)
        if t < S("stop") + 1:
            # hook: game car bounces off, then real car crumples
            if t < S("hook") + 5.0:
                drive = eio(pr(t, wt("hook", "smash") - 0.6, 0.6))
                back_ = eout(pr(t, wt("hook", "wall") + 0.0, 0.5))
                away = eio(pr(t, wt("hook", "keep") - 0.3, 1.6))
                xx = lerp(-300, WALL - 560, drive) - 120 * back_ * (1 - away * 0) + 0 * away
                yy_off = 0
                ga = car_a * (1 - ease(pr(t, wt("hook", "real") - 0.4, 0.3)))
                c.save(); c.translate(0, -40 * math.sin(math.pi * min(1, back_)) if back_ < 1 else 0)
                xx2 = xx - 750 * away
                side_car(c, xx2, ga, col=PINK, dummy=False, wheel_t=t * 8)
                c.restore()
                wall(c, WALL, ga, hit=pr(t, wt("hook", "wall"), 0.5))
                gp = pr(t, wt("hook", "games") - 0.2, 0.4)
                pill(c, "IN GAMES: BOUNCE OFF, KEEP DRIVING", 540, 470, 28, DARK, PINK, a=ga * ease(gp), sc=back(gp), pad=22, outline=PINK)
            ra = car_a * ease(pr(t, wt("hook", "real") - 0.3, 0.4))
            if ra > 0:
                cr = eout(pr(t, wt("hook", "wreck") - 0.2, 0.35))
                drive = eio(pr(t, wt("hook", "real") - 0.3, 1.2 if cr == 0 else 0.01))
                front0 = WALL - 560
                xx = lerp(-400, front0, drive) + 190 * 0.62 * cr
                side_car(c, xx, ra, crush=cr, lean=0.3 * cr, wheel_t=t * 8 * (1 - cr))
                wall(c, WALL, ra, hit=pr(t, wt("hook", "wreck") - 0.1, 0.5))
                rp = pr(t, wt("hook", "real") - 0.2, 0.4)
                pill(c, "REAL CARS: WRECK ON PURPOSE", 540, 470, 28, DARK, CYAN, a=ra * ease(rp), sc=back(rp), pad=22, outline=CYAN)
        else:
            # crumple / cage / team: slow-motion crash
            cr = eio(pr(t, wt("crumple", "fold") - 0.4, 1.6))
            front0 = WALL - 560
            xx = front0 - 60 * (1 - ease(pr(t, S("crumple") - 0.2, 0.8))) + 190 * 0.62 * cr
            zone = ease(pr(t, wt("crumple", "front") - 0.2, 0.4)) * (1 - ease(pr(t, S("cage") - 0.1, 0.4)))
            cell = ease(pr(t, wt("cage", "stiff") - 0.2, 0.4)) * (1 - 0.6 * ease(pr(t, S("team"), 0.4)))
            belt = ease(pr(t, wt("team", "belts") - 0.2, 0.4))
            bag = ease(pr(t, wt("team", "airbags") - 0.1, 0.35))
            lean = 0.25 * cr + 0.35 * ease(pr(t, wt("team", "stretch") - 0.2, 1.0)) * (1 - 0.6 * ease(pr(t, wt("team", "longer"), 0.6)))
            side_car(c, xx, car_a, crush=cr, zone_hi=zone, cell_hi=cell, belt=belt, bag=bag, lean=lean,
                     rear_crush=0.0)
            wall(c, WALL, car_a)
            cz = pr(t, wt("crumple", "crumple") - 0.2, 0.4) * (1 - ease(pr(t, wt("crumple", "absorb") - 0.2, 0.3)))
            pill(c, "CRUMPLE ZONES", 540, 470, 32, DARK, AMBER, a=car_a * ease(cz), sc=back(cz), pad=22, outline=AMBER)
            ab = pr(t, wt("crumple", "absorb") - 0.2, 0.4) * (1 - ease(pr(t, S("cage") - 0.1, 0.3)))
            pill(c, "FOLD + ABSORB ENERGY", 540, 470, 32, DARK, AMBER, a=car_a * ease(ab), sc=back(ab), pad=22, outline=AMBER)
            sc_ = pr(t, wt("cage", "safety") - 0.2, 0.4) * (1 - ease(pr(t, S("team") - 0.1, 0.3)))
            pill(c, "SAFETY CELL · KEEPS ITS SHAPE", 540, 470, 30, DARK, CYAN, a=car_a * ease(sc_), sc=back(sc_), pad=22, outline=CYAN)
            hs = pr(t, wt("cage", "high") - 0.2, 0.4) * (1 - ease(pr(t, S("team") - 0.1, 0.3)))
            text(c, "HIGH-STRENGTH STEEL", 540, 700, 34, CYAN, "black", a=car_a * ease(hs), stroke=6)
            tb = pr(t, wt("team", "belts") - 0.2, 0.4)
            pill(c, "SEAT BELT + AIRBAG", 540, 470, 32, "#052E2B", GREEN, a=car_a * ease(tb), sc=back(tb), pad=22, outline=GREEN)
            ls = pr(t, wt("team", "stretch") - 0.2, 0.4)
            text(c, "YOUR STOP: A LITTLE LONGER", 540, 700, 32, GREEN, "black", a=car_a * ease(ls), stroke=6)

    if stop_a > 0:
        v = 1 - eio(pr(t, wt("stop", "zero") - 0.9, 0.9))
        gauge(c, 540, 880, 230, 0.85 * v, stop_a)
        text(c, "FULL SPEED" if v > 0.5 else "ZERO", 540, 1080, 40, WHITE if v > 0.5 else RED, "black", a=stop_a, stroke=6)
        q = pr(t, wt("stop", "fast") - 0.2, 0.4)
        pill(c, "THE DANGER IS HOW FAST YOU STOP", 540, 470, 28, "#450A0A", RED, a=stop_a * ease(q), sc=back(q), pad=22, outline=RED)

    if graph_a > 0:
        p1 = eio(pr(t, wt("time", "instantly") - 0.3, 0.6))
        p2 = eio(pr(t, wt("time", "stretch") - 0.2, 1.4))
        force_graph(c, graph_a, t, p1, p2)
        e = pr(t, wt("time", "enormous") - 0.3, 0.4)
        text(c, "INSTANT STOP", 370, 700, 30, RED, "black", align="left", a=graph_a * ease(e), stroke=6)
        s2 = pr(t, wt("time", "drops") - 0.3, 0.4)
        text(c, "STRETCHED STOP", 680, 980, 30, GREEN, "black", a=graph_a * ease(s2), stroke=6)
        pill(c, "SAME CRASH · MUCH LOWER PEAK", 540, 470, 28, "#052E2B", GREEN, a=graph_a * ease(s2), sc=back(s2), pad=22, outline=GREEN)

    if hist_a > 0:
        y = pr(t, wt("history", "1959") - 0.3, 0.5)
        c.save(); c.translate(540, 860); safe_scale(c, back(y), back(y))
        text(c, "1959", 0, 60, 220, WHITE, "black", a=hist_a * ease(y), stroke=14)
        c.restore()
        pt = pr(t, wt("history", "patented") - 0.3, 0.4)
        # patent document
        dx, dy = 540, 760
        da = hist_a * ease(pt) * (1 - ease(pr(t, wt("history", "1959") - 0.4, 0.3)))
        if da > 0:
            c.save(); c.translate(dx, dy); safe_scale(c, back(pt), back(pt))
            rr(c, -150, -190, 300, 380, 16); fill(c, "#F8FAFC", da); c.fill()
            for i in range(7):
                rr(c, -110, -130 + i * 40, 220 - (i % 3) * 40, 14, 7); fill(c, "#94A3B8", da); c.fill()
            c.arc(80, 130, 34, 0, 2 * math.pi); fill(c, RED, da); c.fill()
            c.restore()
        pill(c, "PATENTED BY A MERCEDES-BENZ ENGINEER", 540, 470, 26, DARK, WHITE, a=hist_a * ease(pt), sc=back(pt), pad=22, outline=MUTED)
        pc = pr(t, wt("history", "production") - 0.2, 0.4)
        text(c, "FIRST PRODUCTION CAR WITH IT", 540, 1040, 34, YEL, "black", a=hist_a * ease(pc), stroke=6)

    for lid, s, col in (("stop", "THE REAL DANGER", RED), ("time", "THE PHYSICS", GREEN), ("crumple", "THE CRUMPLE ZONE", AMBER),
                        ("cage", "THE SAFETY CELL", CYAN), ("team", "THE BACKUP", GREEN), ("history", "THE ORIGIN", WHITE)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "wall") - 0.05, "pop"), (wt("hook", "keep") - 0.2, "blip"), (wt("hook", "wreck") - 0.2, "rumble"),
            (wt("stop", "zero") - 0.9, "low"), (wt("stop", "fast") - 0.2, "warn"),
            (wt("time", "instantly") - 0.3, "pop"), (wt("time", "stretch") - 0.2, "rise"), (wt("time", "drops") - 0.3, "success"),
            (wt("crumple", "fold") - 0.4, "rumble"), (wt("cage", "stiff") - 0.2, "ping"),
            (wt("team", "airbags") - 0.1, "pop"), (wt("history", "patented") - 0.3, "tick"), (wt("history", "1959") - 0.3, "pop")]
