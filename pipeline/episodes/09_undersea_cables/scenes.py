"""Episode 09: The internet runs along the ocean floor (submarine cables)."""
from hm.core import *
from hm.props import *

SURF = 560
SEABED = 1170
CABLE = [(130, 880), (230, 1060), (340, SEABED - 20), (740, SEABED - 20), (850, 1060), (950, 880)]
LASER = "#F472B6"


def cable_pt(u):
    """Point at fraction u (0..1) along the cable polyline."""
    segs = [(CABLE[i], CABLE[i + 1]) for i in range(len(CABLE) - 1)]
    lens = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs]
    d = u * sum(lens)
    for (a, b), L in zip(segs, lens):
        if d <= L: return lp(a, b, d / L)
        d -= L
    return CABLE[-1]


# ---------- props ----------
def ocean(c, a, t):
    if a <= 0: return
    # water
    c.move_to(0, SURF)
    for i in range(0, 1081, 20):
        c.line_to(i, SURF + 8 * math.sin(i / 60 + t * 2))
    c.line_to(1080, 1360); c.line_to(0, 1360); c.close_path()
    g = cairo.LinearGradient(0, SURF, 0, 1360)
    g.add_color_stop_rgba(0, *hexc("#0E7490")[:3], 0.85 * a); g.add_color_stop_rgba(1, *hexc("#082F49")[:3], a)
    c.set_source(g); c.fill()
    # seabed
    c.move_to(0, 1360)
    for i in range(0, 1081, 30):
        c.line_to(i, SEABED + 12 * math.sin(i / 70) + 8)
    c.line_to(1080, 1360); c.close_path(); fill(c, "#3F3A2E", a); c.fill()
    # continents
    for side in (-1, 1):
        x0 = 0 if side < 0 else 1080
        c.move_to(x0, 1360); c.line_to(x0, SURF - 40)
        c.line_to(x0 - side * 120, SURF - 40); c.line_to(x0 - side * 170, SURF + 30); c.line_to(x0 - side * 160, 900)
        c.line_to(x0 - side * 240, 1360); c.close_path(); fill(c, "#4D7C0F", a); c.fill()
        # building with dish
        bx = x0 - side * 70
        rr(c, bx - 30, SURF - 120, 60, 80, 6); fill(c, "#CBD5E1", a); c.fill()
        c.rectangle(bx - 18, SURF - 100, 12, 12); c.rectangle(bx + 6, SURF - 100, 12, 12); fill(c, "#0F172A", a); c.fill()


def cable(c, a, glow_=0.0, lw=9):
    if a <= 0: return
    if glow_ > 0:
        c.set_line_width(lw + 16); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_source_rgba(*hexc(YEL)[:3], 0.25 * glow_ * a)
        c.move_to(*CABLE[0]); [c.line_to(*p) for p in CABLE[1:]]; c.stroke()
    c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); fill(c, "#0F172A", a)
    c.move_to(*CABLE[0]); [c.line_to(*p) for p in CABLE[1:]]; c.stroke()
    c.set_line_width(3); fill(c, "#475569", a)
    c.move_to(*CABLE[0]); [c.line_to(*p) for p in CABLE[1:]]; c.stroke()


def data_pulses(c, a, t, fade=0.0, repeaters=0.0, n=6, speed=0.22):
    if a <= 0: return
    reps = (0.3, 0.5, 0.7)
    for k in range(n):
        u = (t * speed + k / n) % 1
        bright = 1.0
        if fade > 0:
            last = max([0.0] + [r for r in reps if r <= u]) if repeaters > 0 else 0.0
            bright = 1 - fade * min(1.0, (u - last) * 4.0)
            bright = max(0.15, bright)
        x, y = cable_pt(u)
        glow(c, x, y, 34, LASER, 0.9 * a * bright)
        c.arc(x, y, 7, 0, 2 * math.pi); fill(c, WHITE, a * bright); c.fill()
    if repeaters > 0:
        for r in reps:
            x, y = cable_pt(r)
            fl = max(0.0, math.sin(t * 6 + r * 9))
            glow(c, x, y, 50, GREEN, 0.5 * repeaters * a * fl)
            rr(c, x - 26, y - 14, 52, 28, 12); fill(c, "#94A3B8", repeaters * a); c.fill()
            rr(c, x - 18, y - 6, 36, 12, 6); fill(c, GREEN, repeaters * a * (0.4 + 0.6 * fl)); c.fill()


def satellite_icon(c, x, y, a, crossed):
    if a <= 0: return
    c.save(); c.translate(x, y)
    for sx in (-1, 1):
        rr(c, sx * 34 + (-70 if sx < 0 else 0), -16, 70, 32, 4); fill(c, "#1D4ED8", a); c.fill()
    rr(c, -26, -26, 52, 52, 8); fill(c, "#E2E8F0", a); c.fill()
    if crossed > 0:
        c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, RED, a)
        e = -80 + 160 * crossed
        c.move_to(-80, -60); c.line_to(e, -60 + 120 * crossed * 1.0 * (e + 80) / (160 * max(crossed, 1e-3))); c.stroke()
    c.restore()


def cross_section(c, cx, cy, R, a, t):
    """Cable cut open: plastic jacket, steel wires, copper power conductor, fibres in the centre."""
    if a <= 0: return
    glow(c, cx, cy, R * 1.5, CYAN, 0.2 * a)
    layers = [(1.0, "#1F2937"), (0.84, "#94A3B8"), (0.62, "#D97706"), (0.5, "#334155"), (0.3, "#0B1220")]
    for f, col in layers:
        c.arc(cx, cy, R * f, 0, 2 * math.pi); fill(c, col, a); c.fill()
    for k in range(22):
        ang = k * 2 * math.pi / 22
        c.arc(cx + R * 0.73 * math.cos(ang), cy + R * 0.73 * math.sin(ang), R * 0.085, 0, 2 * math.pi)
        fill(c, "#CBD5E1", a); c.fill()
    for k in range(8):
        ang = k * 2 * math.pi / 8 + t * 0.3
        rr_ = R * 0.17 if k else 0
        x = cx + R * 0.16 * math.cos(ang); y = cy + R * 0.16 * math.sin(ang)
        pulse = 0.5 + 0.5 * math.sin(t * 9 + k)
        glow(c, x, y, R * 0.12, LASER, 0.6 * a * pulse)
        c.arc(x, y, R * 0.045, 0, 2 * math.pi); fill(c, "#FBCFE8", a); c.fill()
    labels = [("PLASTIC JACKET", 1.0, -2.4), ("STEEL ARMOR", 0.78, -0.75), ("COPPER (POWER)", 0.56, 0.5), ("GLASS FIBERS", 0.18, 1.55)]
    return labels


def fibers(c, x, y, w, h, a, t):
    if a <= 0: return
    rr(c, x, y, w, h, 26); fill(c, "#0B1220", 0.95 * a); c.fill_preserve(); fill(c, "#334155", a); c.set_line_width(3); c.stroke()
    for k in range(4):
        yy = y + 70 + k * (h - 140) / 3
        rr(c, x + 30, yy - 9, w - 60, 18, 9); fill(c, "#BAE6FD", 0.22 * a); c.fill()
        for j in range(5):
            ph = (t * 0.45 + j / 5 + k * 0.13) % 1
            px = x + 30 + (w - 60) * ph
            glow(c, px, yy, 36, LASER, 0.9 * a)
            rr(c, px - 22, yy - 5, 44, 10, 5); fill(c, "#FDF2F8", a); c.fill()


def shark(c, x, y, s, a, t):
    if a <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, s, s)
    c.move_to(-120, 0); c.curve_to(-60, -40, 60, -40, 120, -6); c.line_to(120, 6); c.curve_to(60, 30, -60, 30, -120, 0); c.close_path()
    fill(c, "#94A3B8", a); c.fill()
    c.move_to(-10, -28); c.line_to(20, -80); c.line_to(40, -26); c.close_path(); c.fill()
    wag = 18 * math.sin(t * 6)
    c.move_to(-110, 0); c.line_to(-170, -40 + wag); c.line_to(-150, 0); c.line_to(-170, 40 + wag); c.close_path(); c.fill()
    c.arc(80, -8, 5, 0, 2 * math.pi); fill(c, "#0F172A", a); c.fill()
    c.restore()


def boat(c, x, y, a, t, anchor=0.0, net=0.0):
    if a <= 0: return
    bob = 6 * math.sin(t * 2)
    c.save(); c.translate(x, y + bob)
    c.move_to(-110, -10); c.line_to(110, -10); c.line_to(80, 30); c.line_to(-80, 30); c.close_path(); fill(c, "#B91C1C", a); c.fill()
    rr(c, -30, -60, 70, 50, 6); fill(c, "#E2E8F0", a); c.fill()
    c.set_line_width(5); fill(c, "#CBD5E1", a); c.move_to(-80, -10); c.line_to(-80, -90); c.stroke()
    c.restore()
    if net > 0:
        c.set_line_width(3); fill(c, "#CBD5E1", 0.8 * a)
        ny = lerp(y + 30, SEABED - 40, net)
        c.move_to(x - 100, y + 20); c.line_to(x - 200, ny); c.stroke()
        c.move_to(x - 100, y + 20); c.line_to(x - 60, ny); c.stroke()
        for k in range(5):
            c.move_to(x - 200 + k * 35, ny); c.line_to(x - 190 + k * 35, ny - 40); c.stroke()
    if anchor > 0:
        ay = lerp(y + 30, SEABED - 40, anchor)
        c.set_line_width(4); fill(c, "#94A3B8", a); c.move_to(x + 80, y + 20); c.line_to(x + 80, ay - 30); c.stroke()
        c.save(); c.translate(x + 80, ay)
        c.set_line_width(9); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, "#64748B", a)
        c.move_to(0, -34); c.line_to(0, 20); c.stroke()
        c.arc(0, 2, 26, 0.2, math.pi - 0.2); c.stroke()
        c.move_to(-16, -22); c.line_to(16, -22); c.stroke()
        c.restore()


# ---------- the episode ----------
def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "HOW DOES THE INTERNET", "CROSS THE OCEAN?", S("share"))
    zoom = max(ease(pr(t, S("size") + 0.4, 0.5)) * (1 - ease(pr(t, S("boost") - 0.2, 0.4))), 0.0)
    oa = A * ease(pr(t, 0.05, 0.5)) * (1 - 0.8 * zoom)
    if oa > 0:
        ocean(c, oa, t)
        cable(c, oa, glow_=ease(pr(t, wt("hook", "floor") - 0.3, 0.4)) * (1 - ease(pr(t, S("share") + 1.0, 0.5))))
        on = ease(pr(t, wt("hook", "ocean") - 0.3, 0.5))
        fade = ease(pr(t, wt("boost", "fades") - 0.2, 0.5))
        reps = ease(pr(t, wt("boost", "repeaters") - 0.2, 0.5))
        data_pulses(c, oa * on, t, fade=fade * (1 - 0.0), repeaters=reps)
        # satellite crossed out
        sat_a = ease(pr(t, wt("hook", "space") - 0.6, 0.4)) * (1 - ease(pr(t, S("share") + 1.5, 0.4)))
        if t < S("share"):
            satellite_icon(c, 850, 460, oa * sat_a, 0)
            cr = ease(pr(t, wt("hook", "never") - 0.1, 0.4))
            if cr > 0:
                c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, RED, oa * sat_a)
                c.move_to(770, 400); c.line_to(lerp(770, 930, cr), lerp(400, 520, cr)); c.stroke()
        # 99%
        p99 = pr(t, wt("share", "ninety") - 0.2, 0.5)
        if p99 > 0 and t < S("size") + 0.5:
            fa = 1 - ease(pr(t, S("size") + 0.2, 0.3))
            c.save(); c.translate(540, 800); safe_scale(c, back(p99), back(p99))
            text(c, "99%", 0, 50, 190, WHITE, "black", a=oa * fa * ease(p99), stroke=14)
            c.restore()
            text(c, "OF DATA CROSSING OCEANS", 540, 920, 36, YEL, "black", a=oa * fa * ease(pr(t, wt("share", "data") - 0.2, 0.4)), stroke=8)
            sl = pr(t, wt("share", "oceans") - 0.2, 0.4)
            pill(c, "SATELLITES: UNDER 5%", 540, 470, 28, "#0F172A", MUTED, a=oa * fa * ease(sl), sc=back(sl), pad=18, outline=MUTED)
        # power
        pw = ease(pr(t, wt("power", "power") - 0.2, 0.4)) * (1 - ease(pr(t, S("threat"), 0.4)))
        if pw > 0:
            for k in range(8):
                u = (k / 8 + t * 0.5) % 1
                x, y = cable_pt(u)
                glow(c, x, y, 26, YEL, 0.7 * pw * oa)
            v = pr(t, wt("power", "fifteen") - 0.2, 0.4)
            pill(c, "UP TO 15,000 VOLTS DC", 540, 470, 32, "#0F172A", YEL, a=oa * pw * ease(v), sc=back(v), pad=22, outline=YEL)
        rp = pr(t, wt("boost", "repeaters") - 0.1, 0.4) * (1 - ease(pr(t, S("power"), 0.3)))
        pill(c, "REPEATERS BOOST THE LIGHT", 540, 470, 30, "#052E2B", GREEN, a=oa * ease(rp), sc=back(rp), pad=22, outline=GREEN)
        km = pr(t, wt("boost", "hundred") - 0.2, 0.4) * (1 - ease(pr(t, S("power"), 0.3)))
        pill(c, "OFTEN ~100 KM APART", 540, 1290, 28, "#0F172A", WHITE, a=oa * ease(km), sc=back(km), pad=18, outline=MUTED)
        # threats
        th = A * ease(pr(t, S("threat") - 0.1, 0.4))
        if th > 0:
            sh = ease(pr(t, wt("threat", "sharks") - 0.3, 0.4))
            shark(c, lerp(-200, 420, sh) + 20 * math.sin(t), SEABED - 120, 0.8, th * sh * (1 - 0.6 * ease(pr(t, wt("threat", "fishing") - 0.2, 0.4))), t)
            bt = ease(pr(t, wt("threat", "fishing") - 0.3, 0.5))
            boat(c, lerp(1250, 700, bt), SURF - 20, th * bt, t, anchor=ease(pr(t, wt("threat", "anchors") - 0.2, 0.7)), net=ease(pr(t, wt("threat", "boats") - 0.2, 0.7)))
            hit = pr(t, wt("threat", "anchors") + 0.4, 0.4)
            if hit > 0:
                glow(c, 780, SEABED - 40, 90, RED, 0.8 * th * (1 - 0.5 * hit))
            rare = pr(t, wt("threat", "bitten") - 0.1, 0.4) * (1 - ease(pr(t, wt("threat", "fishing") - 0.2, 0.3)))
            pill(c, "SHARK BITES: RARE", 540, 470, 30, "#0F172A", MUTED, a=th * ease(rare), sc=back(rare), pad=20, outline=MUTED)
            top = pr(t, wt("threat", "fishing") - 0.1, 0.4)
            pill(c, "#1 CAUSE: FISHING BOATS & ANCHORS", 540, 470, 28, "#450A0A", RED, a=th * ease(top), sc=back(top), pad=20, outline=RED)

    # ---- zoom: cross-section, then fibres ----
    if zoom > 0:
        za = A * zoom
        xs = ease(pr(t, S("size") + 0.4, 0.5)) * (1 - ease(pr(t, S("light") - 0.1, 0.4)))
        if xs > 0:
            k = back(pr(t, S("size") + 0.4, 0.6))
            labels = cross_section(c, 540, 830, 230 * k, za * xs, t)
            if labels:
                for (lab, f, ang) in labels:
                    la = ease(pr(t, wt("size", "thick") - 0.2 + 0.15 * labels.index((lab, f, ang)), 0.4))
                    ex, ey = 540 + 230 * f * math.cos(ang) * 0.9, 830 + 230 * f * math.sin(ang) * 0.9
                    lx = 540 + 330 * math.cos(ang); ly = 830 + 330 * math.sin(ang)
                    c.set_line_width(2); fill(c, WHITE, 0.6 * za * xs * la); c.move_to(ex, ey); c.line_to(lx, ly); c.stroke()
                    text(c, lab, lx, ly + (-14 if ly < 830 else 34), 24, WHITE, "xbold", a=za * xs * la)
            inch = pr(t, wt("size", "inch") - 0.2, 0.4)
            pill(c, "≈ 25 MM · ABOUT 1 INCH", 540, 470, 30, "#0F172A", CYAN, a=za * xs * ease(inch), sc=back(inch), pad=22, outline=CYAN)
        fb = ease(pr(t, S("light") - 0.1, 0.5))
        if fb > 0:
            fibers(c, 110, 600, 860, 520, za * fb, t)
            hr = pr(t, wt("light", "hair") - 0.2, 0.4)
            pill(c, "GLASS FIBERS · THIN AS A HAIR", 540, 470, 30, "#0F172A", CYAN, a=za * fb * ease(hr), sc=back(hr), pad=22, outline=CYAN)
            ls = pr(t, wt("light", "laser") - 0.2, 0.4)
            pill(c, "DATA = FLASHES OF LASER LIGHT", 540, 1220, 30, "#0F172A", LASER, a=za * fb * ease(ls), sc=back(ls), pad=22, outline=LASER)

    for lid, s, col in (("share", "THE BACKBONE", CYAN), ("size", "THE CABLE", CYAN), ("light", "THE LIGHT", LASER),
                        ("boost", "THE BOOST", GREEN), ("power", "THE POWER", YEL), ("threat", "THE DANGER", RED)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "never") - 0.1, "low"), (wt("hook", "ocean") - 0.3, "ping"),
            (wt("share", "ninety") - 0.2, "pop"), (wt("share", "oceans") - 0.2, "blip"),
            (S("size") + 0.4, "rise"), (wt("size", "inch") - 0.2, "pop"),
            (wt("light", "hair") - 0.2, "blip"), (wt("light", "laser") - 0.2, "ping"),
            (wt("boost", "fades") - 0.2, "low"), (wt("boost", "repeaters") - 0.2, "success"),
            (wt("power", "power") - 0.2, "rumble"), (wt("power", "fifteen") - 0.2, "pop"),
            (wt("threat", "sharks") - 0.3, "low"), (wt("threat", "fishing") - 0.2, "warn"), (wt("threat", "anchors") + 0.4, "rumble")]
