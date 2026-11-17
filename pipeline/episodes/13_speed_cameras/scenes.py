"""Episode 13 (GTA 6 week #3): How speed cameras catch you so fast (radar, lidar, average speed)."""
from hm.core import *
from hm.props import *

DARK = "#0F172A"
PINK = "#F472B6"
LASER = "#EF4444"
GROUND = 1150
LENS = (232, 722)


# ---------- props ----------
def road(c, a):
    if a <= 0: return
    c.rectangle(0, GROUND, 1080, 170); fill(c, "#1E293B", a); c.fill()
    c.set_line_width(6); c.set_dash([50, 34]); fill(c, "#475569", a)
    c.move_to(0, GROUND + 70); c.line_to(1080, GROUND + 70); c.stroke(); c.set_dash([])


def pole_camera(c, a, flash=0.0):
    if a <= 0: return
    c.rectangle(112, 740, 18, GROUND - 740); fill(c, "#64748B", a); c.fill()
    rr(c, 90, 690, 140, 66, 12); fill(c, "#CBD5E1", a); c.fill()
    rr(c, 80, 682, 160, 14, 6); fill(c, "#94A3B8", a); c.fill()
    c.arc(LENS[0], LENS[1], 22, 0, 2 * math.pi); fill(c, "#0B1220", a); c.fill()
    c.arc(LENS[0], LENS[1], 10, 0, 2 * math.pi); fill(c, CYAN, a); c.fill()
    if flash > 0:
        glow(c, LENS[0], LENS[1], 220, WHITE, 0.9 * flash * a)


def lidar_gun(c, a):
    if a <= 0: return
    x, y = 150, 840
    rr(c, x - 60, y - 40, 150, 70, 14); fill(c, "#334155", a); c.fill()
    rr(c, x - 20, y + 20, 44, 90, 10); fill(c, "#1E293B", a); c.fill()
    rr(c, x + 80, y - 28, 30, 46, 6); fill(c, "#0B1220", a); c.fill()
    c.arc(x + 100, y - 5, 10, 0, 2 * math.pi); fill(c, LASER, a); c.fill()
    rr(c, x - 50, y - 30, 70, 30, 6); fill(c, "#0E7490", a); c.fill()


def side_car(c, x, a, col=AMBER, wheel_t=0.0):
    """Car facing LEFT, front bumper at x."""
    if a <= 0: return
    yb = GROUND - 36
    for wx in (x + 90, x + 330):
        c.arc(wx, GROUND - 38, 38, 0, 2 * math.pi); fill(c, "#0B1220", a); c.fill()
        c.arc(wx, GROUND - 38, 16, 0, 2 * math.pi); fill(c, "#64748B", a); c.fill()
    c.move_to(x, yb); c.line_to(x, yb - 55); c.line_to(x + 30, yb - 80); c.line_to(x + 130, yb - 95)
    c.line_to(x + 175, yb - 170); c.line_to(x + 330, yb - 170); c.line_to(x + 370, yb - 95); c.line_to(x + 420, yb - 90)
    c.line_to(x + 420, yb); c.close_path(); fill(c, col, a); c.fill()
    c.move_to(x + 145, yb - 100); c.line_to(x + 182, yb - 158); c.line_to(x + 250, yb - 158); c.line_to(x + 250, yb - 100); c.close_path()
    fill(c, "#BAE6FD", 0.85 * a); c.fill()
    c.move_to(x + 262, yb - 100); c.line_to(x + 262, yb - 158); c.line_to(x + 322, yb - 158); c.line_to(x + 352, yb - 100); c.close_path()
    fill(c, "#BAE6FD", 0.85 * a); c.fill()
    c.rectangle(x - 4, yb - 46, 14, 18); fill(c, "#FEF08A", a); c.fill()
    # speed lines
    c.set_line_width(5); fill(c, WHITE, 0.35 * a)
    for k in range(3):
        L = 60 + 30 * ((k + wheel_t) % 1)
        c.move_to(x + 440, yb - 40 - 40 * k); c.line_to(x + 440 + L, yb - 40 - 40 * k); c.stroke()


def wave_arcs(c, cx, cy, d, t, a, col, spacing, speed, maxr, spread=0.32, rate=1.0):
    """Arcs radiating from (cx,cy) in direction d (+1 right / -1 left)."""
    if a <= 0: return
    base = 0 if d > 0 else math.pi
    c.set_line_width(7); c.set_line_cap(cairo.LINE_CAP_ROUND)
    off = (t * speed) % spacing
    r = off
    while r < maxr:
        fa = a * (1 - r / maxr) ** 0.5
        fill(c, col, fa)
        c.new_path(); c.arc(cx, cy, r + 8, base - spread, base + spread); c.stroke()
        r += spacing


def siren_scene(c, a, t, t0, shift):
    if a <= 0: return
    vs, v = 300.0, 215.0
    sx0, sy = 200, 880
    sx = sx0 + v * max(0.0, t - t0)
    sx = min(sx, 860)
    for k in range(14):
        te = t - k * 0.22
        if te < t0: break
        ex = min(sx0 + v * (te - t0), 860)
        r = vs * (t - te)
        if r > 900: continue
        c.set_line_width(5); fill(c, CYAN, a * max(0.0, 1 - r / 700))
        c.new_path(); c.arc(ex, sy, r, 0, 2 * math.pi); c.stroke()
    # source: siren light bar
    rr(c, sx - 50, sy - 26, 100, 52, 14); fill(c, "#E2E8F0", a); c.fill()
    on = (int(t * 6) % 2 == 0)
    rr(c, sx - 44, sy - 20, 42, 40, 10); fill(c, RED, a * (1 if on else 0.35)); c.fill()
    rr(c, sx + 2, sy - 20, 42, 40, 10); fill(c, "#3B82F6", a * (0.35 if on else 1)); c.fill()


def distance_graph(c, a, p, slope_a):
    if a <= 0: return
    ox, oy, w, h = 180, 1160, 740, 520
    c.set_line_width(5); fill(c, MUTED, a)
    c.move_to(ox, oy - h); c.line_to(ox, oy); c.line_to(ox + w, oy); c.stroke()
    text(c, "DISTANCE TO CAR", ox - 10, oy - h - 24, 26, MUTED, "black", align="left", a=a)
    n = 60
    shown = int(n * p)
    for i in range(shown):
        x = ox + 30 + (w - 60) * i / (n - 1)
        y = oy - h + 60 + (h - 140) * i / (n - 1) + 6 * math.sin(i * 2.1)
        c.arc(x, y, 6, 0, 2 * math.pi); fill(c, LASER, a); c.fill()
    if slope_a > 0:
        c.set_line_width(8); fill(c, GREEN, a * slope_a)
        c.move_to(ox + 30, oy - h + 60); c.line_to(lerp(ox + 30, ox + w - 30, slope_a), lerp(oy - h + 60, oy - 80, slope_a)); c.stroke()
    # time bracket
    c.set_line_width(4); fill(c, WHITE, a * p)
    c.move_to(ox + 30, oy + 30); c.line_to(ox + w - 30, oy + 30); c.stroke()
    for xx in (ox + 30, ox + w - 30):
        c.move_to(xx, oy + 18); c.line_to(xx, oy + 42); c.stroke()


def top_car(c, x, y, a, col=MUTED, hi=0.0, ang=0.0):
    if a <= 0: return
    c.save(); c.translate(x, y); c.rotate(ang)
    if hi > 0: glow(c, 0, 0, 120, LASER, 0.6 * hi * a)
    rr(c, -40, -70, 80, 140, 18); fill(c, lerp_col(col, LASER, hi), a); c.fill()
    rr(c, -30, -40, 60, 34, 8); fill(c, "#BAE6FD", 0.8 * a); c.fill()
    rr(c, -30, 22, 60, 26, 8); fill(c, "#BAE6FD", 0.6 * a); c.fill()
    c.restore()


def plate_tag(c, x, y, txt, a, sc=1.0):
    if a <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, sc, sc)
    rr(c, -175, -36, 350, 72, 14); fill(c, "#F8FAFC", a); c.fill()
    text(c, txt, 0, 10, 26, DARK, "black", a=a)
    c.restore()


def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "HOW SPEED CAMERAS", "CATCH YOU SO FAST", S("radar"))

    side_a = A * (ease(pr(t, 0.05, 0.5)) * (1 - ease(pr(t, S("doppler") - 0.2, 0.4)))
                  + ease(pr(t, S("lidar") - 0.1, 0.5)) * (1 - ease(pr(t, S("samples") - 0.2, 0.4))))
    dop_a = A * ease(pr(t, S("doppler") - 0.1, 0.5)) * (1 - ease(pr(t, S("lidar") - 0.2, 0.4)))
    graph_a = A * ease(pr(t, S("samples") - 0.1, 0.5)) * (1 - ease(pr(t, S("beam") - 0.2, 0.4)))
    beam_a = A * ease(pr(t, S("beam") - 0.1, 0.5)) * (1 - ease(pr(t, S("average") - 0.2, 0.4)))
    avg_a = A * ease(pr(t, S("average") - 0.1, 0.5))

    # ---- side view: hook, radar, lidar ----
    if side_a > 0:
        road(c, side_a)
        lid = t >= S("lidar") - 0.3
        if lid:
            lidar_gun(c, side_a)
        else:
            pole_camera(c, side_a, flash=max(0.0, 1 - abs(t - wt("hook", "cameras")) * 3) if t < S("radar") else 0)
        if t < S("radar"):
            cx = lerp(1100, 560, eout(pr(t, 0.1, 2.0)))
        elif not lid:
            cx = 600 - 30 * math.sin(t * 0.8)
        else:
            cx = 640 - 20 * math.sin(t * 0.8)
        side_car(c, cx, side_a, wheel_t=t * 3)
        if t < S("radar"):
            cp = pr(t, wt("hook", "cops") - 0.2, 0.4) * (1 - ease(pr(t, wt("hook", "real") - 0.2, 0.3)))
            pill(c, "IN GAMES: COPS, INSTANTLY", 540, 470, 30, DARK, PINK, a=side_a * ease(cp), sc=back(cp), pad=22, outline=PINK)
            if cp > 0:
                on = int(t * 6) % 2 == 0
                for dx, col in ((-40, RED), (40, "#3B82F6")):
                    glow(c, 540 + dx, 600, 70, col, 0.8 * side_a * ease(cp) * (1 if (dx < 0) == on else 0.3))
            rp = pr(t, wt("hook", "physics") - 0.3, 0.4)
            pill(c, "REAL LIFE: PHYSICS", 540, 470, 30, DARK, CYAN, a=side_a * ease(rp), sc=back(rp), pad=22, outline=CYAN)
        elif not lid:
            out_a = side_a * ease(pr(t, wt("radar", "fire") - 0.2, 0.4))
            wave_arcs(c, LENS[0] + 20, LENS[1] + 20, 1, t, out_a, CYAN, 70, 160, cx - LENS[0] - 10)
            back_a = side_a * ease(pr(t, wt("radar", "bounce") - 0.3, 0.4))
            wave_arcs(c, cx - 10, GROUND - 90, -1, t, back_a, AMBER, 42, 160, cx - LENS[0] - 30)
            rw = pr(t, wt("radar", "radio") - 0.2, 0.4) * (1 - ease(pr(t, wt("radar", "bounce") - 0.2, 0.3)))
            pill(c, "RADIO WAVES OUT", 540, 470, 30, DARK, CYAN, a=side_a * ease(rw), sc=back(rw), pad=22, outline=CYAN)
            df = pr(t, wt("radar", "different") - 0.2, 0.4)
            pill(c, "ECHO: DIFFERENT FREQUENCY", 540, 470, 30, DARK, AMBER, a=side_a * ease(df), sc=back(df), pad=22, outline=AMBER)
        else:
            on = ease(pr(t, wt("lidar", "fire") - 0.3, 0.4))
            gx, gy = 260, 835
            target = cx - 4
            if on > 0:
                c.set_line_width(4); fill(c, LASER, 0.18 * side_a * on); c.move_to(gx, gy); c.line_to(target, GROUND - 82); c.stroke()
                for k in range(5):
                    ph = (t * 1.3 + k / 5) % 1
                    going = ph < 0.5
                    u = ph * 2 if going else 2 - ph * 2
                    px = lerp(gx, target, u); py = lerp(gy, GROUND - 82, u)
                    glow(c, px, py, 30, LASER, 0.8 * side_a * on)
                    c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, LASER if going else "#FCA5A5", side_a * on)
                    c.move_to(px - 20, py - 1.5); c.line_to(px + 20, py + 1.5); c.stroke()
            ln = pr(t, wt("lidar", "lidar") - 0.2, 0.4) * (1 - ease(pr(t, wt("lidar", "infrared") - 0.3, 0.3)))
            pill(c, "LIDAR = LASER SPEED GUN", 540, 470, 30, DARK, LASER, a=side_a * ease(ln), sc=back(ln), pad=22, outline=LASER)
            ir = pr(t, wt("lidar", "infrared") - 0.2, 0.4) * (1 - ease(pr(t, wt("lidar", "time") - 0.3, 0.3)))
            pill(c, "SHORT INFRARED PULSES", 540, 470, 30, DARK, LASER, a=side_a * ease(ir), sc=back(ir), pad=22, outline=LASER)
            tm = pr(t, wt("lidar", "time") - 0.2, 0.4)
            pill(c, "TIME EACH ROUND TRIP", 540, 470, 30, DARK, WHITE, a=side_a * ease(tm), sc=back(tm), pad=22, outline=MUTED)
            if tm > 0:
                # stopwatch
                sx, sy = 540, 640
                c.arc(sx, sy, 48, 0, 2 * math.pi); fill(c, DARK, side_a * ease(tm)); c.fill_preserve()
                c.set_line_width(6); fill(c, WHITE, side_a * ease(tm)); c.stroke()
                ang = t * 9
                c.move_to(sx, sy); c.line_to(sx + 36 * math.sin(ang), sy - 36 * math.cos(ang)); c.stroke()
                rr(c, sx - 12, sy - 66, 24, 14, 4); c.fill()

    # ---- doppler ----
    if dop_a > 0:
        siren_scene(c, dop_a, t, S("doppler") - 0.2, 0)
        dp = pr(t, wt("doppler", "doppler") - 0.2, 0.4) * (1 - ease(pr(t, wt("doppler", "bigger") - 0.2, 0.3)))
        pill(c, "THE DOPPLER EFFECT", 540, 470, 32, DARK, CYAN, a=dop_a * ease(dp), sc=back(dp), pad=22, outline=CYAN)
        hi = pr(t, wt("doppler", "higher") - 0.2, 0.4)
        text(c, "SQUEEZED = HIGHER", 800, 1240, 30, YEL, "black", a=dop_a * ease(hi), stroke=6)
        text(c, "STRETCHED = LOWER", 270, 1240, 30, MUTED, "black", a=dop_a * ease(hi), stroke=6)
        bg = pr(t, wt("doppler", "bigger") - 0.2, 0.4)
        pill(c, "BIGGER SHIFT = FASTER CAR", 540, 470, 30, "#052E2B", GREEN, a=dop_a * ease(bg), sc=back(bg), pad=22, outline=GREEN)

    # ---- lidar readings graph ----
    if graph_a > 0:
        p = eio(pr(t, wt("samples", "hundreds") - 0.3, 2.4))
        sl = eio(pr(t, wt("samples", "change") - 0.2, 0.8))
        distance_graph(c, graph_a, p, sl)
        th = pr(t, wt("samples", "third") - 0.2, 0.4)
        text(c, "ABOUT 1/3 OF A SECOND", 550, 1240, 30, WHITE, "black", a=graph_a * ease(th), stroke=6)
        hr = pr(t, wt("samples", "hundreds") - 0.2, 0.4) * (1 - ease(pr(t, wt("samples", "change") - 0.2, 0.3)))
        pill(c, "HUNDREDS OF READINGS", 540, 470, 30, DARK, LASER, a=graph_a * ease(hr), sc=back(hr), pad=22, outline=LASER)
        sp = pr(t, wt("samples", "change") - 0.2, 0.4)
        pill(c, "CHANGE IN DISTANCE = SPEED", 540, 470, 30, "#052E2B", GREEN, a=graph_a * ease(sp), sc=back(sp), pad=22, outline=GREEN)

    # ---- narrow beam: top view of traffic ----
    if beam_a > 0:
        for x in (300, 540, 780):
            pass
        c.rectangle(240, 560, 600, 760); fill(c, "#1E293B", beam_a); c.fill()
        c.set_line_width(5); c.set_dash([40, 30]); fill(c, "#475569", beam_a)
        for x in (440, 640):
            c.move_to(x, 560); c.line_to(x, 1320); c.stroke()
        c.set_dash([])
        gx, gy = 540, 1300
        rad = ease(pr(t, wt("beam", "beam") - 0.3, 0.4)) * (1 - 0.6 * ease(pr(t, wt("beam", "narrow") - 0.2, 0.3)))
        c.move_to(gx, gy); c.line_to(220, 600); c.line_to(860, 600); c.close_path()
        c.set_source_rgba(*hexc(CYAN)[:3], 0.16 * beam_a * rad); c.fill()
        cars = [(340, 760), (540, 700), (740, 820), (340, 1040), (740, 1100), (540, 980)]
        tgt = (740, 820)
        nb = ease(pr(t, wt("beam", "narrow") - 0.2, 0.4))
        pk = ease(pr(t, wt("beam", "pick") - 0.2, 0.4))
        for (x, y) in cars:
            yy = y + 30 * math.sin(t * 0.7 + x)
            top_car(c, x, yy, beam_a, hi=pk if (x, y) == tgt else 0)
        ty = tgt[1] + 30 * math.sin(t * 0.7 + tgt[0])
        if nb > 0:
            c.set_line_width(6); fill(c, LASER, beam_a * nb)
            c.move_to(gx, gy); c.line_to(lerp(gx, tgt[0], nb), lerp(gy, ty, nb)); c.stroke()
        lidar_top = (gx, gy)
        c.arc(gx, gy, 24, 0, 2 * math.pi); fill(c, "#334155", beam_a); c.fill()
        text(c, "WIDE RADAR BEAM", 540, 640, 26, CYAN, "black", a=beam_a * rad, stroke=6)
        nw = pr(t, wt("beam", "narrow") - 0.2, 0.4)
        pill(c, "LASER: ~3 FT WIDE AT 1,000 FT", 540, 470, 28, DARK, LASER, a=beam_a * ease(nw), sc=back(nw), pad=22, outline=LASER)

    # ---- average speed ----
    if avg_a > 0:
        c.rectangle(0, 900, 1080, 260); fill(c, "#1E293B", avg_a); c.fill()
        c.set_line_width(5); c.set_dash([40, 30]); fill(c, "#475569", avg_a)
        c.move_to(0, 1030); c.line_to(1080, 1030); c.stroke(); c.set_dash([])
        cam = [(210, "A"), (870, "B")]
        u = eio(pr(t, wt("average", "cameras") - 0.6, 4.0))
        carx = lerp(-80, 1160, u)
        for x, lab in cam:
            c.rectangle(x - 7, 760, 14, 140); fill(c, "#64748B", avg_a); c.fill()
            rr(c, x - 40, 730, 80, 46, 10); fill(c, "#CBD5E1", avg_a); c.fill()
            text(c, lab, x, 770 - 60, 40, YEL, "black", a=avg_a * ease(pr(t, wt("average", "two") - 0.2, 0.4)), stroke=6)
            fl = max(0.0, 1 - abs(carx - x) / 90)
            glow(c, x, 760, 160, WHITE, 0.8 * fl * avg_a)
        top_car(c, carx, 1090, avg_a, col=AMBER, ang=math.pi / 2)
        ta = pr(t, wt("average", "plate") - 0.2, 0.4)
        plate_tag(c, 210, 1260, "HM 2026 · 10:00:00", avg_a * ease(ta), sc=back(ta) * 0.85)
        tb = pr(t, wt("average", "points") + 0.4, 0.4)
        plate_tag(c, 870, 1260, "HM 2026 · 10:00:36", avg_a * ease(tb), sc=back(tb) * 0.85)
        sk = pr(t, wt("average", "skip") - 0.2, 0.4) * (1 - ease(pr(t, wt("average", "distance") - 0.2, 0.3)))
        pill(c, "AVERAGE SPEED CAMERAS", 540, 470, 30, DARK, YEL, a=avg_a * ease(sk), sc=back(sk), pad=22, outline=YEL)
        dv = pr(t, wt("average", "distance") - 0.2, 0.4)
        pill(c, "DISTANCE ÷ TIME = AVERAGE SPEED", 540, 470, 28, "#052E2B", GREEN, a=avg_a * ease(dv), sc=back(dv), pad=22, outline=GREEN)
        # distance bracket
        c.set_line_width(4); fill(c, GREEN, avg_a * ease(dv))
        c.move_to(210, 880); c.line_to(870, 880); c.stroke()

    for lid, s, col in (("radar", "RADAR", CYAN), ("doppler", "THE PHYSICS", CYAN), ("lidar", "LIDAR", LASER),
                        ("samples", "THE MATH", GREEN), ("beam", "THE AIM", LASER), ("average", "THE SLOW CATCH", YEL)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "cops") - 0.2, "warn"), (wt("hook", "cameras") - 0.1, "pop"),
            (wt("radar", "fire") - 0.2, "ping"), (wt("radar", "bounce") - 0.3, "blip"),
            (wt("doppler", "doppler") - 0.2, "rise"), (wt("doppler", "bigger") - 0.2, "ok"),
            (wt("lidar", "fire") - 0.3, "tick"), (wt("lidar", "time") - 0.2, "tick"),
            (wt("samples", "hundreds") - 0.3, "rise"), (wt("samples", "change") - 0.2, "success"),
            (wt("beam", "narrow") - 0.2, "ping"), (wt("beam", "pick") - 0.2, "pop"),
            (wt("average", "plate") - 0.2, "blip"), (wt("average", "distance") - 0.2, "resolve")]
