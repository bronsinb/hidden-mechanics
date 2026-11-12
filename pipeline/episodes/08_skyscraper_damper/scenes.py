"""Episode 08: The 660-tonne ball that keeps a skyscraper steady (tuned mass damper, Taipei 101)."""
from hm.core import *
from hm.props import *

GOLD, GOLD_D = "#FACC15", "#A16207"
BASE = (300, 1330)
H_T = 880
ZOOM = (770, 830)


# ---------- props ----------
def tower(c, lean, a, ball_off=0.0, cut=0.0, t=0.0):
    """Generic stepped skyscraper, rotated about its base by `lean` radians. A cut-away near the top shows the ball."""
    if a <= 0: return
    bx, by = BASE
    c.save(); c.translate(bx, by); c.rotate(lean)
    c.push_group()
    glow(c, 0, 0, 260, "#000000", 0.4)
    rr(c, -80, -170, 160, 170, 6); fill(c, "#334155"); c.fill()
    # eight stacked flared sections
    for i in range(8):
        y0 = -170 - (i + 1) * 78
        c.move_to(-58, y0 + 78); c.line_to(-70, y0); c.line_to(70, y0); c.line_to(58, y0 + 78); c.close_path()
        g = cairo.LinearGradient(-70, 0, 70, 0)
        g.add_color_stop_rgb(0, *hexc("#1E3A5F")[:3]); g.add_color_stop_rgb(0.5, *hexc("#2E6B8F")[:3]); g.add_color_stop_rgb(1, *hexc("#1E3A5F")[:3])
        c.set_source(g); c.fill()
        for k in range(3):
            c.rectangle(-50, y0 + 14 + k * 20, 100, 6); fill(c, "#7DD3FC", 0.25); c.fill()
    # crown + spire
    top = -170 - 8 * 78
    rr(c, -40, top - 60, 80, 60, 8); fill(c, "#1E3A5F"); c.fill()
    c.set_line_width(8); fill(c, "#94A3B8"); c.move_to(0, top - 60); c.line_to(0, top - 150); c.stroke()
    # cut-away showing the damper near the top
    if cut > 0:
        cy_ = -170 - 6.5 * 78
        rr(c, -52, cy_ - 50, 104, 110, 10); fill(c, "#0B1220", cut); c.fill()
        px, py = 0, cy_ - 45
        bxx, byy = px + ball_off, cy_ + 20
        c.set_line_width(3); fill(c, "#CBD5E1", cut)
        for dx in (-14, 14):
            c.move_to(px + dx, py); c.line_to(bxx + dx * 0.6, byy - 22); c.stroke()
        glow(c, bxx, byy, 60, GOLD, 0.5 * cut)
        c.arc(bxx, byy, 26, 0, 2 * math.pi); fill(c, GOLD, cut); c.fill()
    c.pop_group_to_source(); c.paint_with_alpha(a)
    c.restore()


def wind(c, a, t, strength=1.0):
    if a <= 0: return
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(7):
        ph = (t * 0.9 + k * 0.17) % 1
        y = 470 + k * 60
        x = lerp(-200, 900, ph)
        c.set_line_width(5); fill(c, "#CBD5E1", a * strength * math.sin(ph * math.pi) * 0.7)
        c.move_to(x, y); c.curve_to(x + 60, y - 10, x + 110, y + 10, x + 170, y); c.stroke()


def big_ball(c, cx, cy, s, swing, a, t, labels=0.0, dampers=0.0, heat=0.0):
    """Close-up: ball hung on cables from the ceiling; swing is the horizontal offset of the ball (px)."""
    if a <= 0: return
    c.save(); c.translate(cx, cy); safe_scale(c, s, s)
    rr(c, -260, -330, 520, 640, 30); fill(c, "#0F172A", 0.95 * a); c.fill_preserve(); fill(c, "#334155", a); c.set_line_width(4); c.stroke()
    rr(c, -260, -330, 520, 40, 12); fill(c, "#475569", a); c.fill()
    bx, by = swing, 60
    c.set_line_width(5); fill(c, "#94A3B8", a)
    for dx in (-120, -40, 40, 120):
        c.move_to(dx, -290); c.line_to(bx + dx * 0.55, by - 110); c.stroke()
    # dampers (pistons) from the floor to the ball
    if dampers > 0:
        for dx in (-200, 200):
            x0, y0 = dx, 290
            x1, y1 = bx + dx * 0.45, by + 90
            col = lerp_col("#64748B", "#F97316", heat)
            c.set_line_width(26); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_source_rgba(*col[:3], a * dampers)
            c.move_to(x0, y0); c.line_to(lerp(x0, x1, 0.55), lerp(y0, y1, 0.55)); c.stroke()
            c.set_line_width(12); fill(c, "#CBD5E1", a * dampers)
            c.move_to(lerp(x0, x1, 0.5), lerp(y0, y1, 0.5)); c.line_to(x1, y1); c.stroke()
            if heat > 0: glow(c, lerp(x0, x1, 0.3), lerp(y0, y1, 0.3), 70, "#F97316", 0.6 * heat * a * (0.7 + 0.3 * math.sin(t * 8)))
    glow(c, bx, by, 220, GOLD, 0.35 * a)
    c.arc(bx, by, 140, 0, 2 * math.pi)
    g = cairo.RadialGradient(bx - 50, by - 50, 10, bx, by, 140)
    g.add_color_stop_rgba(0, *hexc("#FEF9C3")[:3], a); g.add_color_stop_rgba(0.5, *hexc(GOLD)[:3], a); g.add_color_stop_rgba(1, *hexc(GOLD_D)[:3], a)
    c.set_source(g); c.fill()
    # plate seams
    c.save(); c.arc(bx, by, 140, 0, 2 * math.pi); c.clip()
    c.set_line_width(1.5); fill(c, GOLD_D, 0.5 * a)
    for k in range(-6, 7):
        yy = by + k * 21
        c.move_to(bx - 150, yy); c.line_to(bx + 150, yy); c.stroke()
    c.restore()
    if labels > 0:
        text(c, "660 t", bx, by + 18, 64, "#422006", "black", a=a * labels)
    c.restore()


def sway_plot(c, x, y, w, h, a, t, show_with=0.0):
    if a <= 0: return
    rr(c, x, y, w, h, 22); fill(c, "#0F172A", 0.92 * a); c.fill_preserve(); fill(c, "#334155", a); c.set_line_width(3); c.stroke()
    text(c, "SWAY", x + 24, y + 38, 22, MUTED, "xbold", "left", a=a)
    mid = y + h / 2 + 14
    c.set_line_width(1.5); fill(c, "#334155", a); c.move_to(x + 20, mid); c.line_to(x + w - 20, mid); c.stroke()
    for amp, col, on, lab in ((1.0, RED, 1.0, "WITHOUT"), (0.6, GREEN, show_with, "WITH BALL")):
        if on <= 0: continue
        c.set_line_width(5); fill(c, col, a * on)
        n = 160
        for i in range(n + 1):
            u = i / n
            yy = mid + 8 - (h * 0.26) * amp * math.sin(2 * math.pi * (3 * u - t * 0.5))
            (c.move_to if i == 0 else c.line_to)(x + 20 + (w - 40) * u, yy)
        c.stroke()
        text(c, lab, (x + w - 24) if col == RED else (x + w - 150), y + 38, 22, col, "xbold", "right", a=a * on)


def typhoon(c, x, y, s, a, t):
    if a <= 0: return
    c.save(); c.translate(x, y); c.rotate(-t * 2.5); safe_scale(c, s, s)
    for k in range(3):
        c.set_line_width(14 - 3 * k); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, "#E2E8F0", a * (0.9 - 0.2 * k))
        c.arc(0, 0, 40 + 34 * k, k * 2.1, k * 2.1 + 3.6); c.stroke()
    c.arc(0, 0, 18, 0, 2 * math.pi); fill(c, "#0F172A", a); c.fill()
    c.restore()


# ---------- the episode ----------
def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "WHY DOESN'T THIS", "SKYSCRAPER SWAY?", S("sway"))

    w_ = 2 * math.pi * 0.55                     # sway rhythm (slowed for the eye)
    phase = math.sin(t * w_)
    reduce_ = 1 - 0.4 * ease(pr(t, wt("soak", "cutting") - 0.2, 0.8))
    record = ease(pr(t, wt("record", "typhoon") - 0.2, 0.6))
    sway_amt = (0.02 + 0.03 * ease(pr(t, wt("sway", "bend") - 0.3, 0.6))) * reduce_ * (1 + 0.8 * record)
    lean = sway_amt * phase
    lagging = ease(pr(t, wt("lag", "lags") - 0.3, 0.5))
    ball_off = -lean * 900 * (0.4 + 0.6 * lagging)

    # tower is on stage for the whole episode (left side)
    ta = A * ease(pr(t, 0.1, 0.6))
    cut = ease(pr(t, wt("hook", "ball") - 0.6, 0.5))
    tower(c, lean, ta, ball_off=ball_off * 0.08, cut=cut, t=t)
    wind(c, ta * ease(pr(t, wt("hook", "wind") - 0.3, 0.5)) * (1 - 0.6 * ease(pr(t, S("ball"), 0.4)) + 0.6 * record), t)
    if t < S("ball"):
        tp = pr(t, wt("hook", "taipei") - 0.1, 0.4)
        pill(c, "TAIPEI 101 · 508 m", 770, 1260, 30, "#0F172A", CYAN, a=ta * ease(tp) * (1 - ease(pr(t, S("ball") - 0.4, 0.3))), sc=back(tp), pad=22, outline=CYAN)
        bd = pr(t, wt("sway", "bend") - 0.1, 0.4)
        pill(c, "WIND MAKES IT ROCK", 770, 640, 30, "#0F172A", WHITE, a=ta * ease(bd) * (1 - ease(pr(t, S("ball") - 0.3, 0.3))), sc=back(bd), pad=22, outline=MUTED)

    # ---- close-up of the ball (ball .. soak) ----
    za = A * ease(pr(t, S("ball") - 0.1, 0.5)) * (1 - ease(pr(t, S("record") - 0.1, 0.4)))
    if za > 0:
        lbl = ease(pr(t, wt("ball", "six") - 0.2, 0.4))
        damp = ease(pr(t, wt("soak", "dampers") - 0.2, 0.5))
        heat = ease(pr(t, wt("soak", "heat") - 0.3, 0.5))
        big_ball(c, ZOOM[0], ZOOM[1] - 40, 0.55, ball_off * 1.8, za, t, labels=lbl, dampers=damp, heat=heat)
        pl = pr(t, wt("ball", "forty") - 0.2, 0.4) * (1 - ease(pr(t, S("tune"), 0.3)))
        pill(c, "41 STEEL PLATES · Ø 5.5 m", 770, 470, 26, "#0F172A", GOLD, a=za * ease(pl), sc=back(pl), pad=18, outline=GOLD)
        pe = pr(t, wt("ball", "pendulum") - 0.2, 0.4) * (1 - ease(pr(t, S("tune"), 0.3)))
        pill(c, "A GIANT PENDULUM", 770, 1100, 28, "#0F172A", CYAN, a=za * ease(pe), sc=back(pe), pad=18, outline=CYAN)
        tu = pr(t, wt("tune", "same") - 0.2, 0.4) * (1 - ease(pr(t, S("lag"), 0.3)))
        pill(c, "SAME RHYTHM AS THE TOWER", 770, 1100, 26, "#0F172A", CYAN, a=za * ease(tu), sc=back(tu), pad=18, outline=CYAN)
        lg = pr(t, wt("lag", "lags") - 0.2, 0.4) * (1 - ease(pr(t, S("soak"), 0.3)))
        pill(c, "SWINGS AGAINST THE LEAN", 770, 1100, 26, "#052E2B", GREEN, a=za * ease(lg), sc=back(lg), pad=18, outline=GREEN)
        ht = pr(t, wt("soak", "heat") - 0.2, 0.4) * (1 - ease(pr(t, wt("soak", "cutting") - 0.3, 0.3)))
        pill(c, "MOTION → HEAT", 770, 1100, 28, "#431407", "#F97316", a=za * ease(ht), sc=back(ht), pad=18, outline="#F97316")
        if t > wt("lag", "leans") - 0.3 and t < S("soak") + 0.5:
            la = ease(pr(t, wt("lag", "leans") - 0.3, 0.4)) * (1 - ease(pr(t, S("soak"), 0.4)))
            dir_ = 1 if phase >= 0 else -1
            for (x, col, d) in ((300, RED, dir_), (770, GREEN, -dir_)):
                y = 470 if x == 770 else 330
                c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, col, la * abs(phase))
                c.move_to(x - 60 * d, y); c.line_to(x + 60 * d, y); c.stroke()
                c.move_to(x + 60 * d, y); c.line_to(x + 40 * d, y - 18); c.move_to(x + 60 * d, y); c.line_to(x + 40 * d, y + 18); c.stroke()
    # sway plot during "cutting the sway"
    sp = ease(pr(t, wt("soak", "cutting") - 0.3, 0.5)) * (1 - ease(pr(t, S("record") - 0.1, 0.4))) * A
    if sp > 0:
        sway_plot(c, 560, 1150, 470, 190, sp, t, show_with=ease(pr(t, wt("soak", "forty") - 0.3, 0.5)))
        pill(c, "UP TO 40% LESS SWAY", 770, 470, 28, "#052E2B", GREEN, a=sp * ease(pr(t, wt("soak", "forty") - 0.2, 0.4)), pad=18, outline=GREEN)

    # ---- record: typhoon ----
    ra = A * ease(pr(t, S("record") - 0.1, 0.5))
    if ra > 0:
        typhoon(c, 820, 560, 1.0 * back(pr(t, wt("record", "typhoon") - 0.2, 0.5)), ra, t)
        big_ball(c, 790, 1010, 0.42, 120 * math.sin(t * w_), ra, t, labels=1.0)
        yr = pr(t, wt("record", "2015") - 0.2, 0.4)
        pill(c, "2015 · TYPHOON SOUDELOR", 790, 740, 26, "#0F172A", WHITE, a=ra * ease(yr), sc=back(yr), pad=18, outline=MUTED)
        m = pr(t, wt("record", "meter") - 0.2, 0.4)
        if m > 0:
            c.save(); c.translate(790, 1290); safe_scale(c, back(m), back(m))
            text(c, "1 METER SWING", 0, 16, 54, YEL, "black", a=ra * ease(m), stroke=10)
            c.restore()

    for lid, s, col in (("sway", "THE PROBLEM", RED), ("ball", "THE BALL", GOLD), ("tune", "THE TUNING", CYAN),
                        ("lag", "THE TRICK", GREEN), ("soak", "THE PAYOFF", "#F97316"), ("record", "THE RECORD", YEL)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "taipei") - 0.1, "pop"), (wt("hook", "ball") - 0.6, "rise"), (wt("hook", "wind") - 0.3, "low"),
            (wt("sway", "bend") - 0.1, "warn"), (wt("ball", "ball") - 0.2, "pop"), (wt("ball", "six") - 0.2, "rumble"),
            (wt("ball", "forty") - 0.2, "blip"), (wt("ball", "pendulum") - 0.2, "ping"),
            (wt("tune", "same") - 0.2, "resolve"), (wt("lag", "lags") - 0.2, "wake"),
            (wt("soak", "dampers") - 0.2, "pop"), (wt("soak", "heat") - 0.3, "rise"), (wt("soak", "forty") - 0.2, "success"),
            (wt("record", "typhoon") - 0.2, "warn"), (wt("record", "meter") - 0.2, "pop")]
