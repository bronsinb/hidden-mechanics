"""Episode 20: How do steel ships float? (Archimedes, hull shape, load lines)."""
from hm.core import *
from hm.props import *

DARK = "#0F172A"
STEEL = "#94A3B8"
SEA = "#0E7490"
SEA_D = "#083344"
FRESH = "#38BDF8"
HULL = "#B91C1C"
WL = 880                        # water surface in the tank
TANK = (110, 620, 970, 1330)    # x0, y0, x1, y1


def tank(c, a, t, level=WL, col=SEA):
    if a <= 0: return
    x0, y0, x1, y1 = TANK
    c.move_to(x0, level)
    for x in range(int(x0), int(x1) + 1, 20):
        c.line_to(x, level + 5 * math.sin(x / 45 + t * 2.2))
    c.line_to(x1, y1); c.line_to(x0, y1); c.close_path()
    g = cairo.LinearGradient(0, level, 0, y1)
    g.add_color_stop_rgba(0, *hexc(col)[:3], 0.9 * a); g.add_color_stop_rgba(1, *hexc(SEA_D)[:3], a)
    c.set_source(g); c.fill()
    c.set_line_width(6); fill(c, "#475569", a)
    c.move_to(x0, y0); c.line_to(x0, y1); c.line_to(x1, y1); c.line_to(x1, y0); c.stroke()


def arrow(c, x, y0, y1, col, a, w=12):
    if a <= 0 or abs(y1 - y0) < 4: return
    d = 1 if y1 > y0 else -1
    c.set_line_width(w); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, col, a)
    c.move_to(x, y0); c.line_to(x, y1 - d * 18); c.stroke()
    c.move_to(x - 22, y1 - d * 26); c.line_to(x, y1); c.line_to(x + 22, y1 - d * 26); c.close_path(); c.fill()


def cargo_ship(c, x, y, s, a, t, draft=0.0):
    """Side view; (x,y) = waterline centre. draft shifts the ship down (px before scale)."""
    if a <= 0: return
    c.save(); c.translate(x, y + draft); safe_scale(c, s, s)
    bob = 3 * math.sin(t * 1.8)
    c.translate(0, bob)
    # hull
    c.move_to(-220, -40); c.line_to(230, -40); c.line_to(200, 40); c.line_to(-190, 40); c.line_to(-220, 10); c.close_path()
    fill(c, "#1E293B", a); c.fill()
    c.move_to(-213, 0); c.line_to(222, 0); c.line_to(200, 40); c.line_to(-190, 40); c.line_to(-213, 10); c.close_path()
    fill(c, HULL, a); c.fill()
    # containers
    cols = (AMBER, CYAN, "#22C55E", "#F472B6", "#E2E8F0")
    for i in range(8):
        for j in range(2):
            rr(c, -150 + i * 40, -78 - j * 36, 38, 34, 3); fill(c, cols[(i * 2 + j) % 5], a); c.fill()
    # bridge
    rr(c, -205, -120, 50, 80, 4); fill(c, "#F8FAFC", a); c.fill()
    for k in range(3):
        c.rectangle(-198 + k * 15, -110, 10, 8); fill(c, "#0B1220", a); c.fill()
    rr(c, -190, -140, 16, 22, 3); fill(c, "#475569", a); c.fill()
    c.restore()


def steel_block(c, x, y, a, w=150, h=110):
    if a <= 0: return
    g = cairo.LinearGradient(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
    g.add_color_stop_rgba(0, *hexc("#CBD5E1")[:3], a); g.add_color_stop_rgba(1, *hexc("#475569")[:3], a)
    rr(c, x - w / 2, y - h / 2, w, h, 8); c.set_source(g); c.fill()


def hull_shape(c, x, y, a, w=520, h=180, th=16, fill_air=0.0):
    """Hollow U-hull, top edge at y - h/2."""
    if a <= 0: return
    top, bot = y - h / 2, y + h / 2
    c.move_to(x - w / 2, top); c.line_to(x - w / 2 + 40, bot); c.line_to(x + w / 2 - 40, bot); c.line_to(x + w / 2, top)
    c.line_to(x + w / 2 - th, top); c.line_to(x + w / 2 - 40 - th * 0.6, bot - th); c.line_to(x - w / 2 + 40 + th * 0.6, bot - th)
    c.line_to(x - w / 2 + th, top); c.close_path()
    fill(c, STEEL, a); c.fill()
    if fill_air > 0:
        c.move_to(x - w / 2 + th, top); c.line_to(x - w / 2 + 40 + th * 0.6, bot - th); c.line_to(x + w / 2 - 40 - th * 0.6, bot - th); c.line_to(x + w / 2 - th, top); c.close_path()
        c.set_source_rgba(*hexc("#E0F2FE")[:3], 0.25 * a * fill_air); c.fill()


def displaced(c, x, y_top, y_bot, w_top, w_bot, a, label=True):
    if a <= 0: return
    c.move_to(x - w_top / 2, y_top); c.line_to(x + w_top / 2, y_top); c.line_to(x + w_bot / 2, y_bot); c.line_to(x - w_bot / 2, y_bot); c.close_path()
    c.set_source_rgba(*hexc(FRESH)[:3], 0.25 * a); c.fill_preserve()
    c.set_line_width(4); c.set_dash([14, 10]); fill(c, FRESH, a); c.stroke(); c.set_dash([])


def scale_beam(c, a, tilt, lab_l, lab_r, col_l, col_r):
    if a <= 0: return
    x, y = 540, 565
    c.move_to(x - 30, y + 90); c.line_to(x + 30, y + 90); c.line_to(x, y); c.close_path(); fill(c, "#64748B", a); c.fill()
    c.save(); c.translate(x, y); c.rotate(tilt)
    c.set_line_width(10); fill(c, "#CBD5E1", a); c.move_to(-260, 0); c.line_to(260, 0); c.stroke()
    c.restore()
    for sx, lab, col in ((-1, lab_l, col_l), (1, lab_r, col_r)):
        px = x + sx * 260 * math.cos(tilt); py = y + sx * 260 * math.sin(tilt)
        c.set_line_width(3); fill(c, "#CBD5E1", a); c.move_to(px, py); c.line_to(px, py + 60); c.stroke()
        rr(c, px - 110, py + 60, 220, 18, 8); c.fill()
        text(c, lab, px, py + 118, 26, col, "black", a=a, stroke=6)


def plimsoll(c, a, t, fresh):
    if a <= 0: return
    # hull side close-up
    c.rectangle(80, 560, 920, 780); fill(c, "#1E293B", a); c.fill()
    c.rectangle(80, 950, 920, 390); fill(c, HULL, a); c.fill()
    # rivets
    for i in range(10):
        for j in range(8):
            c.arc(110 + i * 95, 590 + j * 95, 4, 0, 2 * math.pi); fill(c, "#0F172A", 0.6 * a); c.fill()
    mx, my = 380, 960
    c.set_line_width(9); fill(c, WHITE, a)
    c.new_path(); c.arc(mx, my, 70, 0, 2 * math.pi); c.stroke()
    c.move_to(mx - 110, my); c.line_to(mx + 110, my); c.stroke()
    text(c, "L", mx - 55, my - 20, 34, WHITE, "black", a=a)
    text(c, "R", mx + 55, my - 20, 34, WHITE, "black", a=a)
    lx = 620
    c.move_to(lx, my - 140); c.line_to(lx, my + 70); c.stroke()
    marks = [("TF", -130), ("F", -100), ("T", -30), ("S", 0), ("W", 30)]
    for lab, dy in marks:
        c.move_to(lx, my + dy); c.line_to(lx + (100 if lab in ("TF", "F") else -0) + 100, my + dy); c.stroke()
        text(c, lab, lx + 230, my + dy + 12, 30, WHITE, "black", align="left", a=a)
    # water at "S" (salt summer) rising to "F" (fresh)
    lvl = lerp(my + 4, my - 96, fresh)
    col = lerp_col(SEA, FRESH, fresh)
    c.move_to(80, lvl)
    for x in range(80, 1001, 20): c.line_to(x, lvl + 6 * math.sin(x / 40 + t * 2.4))
    c.line_to(1000, 1340); c.line_to(80, 1340); c.close_path()
    fill(c, col, 0.72 * a); c.fill()


def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "HOW DO STEEL SHIPS", "FLOAT?", S("push"))

    tank_a = A * ease(pr(t, 0.05, 0.5)) * (1 - ease(pr(t, S("air") - 0.2, 0.4)))
    air_a = A * ease(pr(t, S("air") - 0.1, 0.5)) * (1 - ease(pr(t, S("settle") - 0.2, 0.4)))
    set_a = A * ease(pr(t, S("settle") - 0.1, 0.5)) * (1 - ease(pr(t, S("plimsoll") - 0.2, 0.4)))
    pl_a = A * ease(pr(t, S("plimsoll") - 0.1, 0.5))

    if tank_a > 0:
        tank(c, tank_a, t)
        if t < S("push"):
            sink = eio(pr(t, wt("hook", "sinks") - 0.5, 1.1))
            by = lerp(700, 1260, sink)
            steel_block(c, 300, by, tank_a, w=150, h=60)
            text(c, "STEEL BAR", 300, 640, 28, STEEL, "black", a=tank_a * (1 - sink * 0.6), stroke=6)
            sh = ease(pr(t, wt("hook", "ship") - 0.3, 0.5))
            cargo_ship(c, 700, WL, 0.75, tank_a * sh, t)
            fl = pr(t, wt("hook", "float") - 0.3, 0.4)
            text(c, "?", 700, 700, 120, YEL, "black", a=tank_a * ease(fl), stroke=10)
        elif t < S("block"):
            # generic object: buoyancy = weight of water pushed aside
            ox, oy = 540, WL + 20
            c.save(); c.translate(ox, oy); rr(c, -110, -70, 220, 140, 20); c.restore(); fill(c, AMBER, tank_a); c.fill()
            up = ease(pr(t, wt("push", "pushed") - 0.3, 0.5))
            arrow(c, ox, oy + 160, oy + 160 - 200 * back(up) * 0.9, CYAN, tank_a * up, w=14)
            text(c, "BUOYANCY", ox + 150, oy + 120, 28, CYAN, "black", align="left", a=tank_a * up, stroke=6)
            ds = ease(pr(t, wt("push", "aside") - 0.4, 0.5))
            displaced(c, ox, WL, oy + 70, 220, 220, tank_a * ds)
            eq = pr(t, wt("push", "equal") - 0.2, 0.4)
            pill(c, "PUSH UP = WEIGHT OF WATER PUSHED ASIDE", 540, 470, 24, DARK, CYAN, a=tank_a * ease(eq), sc=back(eq), pad=20, outline=CYAN)
        elif t < S("shape"):
            sink = eio(pr(t, wt("block", "sinks") - 0.5, 0.9))
            by = lerp(WL + 30, 1250, sink)
            steel_block(c, 540, by, tank_a)
            dsp = ease(pr(t, wt("block", "little") - 0.3, 0.4))
            displaced(c, 540, by - 55, by + 55, 150, 150, tank_a * dsp * (1 - sink))
            arrow(c, 540, by - 70, by - 70 - 60 * dsp, CYAN, tank_a * dsp, w=10)
            wgt = ease(pr(t, wt("block", "weight") - 0.3, 0.4))
            arrow(c, 540, by + 60, min(1310, by + 60 + 200 * wgt), RED, tank_a * wgt * (1 - sink * 0.8), w=14)
            lw = pr(t, wt("block", "little") - 0.2, 0.4) * (1 - ease(pr(t, wt("block", "weight") - 0.3, 0.3)))
            pill(c, "SMALL PUSH UP", 540, 470, 30, DARK, CYAN, a=tank_a * ease(lw), sc=back(lw), pad=22, outline=CYAN)
            hw = pr(t, wt("block", "weight") - 0.2, 0.4)
            pill(c, "WEIGHT WINS → SINKS", 540, 470, 30, "#450A0A", RED, a=tank_a * ease(hw), sc=back(hw), pad=22, outline=RED)
        else:
            m = ease(pr(t, S("shape") - 0.1, 0.6))
            steel_block(c, 540, WL - 120, tank_a * (1 - m))
            hy = lerp(WL - 140, WL + 10, eio(pr(t, wt("shape", "hull") - 0.2, 1.0)))
            hull_shape(c, 540, hy, tank_a * m)
            dsp = ease(pr(t, wt("shape", "far") - 0.4, 0.4))
            displaced(c, 540, WL, hy + 90, 470, 430, tank_a * dsp)
            arrow(c, 540, hy + 150, hy + 150 - 240 * dsp, CYAN, tank_a * dsp, w=16)
            hh = pr(t, wt("shape", "hollow") - 0.2, 0.4) * (1 - ease(pr(t, wt("shape", "far") - 0.3, 0.3)))
            pill(c, "SAME STEEL · HOLLOW HULL", 540, 470, 30, DARK, STEEL, a=tank_a * ease(hh), sc=back(hh), pad=22, outline=STEEL)
            fm = pr(t, wt("shape", "far") - 0.2, 0.4)
            pill(c, "FAR MORE WATER PUSHED ASIDE", 540, 470, 28, DARK, CYAN, a=tank_a * ease(fm), sc=back(fm), pad=22, outline=CYAN)

    if air_a > 0:
        # transverse cross-section of a ship: steel shell, decks, mostly air inside
        cx, top, bot = 540, 640, 1180
        tank(c, air_a, t, level=1000)
        c.move_to(cx - 330, top); c.line_to(cx - 330, bot - 120); c.curve_to(cx - 330, bot, cx - 250, bot, cx - 150, bot)
        c.line_to(cx + 150, bot); c.curve_to(cx + 250, bot, cx + 330, bot, cx + 330, bot - 120); c.line_to(cx + 330, top); c.close_path()
        ai = ease(pr(t, wt("air", "air") - 0.3, 0.4))
        c.set_source_rgba(*hexc("#E0F2FE")[:3], (0.08 + 0.25 * ai) * air_a); c.fill_preserve()
        c.set_line_width(18); fill(c, STEEL, air_a); c.stroke()
        for yy in (820, 980):
            c.set_line_width(8); c.move_to(cx - 322, yy); c.line_to(cx + 322, yy); c.stroke()
        text(c, "AIR", cx, 740, 60, "#E0F2FE", "black", a=air_a * ai, stroke=8)
        text(c, "AIR", cx, 910, 50, "#E0F2FE", "black", a=air_a * ai * 0.9, stroke=8)
        text(c, "AIR", cx, 1080, 40, "#E0F2FE", "black", a=air_a * ai * 0.8, stroke=8)
        dn = pr(t, wt("air", "density") - 0.3, 0.4)
        pill(c, "AVERAGE DENSITY < WATER", 540, 470, 32, "#052E2B", GREEN, a=air_a * ease(dn), sc=back(dn), pad=22, outline=GREEN)
        ms = pr(t, wt("air", "most") - 0.2, 0.4) * (1 - ease(pr(t, wt("air", "density") - 0.3, 0.3)))
        pill(c, "STEEL SHELL, MOSTLY AIR INSIDE", 540, 470, 28, DARK, STEEL, a=air_a * ease(ms), sc=back(ms), pad=22, outline=STEEL)

    if set_a > 0:
        tank(c, set_a, t)
        u = max(0.0, t - S("settle") + 0.1)
        draft = 70 - 70 * (1 - math.exp(-1.1 * u) * math.cos(3.0 * u)) if u > 0 else 70
        draft = -draft
        cargo_ship(c, 540, WL + 10, 1.05, set_a, t, draft=draft)
        tilt = 0.35 * math.exp(-1.0 * u) * math.cos(2.6 * u)
        eq = ease(pr(t, wt("settle", "exactly") - 0.3, 0.4))
        scale_beam(c, set_a, tilt * (1 - eq), "SHIP", "WATER PUSHED ASIDE", WHITE, FRESH)
        ex = pr(t, wt("settle", "exactly") - 0.2, 0.4)
        pill(c, "EXACTLY BALANCED", 540, 470, 32, "#052E2B", GREEN, a=set_a * ease(ex), sc=back(ex), pad=22, outline=GREEN)

    if pl_a > 0:
        fr = eio(pr(t, wt("plimsoll", "fresh") - 0.3, 1.0))
        plimsoll(c, pl_a, t, fr)
        pm = pr(t, wt("plimsoll", "plimsoll") - 0.2, 0.4) * (1 - ease(pr(t, wt("plimsoll", "fresh") - 0.3, 0.3)))
        pill(c, "LOAD LINE · PLIMSOLL MARK", 540, 470, 30, DARK, WHITE, a=pl_a * ease(pm), sc=back(pm), pad=22, outline=MUTED)
        fp = pr(t, wt("plimsoll", "fresh") - 0.2, 0.4)
        pill(c, "FRESH WATER: SITS LOWER", 540, 470, 30, DARK, FRESH, a=pl_a * ease(fp), sc=back(fp), pad=22, outline=FRESH)

    for lid, s, col in (("push", "THE RULE", CYAN), ("block", "THE BLOCK", RED), ("shape", "THE HULL", STEEL),
                        ("air", "THE SECRET", GREEN), ("settle", "THE BALANCE", GREEN), ("plimsoll", "THE LIMIT", WHITE)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "sinks") - 0.5, "low"), (wt("hook", "ship") - 0.3, "blip"), (wt("hook", "float") - 0.3, "pop"),
            (wt("push", "pushed") - 0.3, "rise"), (wt("push", "aside") - 0.4, "ping"),
            (wt("block", "weight") - 0.3, "warn"), (wt("block", "sinks") - 0.5, "low"),
            (wt("shape", "hull") - 0.2, "pop"), (wt("shape", "far") - 0.3, "rise"),
            (wt("air", "air") - 0.3, "ping"), (wt("air", "density") - 0.3, "success"),
            (wt("settle", "settles") - 0.2, "rumble"), (wt("settle", "exactly") - 0.3, "ok"),
            (wt("plimsoll", "plimsoll") - 0.2, "tick"), (wt("plimsoll", "fresh") - 0.3, "rise")]
