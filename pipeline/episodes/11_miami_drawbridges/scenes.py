"""Episode 11 (GTA 6 week #1): Why Miami's roads stand up - bascule drawbridges."""
from hm.core import *
from hm.props import *

DARK = "#0F172A"
STEEL = "#94A3B8"
ROAD = "#334155"
CONC = "#57534E"
WATER_Y = 1180
PINK = "#F472B6"


# ---------- shared bits ----------
def leaf(c, px, py, L, d, th, a, thick=34, tail=0, tail_h=0, col=STEEL, cw_col="#78716C", cw_a=1.0, glow_cw=0.0):
    """Bascule leaf pivoting at (px,py). d=+1 extends right, -1 left. th = opening angle (rad).
    tail: counterweight length behind the pivot, tail_h: its height (hangs below the deck)."""
    if a <= 0: return
    c.save(); c.translate(px, py)
    c.rotate(-th if d > 0 else th)
    if tail > 0 and cw_a > 0:
        x0 = -tail if d > 0 else 0
        if glow_cw > 0: glow(c, -d * tail * 0.55, tail_h * 0.5, tail * 0.9, AMBER, 0.6 * glow_cw * a)
        rr(c, x0, thick * 0.3, tail, tail_h, 10); fill(c, cw_col, a * cw_a); c.fill()
        c.rectangle(-d * 6 - 6, 0, 12, thick * 0.3 + 4); fill(c, cw_col, a * cw_a); c.fill()
    x0 = 0 if d > 0 else -L
    rr(c, x0, -thick / 2, L, thick, 6); fill(c, col, a); c.fill()
    c.rectangle(x0, -thick / 2, L, 7); fill(c, "#E2E8F0", a); c.fill()
    # lane stripes
    c.set_line_width(4); c.set_dash([22, 16]); fill(c, YEL, 0.8 * a)
    c.move_to(x0 + 10, -thick / 2 + 3); c.line_to(x0 + L - 10, -thick / 2 + 3); c.stroke(); c.set_dash([])
    c.restore()


def palm(c, x, y, s, a):
    if a <= 0: return
    c.set_line_width(10 * s); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, "#7C5E3C", a)
    c.move_to(x, y); c.curve_to(x + 8 * s, y - 60 * s, x - 6 * s, y - 110 * s, x + 6 * s, y - 150 * s); c.stroke()
    tx, ty = x + 6 * s, y - 150 * s
    fill(c, "#15803D", a)
    for ang in (-2.6, -2.0, -1.2, -0.5, 0.1, 0.6):
        c.set_line_width(12 * s)
        ex, ey = tx + 70 * s * math.cos(ang), ty + 70 * s * math.sin(ang) + 25 * s
        c.move_to(tx, ty); c.curve_to(tx + 35 * s * math.cos(ang), ty + 35 * s * math.sin(ang) - 15 * s, ex, ey - 10 * s, ex, ey); c.stroke()


def skyline(c, a):
    if a <= 0: return
    bs = [(40, 140, 330), (150, 110, 420), (250, 90, 300), (820, 120, 380), (930, 110, 470), (1000, 80, 260),
          (360, 70, 220), (650, 80, 250)]
    for x, w, h in bs:
        rr(c, x, 1000 - h, w, h, 6); fill(c, "#1E293B", a); c.fill()
        for i in range(int(h // 46)):
            for j in range(int(w // 34)):
                if (i * 7 + j * 3 + x) % 5 < 3:
                    c.rectangle(x + 12 + j * 34, 1000 - h + 18 + i * 46, 14, 18); fill(c, PINK if (i + j + x) % 4 == 0 else CYAN, 0.35 * a); c.fill()


def water(c, a, t, y0=WATER_Y, y1=1340):
    if a <= 0: return
    c.move_to(0, y0)
    for i in range(0, 1081, 20): c.line_to(i, y0 + 6 * math.sin(i / 50 + t * 2.4))
    c.line_to(1080, y1); c.line_to(0, y1); c.close_path()
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgba(0, *hexc("#0E7490")[:3], 0.95 * a); g.add_color_stop_rgba(1, *hexc("#082F49")[:3], a)
    c.set_source(g); c.fill()


def boat(c, x, y, a, t, mast=260):
    if a <= 0: return
    bob = 5 * math.sin(t * 2.2)
    c.save(); c.translate(x, y + bob)
    c.move_to(-110, -20); c.line_to(110, -20); c.line_to(80, 22); c.line_to(-80, 22); c.close_path(); fill(c, "#F8FAFC", a); c.fill()
    c.rectangle(-100, -4, 200, 8); fill(c, CYAN, a); c.fill()
    c.set_line_width(7); fill(c, "#CBD5E1", a); c.move_to(0, -20); c.line_to(0, -20 - mast); c.stroke()
    c.move_to(6, -30 - mast * 0.95); c.line_to(6, -34); c.line_to(95, -34); c.close_path(); fill(c, "#E2E8F0", 0.9 * a); c.fill()
    c.move_to(-6, -30 - mast * 0.85); c.line_to(-6, -40); c.line_to(-70, -40); c.close_path(); fill(c, PINK, 0.85 * a); c.fill()
    c.restore()


def car(c, x, y, a, col=AMBER):
    if a <= 0: return
    rr(c, x - 44, y - 30, 88, 26, 8); fill(c, col, a); c.fill()
    rr(c, x - 24, y - 50, 48, 24, 8); fill(c, col, a); c.fill()
    for wx in (-24, 24):
        c.arc(x + wx, y - 4, 10, 0, 2 * math.pi); fill(c, "#0B1220", a); c.fill()


def gate(c, x, y, down, a):
    if a <= 0: return
    c.rectangle(x - 6, y - 70, 12, 70); fill(c, "#CBD5E1", a); c.fill()
    ang = lerp(-1.4, 0, down)
    c.save(); c.translate(x, y - 60); c.rotate(ang)
    for k in range(5):
        c.rectangle(k * 24, -6, 24, 12); fill(c, RED if k % 2 == 0 else WHITE, a); c.fill()
    c.restore()
    c.arc(x, y - 75, 9, 0, 2 * math.pi); fill(c, RED, a * (0.4 + 0.6 * down * (0.5 + 0.5 * math.sin(10 * x + 12 * a)))); c.fill()


def wide_scene(c, a, t, th, boat_x, cars_x=0.0, gate_down=0.0):
    if a <= 0: return
    skyline(c, a)
    water(c, a, t)
    # banks
    for x0, x1 in ((0, 300), (780, 1080)):
        c.rectangle(x0, 1000, x1 - x0, 340); fill(c, CONC, a); c.fill()
        c.rectangle(x0, 984, x1 - x0, 20); fill(c, ROAD, a); c.fill()
    # counterweight pits
    for px in (300, 780):
        rr(c, px - 150 if px < 540 else px, 1010, 150, 150, 8); fill(c, "#292524", a); c.fill()
    palm(c, 70, 990, 0.9, a); palm(c, 1010, 990, 0.95, a); palm(c, 190, 990, 0.7, a)
    c.save(); c.rectangle(300, 0, 480, 1340); c.clip()
    boat(c, boat_x, WATER_Y - 4, a, t)
    c.restore()
    leaf(c, 300, 994, 240, 1, th, a, thick=26, tail=120, tail_h=100)
    leaf(c, 780, 994, 240, -1, th, a, thick=26, tail=120, tail_h=100)
    car(c, 150 + cars_x, 984, a)
    gate(c, 250, 984, gate_down, a)
    gate(c, 830, 984, gate_down, a)


# ---------- map of the river ----------
BR_X = (230, 400, 570, 740, 900)


def ry(x): return 900 + 140 * math.sin(x / 165 + 0.6)


def river_map(c, a, t, boat_u):
    if a <= 0: return
    # streets
    for x in BR_X:
        c.set_line_width(26); fill(c, "#1E293B", a); c.move_to(x, 560); c.line_to(x, 1300); c.stroke()
    for yy in (640, 1220):
        c.set_line_width(20); fill(c, "#1E293B", a); c.move_to(80, yy); c.line_to(1000, yy); c.stroke()
    # river band
    c.set_line_width(120); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, "#0E7490", a)
    c.move_to(60, ry(60))
    for x in range(60, 1021, 15): c.line_to(x, ry(x))
    c.stroke()
    bx = lerp(40, 1060, boat_u)
    for x in BR_X:
        op = ease(cl(1 - (abs(bx - x) - 60) / 90))
        half = 70 * (1 - 0.85 * op)
        y = ry(x)
        col = lerp_col(STEEL, YEL, op)
        c.set_line_width(26); c.set_line_cap(cairo.LINE_CAP_BUTT); fill(c, col, a)
        c.move_to(x, y - 70); c.line_to(x, y - 70 + half); c.stroke()
        c.move_to(x, y + 70); c.line_to(x, y + 70 - half); c.stroke()
        if op > 0.3: glow(c, x, y, 70, YEL, 0.35 * op * a)
    # boat (top view)
    by = ry(bx); ang = math.atan2(ry(bx + 5) - ry(bx - 5), 10)
    c.save(); c.translate(bx, by); c.rotate(ang)
    c.move_to(-34, -14); c.line_to(22, -14); c.line_to(40, 0); c.line_to(22, 14); c.line_to(-34, 14); c.close_path(); fill(c, WHITE, a); c.fill()
    c.restore()
    c.set_line_width(3); fill(c, WHITE, 0.35 * a)
    for k in range(1, 6):
        c.arc(bx - 30 * k * math.cos(ang), ry(bx - 30 * k), 4 + 2 * k, 0, 2 * math.pi); c.stroke()


# ---------- seesaw icon ----------
def seesaw(c, x, y, a, tilt):
    if a <= 0: return
    c.move_to(x - 50, y + 90); c.line_to(x + 50, y + 90); c.line_to(x, y); c.close_path(); fill(c, AMBER, a); c.fill()
    c.save(); c.translate(x, y); c.rotate(tilt)
    rr(c, -260, -22, 520, 22, 8); fill(c, STEEL, a); c.fill()
    for sx, col in ((-220, CYAN), (220, PINK)):
        c.arc(sx, -62, 30, 0, 2 * math.pi); fill(c, col, a); c.fill()
        rr(c, sx - 26, -40, 52, 22, 8); c.fill()
    c.restore()


# ---------- close-up of one leaf ----------
CP = (360, 1000)


def close_scene(c, a, t, th, cw, trun, lvl, motor):
    if a <= 0: return
    water(c, a, t, y0=1150)
    c.rectangle(0, 1000, 470, 340); fill(c, CONC, a); c.fill()
    rr(c, 70, 1012, 300, 250, 10); fill(c, "#1C1917", a); c.fill()      # pit
    c.rectangle(0, 984, 140, 20); fill(c, ROAD, a); c.fill()
    leaf(c, CP[0], CP[1], 640, 1, th, a, thick=48, tail=260, tail_h=180, cw_a=cw, glow_cw=cw * (1 - lvl * 0.3) * 0.8)
    # trunnion
    if trun > 0:
        glow(c, CP[0], CP[1], 90, CYAN, 0.5 * trun * a)
    c.arc(CP[0], CP[1], 30, 0, 2 * math.pi); fill(c, "#CBD5E1", a); c.fill()
    c.arc(CP[0], CP[1], 12, 0, 2 * math.pi); fill(c, DARK, a); c.fill()
    if trun > 0:
        c.set_line_width(6); fill(c, CYAN, a * trun)
        c.arc(CP[0], CP[1], 46 * back(trun), 0, 2 * math.pi); c.stroke()
    # motor + gear
    if motor > 0:
        mx, my = 250, 1200
        rr(c, mx - 60, my - 34, 90, 68, 12); fill(c, "#475569", a * motor); c.fill()
        text(c, "M", mx - 15, my + 14, 36, WHITE, "black", a=a * motor)
        gx, gy = mx + 70, my
        c.save(); c.translate(gx, gy); c.rotate(t * 4 * (1 if th < 1.2 else 0))
        for k in range(10):
            c.save(); c.rotate(k * math.pi / 5); c.rectangle(-7, -38, 14, 14); fill(c, AMBER, a * motor); c.fill(); c.restore()
        c.arc(0, 0, 28, 0, 2 * math.pi); fill(c, AMBER, a * motor); c.fill()
        c.arc(0, 0, 8, 0, 2 * math.pi); fill(c, DARK, a * motor); c.fill()
        c.restore()
    # balance level
    if lvl > 0:
        c.save(); c.translate(540, 700)
        rr(c, -170, -26, 340, 52, 26); fill(c, DARK, a * lvl); c.fill_preserve(); c.set_line_width(4); fill(c, GREEN, a * lvl); c.stroke()
        bx = 60 * math.cos(t * 2) * max(0.0, 1 - (t - 28.6) * 0.5) if t < 31 else 0
        c.arc(bx, 0, 16, 0, 2 * math.pi); fill(c, GREEN, a * lvl); c.fill()
        c.set_line_width(3); fill(c, WHITE, 0.6 * a * lvl)
        for sx in (-26, 26): c.move_to(sx, -18); c.line_to(sx, 18); c.stroke()
        c.restore()


def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "MIAMI'S ROADS", "STAND UP FOR BOATS", S("river"))

    wide_a = A * (ease(pr(t, 0.05, 0.5)) * (1 - ease(pr(t, S("river") - 0.2, 0.4))) + ease(pr(t, S("rule") - 0.2, 0.5)))
    map_a = A * ease(pr(t, S("river") - 0.1, 0.5)) * (1 - ease(pr(t, S("name") - 0.2, 0.4)))
    saw_a = A * ease(pr(t, wt("name", "french") - 0.4, 0.4)) * (1 - ease(pr(t, S("pivot") - 0.2, 0.4)))
    close_a = A * ease(pr(t, S("pivot") - 0.1, 0.5)) * (1 - ease(pr(t, S("rule") - 0.3, 0.4)))

    # ---- wide view: hook + rule ----
    if wide_a > 0:
        if t < S("river"):
            th = 1.25 * eio(pr(t, wt("hook", "stand") - 0.3, 1.0))
            bx = lerp(150, 930, eio(pr(t, wt("hook", "stand") + 0.1, 1.8)))
            wide_scene(c, wide_a, t, th, bx, gate_down=ease(pr(t, wt("hook", "roads") - 0.5, 0.4)))
            g = pr(t, wt("hook", "fake") - 0.3, 0.4) * (1 - ease(pr(t, wt("hook", "real") - 0.2, 0.3)))
            pill(c, "GTA 6: A FICTIONAL MIAMI", 540, 470, 30, DARK, PINK, a=wide_a * ease(g), sc=back(g), pad=22, outline=PINK)
            r = pr(t, wt("hook", "real") - 0.2, 0.4)
            pill(c, "THE REAL MIAMI", 540, 470, 30, DARK, CYAN, a=wide_a * ease(r), sc=back(r), pad=22, outline=CYAN)
        else:
            op = eio(pr(t, wt("rule", "win") - 0.4, 1.0)) * (1 - eio(pr(t, wt("rule", "except") - 0.1, 1.0)))
            bx = lerp(150, 930, eio(pr(t, wt("rule", "win") - 0.1, 2.8)))
            cars = 160 * eio(pr(t, wt("rule", "rush") + 0.2, 1.2))
            gd = 1 - ease(pr(t, wt("rule", "rush") - 0.3, 0.4))
            wide_scene(c, wide_a, t, 1.25 * op, bx, cars_x=cars, gate_down=gd)
            w = pr(t, wt("rule", "win") - 0.2, 0.4) * (1 - ease(pr(t, wt("rule", "federal") - 0.2, 0.3)))
            pill(c, "BOATS FIRST", 540, 470, 32, "#052E2B", GREEN, a=wide_a * ease(w), sc=back(w), pad=22, outline=GREEN)
            f = pr(t, wt("rule", "federal") - 0.2, 0.4) * (1 - ease(pr(t, wt("rule", "except") - 0.2, 0.3)))
            pill(c, "U.S. COAST GUARD RULES", 540, 470, 30, DARK, WHITE, a=wide_a * ease(f), sc=back(f), pad=22, outline=MUTED)
            e = pr(t, wt("rule", "except") - 0.2, 0.4)
            pill(c, "WEEKDAY RUSH HOURS: CARS FIRST", 540, 470, 28, "#450A0A", AMBER, a=wide_a * ease(e), sc=back(e), pad=22, outline=AMBER)

    # ---- river map ----
    if map_a > 0:
        u = eio(pr(t, wt("river", "row") - 0.6, 3.6))
        river_map(c, map_a, t, u)
        m = pr(t, wt("river", "miami") - 0.2, 0.4)
        pill(c, "MIAMI RIVER", 540, 470, 32, DARK, CYAN, a=map_a * ease(m), sc=back(m), pad=22, outline=CYAN)
        s = pr(t, wt("river", "signal") - 0.2, 0.4)
        pill(c, "THEY OPEN ON SIGNAL", 540, 1300, 28, DARK, YEL, a=map_a * ease(s), sc=back(s), pad=20, outline=YEL)

    # ---- name: bascule = seesaw ----
    nm = A * ease(pr(t, S("name") - 0.1, 0.4)) * (1 - ease(pr(t, S("pivot") - 0.2, 0.4)))
    if nm > 0:
        b = pr(t, wt("name", "bascule") - 0.2, 0.5)
        c.save(); c.translate(540, 720); safe_scale(c, back(b), back(b))
        text(c, "BASCULE", 0, 40, 130, WHITE, "black", a=nm * ease(b), stroke=12)
        c.restore()
        fr = pr(t, wt("name", "french") - 0.2, 0.4)
        text(c, "FRENCH FOR “SEESAW”", 540, 850, 44, YEL, "black", a=nm * ease(fr), stroke=8)
        seesaw(c, 540, 1080, saw_a, 0.28 * math.sin((t - wt("name", "seesaw")) * 2.4) * ease(pr(t, wt("name", "seesaw") - 0.2, 0.4)))

    # ---- close-up ----
    if close_a > 0:
        th = 1.2 * eio(pr(t, wt("motor", "swing") - 0.2, 1.6))
        cw = ease(pr(t, wt("counter", "counterweight") - 0.3, 0.5))
        trun = ease(pr(t, wt("pivot", "trunnion") - 0.2, 0.5))
        lvl = ease(pr(t, wt("counter", "balances") - 0.2, 0.5)) * (1 - ease(pr(t, S("motor") + 0.4, 0.4)))
        motor = ease(pr(t, wt("motor", "motors") - 0.3, 0.4))
        # leaf highlight pulse at "leaf"
        close_scene(c, close_a, t, th, cw, trun, lvl, motor)
        lf = pr(t, wt("pivot", "leaf") - 0.2, 0.4) * (1 - ease(pr(t, wt("pivot", "trunnion") - 0.2, 0.3)))
        pill(c, "THE LEAF", 680, 900, 30, DARK, WHITE, a=close_a * ease(lf), sc=back(lf), pad=20, outline=MUTED)
        tr = pr(t, wt("pivot", "trunnion") - 0.2, 0.4) * (1 - ease(pr(t, S("counter") + 0.3, 0.3)))
        pill(c, "TRUNNION = GIANT PIVOT AXLE", 540, 470, 28, DARK, CYAN, a=close_a * ease(tr), sc=back(tr), pad=22, outline=CYAN)
        cwp = pr(t, wt("counter", "counterweight") - 0.2, 0.4) * (1 - ease(pr(t, S("motor"), 0.3)))
        pill(c, "COUNTERWEIGHT", 540, 470, 32, DARK, AMBER, a=close_a * ease(cwp), sc=back(cwp), pad=22, outline=AMBER)
        bl = pr(t, wt("counter", "balances") - 0.2, 0.4) * (1 - ease(pr(t, S("motor") + 0.4, 0.4)))
        text(c, "BALANCED", 540, 790, 34, GREEN, "black", a=close_a * ease(bl), stroke=6)
        mo = pr(t, wt("motor", "small") - 0.2, 0.4)
        pill(c, "SMALL MOTORS · BIG BRIDGE", 540, 470, 30, "#052E2B", GREEN, a=close_a * ease(mo), sc=back(mo), pad=22, outline=GREEN)

    for lid, s, col in (("river", "THE REAL VICE CITY", PINK), ("name", "THE NAME", CYAN), ("pivot", "THE PIVOT", CYAN),
                        ("counter", "THE SECRET", AMBER), ("motor", "THE LIFT", GREEN), ("rule", "THE RULE", WHITE)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "fake") - 0.3, "blip"), (wt("hook", "stand") - 0.3, "rumble"), (wt("hook", "boats") - 0.2, "pop"),
            (wt("river", "miami") - 0.2, "ping"), (wt("river", "row") - 0.4, "rise"), (wt("river", "signal") - 0.2, "blip"),
            (wt("name", "bascule") - 0.2, "pop"), (wt("name", "seesaw") - 0.2, "blip"),
            (wt("pivot", "leaf") - 0.2, "tick"), (wt("pivot", "trunnion") - 0.2, "ping"),
            (wt("counter", "counterweight") - 0.3, "low"), (wt("counter", "balances") - 0.2, "ok"),
            (wt("motor", "motors") - 0.3, "blip"), (wt("motor", "swing") - 0.2, "rise"),
            (wt("rule", "win") - 0.4, "rumble"), (wt("rule", "except") - 0.2, "warn")]
