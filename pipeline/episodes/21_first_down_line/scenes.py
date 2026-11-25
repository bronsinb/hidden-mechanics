"""Episode 21: How the yellow first-down line works (Thanksgiving football)."""
from hm.core import *
from hm.props import *

DARK = "#0F172A"
GRASS_A = "#15803D"
GRASS_B = "#166534"
FD = "#FACC15"
BLUE_T = "#1D4ED8"
RED_T = "#B91C1C"

# TV frame on screen
VX0, VY0, VX1, VY1 = 60, 600, 1020, 1300


def proj(X, Z, cam):
    """World (X yards along field, Z yards from near sideline, Y=0) -> screen. cam = (Xc, H, D, f, pitch, crown)."""
    Xc, H, D, f, pitch, crown = cam
    Y = crown * math.sin(math.pi * cl(Z / 53.3))          # field crest
    x = X - Xc; y = Y - H; z = Z + D
    cp, sp = math.cos(pitch), math.sin(pitch)
    y2 = y * cp + z * sp; z2 = -y * sp + z * cp
    z2 = max(z2, 1.0)
    cxs = (VX0 + VX1) / 2; cys = (VY0 + VY1) / 2
    return cxs + f * x / z2, cys - f * y2 / z2


def field(c, a, t, cam, line_X=None, line_a=0.0, wire=0.0, players=None, glue_flash=0.0):
    if a <= 0: return
    c.save(); rr(c, VX0, VY0, VX1 - VX0, VY1 - VY0, 18); c.clip()
    c.rectangle(VX0, VY0, VX1 - VX0, VY1 - VY0); fill(c, "#0B1220", a); c.fill()
    # stands
    c.rectangle(VX0, VY0, VX1 - VX0, 240); fill(c, "#1E293B", a); c.fill()
    for i in range(40):
        for j in range(5):
            c.arc(VX0 + 12 + i * 25 + (j % 2) * 12, VY0 + 30 + j * 34, 7, 0, 2 * math.pi)
            fill(c, ("#F59E0B", "#E2E8F0", "#60A5FA", "#F87171")[(i + j * 3) % 4], 0.5 * a); c.fill()
    # grass stripes (5-yard bands)
    Xc = cam[0]
    x0 = int((Xc - 60) // 5 * 5)
    for X in range(x0, x0 + 125, 5):
        quad = [proj(X, -30, cam), proj(X + 5, -30, cam), proj(X + 5, 60, cam), proj(X, 60, cam)]
        c.move_to(*quad[0]); [c.line_to(*q) for q in quad[1:]]; c.close_path()
        fill(c, GRASS_A if (X // 5) % 2 == 0 else GRASS_B, a); c.fill()
    # yard lines + hash marks
    for X in range(x0, x0 + 125, 5):
        c.set_line_width(4); fill(c, WHITE, 0.85 * a)
        pts = [proj(X, z, cam) for z in range(0, 54, 4)]
        c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.stroke()
    # sidelines
    for Z in (0, 53.3):
        pts = [proj(X, Z, cam) for X in range(x0, x0 + 125, 5)]
        c.set_line_width(6); fill(c, WHITE, a); c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.stroke()
    # 3D wireframe overlay
    if wire > 0:
        c.set_line_width(2); fill(c, CYAN, a * wire)
        for Z in range(0, 54, 6):
            pts = [proj(X, Z, cam) for X in range(x0, x0 + 125, 4)]
            c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.stroke()
        for X in range(x0, x0 + 125, 4):
            pts = [proj(X, z, cam) for z in range(0, 54, 3)]
            c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.stroke()
    # the first-down line (under players)
    if line_X is not None and line_a > 0:
        pts = [proj(line_X, z, cam) for z in [i * 53.3 / 30 for i in range(31)]]
        if glue_flash > 0:
            c.set_line_width(26); c.set_source_rgba(*hexc(FD)[:3], 0.35 * a * glue_flash)
            c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.stroke()
        c.set_line_width(11); fill(c, FD, a * line_a)
        c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.stroke()
    # players on top
    if players:
        for (X, Z, col) in players:
            px, py = proj(X, Z, cam)
            s = 42 * 40 / (Z + cam[2])
            c.save(); c.translate(px, py)
            rr(c, -0.35 * s, -1.9 * s, 0.7 * s, 1.0 * s, 0.2 * s); fill(c, col, a); c.fill()          # jersey
            rr(c, -0.3 * s, -0.95 * s, 0.24 * s, 0.95 * s, 0.1 * s); fill(c, "#F8FAFC", a); c.fill()   # legs
            rr(c, 0.06 * s, -0.95 * s, 0.24 * s, 0.95 * s, 0.1 * s); c.fill()
            c.arc(0, -2.2 * s, 0.32 * s, 0, 2 * math.pi); fill(c, "#E5E7EB" if col == RED_T else "#CBD5E1", a); c.fill()
            c.restore()
    c.restore()
    rr(c, VX0, VY0, VX1 - VX0, VY1 - VY0, 18); c.set_line_width(6); fill(c, "#334155", a); c.stroke()


def tv_camera(c, x, y, a, t, hi=0.0, labels=0.0):
    if a <= 0: return
    # tripod
    c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, "#475569", a)
    for dx in (-120, 0, 120):
        c.move_to(x, y + 60); c.line_to(x + dx, y + 360); c.stroke()
    pan = 0.25 * math.sin(t * 0.9); tilt = 0.12 * math.sin(t * 1.3)
    c.save(); c.translate(x, y); c.rotate(tilt)
    rr(c, -190, -80, 300, 150, 22); fill(c, "#334155", a); c.fill()
    rr(c, 110, -60, 150 + 30 * math.sin(t * 1.1), 110, 16); fill(c, "#1E293B", a); c.fill()          # lens (zoom breathing)
    c.arc(260 + 30 * math.sin(t * 1.1), -5, 50, -math.pi / 2, math.pi / 2); fill(c, "#0B1220", a); c.fill()
    rr(c, -170, -130, 120, 50, 10); fill(c, "#475569", a); c.fill()
    c.restore()
    # sensor nodes
    if hi > 0:
        nodes = [("PAN", x - 10, y + 70, CYAN, "pan"), ("TILT", x - 120, y - 40, AMBER, "tilt"),
                 ("ZOOM", x + 200, y - 90, GREEN, "zoom"), ("FOCUS", x + 230, y + 70, PURPLE, "focus")]
        for lab, nx, ny, col, w in nodes:
            q = ease(pr(t, wt("sensors", w) - 0.3, 0.4))
            if q <= 0: continue
            glow(c, nx, ny, 40, col, 0.8 * a * q)
            c.arc(nx, ny, 12 * back(pr(t, wt("sensors", w) - 0.3, 0.4)), 0, 2 * math.pi); fill(c, col, a * q); c.fill()
            text(c, lab, nx, ny + (60 if ny > y else -30), 30, col, "black", a=a * q, stroke=6)


def swatches(c, a, t):
    if a <= 0: return
    rows = [("GRASS", (GRASS_A, GRASS_B, "#22C55E", "#14532D"), True, "grass"),
            ("JERSEYS", (BLUE_T, RED_T, "#F8FAFC", "#CBD5E1"), False, "players")]
    for k, (lab, cols, ok, w) in enumerate(rows):
        q = ease(pr(t, wt("key", w) - 0.3, 0.4))
        if q <= 0: continue
        y = 1190 + 0 * k
        x0 = 120 if k == 0 else 600
        rr(c, x0 - 16, y - 66, 350, 132, 16); fill(c, DARK, 0.88 * a * q); c.fill()
        text(c, lab, x0, y - 30 + 0, 26, WHITE, "black", align="left", a=a * q)
        for i, col in enumerate(cols):
            rr(c, x0 + i * 62, y - 10, 54, 54, 10); fill(c, col, a * q); c.fill()
        if ok: check(c, x0 + 290, y + 17, 26, GREEN, a=a * q)
        else: cross(c, x0 + 290, y + 17, 26, RED, a=a * q)


def film_strip(c, a, t, off):
    if a <= 0: return
    for row, (lab, col, dx) in enumerate((("CAMERA", WHITE, 0.0), ("ON AIR", FD, off))):
        y = 820 + row * 230
        text(c, lab, 120, y - 30, 28, col, "black", align="left", a=a)
        for i in range(-3, 8):
            x = 120 + i * 110 + dx * 110
            if x < 110 or x + 96 > 975: continue
            rr(c, x, y, 96, 130, 10); fill(c, "#1E293B", a); c.fill()
            rr(c, x + 8, y + 10, 80, 110, 6); fill(c, GRASS_A, a); c.fill()
            c.set_line_width(5); fill(c, FD if row == 1 else WHITE, a * (1 if row == 1 else 0.5))
            c.move_to(x + 30 + (i * 7) % 30, y + 14); c.line_to(x + 40 + (i * 7) % 30, y + 116); c.stroke()


def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "HOW THE YELLOW", "FIRST-DOWN LINE WORKS", S("sensors"))

    f_a = A * (ease(pr(t, 0.05, 0.5)) * (1 - ease(pr(t, S("sensors") - 0.2, 0.4)))
               + ease(pr(t, S("model") - 0.1, 0.5)) * (1 - ease(pr(t, S("delay") - 0.2, 0.4)))
               + ease(pr(t, S("history") - 0.1, 0.5)))
    cam_a = A * ease(pr(t, S("sensors") - 0.1, 0.5)) * (1 - ease(pr(t, S("model") - 0.2, 0.4)))
    del_a = A * ease(pr(t, S("delay") - 0.1, 0.5)) * (1 - ease(pr(t, S("history") - 0.2, 0.4)))

    if f_a > 0:
        pan = 6 * math.sin(t * 0.35)
        zoom = 1.0
        if S("draw") - 0.2 < t < S("key"):
            pan = 10 * math.sin((t - S("draw")) * 0.9)
            zoom = 1 + 0.35 * (0.5 + 0.5 * math.sin((t - S("draw")) * 0.7 - 1.5))
        if S("key") - 0.2 < t < S("delay"):
            pan = 2 * math.sin(t * 0.5)
        crown = 0.0
        if S("model") - 0.2 < t < S("draw") + 1:
            crown = 1.6 * ease(pr(t, wt("model", "curve") - 0.4, 0.6)) * (1 - ease(pr(t, S("draw") + 0.2, 0.6)))
        cam = (pan, 24, 26, 640 * zoom, 0.55, crown)
        la = ease(pr(t, wt("hook", "yellow") - 0.3, 0.4))
        wire = ease(pr(t, wt("model", "3d") - 0.4, 0.5)) * (1 - ease(pr(t, S("draw") + 0.3, 0.5))) if S("model") - 0.2 < t < S("key") else 0
        if S("model") - 0.2 < t < S("draw") - 0.2:
            la = 0.25
        players = None
        if S("key") - 0.2 < t < S("delay"):
            u = (t - wt("key", "players") + 0.8)
            players = [(lerp(-12, 12, cl(u / 3.2)), 22, BLUE_T), (lerp(14, -10, cl(u / 3.6)), 30, RED_T), (lerp(-8, 8, cl(u / 3.0)), 14, BLUE_T)]
        glue = ease(pr(t, wt("hook", "glued") - 0.3, 0.4)) * (1 - ease(pr(t, S("sensors") - 0.3, 0.3)))
        field(c, f_a, t, cam, line_X=0.0, line_a=la, wire=wire, players=players, glue_flash=glue)
        if t < S("sensors"):
            np_ = pr(t, wt("hook", "painted") - 0.3, 0.4)
            pill(c, "NOT PAINTED ON THE FIELD", 540, 470, 30, DARK, FD, a=f_a * ease(np_), sc=back(np_), pad=22, outline=FD)
        elif t < S("draw"):
            mp = pr(t, wt("model", "3d") - 0.3, 0.4)
            pill(c, "3D MODEL OF THE FIELD", 540, 470, 30, DARK, CYAN, a=f_a * ease(mp), sc=back(mp), pad=22, outline=CYAN)
            cv = pr(t, wt("model", "curve") - 0.3, 0.4)
            text(c, "EVEN THE SLIGHT CROWN", 540, 1360, 30, CYAN, "black", a=f_a * ease(cv), stroke=6)
        elif t < S("key"):
            cb = pr(t, wt("draw", "combine") - 0.2, 0.4) * (1 - ease(pr(t, wt("draw", "recalculating") - 0.3, 0.3)))
            pill(c, "CAMERA DATA + FIELD MODEL", 540, 470, 30, DARK, WHITE, a=f_a * ease(cb), sc=back(cb), pad=22, outline=MUTED)
            rc = pr(t, wt("draw", "recalculating") - 0.2, 0.4)
            pill(c, "RECALCULATED 30× A SECOND", 540, 470, 30, DARK, FD, a=f_a * ease(rc), sc=back(rc), pad=22, outline=FD)
        elif t < S("delay"):
            swatches(c, f_a, t)
            tk = pr(t, wt("key", "trick") - 0.2, 0.4) * (1 - ease(pr(t, wt("key", "players") - 0.3, 0.3)))
            pill(c, "ONLY DRAWN OVER GRASS COLORS", 540, 470, 28, "#052E2B", GREEN, a=f_a * ease(tk), sc=back(tk), pad=22, outline=GREEN)
            pw = pr(t, wt("key", "players") - 0.2, 0.4)
            pill(c, "PLAYERS STAY ON TOP", 540, 470, 30, DARK, FD, a=f_a * ease(pw), sc=back(pw), pad=22, outline=FD)
        else:
            es = pr(t, wt("history", "espn") - 0.3, 0.4)
            pill(c, "DEBUTED ON ESPN · LATE 1990s", 540, 470, 28, DARK, FD, a=f_a * ease(es), sc=back(es), pad=22, outline=FD)

    if cam_a > 0:
        tv_camera(c, 440, 860, cam_a, t, hi=1.0)
        sp = pr(t, wt("sensors", "sensors") - 0.2, 0.4)
        pill(c, "SENSORS ON EVERY CAMERA", 540, 470, 30, DARK, CYAN, a=cam_a * ease(sp), sc=back(sp), pad=22, outline=CYAN)

    if del_a > 0:
        off = 2.0 * ease(pr(t, wt("delay", "delayed") - 0.3, 0.6))
        film_strip(c, del_a, t, off)
        fw = pr(t, wt("delay", "few") - 0.3, 0.4)
        pill(c, "A FEW FRAMES OF DELAY", 540, 470, 30, DARK, WHITE, a=del_a * ease(fw), sc=back(fw), pad=22, outline=MUTED)
        sy = pr(t, wt("delay", "sync") - 0.3, 0.4)
        text(c, "LINE + PICTURE IN SYNC", 540, 1290, 34, GREEN, "black", a=del_a * ease(sy), stroke=6)

    for lid, s, col in (("sensors", "THE CAMERA", CYAN), ("model", "THE MAP", CYAN), ("draw", "THE MATH", FD),
                        ("key", "THE TRICK", GREEN), ("delay", "THE SYNC", WHITE), ("history", "THE ORIGIN", FD)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "yellow") - 0.3, "pop"), (wt("hook", "painted") - 0.3, "warn"), (wt("hook", "glued") - 0.3, "ping"),
            (wt("sensors", "pan") - 0.3, "tick"), (wt("sensors", "tilt") - 0.3, "tick"), (wt("sensors", "zoom") - 0.3, "tick"),
            (wt("sensors", "focus") - 0.3, "tick"), (wt("model", "3d") - 0.4, "rise"),
            (wt("draw", "combine") - 0.2, "blip"), (wt("draw", "recalculating") - 0.2, "ping"),
            (wt("key", "trick") - 0.2, "pop"), (wt("key", "players") - 0.2, "success"),
            (wt("delay", "few") - 0.3, "tick"), (wt("delay", "sync") - 0.3, "ok"), (wt("history", "espn") - 0.3, "resolve")]
