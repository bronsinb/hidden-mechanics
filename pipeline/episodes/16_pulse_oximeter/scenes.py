"""Episode 16: How a finger clip reads your blood oxygen (pulse oximeter)."""
from hm.core import *
from hm.props import *

DARK = "#0F172A"
SKIN = "#E0A47E"
SKIN_D = "#C98A63"
RED_L = "#EF4444"
IR = "#A855F7"            # infrared shown as violet (it's invisible)
O2 = "#F43F5E"            # oxygen-rich blood
DEOX = "#7F1D3A"          # oxygen-poor blood
CX, CY, R = 540, 900, 200


def heart(c, x, y, s, col, a):
    if a <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, s, s)
    c.move_to(0, 30); c.curve_to(-60, -10, -40, -60, 0, -30); c.curve_to(40, -60, 60, -10, 0, 30); c.close_path()
    fill(c, col, a); c.fill(); c.restore()


def beat(t):
    """0..1 heartbeat pulse at ~72 bpm."""
    ph = (t * 1.2) % 1
    return math.exp(-((ph - 0.12) / 0.06) ** 2) + 0.35 * math.exp(-((ph - 0.32) / 0.07) ** 2)


# ---------- hook: the clip on a finger ----------
def clip_device(c, a, t, spo2="98", show=1.0):
    if a <= 0: return
    # finger coming from the left
    rr(c, 40, 830, 640, 150, 75); fill(c, SKIN, a); c.fill()
    rr(c, 520, 846, 150, 118, 50); fill(c, "#F1C2A2", a); c.fill()          # nail area
    c.set_line_width(4); fill(c, SKIN_D, a)
    for x in (230, 380):
        c.move_to(x, 845); c.curve_to(x + 8, 880, x + 8, 930, x, 965); c.stroke()
    # clip body
    rr(c, 400, 700, 460, 130, 50); fill(c, "#E2E8F0", a); c.fill()          # top jaw
    rr(c, 400, 980, 460, 120, 50); fill(c, "#CBD5E1", a); c.fill()          # bottom jaw
    rr(c, 780, 760, 120, 280, 40); fill(c, "#94A3B8", a); c.fill()          # hinge
    # screen
    rr(c, 440, 718, 380, 94, 18); fill(c, "#0B1220", a); c.fill()
    text(c, "SpO2", 470, 760, 24, CYAN, "black", align="left", a=a * show)
    text(c, spo2 + "%", 470, 800, 38, CYAN, "black", align="left", a=a * show)
    heart(c, 690, 755, 0.35 * (1 + 0.25 * beat(t)), RED_L, a * show)
    text(c, "72", 740, 800, 38, RED_L, "black", align="left", a=a * show)


def needle_crossed(c, x, y, a, cross):
    if a <= 0: return
    c.save(); c.translate(x, y); c.rotate(-0.6)
    rr(c, -70, -16, 110, 32, 8); fill(c, "#E2E8F0", a); c.fill()
    c.rectangle(-90, -6, 20, 12); fill(c, "#94A3B8", a); c.fill()
    c.set_line_width(4); fill(c, "#CBD5E1", a); c.move_to(40, 0); c.line_to(110, 0); c.stroke()
    c.restore()
    if cross > 0:
        c.set_line_width(12); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, RED, a)
        c.move_to(x - 90, y - 90); c.line_to(lerp(x - 90, x + 90, cross), lerp(y - 90, y + 90, cross)); c.stroke()


# ---------- cross-section ----------
def cross_section(c, a, t, labels=0.0, pulse=0.0, red_beam=0.0, ir_beam=0.0, art_hi=0.0):
    if a <= 0: return
    # clip jaws
    rr(c, CX - 170, CY - R - 120, 340, 90, 30); fill(c, "#E2E8F0", a); c.fill()
    rr(c, CX - 170, CY + R + 30, 340, 90, 30); fill(c, "#CBD5E1", a); c.fill()
    # LEDs + detector
    for dx, col in ((-36, RED_L), (36, IR)):
        glow(c, CX + dx, CY - R - 40, 40, col, 0.6 * a * (red_beam if col == RED_L else ir_beam))
        c.arc(CX + dx, CY - R - 46, 16, 0, 2 * math.pi); fill(c, col, a); c.fill()
    rr(c, CX - 60, CY + R + 36, 120, 30, 8); fill(c, "#1E293B", a); c.fill()
    text(c, "SENSOR", CX, CY + R + 100, 22, MUTED, "black", a=a)
    # finger layers
    c.arc(CX, CY, R, 0, 2 * math.pi); fill(c, SKIN, a); c.fill()
    c.arc(CX, CY, R - 26, 0, 2 * math.pi); fill(c, "#F3B9A0", a); c.fill()
    c.save(); c.translate(CX, CY + 10); c.scale(1.0, 0.7)
    c.arc(0, 0, 70, 0, 2 * math.pi); c.restore(); fill(c, "#F8FAFC", a); c.fill()            # bone
    for vx, vy in ((-110, 70), (110, 80), (-60, 140)):
        c.arc(CX + vx, CY + vy, 20, 0, 2 * math.pi); fill(c, "#6D28D9", 0.85 * a); c.fill()   # veins
    ar = 26 * (1 + 0.35 * pulse * beat(t))
    for ax_, ay_ in ((-90, -90), (95, -95)):
        if art_hi > 0: glow(c, CX + ax_, CY + ay_, ar * 2.4, O2, 0.6 * art_hi * a)
        c.arc(CX + ax_, CY + ay_, ar, 0, 2 * math.pi); fill(c, O2, a); c.fill()              # arteries
    # beams
    for dx, col, on in ((-36, RED_L, red_beam), (36, IR, ir_beam)):
        if on <= 0: continue
        c.set_line_width(22); c.set_source_rgba(*hexc(col)[:3], 0.35 * a * on)
        c.move_to(CX + dx, CY - R - 30); c.line_to(CX + dx, CY + R + 36); c.stroke()
        for k in range(4):
            u = (t * 1.4 + k / 4) % 1
            y = lerp(CY - R - 30, CY + R + 36, u)
            glow(c, CX + dx, y, 22, col, 0.8 * a * on)
    if labels > 0:
        la = a * labels
        for txt, lx, ly, px, py, col in (("SKIN", 860, 720, CX + 150, CY - 130, SKIN),
                                         ("BONE", 860, 920, CX + 60, CY + 10, WHITE),
                                         ("VEINS", 220, 1040, CX - 110, CY + 70, "#A78BFA"),
                                         ("ARTERY", 220, 760, CX - 90, CY - 90, O2)):
            c.set_line_width(3); fill(c, col, 0.7 * la); c.move_to(lx + (-60 if lx > 540 else 60), ly - 10); c.line_to(px, py); c.stroke()
            text(c, txt, lx, ly, 30, col, "black", a=la, stroke=6)


def absorb_panel(c, x, a, t, cell_col, red_out, ir_out, title, tcol):
    if a <= 0: return
    w = 380
    rr(c, x - w / 2, 640, w, 640, 28); fill(c, "#0B1220", a); c.fill()
    text(c, title, x, 690, 30, tcol, "black", a=a)
    # incoming beams
    for dx, col, out in ((-60, RED_L, red_out), (60, IR, ir_out)):
        c.set_line_width(26); c.set_source_rgba(*hexc(col)[:3], 0.8 * a)
        c.move_to(x + dx, 720); c.line_to(x + dx, 860); c.stroke()
        c.set_line_width(26 * out + 1); c.set_source_rgba(*hexc(col)[:3], 0.8 * a * (0.3 + 0.7 * out))
        c.move_to(x + dx, 1040); c.line_to(x + dx, 1200); c.stroke()
        if out < 0.5:
            text(c, "SOAKED UP", x + dx, 1250, 20, col, "black", a=a)
    # blood cells
    rr(c, x - 160, 870, 320, 160, 30); fill(c, "#3F0D1A", a); c.fill()
    for k in range(9):
        cx = x - 120 + (k % 5) * 60 + 15 * math.sin(t * 1.5 + k); cy = 905 + (k // 5) * 80 + 10 * math.cos(t * 1.3 + k)
        c.save(); c.translate(cx, cy); c.scale(1, 0.6); c.arc(0, 0, 28, 0, 2 * math.pi); c.restore()
        fill(c, cell_col, a); c.fill()
    text(c, "RED", x - 60, 760 - 10 - 20, 22, RED_L, "black", a=0)


def ppg_wave(c, a, t, ac_hi):
    if a <= 0: return
    x0, x1, base = 120, 960, 1180
    dc_top = 980
    rr(c, x0 - 20, 640, x1 - x0 + 40, 640, 26); fill(c, "#0B1220", a); c.fill()
    # steady part
    c.rectangle(x0, dc_top, x1 - x0, base - dc_top); c.set_source_rgba(*hexc("#6D28D9")[:3], 0.35 * a); c.fill()
    text(c, "SKIN, BONE, VEINS: STEADY", 540, 1100, 28, "#C4B5FD", "black", a=a)
    # pulsing part
    c.new_path()
    pts = []
    for i in range(0, 241):
        x = lerp(x0, x1, i / 240)
        tt = t - (x1 - x) / 300
        y = dc_top - 140 * beat(tt)
        pts.append((x, y))
    c.move_to(x0, dc_top)
    for p in pts: c.line_to(*p)
    c.line_to(x1, dc_top); c.close_path()
    c.set_source_rgba(*hexc(O2)[:3], (0.2 + 0.4 * ac_hi) * a); c.fill()
    c.set_line_width(7); fill(c, O2, a); c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.stroke()
    text(c, "ARTERIAL BLOOD: PULSES", 540, 760, 28, O2, "black", a=a * ac_hi, stroke=6)


def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "HOW A FINGER CLIP", "READS YOUR OXYGEN", S("light"))

    dev_a = A * (ease(pr(t, 0.05, 0.5)) * (1 - ease(pr(t, S("light") - 0.2, 0.4)))
                 + ease(pr(t, S("ratio") - 0.1, 0.5)) * (1 - ease(pr(t, S("tissue") - 0.2, 0.4)))
                 + ease(pr(t, S("limits") - 0.1, 0.5)))
    xs_a = A * (ease(pr(t, S("light") - 0.1, 0.5)) * (1 - ease(pr(t, S("blood") - 0.2, 0.4)))
                + ease(pr(t, S("tissue") - 0.1, 0.5)) * (1 - ease(pr(t, wt("pulse", "so") - 0.3, 0.4))))
    ab_a = A * ease(pr(t, S("blood") - 0.1, 0.5)) * (1 - ease(pr(t, S("ratio") - 0.2, 0.4)))
    ppg_a = A * ease(pr(t, wt("pulse", "so") - 0.2, 0.5)) * (1 - ease(pr(t, S("limits") - 0.2, 0.4)))

    if dev_a > 0:
        if t < S("light"):
            clip_device(c, dev_a, t, show=ease(pr(t, wt("hook", "seconds") - 0.2, 0.4)))
            nd = ease(pr(t, wt("hook", "needle") - 0.4, 0.4))
            needle_crossed(c, 540, 1240, dev_a * nd, ease(pr(t, wt("hook", "needle") - 0.1, 0.3)))
        elif t < S("limits"):
            v = int(round(lerp(85, 98, eio(pr(t, wt("ratio", "saturated") - 0.4, 1.0)))))
            clip_device(c, dev_a, t, spo2=str(v))
            rt = pr(t, wt("ratio", "ratio") - 0.2, 0.4)
            pill(c, "RED ÷ INFRARED", 540, 470, 34, DARK, WHITE, a=dev_a * ease(rt), sc=back(rt), pad=24, outline=MUTED)
            sa = pr(t, wt("ratio", "saturated") - 0.2, 0.4)
            pill(c, "= OXYGEN SATURATION (SpO2)", 540, 1240, 30, DARK, CYAN, a=dev_a * ease(sa), sc=back(sa), pad=22, outline=CYAN)
        else:
            flick = "--" if int(t * 3) % 2 else "9?"
            clip_device(c, dev_a, t, spo2=flick if t > wt("limits", "less") - 0.3 else "97")
            icons = [("MOVEMENT", "movement", AMBER), ("COLD FINGERS", "cold", CYAN), ("POOR CIRCULATION", "circulation", PURPLE)]
            for k, (lab, w, col) in enumerate(icons):
                q = pr(t, wt("limits", w) - 0.2, 0.4)
                pill(c, lab, 540, 1150 + k * 70, 28, DARK, col, a=dev_a * ease(q), sc=back(q), pad=18, outline=col)
            lr = pr(t, wt("limits", "less") - 0.2, 0.4)
            pill(c, "LESS RELIABLE READINGS", 540, 470, 30, "#450A0A", RED, a=dev_a * ease(lr), sc=back(lr), pad=22, outline=RED)

    if xs_a > 0:
        if t < S("blood"):
            rb = ease(pr(t, wt("light", "red") - 0.2, 0.4))
            ib = ease(pr(t, wt("light", "infrared") - 0.3, 0.4))
            cross_section(c, xs_a, t, red_beam=rb, ir_beam=ib)
            tw = pr(t, wt("light", "two") - 0.2, 0.4) * (1 - ease(pr(t, wt("light", "sensor") - 0.3, 0.3)))
            pill(c, "RED + INFRARED (INVISIBLE)", 540, 470, 30, DARK, IR, a=xs_a * ease(tw), sc=back(tw), pad=22, outline=IR)
            sn = pr(t, wt("light", "sensor") - 0.2, 0.4)
            pill(c, "SENSOR: WHAT GETS THROUGH?", 540, 470, 30, DARK, WHITE, a=xs_a * ease(sn), sc=back(sn), pad=22, outline=MUTED)
        else:
            lab = ease(pr(t, wt("tissue", "skin") - 0.3, 0.5)) * (1 - 0.5 * ease(pr(t, wt("tissue", "heartbeat") - 0.2, 0.4)))
            pu = ease(pr(t, wt("tissue", "heartbeat") - 0.3, 0.4))
            cross_section(c, xs_a, t, labels=lab, pulse=pu, red_beam=0.5, ir_beam=0.5, art_hi=ease(pr(t, wt("pulse", "arterial") - 0.3, 0.4)))
            hb = pr(t, wt("tissue", "heartbeat") - 0.2, 0.4)
            heart(c, 540, 1300, 0.8 * (1 + 0.25 * beat(t)), RED_L, xs_a * ease(hb))
            tr = pr(t, wt("tissue", "trick") - 0.2, 0.4)
            pill(c, "THE TRICK: YOUR HEARTBEAT", 540, 470, 30, "#450A0A", RED_L, a=xs_a * ease(tr), sc=back(tr), pad=22, outline=RED_L)

    if ab_a > 0:
        rich = ease(pr(t, wt("blood", "rich") - 0.2, 0.5))
        poor = ease(pr(t, wt("blood", "low") - 0.2, 0.5))
        absorb_panel(c, 300, ab_a * rich, t, O2, red_out=1.0, ir_out=0.25, title="OXYGEN-RICH", tcol=O2)
        absorb_panel(c, 780, ab_a * poor, t, DEOX, red_out=0.25, ir_out=1.0, title="OXYGEN-POOR", tcol="#FDA4AF")

    if ppg_a > 0:
        ppg_wave(c, ppg_a, t, ease(pr(t, wt("pulse", "pulses") - 0.4, 0.4)))
        on = pr(t, wt("pulse", "only") - 0.2, 0.4)
        pill(c, "ONLY READ THE PULSING PART", 540, 470, 30, DARK, O2, a=ppg_a * ease(on), sc=back(on), pad=22, outline=O2)

    for lid, s, col in (("light", "THE LIGHT", IR), ("blood", "THE COLOR TRICK", O2), ("ratio", "THE MATH", CYAN),
                        ("tissue", "THE PROBLEM", AMBER), ("pulse", "THE PULSE", O2), ("limits", "THE CATCH", RED)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "seconds") - 0.2, "blip"), (wt("hook", "needle") - 0.1, "warn"),
            (wt("light", "red") - 0.2, "ping"), (wt("light", "infrared") - 0.3, "ping"), (wt("light", "sensor") - 0.2, "tick"),
            (wt("blood", "rich") - 0.2, "pop"), (wt("blood", "low") - 0.2, "pop"),
            (wt("ratio", "ratio") - 0.2, "rise"), (wt("ratio", "saturated") - 0.2, "success"),
            (wt("tissue", "skin") - 0.3, "tick"), (wt("tissue", "heartbeat") - 0.3, "low"),
            (wt("pulse", "only") - 0.2, "ping"), (wt("limits", "movement") - 0.2, "warn"), (wt("limits", "less") - 0.2, "low")]
