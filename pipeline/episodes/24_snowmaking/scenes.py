"""Episode 24: How ski resorts make snow."""
from hm.core import *
from hm.props import *

DARK = "#0F172A"
ICE = "#E0F2FE"
DROP = "#38BDF8"
SNOW = "#F8FAFC"
HEAT = "#F97316"


def hexflake(c, x, y, r, a, rot=0.0, col=SNOW, lw=3):
    if a <= 0: return
    c.save(); c.translate(x, y); c.rotate(rot)
    c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, col, a)
    for k in range(6):
        ang = k * math.pi / 3
        ex, ey = r * math.cos(ang), r * math.sin(ang)
        c.move_to(0, 0); c.line_to(ex, ey)
        for f in (0.45, 0.72):
            bx, by = ex * f, ey * f
            for s in (-1, 1):
                c.move_to(bx, by); c.line_to(bx + r * 0.28 * math.cos(ang + s * 0.8), by + r * 0.28 * math.sin(ang + s * 0.8))
    c.stroke(); c.restore()


def mountain(c, a):
    if a <= 0: return
    c.move_to(0, 1330); c.line_to(0, 900); c.line_to(300, 640); c.line_to(520, 760); c.line_to(760, 600); c.line_to(1080, 820); c.line_to(1080, 1330); c.close_path()
    fill(c, "#334155", a); c.fill()
    c.move_to(0, 1330); c.line_to(0, 1060); c.curve_to(300, 980, 700, 1100, 1080, 1000); c.line_to(1080, 1330); c.close_path()
    fill(c, SNOW, 0.92 * a); c.fill()
    for x, h in ((80, 1080), (980, 1020), (160, 1100)):
        c.move_to(x - 30, h); c.line_to(x, h - 90); c.line_to(x + 30, h); c.close_path(); fill(c, "#166534", a); c.fill()


def fan_gun(c, x, y, a, t, spray=1.0, s=1.0, plume_len=520):
    if a <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, s, s)
    # stand
    c.set_line_width(10); fill(c, "#475569", a)
    c.move_to(0, 0); c.line_to(-60, 160); c.move_to(0, 0); c.line_to(60, 160); c.stroke()
    c.save(); c.rotate(-0.35)
    rr(c, -40, -70, 230, 140, 30); fill(c, "#F59E0B", a); c.fill()           # barrel
    c.save(); c.translate(190, 0); c.scale(0.35, 1)
    c.arc(0, 0, 70, 0, 2 * math.pi); c.restore(); fill(c, "#1E293B", a); c.fill()
    for k in range(5):
        ang = t * 14 + k * 2 * math.pi / 5
        c.set_line_width(8); fill(c, "#94A3B8", a)
        c.move_to(190, 0); c.line_to(190 + 18 * math.cos(ang), 60 * math.sin(ang)); c.stroke()
    c.restore()
    c.restore()
    if spray > 0:
        ox, oy = x + 190 * s * math.cos(-0.35), y + 190 * s * math.sin(-0.35)
        for k in range(60):
            ph = (t * 0.55 + k * 0.0167) % 1
            d = plume_len * ph
            px = ox + d * math.cos(-0.35) * 1.0
            py = oy + d * math.sin(-0.35) + 0.0009 * d * d * 1.6 + 30 * math.sin(k * 3.1) * ph
            frozen = ph > 0.45
            if frozen:
                hexflake(c, px, py, 7 + 3 * ph, a * spray * (1 - 0.4 * ph), rot=k + t)
            else:
                c.arc(px, py, 4, 0, 2 * math.pi); fill(c, DROP, a * spray); c.fill()


def droplet_lab(c, a, t, evap, freeze, seed=0.0):
    """Close-up: a cloud of droplets; some evaporate (heat leaves), the rest freeze."""
    if a <= 0: return
    rr(c, 90, 600, 900, 700, 30); fill(c, "#0B1220", a); c.fill()
    for k in range(22):
        x = 170 + (k * 173) % 760; y = 680 + (k * 97) % 540
        x += 8 * math.sin(t * 1.2 + k); y += 6 * math.cos(t * 1.4 + k)
        evaporator = k % 4 == 0
        if evaporator:
            q = evap
            if q < 1:
                c.arc(x, y, 18 * (1 - q), 0, 2 * math.pi); fill(c, DROP, a * (1 - q)); c.fill()
            if q > 0:
                for j in range(3):
                    ph = (t * 0.9 + j / 3 + k * 0.1) % 1
                    c.set_line_width(4); fill(c, HEAT, a * q * (1 - ph))
                    yy = y - 30 - 90 * ph
                    c.move_to(x - 6, yy)
                    for s_ in range(1, 6): c.line_to(x - 6 + 8 * math.sin(s_ * 1.4 + t * 6), yy - s_ * 9)
                    c.stroke()
        else:
            f = freeze * (1.0 if seed <= 0 else 1.0)
            if seed > 0:
                c.arc(x, y, 5, 0, 2 * math.pi); fill(c, AMBER, a * seed); c.fill()
            if f < 1:
                c.arc(x, y, 18, 0, 2 * math.pi); fill(c, DROP, a * (1 - f)); c.fill()
            if f > 0:
                hexflake(c, x, y, 26 * f, a * f, rot=k * 0.4, lw=4)


def thermometer(c, x, y, a, level, col):
    if a <= 0: return
    rr(c, x - 22, y - 240, 44, 260, 22); fill(c, "#E2E8F0", a); c.fill()
    c.arc(x, y + 30, 40, 0, 2 * math.pi); c.fill()
    h = 220 * level
    rr(c, x - 12, y + 10 - h, 24, h + 10, 12); fill(c, col, a); c.fill()
    c.arc(x, y + 30, 30, 0, 2 * math.pi); fill(c, col, a); c.fill()


def humidity_chart(c, a, t, dot):
    if a <= 0: return
    ox, oy, w, h = 200, 1240, 740, 560
    c.set_line_width(5); fill(c, MUTED, a)
    c.move_to(ox, oy - h); c.line_to(ox, oy); c.line_to(ox + w, oy); c.stroke()
    text(c, "AIR TEMPERATURE →", ox + w, oy + 44, 24, MUTED, "black", align="right", a=a)
    c.save(); c.translate(ox - 30, oy - h / 2); c.rotate(-math.pi / 2)
    text(c, "HUMIDITY →", 0, 0, 24, MUTED, "black", a=a); c.restore()
    # freezing line at x = 32F
    fx = ox + w * 0.45
    c.set_line_width(3); c.set_dash([10, 8]); fill(c, WHITE, 0.6 * a); c.move_to(fx, oy); c.line_to(fx, oy - h); c.stroke(); c.set_dash([])
    text(c, "32°F", fx, oy + 44, 24, WHITE, "black", a=a)
    # snow-possible region: colder or drier (boundary slopes)
    c.move_to(ox, oy); c.line_to(ox, oy - h); c.line_to(ox + w * 0.35, oy - h); c.line_to(ox + w * 0.65, oy); c.close_path()
    c.set_source_rgba(*hexc(CYAN)[:3], 0.25 * a); c.fill()
    text(c, "SNOW", ox + w * 0.16, oy - h * 0.45, 40, CYAN, "black", a=a, stroke=6)
    text(c, "NO SNOW", ox + w * 0.75, oy - h * 0.55, 36, "#F87171", "black", a=a, stroke=6)
    if dot > 0:
        dx, dy = ox + w * 0.58, oy - h * 0.18
        glow(c, dx, dy, 50, YEL, 0.8 * a * dot)
        c.arc(dx, dy, 14 * back(dot), 0, 2 * math.pi); fill(c, YEL, a * dot); c.fill()
        text(c, "37°F, VERY DRY AIR", dx + 10, dy - 30, 26, YEL, "black", a=a * dot, stroke=6)


def pellet(c, x, y, r, a):
    g = cairo.RadialGradient(x - r * 0.3, y - r * 0.3, r * 0.1, x, y, r)
    g.add_color_stop_rgba(0, 1, 1, 1, a); g.add_color_stop_rgba(1, *hexc("#BAE6FD")[:3], a)
    c.arc(x, y, r, 0, 2 * math.pi); c.set_source(g); c.fill()


def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "HOW SKI RESORTS", "MAKE SNOW", S("mist"))

    hill_a = A * ease(pr(t, 0.05, 0.5)) * (1 - ease(pr(t, S("cool") - 0.2, 0.4)))
    lab_a = A * ease(pr(t, S("cool") - 0.1, 0.5)) * (1 - ease(pr(t, S("humidity") - 0.2, 0.4)))
    ch_a = A * ease(pr(t, S("humidity") - 0.1, 0.5)) * (1 - ease(pr(t, S("dense") - 0.2, 0.4)))
    dn_a = A * ease(pr(t, S("dense") - 0.1, 0.5))

    if hill_a > 0:
        mountain(c, hill_a)
        sp = ease(pr(t, wt("hook", "cannon") - 0.5, 0.4)) if t < S("mist") else 1.0
        fan_gun(c, 250, 1000, hill_a, t, spray=sp, s=1.0 if t < S("mist") else 1.15)
        if t < S("mist"):
            sk = pr(t, wt("hook", "sky") - 0.3, 0.4)
            pill(c, "NOT FROM THE SKY", 540, 470, 32, DARK, ICE, a=hill_a * ease(sk), sc=back(sk), pad=22, outline=ICE)
        else:
            fm = pr(t, wt("mist", "mist") - 0.2, 0.4) * (1 - ease(pr(t, wt("mist", "fan") - 0.3, 0.3)))
            pill(c, "FINE MIST OF WATER", 540, 470, 32, DARK, DROP, a=hill_a * ease(fm), sc=back(fm), pad=22, outline=DROP)
            fa = pr(t, wt("mist", "fan") - 0.2, 0.4)
            pill(c, "FAN OR COMPRESSED AIR", 540, 470, 30, DARK, AMBER, a=hill_a * ease(fa), sc=back(fa), pad=22, outline=AMBER)

    if lab_a > 0:
        ev = ease(pr(t, wt("cool", "evaporate") - 0.3, 0.8))
        fr = ease(pr(t, wt("cool", "freeze") - 0.3, 0.8))
        sd = ease(pr(t, wt("seed", "nucleating") - 0.3, 0.4))
        droplet_lab(c, lab_a, t, ev, fr, seed=sd)
        tl = 0.8 - 0.55 * ease(pr(t, wt("cool", "cooling") - 0.3, 1.0))
        thermometer(c, 940, 1180, lab_a * ease(pr(t, wt("cool", "heat") - 0.3, 0.4)), tl, lerp_col(HEAT, DROP, 1 - tl))
        ep = pr(t, wt("cool", "evaporate") - 0.2, 0.4) * (1 - ease(pr(t, wt("cool", "cooling") - 0.3, 0.3)))
        pill(c, "EVAPORATION PULLS OUT HEAT", 540, 470, 30, "#431407", HEAT, a=lab_a * ease(ep), sc=back(ep), pad=22, outline=HEAT)
        cf = pr(t, wt("cool", "cooling") - 0.2, 0.4) * (1 - ease(pr(t, S("seed") - 0.2, 0.3)))
        pill(c, "COLDER AIR → DROPLETS FREEZE", 540, 470, 28, DARK, ICE, a=lab_a * ease(cf), sc=back(cf), pad=22, outline=ICE)
        np_ = pr(t, wt("seed", "nucleating") - 0.2, 0.4)
        pill(c, "NUCLEATING AGENTS: FREEZE FASTER", 540, 470, 26, DARK, AMBER, a=lab_a * ease(np_), sc=back(np_), pad=22, outline=AMBER)

    if ch_a > 0:
        humidity_chart(c, ch_a, t, pr(t, wt("humidity", "above") - 0.4, 0.5))
        wb = pr(t, wt("humidity", "wet") - 0.2, 0.4) * (1 - ease(pr(t, wt("humidity", "dry") - 0.3, 0.3)))
        pill(c, "WATCH THE WET-BULB TEMPERATURE", 540, 470, 28, DARK, CYAN, a=ch_a * ease(wb), sc=back(wb), pad=22, outline=CYAN)
        hm_ = pr(t, wt("humidity", "humidity") - 0.2, 0.4) * (1 - ease(pr(t, wt("humidity", "wet") - 0.3, 0.3)))
        pill(c, "HUMIDITY MATTERS TOO", 540, 470, 30, DARK, WHITE, a=ch_a * ease(hm_), sc=back(hm_), pad=22, outline=MUTED)
        dr = pr(t, wt("humidity", "dry") - 0.2, 0.4)
        pill(c, "DRY AIR = SNOW ABOVE FREEZING", 540, 470, 28, DARK, YEL, a=ch_a * ease(dr), sc=back(dr), pad=22, outline=YEL)

    if dn_a > 0:
        nat = ease(pr(t, wt("dense", "cloud") - 0.6, 0.5))
        mach = ease(pr(t, wt("dense", "denser") - 0.4, 0.5))
        pellet(c, 330, 900, 120 * back(pr(t, wt("dense", "denser") - 0.4, 0.5)) if mach > 0 else 0.001, dn_a * mach)
        text(c, "MACHINE SNOW", 330, 1100, 30, ICE, "black", a=dn_a * mach, stroke=6)
        text(c, "DENSE + ROUND", 330, 1145, 26, MUTED, "black", a=dn_a * mach)
        hexflake(c, 760, 900, 140 * nat + 0.01, dn_a * nat, rot=t * 0.2, lw=10)
        text(c, "NATURAL SNOW", 760, 1100, 30, ICE, "black", a=dn_a * nat, stroke=6)
        text(c, "AIRY CRYSTALS", 760, 1145, 26, MUTED, "black", a=dn_a * nat)
        sd = pr(t, wt("dense", "short") - 0.3, 0.4)
        pill(c, "ONLY A SHORT DROP TO FREEZE", 540, 470, 28, DARK, ICE, a=dn_a * ease(sd), sc=back(sd), pad=22, outline=ICE)

    for lid, s, col in (("mist", "THE SPRAY", DROP), ("cool", "THE CHILL", HEAT), ("seed", "THE SHORTCUT", AMBER),
                        ("humidity", "THE WEATHER", CYAN), ("dense", "THE DIFFERENCE", ICE)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "sky") - 0.3, "blip"), (wt("hook", "cannon") - 0.5, "rumble"),
            (wt("mist", "mist") - 0.2, "rise"), (wt("mist", "fan") - 0.2, "tick"),
            (wt("cool", "evaporate") - 0.3, "low"), (wt("cool", "freeze") - 0.3, "ping"),
            (wt("seed", "nucleating") - 0.3, "pop"), (wt("humidity", "wet") - 0.2, "tick"),
            (wt("humidity", "above") - 0.4, "success"), (wt("dense", "denser") - 0.4, "pop"), (wt("dense", "cloud") - 0.6, "ping")]
