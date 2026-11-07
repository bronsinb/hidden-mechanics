"""Episode 03: How your phone knows which way is up (MEMS accelerometer)."""
from hm.core import *
from hm.props import *

CELL = (540, 840)
SIL = "#7DD3FC"


# ---------- props for this episode ----------
def phone(c, cx, cy, s, ang, a, content_rot=0.0, chip=0.0, t=0.0):
    """Phone body rotated by ang (radians); screen content rotated by content_rot."""
    if a <= 0: return
    c.save(); c.translate(cx, cy); c.rotate(ang); safe_scale(c, s, s)
    c.push_group()
    glow(c, 0, 20, 420, "#000000", 0.5)
    rr(c, -160, -320, 320, 640, 54); fill(c, "#1F2937"); c.fill_preserve()
    fill(c, "#475569"); c.set_line_width(5); c.stroke()
    rr(c, -142, -300, 284, 600, 40)
    g = cairo.LinearGradient(0, -300, 0, 300)
    g.add_color_stop_rgb(0, *hexc("#0F172A")[:3]); g.add_color_stop_rgb(1, *hexc("#1E293B")[:3])
    c.set_source(g); c.fill()
    rr(c, -40, -288, 80, 18, 9); fill(c, "#020617"); c.fill()
    # screen content: a video card that stays upright
    c.save(); rr(c, -142, -300, 284, 600, 40); c.clip()
    c.rotate(content_rot)
    rr(c, -125, -78, 250, 140, 16)
    g = cairo.LinearGradient(0, -78, 0, 62)
    g.add_color_stop_rgb(0, *hexc("#38BDF8")[:3]); g.add_color_stop_rgb(1, *hexc("#6366F1")[:3])
    c.set_source(g); c.fill()
    c.move_to(-16, -30); c.line_to(26, -8); c.line_to(-16, 14); c.close_path(); fill(c, "#FFFFFF", 0.9); c.fill()
    for i, w in enumerate((200, 150)):
        rr(c, -125, 82 + i * 28, w, 14, 7); fill(c, "#334155"); c.fill()
    c.restore()
    if chip > 0:
        rr(c, 55, 175, 46, 46, 8); fill(c, "#0B1220"); c.fill_preserve()
        fill(c, YEL, chip); c.set_line_width(3); c.stroke()
        glow(c, 78, 198, 90, YEL, 0.5 * chip * (0.7 + 0.3 * math.sin(t * 7)))
    c.pop_group_to_source(); c.paint_with_alpha(a)
    c.restore()


def spring(c, x0, y0, x1, y1, n=7, amp=16, col=METAL if False else "#94A3B8", a=1.0, lw=5):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); fill(c, col, a)
    c.move_to(x0, y0)
    seg = 2 * n
    for i in range(1, seg):
        f = i / seg
        side = amp if i % 2 else -amp
        c.line_to(x0 + dx * f + px * side, y0 + dy * f + py * side)
    c.line_to(x1, y1); c.stroke()


def cell(c, cx, cy, s, d, a, plates=1.0, mass=1.0, springs=1.0, gaps=0.0, t=0.0):
    """One accelerometer axis: silicon mass on springs between two fixed plates. d = downward shift (px)."""
    if a <= 0: return
    c.save(); c.translate(cx, cy); safe_scale(c, s, s)
    # frame
    rr(c, -300, -250, 600, 500, 36); fill(c, "#0F172A", 0.95 * a); c.fill_preserve()
    fill(c, "#334155", a); c.set_line_width(4); c.stroke()
    for sx in (-1, 1):
        rr(c, sx * 270 - 18, -60, 36, 120, 8); fill(c, "#475569", a); c.fill()
    my = d
    # springs (mass sides -> posts)
    if springs > 0:
        for sx in (-1, 1):
            x0 = sx * 110; x1 = lerp(x0, sx * 254, springs)
            spring(c, x0, my, x1, 0, n=6, amp=14, a=a, lw=5)
    # fixed plates
    if plates > 0:
        for sy in (-1, 1):
            rr(c, -150, sy * 140 - 14 + (sy * 30 * (1 - plates)), 300, 28, 8)
            fill(c, AMBER, a * plates); c.fill()
            text(c, "FIXED PLATE", 0, sy * 140 + 8 + sy * 30, 20, "#0B1220", "xbold", a=a * plates * 0) if False else None
    # mass
    if mass > 0:
        c.save(); c.translate(0, my); safe_scale(c, mass, mass)
        rr(c, -110, -70, 220, 140, 14)
        g = cairo.LinearGradient(-110, -70, 110, 70)
        g.add_color_stop_rgba(0, *hexc("#BAE6FD")[:3], a); g.add_color_stop_rgba(1, *hexc("#0EA5E9")[:3], a)
        c.set_source(g); c.fill()
        for i in range(5):
            c.rectangle(-90 + i * 40, -55, 20, 110)
        fill(c, "#0369A1", 0.25 * a); c.fill()
        c.restore()
    # gap markers
    if gaps > 0:
        top_gap = (140 - 14) - (70 - my)       # plate inner edge to mass top
        bot_gap = (140 - 14) - (70 + my)
        for sy, gap, col, lab in ((-1, top_gap, GREEN, "GAP GROWS"), (1, bot_gap, RED, "GAP SHRINKS")):
            y_mass = my + sy * 70
            y_plate = sy * (140 - 14)
            x = 175
            fill(c, col, gaps * a); c.set_line_width(4)
            c.move_to(x, y_mass); c.line_to(x, y_plate); c.stroke()
            for yy in (y_mass, y_plate):
                c.move_to(x - 12, yy); c.line_to(x + 12, yy); c.stroke()
            text(c, lab, -318, (y_mass + y_plate) / 2 + 9, 24, col, "xbold", "right", a=gaps * a)
    c.restore()


def bars_panel(c, x, y, a, top, bot, label="CHIP READS"):
    if a <= 0: return
    rr(c, x, y, 440, 150, 24); fill(c, "#0F172A", 0.92 * a); c.fill_preserve()
    fill(c, CYAN, 0.6 * a); c.set_line_width(3); c.stroke()
    text(c, label, x + 26, y + 40, 24, MUTED, "xbold", "left", a=a)
    for i, (nm, v, col) in enumerate((("TOP", top, GREEN), ("BOTTOM", bot, RED))):
        yy = y + 70 + i * 40
        text(c, nm, x + 26, yy + 18, 24, WHITE, "bold", "left", a=a)
        rr(c, x + 150, yy, 260, 24, 12); fill(c, "#1E293B", a); c.fill()
        rr(c, x + 150, yy, max(24, 260 * cl(v)), 24, 12); fill(c, col, a); c.fill()


def g_arrow(c, x, y, length, a, ang=math.pi / 2, label="g"):
    if a <= 0: return
    x1, y1 = x + length * math.cos(ang), y + length * math.sin(ang)
    glow(c, x1, y1, 50, PURPLE, 0.5 * a)
    c.set_line_width(12); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, PURPLE, a)
    c.move_to(x, y); c.line_to(x1, y1); c.stroke()
    for side in (-1, 1):
        c.move_to(x1, y1); c.line_to(x1 - 34 * math.cos(ang + side * 0.5), y1 - 34 * math.sin(ang + side * 0.5)); c.stroke()
    if label:
        text(c, label, x + 40, y + length * 0.5, 52, PURPLE, "black", "left", a=a)


def hard_drive(c, cx, cy, s, a, park, t):
    """Top view of a laptop hard drive; park 0 = head over the platter, 1 = parked on the ramp."""
    if a <= 0: return
    c.save(); c.translate(cx, cy); safe_scale(c, s, s)
    rr(c, -300, -230, 600, 460, 30); fill(c, "#334155", a); c.fill_preserve()
    fill(c, "#64748B", a); c.set_line_width(4); c.stroke()
    px, py = -60, 0
    c.arc(px, py, 190, 0, 2 * math.pi)
    g = cairo.RadialGradient(px - 50, py - 60, 20, px, py, 190)
    g.add_color_stop_rgba(0, *hexc("#F1F5F9")[:3], a); g.add_color_stop_rgba(1, *hexc("#94A3B8")[:3], a)
    c.set_source(g); c.fill()
    c.set_line_width(2)
    for r in (60, 100, 140, 175):
        fill(c, "#64748B", 0.35 * a); c.arc(px, py, r, 0, 2 * math.pi); c.stroke()
    sp = t * 9
    fill(c, "#FFFFFF", 0.35 * a); c.set_line_width(6)
    c.arc(px, py, 120, sp, sp + 0.8); c.stroke()
    c.arc(px, py, 22, 0, 2 * math.pi); fill(c, "#475569", a); c.fill()
    # parking ramp
    rr(c, 205, -150, 40, 70, 8); fill(c, "#0F172A", a); c.fill()
    # actuator arm pivots at (230, 150)
    ang = lerp(-2.45, -1.62, ease(park))
    c.save(); c.translate(230, 150); c.rotate(ang)
    rr(c, -14, -14, 300, 28, 12); fill(c, "#CBD5E1", a); c.fill()
    rr(c, 270, -10, 40, 20, 6); fill(c, AMBER, a); c.fill()
    c.restore()
    c.arc(230, 150, 30, 0, 2 * math.pi); fill(c, "#1E293B", a); c.fill()
    c.restore()


# ---------- the episode ----------
def draw(c, t):
    A = 1 - cta_amount(t)

    # ---- hook: phone rotates, screen follows, chip glows ----
    hook_title(c, t, "HOW DOES YOUR PHONE", "KNOW WHICH WAY IS UP?", S("mass"))
    ha = (1 - ease(pr(t, S("mass") - 0.1, 0.45))) * A
    if ha > 0:
        enter = back(pr(t, 0.05, 0.6))
        turn = eio(pr(t, wt("hook", "sideways") - 0.1, 0.8))
        follow = eio(pr(t, wt("hook", "follows") - 0.15, 0.6))
        chip = ease(pr(t, wt("hook", "tiny"), 0.4))
        zoom = 1 + 0.25 * ease(pr(t, wt("hook", "weight"), 0.8))
        phone(c, 540, 860, 0.95 * enter * zoom, -turn * math.pi / 2, ha, content_rot=follow * math.pi / 2, chip=chip, t=t)
        q = back(pr(t, wt("hook", "how"), 0.35)) * (1 - chip)
        if q > 0:
            c.save(); c.translate(870, 600); safe_scale(c, q, q)
            text(c, "?", 0, 0, 170, YEL, "black", stroke=16); c.restore()

    # ---- the cell: mass / gravity / plates ----
    ca = ease(pr(t, S("mass") - 0.1, 0.5)) * (1 - ease(pr(t, S("axes") - 0.1, 0.4))) * A
    if ca > 0:
        mass = back(pr(t, wt("mass", "speck") - 0.1, 0.45))
        springs = eout(pr(t, wt("mass", "springs") - 0.4, 0.7))
        d = 34 * eout(pr(t, wt("gravity", "shifts") - 0.1, 0.8)) + 2 * math.sin(t * 5) * springs
        plates = eout(pr(t, wt("plates", "fixed") - 0.1, 0.6))
        gaps = ease(pr(t, wt("plates", "gap") - 0.2, 0.4))
        cell(c, CELL[0], CELL[1], 1.0, d, ca, plates=plates, mass=mass, springs=springs, gaps=gaps, t=t)
        ac = pr(t, wt("mass", "accelerometer") - 0.2, 0.4)
        pill(c, "ACCELEROMETER CHIP · ONE AXIS", 540, 470, 30, "#0F172A", CYAN, a=ca * ease(ac), sc=back(ac), pad=22, outline=CYAN)
        gv = ease(pr(t, wt("gravity", "gravity") - 0.1, 0.4))
        g_arrow(c, 920, 700, 260, ca * gv)
        if gv > 0:
            text(c, "GRAVITY", 920, 1010, 28, PURPLE, "xbold", a=ca * gv)
        if wt("gravity", "pulls") - 0.3 < t < S("plates") + 0.2:
            la = ease(pr(t, wt("gravity", "shifts"), 0.3)) * (1 - ease(pr(t, S("plates"), 0.3)))
            pill(c, "MASS SHIFTS DOWN", 540, 1185, 32, "#0F172A", SIL, a=ca * la, pad=24, outline=SIL)
        fp = ease(pr(t, wt("plates", "fixed"), 0.4)) * (1 - ease(pr(t, wt("plates", "gap") - 0.3, 0.3)))
        if fp > 0:
            pill(c, "FIXED PLATES", 540, 1185, 32, "#0F172A", AMBER, a=ca * fp, pad=24, outline=AMBER)
        me = pr(t, wt("plates", "measures") - 0.2, 0.4)
        if me > 0:
            rd = ease(pr(t, wt("plates", "difference") - 0.3, 0.5))
            bars_panel(c, 320, 1130, ca * ease(me), 0.35 + 0.0 * rd, 0.35 + 0.5 * rd)

    # ---- axes: three sensors ----
    xa = ease(pr(t, S("axes") - 0.1, 0.5)) * (1 - ease(pr(t, S("rotate") - 0.1, 0.4))) * A
    if xa > 0:
        for i, (nm, col) in enumerate((("X", RED), ("Y", GREEN), ("Z", CYAN))):
            k = back(pr(t, wt("axes", "three") + 0.18 * i, 0.45))
            cx = 230 + i * 310
            cell(c, cx, 640, 0.42 * k, 10, xa, t=t)
            pill(c, f"{nm} AXIS", cx, 790, 28, "#0F172A", col, a=xa * ease(k), pad=18, outline=col)
        dn = pr(t, wt("axes", "down") - 0.3, 0.5)
        if dn > 0:
            phone(c, 400, 1080, 0.42, 0, xa * ease(dn))
            g_arrow(c, 640, 960, 220, xa * ease(dn), label="")
            text(c, "DOWN", 700, 1110, 40, PURPLE, "black", "left", a=xa * ease(dn))

    # ---- rotate: tilt the phone ----
    ra = ease(pr(t, S("rotate") - 0.1, 0.5)) * (1 - ease(pr(t, S("fall") - 0.1, 0.3))) * A
    if ra > 0:
        tilt = eio(pr(t, wt("rotate", "tilt") - 0.1, 1.2))
        follow = eio(pr(t, wt("rotate", "turns") - 0.3, 0.6))
        ang = -tilt * math.pi / 2
        phone(c, 450, 850, 0.8, ang, ra, content_rot=follow * math.pi / 2)
        g_arrow(c, 870, 640, 330, ra * ease(pr(t, wt("rotate", "gravity") - 0.1, 0.4)))
        # readout: gravity seen from the phone's own axes
        px_ = math.sin(-ang); py_ = math.cos(ang)
        rr(c, 140, 1170, 800, 130, 24); fill(c, "#0F172A", 0.92 * ra); c.fill_preserve()
        fill(c, CYAN, 0.6 * ra); c.set_line_width(3); c.stroke()
        for i, (nm, v, col) in enumerate((("X", px_, RED), ("Y", py_, GREEN))):
            yy = 1200 + i * 48
            text(c, f"{nm} AXIS", 170, yy + 20, 26, WHITE, "xbold", "left", a=ra)
            rr(c, 330, yy, 580, 26, 13); fill(c, "#1E293B", ra); c.fill()
            rr(c, 330, yy, max(26, 580 * abs(v)), 26, 13); fill(c, col, ra); c.fill()
        sc = pr(t, wt("rotate", "screen") - 0.1, 0.4)
        pill(c, "SCREEN ROTATES", 540, 450, 32, "#0F172A", GREEN, a=ra * ease(sc), sc=back(sc), pad=24, outline=GREEN)

    # ---- fall: weight floats, reads zero ----
    fa = ease(pr(t, S("fall") - 0.1, 0.4)) * (1 - ease(pr(t, S("laptop") - 0.1, 0.4))) * A
    if fa > 0:
        drop = pr(t, wt("fall", "drop"), 3.6)
        y = lerp(560, 1350, (drop * 1.6) % 1.0) if drop > 0 else 560
        spin = drop * 3.2
        for k in range(1, 4):
            c.set_line_width(5); fill(c, WHITE, 0.15 * fa)
            c.move_to(300 - 30 * k, y - 90 - 40 * k); c.line_to(300 - 30 * k, y - 200 - 40 * k); c.stroke()
        phone(c, 300, y, 0.45, spin, fa)
        fl = ease(pr(t, wt("fall", "floats") - 0.3, 0.6))
        d = 34 * (1 - fl) + 4 * math.sin(t * 3) * fl
        cell(c, 760, 760, 0.55, d, fa, t=t)
        text(c, "INSIDE THE CHIP", 760, 590, 26, MUTED, "xbold", a=fa)
        z = pr(t, wt("fall", "zero") - 0.1, 0.4)
        if z > 0:
            c.save(); c.translate(760, 1060); safe_scale(c, back(z), back(z))
            glow(c, 0, -30, 160, YEL, 0.25 * fa)
            text(c, "0 g", 0, 20, 120, YEL, "black", a=fa * ease(z), stroke=12)
            c.restore()
        ff = pr(t, wt("fall", "free") - 0.1, 0.4)
        pill(c, "FREE FALL = WEIGHTLESS", 540, 450, 32, "#0F172A", YEL, a=fa * ease(ff), sc=back(ff), pad=24, outline=YEL)

    # ---- laptop: hard drive heads park ----
    la = ease(pr(t, S("laptop") - 0.1, 0.5)) * A
    if la > 0:
        park = pr(t, wt("laptop", "pull") - 0.1, 0.7)
        hard_drive(c, 540, 860, 1.15, la, park, t)
        ap = pr(t, wt("laptop", "apple") - 0.1, 0.4)
        pill(c, "SUDDEN MOTION SENSOR · 2005", 540, 470, 30, "#0F172A", CYAN, a=la * ease(ap), sc=back(ap), pad=22, outline=CYAN)
        hp = pr(t, wt("laptop", "away") - 0.1, 0.4)
        if hp > 0:
            c.save(); c.translate(540, 1240); safe_scale(c, back(hp), back(hp))
            rr(c, -250, -38, 500, 76, 38); fill(c, "#052E2B", la); c.fill_preserve(); fill(c, GREEN, la); c.set_line_width(3); c.stroke()
            text(c, "HEADS PARKED", -30, 12, 34, GREEN, "xbold", a=la)
            check(c, 190, 0, 36, GREEN, la, lw=8, p=pr(t, wt("laptop", "away") + 0.1, 0.4))
            c.restore()

    for lid, s, col in (("mass", "THE SENSOR", CYAN), ("gravity", "GRAVITY", PURPLE), ("plates", "MEASURING THE SHIFT", AMBER),
                        ("axes", "THREE AXES", CYAN), ("rotate", "ROTATION", GREEN), ("fall", "THE TWIST", YEL),
                        ("laptop", "BONUS: SAVING HARD DRIVES", PURPLE)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "sideways") - 0.1, "pop"), (wt("hook", "follows") - 0.15, "blip"), (wt("hook", "tiny"), "rise"),
            (wt("mass", "accelerometer") - 0.2, "pop"), (wt("mass", "speck") - 0.1, "pop"), (wt("mass", "springs") - 0.3, "ping"),
            (wt("gravity", "gravity") - 0.1, "low"), (wt("gravity", "shifts") - 0.1, "blip"),
            (wt("plates", "fixed") - 0.1, "pop"), (wt("plates", "gap") - 0.2, "blip"), (wt("plates", "difference") - 0.3, "ok"),
            (wt("axes", "three"), "pop"), (wt("axes", "three") + 0.18, "pop"), (wt("axes", "three") + 0.36, "pop"),
            (wt("axes", "down") - 0.3, "resolve"), (wt("rotate", "tilt") - 0.1, "rise"), (wt("rotate", "turns") - 0.3, "success"),
            (wt("fall", "drop"), "warn"), (wt("fall", "zero") - 0.1, "ping"),
            (wt("laptop", "apple") - 0.1, "pop"), (wt("laptop", "pull") - 0.1, "rumble"), (wt("laptop", "away"), "ok")]
