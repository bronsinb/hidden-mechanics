"""Episode 05: How a red light knows you're waiting (inductive loop detector)."""
from hm.core import *
from hm.props import *

ROAD_X0, ROAD_X1 = 250, 830
STOP_Y = 610
LOOP = (380, 660, 320, 300)          # x, y, w, h of the loop rectangle
COPPER = "#F59E0B"
CAB = (965, 1190)


# ---------- props for this episode ----------
def road(c, a, cut_glow=0.0, wire=0.0, t=0.0):
    if a <= 0: return
    rr(c, ROAD_X0, 380, ROAD_X1 - ROAD_X0, 980, 0); fill(c, "#1F2937", a); c.fill()
    # lane edges and centre dashes
    fill(c, "#E2E8F0", 0.8 * a)
    for x in (ROAD_X0 + 14, ROAD_X1 - 22):
        c.rectangle(x, 380, 8, 980); c.fill()
    # stop bar
    c.rectangle(ROAD_X0 + 30, STOP_Y - 12, ROAD_X1 - ROAD_X0 - 60, 24); fill(c, WHITE, 0.9 * a); c.fill()
    # saw cuts (loop outline + lead-in)
    x, y, w, h = LOOP
    col = lerp_col("#0B1220", YEL, cut_glow)
    c.set_line_width(6 + 4 * cut_glow); c.set_source_rgba(*col[:3], a)
    c.rectangle(x, y, w, h); c.stroke()
    c.move_to(x + w, y + h / 2); c.line_to(ROAD_X1, y + h / 2); c.stroke()
    if cut_glow > 0:
        c.set_line_width(22); c.set_source_rgba(*hexc(YEL)[:3], 0.18 * cut_glow * a)
        c.rectangle(x, y, w, h); c.stroke()
    if wire > 0:
        for k in range(3):
            c.set_line_width(3); fill(c, COPPER, wire * a)
            c.rectangle(x - 6 + k * 6, y - 6 + k * 6, w + 12 - k * 12, h + 12 - k * 12); c.stroke()


def traffic_light(c, x, y, s, a, state):
    """state: 0 red, 1 green (blends)."""
    if a <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, s, s)
    rr(c, -8, 150, 16, 260, 6); fill(c, "#475569", a); c.fill()
    rr(c, -60, -170, 120, 330, 26); fill(c, "#0F172A", a); c.fill_preserve(); fill(c, "#334155", a); c.set_line_width(4); c.stroke()
    for i, (col, on) in enumerate(((RED, 1 - state), (AMBER, 0.0), (GREEN, state))):
        cy = -110 + i * 105
        if on > 0: glow(c, 0, cy, 110, col, 0.6 * on * a)
        c.arc(0, cy, 38, 0, 2 * math.pi); fill(c, lerp_col("#1E293B", col, 0.15 + 0.85 * on), a); c.fill()
    c.restore()


def cabinet(c, a, active=0.0, t=0.0):
    if a <= 0: return
    x, y = CAB
    if active > 0: glow(c, x, y, 130, CYAN, 0.45 * active * a)
    rr(c, x - 70, y - 90, 140, 180, 14); fill(c, "#64748B", a); c.fill_preserve(); fill(c, "#94A3B8", a); c.set_line_width(4); c.stroke()
    rr(c, x - 50, y - 70, 100, 50, 8); fill(c, "#0F172A", a); c.fill()
    blink = 0.5 + 0.5 * math.sin(t * 9)
    c.arc(x - 25, y - 45, 7, 0, 2 * math.pi); fill(c, GREEN, a * (0.4 + 0.6 * active * blink)); c.fill()
    c.arc(x, y - 45, 7, 0, 2 * math.pi); fill(c, CYAN, a * (0.3 + 0.7 * active)); c.fill()
    text(c, "DETECTOR", x, y + 120, 22, MUTED, "xbold", a=a)
    # lead wire from loop to cabinet
    lx, ly, lw, lh = LOOP
    fill(c, COPPER, 0.8 * a); c.set_line_width(4)
    c.move_to(ROAD_X1, ly + lh / 2); c.line_to(x - 40, ly + lh / 2); c.line_to(x - 40, y - 90); c.stroke()


def current_dots(c, a, t, speed=1.0):
    if a <= 0: return
    x, y, w, h = LOOP
    per = 2 * (w + h)
    for k in range(14):
        d = (k / 14 * per + t * 260 * speed) % per
        if d < w: px, py = x + d, y
        elif d < w + h: px, py = x + w, y + (d - w)
        elif d < 2 * w + h: px, py = x + w - (d - w - h), y + h
        else: px, py = x, y + h - (d - 2 * w - h)
        glow(c, px, py, 22, COPPER, 0.7 * a)
        c.arc(px, py, 6, 0, 2 * math.pi); fill(c, "#FEF3C7", a); c.fill()


def field_rings(c, a, strength, t):
    if a <= 0 or strength <= 0: return
    x, y, w, h = LOOP
    cx, cy = x + w / 2, y + h / 2
    rgb = hexc(PURPLE)
    for k in range(4):
        ph = (t * 0.7 + k / 4) % 1
        sc = 0.3 + 0.9 * ph
        c.save(); c.translate(cx, cy); safe_scale(c, sc, sc)
        rr(c, -w / 2 - 10, -h / 2 - 10, w + 20, h + 20, 60)
        c.restore()
        c.set_line_width(4); c.set_dash([14, 10])
        c.set_source_rgba(rgb[0], rgb[1], rgb[2], a * strength * (1 - ph) * 0.9); c.stroke(); c.set_dash([])


def eddies(c, cx, cy, a, t):
    if a <= 0: return
    for k, (dx, dy) in enumerate(((-40, -90), (40, -10), (-30, 80), (35, 140))):
        x, y = cx + dx, cy + dy
        r = 26
        rot = t * 6 + k
        c.set_line_width(5); fill(c, CYAN, a); c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.arc(x, y, r, rot, rot + 4.6); c.stroke()
        ex, ey = x + r * math.cos(rot + 4.6), y + r * math.sin(rot + 4.6)
        ang = rot + 4.6 + math.pi / 2
        c.move_to(ex, ey); c.line_to(ex - 12 * math.cos(ang - 0.6), ey - 12 * math.sin(ang - 0.6)); c.stroke()


def meter(c, x, y, a, val, label):
    if a <= 0: return
    rr(c, x, y, 470, 120, 22); fill(c, "#0F172A", 0.92 * a); c.fill_preserve(); fill(c, PURPLE, 0.6 * a); c.set_line_width(3); c.stroke()
    text(c, label, x + 24, y + 42, 22, MUTED, "xbold", "left", a=a)
    rr(c, x + 24, y + 64, 422, 30, 15); fill(c, "#1E293B", a); c.fill()
    rr(c, x + 24, y + 64, max(30, 422 * cl(val)), 30, 15); fill(c, PURPLE, a); c.fill()


def bike(c, cx, cy, s, a):
    """Top view of a bicycle, front wheel up."""
    if a <= 0: return
    c.save(); c.translate(cx, cy); safe_scale(c, s, s)
    for wy in (-95, 95):
        rr(c, -9, wy - 62, 18, 124, 9); fill(c, "#94A3B8", a); c.fill()
        rr(c, -4, wy - 62, 8, 124, 4); fill(c, "#0F172A", a); c.fill()
    c.set_line_width(8); fill(c, CYAN, a); c.move_to(0, -95); c.line_to(0, 95); c.stroke()
    c.set_line_width(7); fill(c, "#CBD5E1", a); c.move_to(-48, -110); c.line_to(48, -110); c.stroke()
    rr(c, -14, 30, 28, 44, 10); fill(c, "#334155", a); c.fill()
    # rider (head + shoulders)
    c.arc(0, -10, 34, 0, 2 * math.pi); fill(c, "#F59E0B", a); c.fill()
    rr(c, -46, 10, 92, 34, 16); fill(c, "#2563EB", a); c.fill()
    c.restore()


# ---------- the episode ----------
def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "HOW DOES A RED LIGHT", "KNOW YOU'RE WAITING?", S("loop"))
    scene = A * ease(pr(t, 0.1, 0.5)) * (1 - ease(pr(t, S("bike") - 0.15, 0.35)))
    bike_scene = A * ease(pr(t, S("bike") - 0.1, 0.4))

    # ----- main intersection (hook .. detect) -----
    if scene > 0:
        cut = ease(pr(t, wt("hook", "look") - 0.1, 0.5)) * (1 - ease(pr(t, wt("loop", "loop") + 0.6, 0.6)))
        wire = ease(pr(t, wt("loop", "loop") - 0.2, 0.6))
        road(c, scene, cut_glow=cut, wire=wire, t=t)
        green = ease(pr(t, wt("detect", "green") - 0.1, 0.5))
        traffic_light(c, 945, 540, 0.75, scene, green)
        act = ease(pr(t, wt("field", "box") - 0.2, 0.5))
        cabinet(c, scene * ease(pr(t, wt("field", "box") - 0.4, 0.4)), active=act, t=t)
        cur = ease(pr(t, wt("field", "current") - 0.4, 0.5))
        current_dots(c, scene * cur, t)
        # car: drives in, stops at the stop bar, then moves when green
        x, y, w, h = LOOP
        arrive = eout(pr(t, 0.2, 2.6))
        go = eio(pr(t, wt("detect", "way") + 0.2, 1.4))
        car_y = lerp(1500, y + h / 2, arrive) - 900 * go
        # car is pulled back off the loop during "field" so the field reads clearly, then rolls on at "rolls"
        off = ease(pr(t, S("field") - 0.4, 0.6)) * (1 - ease(pr(t, wt("car", "rolls") - 0.3, 1.0)))
        car_y += 260 * off
        weaken = ease(pr(t, wt("car", "weaken") - 0.3, 0.6))
        fstrength = ease(pr(t, wt("field", "magnetic") - 0.3, 0.6)) * (1 - 0.65 * weaken)
        field_rings(c, scene, fstrength, t)
        car(c, 540, car_y, 0.52, alpha=scene)
        eddies(c, 540, car_y, scene * ease(pr(t, wt("car", "swirl") - 0.4, 0.4)) * (1 - ease(pr(t, S("detect") + 0.5, 0.4))), t)
        if t < S("loop"):
            ld = pr(t, wt("hook", "look") - 0.1, 0.4)
            pill(c, "LOOK DOWN", 540, 1310, 32, "#0F172A", YEL, a=scene * ease(ld), sc=back(ld), pad=24, outline=YEL)
        wl = pr(t, wt("loop", "loop") - 0.1, 0.4) * (1 - ease(pr(t, S("field") - 0.1, 0.3)))
        pill(c, "WIRE LOOP UNDER THE ROAD", 540, 1310, 30, "#0F172A", COPPER, a=scene * ease(wl), sc=back(wl), pad=22, outline=COPPER)
        mf = pr(t, wt("field", "magnetic") - 0.2, 0.4) * (1 - ease(pr(t, S("car") - 0.1, 0.3)))
        pill(c, "MAGNETIC FIELD", 540, 1310, 32, "#0F172A", PURPLE, a=scene * ease(mf), sc=back(mf), pad=24, outline=PURPLE)
        ac = pr(t, wt("field", "alternating") - 0.2, 0.4) * (1 - ease(pr(t, S("car") - 0.1, 0.3)))
        pill(c, "AC · 10–200 kHz", 945, 1010, 26, "#0F172A", COPPER, a=scene * ease(ac), sc=back(ac), pad=16, outline=COPPER)
        # inductance meter during car / detect
        ma = ease(pr(t, wt("car", "tiny") - 0.3, 0.4)) * (1 - ease(pr(t, wt("detect", "way"), 0.4)))
        if ma > 0:
            meter(c, 60, 400, ma, 0.85 - 0.45 * weaken, "LOOP INDUCTANCE")
        sig = pr(t, wt("detect", "tells") - 0.1, 1.0)
        if 0 < sig < 1:
            px, py = lp((CAB[0], CAB[1] - 90), (945, 660), eio(sig))
            glow(c, px, py, 40, CYAN, 0.9 * scene); c.arc(px, py, 10, 0, 2 * math.pi); fill(c, WHITE, scene); c.fill()
        cw = pr(t, wt("detect", "car") - 0.1, 0.4) * (1 - ease(pr(t, S("bike") - 0.3, 0.3)))
        pill(c, "CAR WAITING", 540, 1310, 32, "#052E2B", GREEN, a=scene * ease(cw), sc=back(cw), pad=24, outline=GREEN)

    # ----- bike scene -----
    if bike_scene > 0:
        road(c, bike_scene, cut_glow=ease(pr(t, wt("tip", "cut") - 0.3, 0.5)), wire=0.0, t=t)
        traffic_light(c, 945, 540, 0.75, bike_scene, 0)
        x, y, w, h = LOOP
        move = eio(pr(t, wt("tip", "stop") - 0.1, 1.2))
        # bike sits in the middle of the loop (weak spot), then moves so its wheels are over the cut line
        bx = lerp(x + w / 2, x + 4, move)
        bike(c, bx, y + h / 2 + 40, 1.0, bike_scene)
        weak = 0.12 + 0.55 * move
        meter(c, 60, 400, bike_scene, weak, "LOOP SIGNAL CHANGE")
        lm = pr(t, wt("bike", "less") - 0.1, 0.4) * (1 - ease(pr(t, S("tip"), 0.3)))
        pill(c, "LESS METAL · WEAK SIGNAL", 540, 1310, 30, "#450A0A", RED, a=bike_scene * ease(lm), sc=back(lm), pad=22, outline=RED)
        ms = pr(t, wt("tip", "most") - 0.1, 0.4)
        if ms > 0:
            c.save(); c.translate(540, 1310); safe_scale(c, back(ms), back(ms))
            rr(c, -280, -38, 560, 76, 38); fill(c, "#052E2B", bike_scene); c.fill_preserve(); fill(c, GREEN, bike_scene); c.set_line_width(3); c.stroke()
            text(c, "WHEELS OVER THE CUT", -30, 12, 32, GREEN, "xbold", a=bike_scene)
            check(c, 225, 0, 34, GREEN, bike_scene, lw=8, p=pr(t, wt("tip", "most") + 0.1, 0.4))
            c.restore()

    for lid, s, col in (("loop", "THE LOOP", COPPER), ("field", "THE FIELD", PURPLE), ("car", "THE CAR", CYAN),
                        ("detect", "THE SIGNAL", GREEN), ("bike", "THE CATCH", RED), ("tip", "TIP FOR CYCLISTS", GREEN)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(1.6, "low"), (wt("hook", "look") - 0.1, "rise"), (wt("loop", "loop") - 0.2, "pop"),
            (wt("field", "box") - 0.3, "pop"), (wt("field", "current") - 0.4, "ping"), (wt("field", "magnetic") - 0.3, "wake"),
            (wt("car", "rolls") - 0.3, "rumble"), (wt("car", "swirl") - 0.4, "blip"), (wt("car", "weaken") - 0.3, "low"),
            (wt("detect", "tells") - 0.1, "blip"), (wt("detect", "green") - 0.1, "success"),
            (wt("bike", "bike") - 0.1, "pop"), (wt("bike", "miss") - 0.1, "warn"),
            (wt("tip", "stop") - 0.1, "rise"), (wt("tip", "most") - 0.1, "ok")]
