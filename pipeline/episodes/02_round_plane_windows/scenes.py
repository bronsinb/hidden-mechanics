"""Episode 02: Why airplane windows are round."""
import numpy as np
from hm.core import *
from hm.props import *

SKY_T, SKY_B = "#7DD3FC", "#2563EB"
METAL, METAL_D = "#94A3B8", "#475569"
PANEL = (90, 470, 900, 760)          # x, y, w, h of the skin panel
HOLE_C = (540, 850)


# ---------- props for this episode ----------
def window(c, cx, cy, w, h, m, a=1.0, glass=True, frame_col="#CBD5E1"):
    """m = 0 round(ed) window, m = 1 square window."""
    if a <= 0: return
    r = lerp(min(w, h) * 0.48, 8, cl(m))
    fw = 22
    rr(c, cx - w / 2 - fw, cy - h / 2 - fw, w + 2 * fw, h + 2 * fw, r + fw * (1 - m * 0.6))
    fill(c, frame_col, a); c.fill()
    rr(c, cx - w / 2, cy - h / 2, w, h, r)
    if glass:
        g = cairo.LinearGradient(0, cy - h / 2, 0, cy + h / 2)
        g.add_color_stop_rgba(0, *hexc(SKY_T)[:3], a); g.add_color_stop_rgba(1, *hexc(SKY_B)[:3], a)
        c.set_source(g); c.fill()
        # cloud + glint
        c.save(); rr(c, cx - w / 2, cy - h / 2, w, h, r); c.clip()
        fill(c, "#FFFFFF", 0.85 * a)
        for dx, dy, rad in ((-0.18, 0.22, 0.16), (0.02, 0.18, 0.2), (0.22, 0.24, 0.14)):
            c.new_sub_path(); c.arc(cx + dx * w, cy + dy * h, rad * w, 0, 2 * math.pi)
        c.fill()
        c.move_to(cx - w * 0.3, cy - h * 0.5); c.line_to(cx - w * 0.1, cy - h * 0.5); c.line_to(cx - w * 0.5, cy + h * 0.1); c.line_to(cx - w * 0.5, cy - h * 0.1); c.close_path()
        fill(c, "#FFFFFF", 0.18 * a); c.fill()
        c.restore()
    else:
        fill(c, "#0B1220", a); c.fill()


def crack(c, x, y, ang, length, prog, a, seed=3, lw=7, col=RED):
    if prog <= 0 or a <= 0: return
    rnd = np.random.default_rng(seed)
    n = 9
    pts = [(x, y)]
    for i in range(1, n + 1):
        d = length * i / n
        jit = rnd.uniform(-0.45, 0.45)
        pts.append((x + d * math.cos(ang + jit * 0.5), y + d * math.sin(ang + jit * 0.5)))
    k = prog * n
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    for width, colr, aa in ((lw + 10, col, 0.25), (lw, col, 1.0), (2, "#FEE2E2", 0.9)):
        c.set_line_width(width); fill(c, colr, a * aa)
        c.move_to(*pts[0])
        for i in range(1, int(k) + 1): c.line_to(*pts[i])
        if int(k) < n:
            c.line_to(*lp(pts[int(k)], pts[int(k) + 1], k - int(k)))
        c.stroke()
    tip = pts[min(n, int(k))]
    glow(c, tip[0], tip[1], 40, col, 0.6 * a)


def clearance(xs, m, R, A):
    rnd_ = np.sqrt(np.clip(R * R - xs * xs, 0, None))
    sq = np.where(np.abs(xs) <= A, A, 0.0)
    return rnd_ * (1 - m) + sq * m


def stress_field(c, t, m, a, hot=0.0, crack_mask=0.0):
    """Horizontal stress lines flowing around a window-shaped hole at HOLE_C. m: 0 round .. 1 square."""
    if a <= 0: return
    px, py, pw, ph = PANEL
    cx, cy = HOLE_C
    R, A = 130, 118
    xs = np.linspace(px - cx + 10, px + pw - cx - 10, 260)
    base = clearance(xs, m, R, A) + 26
    c.save(); rr(c, px, py, pw, ph, 36); c.clip()
    # panel
    g = cairo.LinearGradient(px, py, px + pw, py + ph)
    g.add_color_stop_rgba(0, *hexc("#1E293B")[:3], 0.95 * a); g.add_color_stop_rgba(1, *hexc("#0F172A")[:3], 0.95 * a)
    c.set_source(g); c.paint()
    for yy in range(py + 40, py + ph, 120):
        for xx in range(px + 40, px + pw, 120):
            c.new_sub_path(); c.arc(xx, yy, 5, 0, 2 * math.pi)
    fill(c, "#334155", a); c.fill()
    rgb_c, rgb_r = hexc(CYAN), hexc(RED)
    for y0 in np.arange(-ph / 2 + 30, ph / 2 - 20, 34):
        ay = abs(y0)
        fall = math.exp(-max(0.0, ay - R) / (1.6 * R))
        w = int(6 + 26 * (1 - m) + 6 * min(1, ay / R))
        k = np.ones(w) / w
        cl_ = np.convolve(np.pad(base, (w, w), mode="edge"), k, mode="same")[w:-w]
        yy = np.sign(y0 if y0 != 0 else 1) * np.sqrt(y0 * y0 + (cl_ * fall) ** 2)
        slope = np.abs(np.gradient(yy, xs))
        stress = np.clip(slope * 0.9, 0, 1) * hot
        c.set_line_width(3.2 + 1.6 * fall)
        seglen = np.hypot(np.diff(xs), np.diff(yy))
        cum = np.concatenate([[0.0], np.cumsum(seglen)])
        for i in range(len(xs) - 1):
            c.set_dash([16, 12], cum[i] - t * 70)
            s = stress[i]
            col = tuple(lerp(rgb_c[j], rgb_r[j], s) for j in range(3))
            c.set_source_rgba(*col, a * (0.45 + 0.5 * fall + 0.3 * s))
            c.move_to(cx + xs[i], cy + yy[i]); c.line_to(cx + xs[i + 1], cy + yy[i + 1]); c.stroke()
        c.set_dash([])
    c.restore()
    c.set_line_width(3); fill(c, "#64748B", 0.8 * a); rr(c, px, py, pw, ph, 36); c.stroke()
    window(c, cx, cy, 2 * lerp(R, A, m) - 44, 2 * lerp(R, A, m) - 44, m, a)
    if hot > 0:
        for sx in (-1, 1):
            for sy in (-1, 1):
                pulse = 0.75 + 0.25 * math.sin(t * 9 + sx + 2 * sy)
                glow(c, cx + sx * (A - 8), cy + sy * (A - 8), 95, RED, 0.75 * hot * a * pulse)
                c.arc(cx + sx * (A - 8), cy + sy * (A - 8), 9, 0, 2 * math.pi); fill(c, "#FEE2E2", hot * a); c.fill()


def section(c, cx, cy, R, swell, t, a, air=0.0, arrows=0.0):
    """Fuselage cross-section: skin ring, floor, seats, cabin air, outward pressure arrows."""
    if a <= 0: return
    Rs = R * (1 + 0.05 * swell)
    glow(c, cx, cy, Rs * 1.5, CYAN, 0.12 * a * (0.5 + swell))
    c.arc(cx, cy, Rs, 0, 2 * math.pi); fill(c, "#0F172A", 0.95 * a); c.fill()
    # cabin air dots
    if air > 0:
        rnd = np.random.default_rng(5)
        for i in range(int(90 * air)):
            ang = rnd.uniform(0, 2 * math.pi); rad = Rs * 0.86 * math.sqrt(rnd.uniform(0, 1))
            x = cx + rad * math.cos(ang + 0.15 * math.sin(t * 1.3 + i))
            y = cy + rad * math.sin(ang + 0.15 * math.sin(t * 1.3 + i))
            if y > cy + Rs * 0.45: continue
            c.new_sub_path(); c.arc(x, y, 6, 0, 2 * math.pi)
        fill(c, "#7DD3FC", 0.55 * a); c.fill()
    # floor + seats
    fy = cy + Rs * 0.45
    c.save(); c.arc(cx, cy, Rs - 10, 0, 2 * math.pi); c.clip()
    c.rectangle(cx - Rs, fy, 2 * Rs, Rs); fill(c, "#1E293B", a); c.fill()
    c.restore()
    for sx in (-1, 1):
        for k in range(2):
            x = cx + sx * (Rs * 0.28 + k * Rs * 0.2)
            rr(c, x - 26, fy - 80, 52, 80, 12); fill(c, "#334155", a); c.fill()
            rr(c, x - 30, fy - 30, 60, 24, 8); fill(c, "#475569", a); c.fill()
    # windows on the sides
    for sx in (-1, 1):
        wx = cx + sx * Rs * 0.93
        rr(c, wx - 9, cy - 46, 18, 70, 9); fill(c, SKY_T, a); c.fill()
    # skin
    c.set_line_width(22); fill(c, METAL, a); c.arc(cx, cy, Rs, 0, 2 * math.pi); c.stroke()
    c.set_line_width(4); fill(c, "#E2E8F0", 0.5 * a); c.arc(cx, cy, Rs + 8, math.pi * 1.1, math.pi * 1.6); c.stroke()
    # arrows
    if arrows > 0:
        for i in range(12):
            ang = i * 2 * math.pi / 12 + 0.26
            ph = (t * 0.9 + i * 0.08) % 1
            r0 = Rs * 0.55 + Rs * 0.25 * ph
            x0, y0 = cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)
            x1, y1 = cx + (r0 + 70) * math.cos(ang), cy + (r0 + 70) * math.sin(ang)
            aa = arrows * a * math.sin(ph * math.pi)
            c.set_line_width(9); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, AMBER, aa)
            c.move_to(x0, y0); c.line_to(x1, y1); c.stroke()
            for side in (-1, 1):
                c.move_to(x1, y1)
                c.line_to(x1 - 24 * math.cos(ang + side * 0.5), y1 - 24 * math.sin(ang + side * 0.5)); c.stroke()


def jet(c, cx, cy, s, a, split=0.0, t=0.0):
    """Side view of a 1950s jet airliner (generic). split > 0 breaks the body behind the wing."""
    if a <= 0: return
    c.save(); c.translate(cx, cy); safe_scale(c, s, s)
    cut = 40
    for part in (0, 1):
        c.save()
        if split > 0:
            if part == 0: c.translate(-30 * split, 40 * split * split); c.rotate(-0.12 * split)
            else: c.translate(60 * split, 120 * split * split); c.rotate(0.22 * split)
        c.rectangle(-700 if part == 0 else cut, -400, 740 if part == 0 else 700, 800); c.clip()
        # tail fin
        c.move_to(330, -40); c.line_to(420, -190); c.line_to(470, -190); c.line_to(455, -40); c.close_path()
        fill(c, "#CBD5E1", a); c.fill()
        # body
        c.move_to(-470, 10)
        c.curve_to(-470, -45, -420, -62, -350, -62); c.line_to(380, -50); c.line_to(470, -30); c.line_to(470, 20)
        c.line_to(380, 50); c.line_to(-350, 62); c.curve_to(-420, 62, -470, 50, -470, 10); c.close_path()
        g = cairo.LinearGradient(0, -62, 0, 62)
        g.add_color_stop_rgba(0, *hexc("#F1F5F9")[:3], a); g.add_color_stop_rgba(1, *hexc("#94A3B8")[:3], a)
        c.set_source(g); c.fill()
        rr(c, -440, -16, 900, 14, 7); fill(c, "#2563EB", a); c.fill()
        # cockpit
        c.move_to(-430, -18); c.line_to(-400, -40); c.line_to(-370, -40); c.line_to(-380, -18); c.close_path()
        fill(c, "#0F172A", a); c.fill()
        # square windows
        for i in range(14):
            wx = -320 + i * 48
            c.rectangle(wx, -38, 20, 20); fill(c, "#0F172A", a); c.fill()
        # wing + tailplane
        c.move_to(-120, 30); c.line_to(80, 30); c.line_to(190, 95); c.line_to(140, 100); c.close_path()
        fill(c, "#94A3B8", a); c.fill()
        c.move_to(360, 0); c.line_to(430, 0); c.line_to(470, 22); c.line_to(440, 24); c.close_path(); c.fill()
        c.restore()
    if split > 0:
        glow(c, cut + 10, 0, 160, RED, 0.6 * a * (1 - split * 0.5))
    c.restore()


def pane_stack(c, cx, cy, a, t, hole=0.0, load=0.0, fog=0.0):
    """Cross-section of a cabin window: outer, middle (with breather hole), inner scratch pane."""
    if a <= 0: return
    # outside / cabin backgrounds
    rr(c, cx - 430, cy - 300, 280, 600, 30); fill(c, "#0C4A6E", 0.55 * a); c.fill()
    text(c, "OUTSIDE", cx - 290, cy - 330, 28, MUTED, "xbold", a=a)
    text(c, "CABIN", cx + 290, cy - 330, 28, MUTED, "xbold", a=a)
    xs = {"OUTER": cx - 130, "MIDDLE": cx, "INNER": cx + 130}
    widths = {"OUTER": 40, "MIDDLE": 30, "INNER": 14}
    for name, x in xs.items():
        w = widths[name]
        hl = load if name == "OUTER" else 0
        rr(c, x - w / 2, cy - 260, w, 520, w / 2)
        g = cairo.LinearGradient(x - w / 2, 0, x + w / 2, 0)
        g.add_color_stop_rgba(0, *hexc("#BAE6FD")[:3], 0.55 * a); g.add_color_stop_rgba(1, *hexc("#E0F2FE")[:3], 0.8 * a)
        c.set_source(g); c.fill_preserve()
        fill(c, lerp_col("#7DD3FC", GREEN, hl), a); c.set_line_width(3 + 4 * hl); c.stroke()
        if hl > 0: glow(c, x, cy, 200, GREEN, 0.25 * hl * a)
        text(c, name, x, cy + 310, 26, WHITE, "xbold", a=a)
    # breather hole in middle pane
    hy = cy + 150
    c.rectangle(xs["MIDDLE"] - 20, hy - 9, 40, 18); fill(c, "#0B1222", a); c.fill()
    if hole > 0:
        r = 46 + 6 * math.sin(t * 6)
        c.set_line_width(5); fill(c, YEL, hole * a); c.arc(xs["MIDDLE"], hy, r, 0, 2 * math.pi); c.stroke()
        # air flowing through hole from cabin side into the gap
        for k in range(3):
            ph = (t * 0.9 + k / 3) % 1
            x = lerp(xs["INNER"] - 20, xs["OUTER"] + 30, ph)
            y = hy if x > xs["MIDDLE"] - 25 else hy - (xs["MIDDLE"] - 25 - x) * 0.8
            c.arc(x, y, 7, 0, 2 * math.pi); fill(c, "#E0F2FE", hole * a * math.sin(ph * math.pi)); c.fill()
    # cabin pressure arrows hitting the outer pane
    if load > 0:
        for i in range(5):
            y = cy - 200 + i * 80
            ph = (t * 1.2 + i * 0.2) % 1
            x1 = xs["OUTER"] + 30 + 40 * (1 - ph)
            c.set_line_width(8); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, AMBER, load * a * (0.4 + 0.6 * math.sin(ph * math.pi)))
            c.move_to(x1 + 50, y); c.line_to(x1, y); c.stroke()
            c.move_to(x1, y); c.line_to(x1 + 18, y - 14); c.move_to(x1, y); c.line_to(x1 + 18, y + 14); c.stroke()
    # fog between panes clears
    if fog > 0:
        rnd = np.random.default_rng(2)
        for i in range(40):
            x = xs["OUTER"] + rnd.uniform(25, 110); y = cy + rnd.uniform(-240, 240)
            c.new_sub_path(); c.arc(x, y, rnd.uniform(4, 9), 0, 2 * math.pi)
        fill(c, "#F8FAFC", 0.5 * fog * a); c.fill()


# ---------- the episode ----------
def draw(c, t):
    cta = cta_amount(t)
    A = 1 - cta

    # ---- hook: round vs square windows ----
    hook_title(c, t, "WHY ARE PLANE WINDOWS", "ALWAYS ROUND?", S("pressure"))
    ha = (1 - ease(pr(t, S("pressure") - 0.1, 0.4))) * A
    if ha > 0:
        k1 = back(pr(t, wt("hook", "windows") - 0.1, 0.45)); k2 = back(pr(t, wt("hook", "windows") + 0.15, 0.45))
        tore = pr(t, wt("hook", "tore"), 0.6)
        shake = 10 * math.sin(t * 60) * (1 - tore) if 0 < tore < 1 else 0
        if k1 > 0:
            c.save(); c.translate(300, 860); safe_scale(c, k1, k1)
            window(c, 0, 0, 220, 320, 0, ha)
            if tore > 0: glow(c, 0, 0, 260, GREEN, 0.25 * tore * ha)
            c.restore()
            pill(c, "ROUND", 300, 1130, 34, "#0F172A", GREEN if tore > 0 else WHITE, a=ha * ease(k1), pad=22, outline=GREEN if tore > 0 else MUTED)
        if k2 > 0:
            c.save(); c.translate(780 + shake, 860); safe_scale(c, k2, k2)
            window(c, 0, 0, 260, 300, 1, ha, frame_col=lerp_col("#CBD5E1", "#FCA5A5", tore))
            crack(c, 150, -165, -1.25, 150, tore, ha, seed=4)
            crack(c, -150, 165, 1.95, 120, pr(t, wt("hook", "tore") + 0.2, 0.5), ha, seed=9)
            c.restore()
            pill(c, "SQUARE", 780, 1130, 34, "#0F172A", RED if tore > 0 else WHITE, a=ha * ease(k2), pad=22, outline=RED if tore > 0 else MUTED)

    # ---- pressure: fuselage swells ----
    pa = ease(pr(t, S("pressure"), 0.5)) * (1 - ease(pr(t, S("flow") - 0.1, 0.4))) * A
    if pa > 0:
        swell_t = wt("pressure", "swells")
        cyc = max(0.0, t - swell_t)
        swell = ease(pr(t, swell_t - 0.2, 0.5)) * (0.6 + 0.4 * math.sin(cyc * 4.2))
        section(c, 540, 860, 290, swell, t, pa, air=ease(pr(t, wt("pressure", "pumped"), 1.2)),
                arrows=ease(pr(t, wt("pressure", "air") - 0.1, 0.5)))
        al = pr(t, wt("pressure", "altitude") - 0.2, 0.4)
        pill(c, "CRUISING · ~11 KM UP", 540, 440, 32, "#0F172A", CYAN, a=pa * ease(al), sc=back(al), pad=24, outline=CYAN)
        bl = pr(t, wt("pressure", "balloon"), 0.4)
        pill(c, "SKIN STRETCHES EVERY FLIGHT", 540, 1285, 32, "#0F172A", AMBER, a=pa * ease(bl), sc=back(bl), pad=24, outline=AMBER)

    # ---- flow / corners / cause / round: the skin panel ----
    fa = ease(pr(t, S("flow"), 0.5)) * (1 - ease(pr(t, S("comet") - 0.1, 0.4)))
    fa = max(fa, ease(pr(t, S("cause"), 0.5)) * (1 - ease(pr(t, S("hole") - 0.1, 0.4)))) * A
    if fa > 0:
        to_sq = ease(pr(t, wt("corners", "sharp") - 0.1, 0.7))
        to_rd = ease(pr(t, wt("round", "rounded") - 0.1, 0.9))
        m = to_sq * (1 - to_rd)
        hot = ease(pr(t, wt("corners", "squeezes"), 0.5)) * (1 - to_rd)
        if S("comet") <= t < S("cause"): hot = 0
        stress_field(c, t, m, fa, hot=hot)
        lab = pr(t, wt("flow", "flows") - 0.1, 0.4) * (1 - ease(pr(t, S("corners"), 0.3)))
        if lab > 0:
            pill(c, "STRESS FLOWS AROUND THE HOLE", 540, 1300, 32, "#0F172A", CYAN, a=fa * ease(lab), pad=24, outline=CYAN)
        hs = pr(t, wt("corners", "several"), 0.4) * (1 - ease(pr(t, S("comet") - 0.2, 0.3)))
        if hs > 0:
            pill(c, "HOT SPOTS AT THE CORNERS", 540, 1300, 34, "#450A0A", RED, a=fa * ease(hs), sc=back(hs), pad=26, outline=RED)
        # cause: crack grows in steps, one per "flight"
        if S("cause") - 0.2 <= t < S("round") + 0.6:
            n0 = wt("cause", "grew") - 0.4
            steps = max(0.0, (t - n0) / 0.45)
            prog = min(1.0, (math.floor(steps) + ease(steps % 1)) / 9) if t > n0 else 0
            ca = 1 - ease(pr(t, wt("round", "rounded"), 0.5))
            crack(c, HOLE_C[0] + 110, HOLE_C[1] - 110, -0.75, 300, prog, fa * ca, seed=11, lw=8)
            fl = pr(t, wt("cause", "flight") - 0.1, 0.3)
            if fl > 0 and t < S("round"):
                k = int(1 + max(0.0, steps))
                pill(c, f"FLIGHT {k:,}", 830, 510, 30, "#0F172A", AMBER, a=fa * ease(fl) * ca, pad=18, outline=AMBER)
            fg = pr(t, wt("cause", "fatigue") - 0.1, 0.4)
            if fg > 0:
                pill(c, "METAL FATIGUE", 540, 1300, 36, "#450A0A", RED, a=fa * ease(fg) * ca, sc=back(fg), pad=28, outline=RED)
        nw = pr(t, wt("round", "weak"), 0.4)
        if nw > 0:
            c.save(); c.translate(540, 1300); safe_scale(c, back(nw), back(nw))
            rr(c, -230, -38, 460, 76, 38); fill(c, "#052E2B", fa); c.fill_preserve(); fill(c, GREEN, fa); c.set_line_width(3); c.stroke()
            text(c, "NO WEAK POINT", -30, 12, 34, GREEN, "xbold", a=fa)
            check(c, 170, 0, 36, GREEN, fa, lw=8, p=pr(t, wt("round", "weak") + 0.15, 0.4))
            c.restore()

    # ---- comet ----
    ca_ = ease(pr(t, S("comet") - 0.1, 0.5)) * (1 - ease(pr(t, S("cause") - 0.1, 0.4))) * A
    if ca_ > 0:
        yr = pr(t, wt("comet", "1954"), 0.4)
        c.save(); c.translate(540, 520); safe_scale(c, back(yr), back(yr))
        text(c, "1954", 0, 40, 150, WHITE, "black", a=ca_ * ease(yr)); c.restore()
        enter = eout(pr(t, wt("comet", "two") - 0.3, 1.0))
        split = eio(pr(t, wt("comet", "broke"), 1.2))
        jet(c, lerp(1500, 540, enter) + 20 * split, 800 + 30 * split, 0.92, ca_, split=split, t=t)
        dh = pr(t, wt("comet", "havilland") - 0.1, 0.4)
        pill(c, "DE HAVILLAND COMET", 540, 1150, 34, "#0F172A", WHITE, a=ca_ * ease(dh), sc=back(dh), pad=24, outline=MUTED)
        fj = pr(t, wt("comet", "first"), 0.4)
        pill(c, "WORLD'S FIRST JET AIRLINER", 540, 1240, 30, "#0F172A", CYAN, a=ca_ * ease(fj), sc=back(fj), pad=22, outline=CYAN)
        if split > 0:
            flash = max(0.0, 1 - (t - wt("comet", "broke")) / 0.5)
            c.rectangle(0, 0, W, H); fill(c, RED, 0.18 * flash * ca_); c.fill()

    # ---- the hole: three panes ----
    wa = ease(pr(t, S("hole"), 0.5)) * A
    if wa > 0:
        hole = ease(pr(t, wt("hole", "hole") - 0.2, 0.4))
        load = ease(pr(t, wt("hole", "outer") - 0.1, 0.4))
        fog = (1 - ease(pr(t, wt("hole", "fogging"), 0.9))) * ease(pr(t, wt("hole", "stops") - 0.6, 0.3))
        pane_stack(c, 540, 860, wa, t, hole=hole, load=load, fog=fog)
        b1 = pr(t, wt("hole", "carry") - 0.1, 0.4)
        pill(c, "OUTER PANE TAKES THE LOAD", 540, 440, 32, "#052E2B", GREEN, a=wa * ease(b1) * (1 - ease(pr(t, wt("hole", "stops"), 0.3))), sc=back(b1), pad=24, outline=GREEN)
        b2 = pr(t, wt("hole", "fogging"), 0.4)
        pill(c, "MIDDLE PANE = BACKUP · NO FOG", 540, 440, 32, "#0F172A", CYAN, a=wa * ease(b2), sc=back(b2), pad=24, outline=CYAN)

    labels = [("pressure", "CABIN PRESSURE", AMBER), ("flow", "STRESS", CYAN), ("corners", "SHARP CORNERS", RED),
              ("comet", "THE COMET DISASTERS", RED), ("cause", "WHAT WENT WRONG", RED), ("round", "THE FIX: ROUND", GREEN),
              ("hole", "BONUS: THE TINY HOLE", PURPLE)]
    for lid, s, col in labels:
        scene_label(c, t, lid, s, col)


def SFX():
    cues = [(wt("hook", "windows") - 0.1, "pop"), (wt("hook", "windows") + 0.15, "pop"), (wt("hook", "tore"), "warn"),
            (wt("pressure", "altitude") - 0.2, "blip"), (wt("pressure", "pumped"), "rise"), (wt("pressure", "swells"), "ping"),
            (wt("flow", "flows"), "ping"), (wt("corners", "sharp"), "low"), (wt("corners", "several"), "warn"),
            (wt("comet", "1954"), "pop"), (wt("comet", "broke"), "rumble"), (wt("comet", "broke") + 0.1, "warn"),
            (wt("cause", "fatigue"), "low"), (wt("round", "rounded"), "rise"), (wt("round", "weak"), "success"),
            (wt("hole", "hole") - 0.2, "pop"), (wt("hole", "carry"), "ok"), (wt("hole", "fogging"), "resolve")]
    n0 = wt("cause", "grew") - 0.4
    k = 0
    while n0 + k * 0.45 < S("round") and k < 12:
        cues.append((n0 + k * 0.45, "tick")); k += 1
    return cues
