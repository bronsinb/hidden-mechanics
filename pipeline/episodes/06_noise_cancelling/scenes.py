"""Episode 06: How noise-cancelling headphones erase sound."""
from hm.core import *
from hm.props import *

NOISE, ANTI, SUM = RED, CYAN, GREEN
CUP = (600, 700)          # centre of the ear-cup cross-section


# ---------- props ----------
def headphones(c, cx, cy, s, a):
    if a <= 0: return
    c.save(); c.translate(cx, cy); safe_scale(c, s, s)
    c.push_group()
    glow(c, 0, 60, 380, "#000000", 0.5)
    c.set_line_width(46); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, "#334155")
    c.arc(0, 40, 230, math.pi * 1.08, math.pi * 1.92); c.stroke()
    c.set_line_width(20); fill(c, "#64748B"); c.arc(0, 40, 230, math.pi * 1.12, math.pi * 1.88); c.stroke()
    for sx in (-1, 1):
        rr(c, sx * 235 - 80, -10, 160, 230, 70); fill(c, "#1E293B"); c.fill_preserve(); fill(c, "#475569"); c.set_line_width(6); c.stroke()
        rr(c, sx * 235 - 50, 30, 100, 150, 46); fill(c, "#0F172A"); c.fill()
        c.arc(sx * 235 + sx * 62, 40, 9, 0, 2 * math.pi); fill(c, CYAN); c.fill()
    c.pop_group_to_source(); c.paint_with_alpha(a)
    c.restore()


def jet(c, x, y, s, a, t):
    if a <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, s, s)
    rr(c, -110, -70, 220, 140, 70); fill(c, "#94A3B8", a); c.fill()
    c.arc(-40, 0, 60, 0, 2 * math.pi); fill(c, "#0F172A", a); c.fill()
    for k in range(6):
        ang = t * 12 + k * math.pi / 3
        c.set_line_width(10); fill(c, "#CBD5E1", a)
        c.move_to(-40, 0); c.line_to(-40 + 52 * math.cos(ang), 52 * math.sin(ang)); c.stroke()
    c.arc(-40, 0, 14, 0, 2 * math.pi); fill(c, "#475569", a); c.fill()
    c.restore()


def ear(c, x, y, a):
    if a <= 0: return
    c.save(); c.translate(x, y)
    c.move_to(30, -110); c.curve_to(-60, -120, -70, 10, -20, 40); c.curve_to(0, 60, -10, 110, 30, 110); c.close_path()
    fill(c, "#FDBA74", a); c.fill()
    c.move_to(20, -70); c.curve_to(-25, -70, -30, 0, 5, 20); c.set_line_width(8); fill(c, "#EA580C", 0.7 * a); c.stroke()
    c.restore()


def cup_section(c, a, t, out_mic=0.0, in_mic=0.0, speaker=0.0, cushion=0.0, noise_in=0.0, anti_out=0.0, leak=0.0):
    """Cross-section of an over-ear cup: ear on the left, shell on the right."""
    if a <= 0: return
    cx, cy = CUP
    ear(c, cx - 300, cy, a)
    # cushions (top and bottom, against the head)
    for sy in (-1, 1):
        rr(c, cx - 250, cy + sy * 160 - 40, 70, 80, 30)
        fill(c, lerp_col("#475569", AMBER, cushion), a); c.fill()
        if cushion > 0: glow(c, cx - 215, cy + sy * 160, 80, AMBER, 0.35 * cushion * a)
    # shell
    c.move_to(cx - 180, cy - 210); c.curve_to(cx + 120, cy - 230, cx + 170, cy - 120, cx + 170, cy)
    c.curve_to(cx + 170, cy + 120, cx + 120, cy + 230, cx - 180, cy + 210); c.close_path()
    fill(c, "#1E293B", a); c.fill_preserve(); fill(c, "#475569", a); c.set_line_width(8); c.stroke()
    # speaker driver
    if speaker > 0: glow(c, cx - 40, cy, 140, ANTI, 0.45 * speaker * a)
    c.move_to(cx - 20, cy - 110); c.line_to(cx - 90, cy - 70); c.line_to(cx - 90, cy + 70); c.line_to(cx - 20, cy + 110); c.close_path()
    fill(c, lerp_col("#334155", ANTI, 0.4 * speaker), a); c.fill()
    rr(c, cx - 20, cy - 40, 60, 80, 10); fill(c, "#64748B", a); c.fill()
    text(c, "SPEAKER", cx + 20, cy + 150, 22, MUTED, "xbold", a=a)
    # outside mic
    if out_mic > 0: glow(c, cx + 172, cy - 120, 70, YEL, 0.6 * out_mic * a)
    c.arc(cx + 172, cy - 120, 16, 0, 2 * math.pi); fill(c, lerp_col("#64748B", YEL, out_mic), a); c.fill()
    # inside mic
    if in_mic > 0: glow(c, cx - 140, cy - 60, 60, YEL, 0.6 * in_mic * a)
    c.arc(cx - 140, cy - 60, 13, 0, 2 * math.pi); fill(c, lerp_col("#64748B", YEL, in_mic), a); c.fill()
    # noise arriving from the right
    if noise_in > 0:
        for k in range(3):
            ph = (t * 0.9 + k / 3) % 1
            r = lerp(420, 190, ph)
            c.set_line_width(8); fill(c, NOISE, noise_in * a * (0.3 + 0.7 * ph))
            c.arc(cx + 480, cy, r, math.pi - 0.45, math.pi + 0.45); c.stroke()
    if anti_out > 0:
        for k in range(3):
            ph = (t * 0.9 + k / 3) % 1
            r = lerp(30, 150, ph)
            c.set_line_width(7); fill(c, ANTI, anti_out * a * (1 - ph))
            c.arc(cx - 90, cy, r, math.pi - 0.6, math.pi + 0.6); c.stroke()
    if leak > 0:
        c.set_line_width(5); fill(c, NOISE, leak * a)
        for k in range(2):
            ph = (t * 1.3 + k / 2) % 1
            c.arc(cx - 160, cy, 20 + 40 * ph, math.pi - 0.5, math.pi + 0.5); c.stroke()


def wave(c, x0, y, w, amp, fn, col, a, lw=6):
    if a <= 0: return
    c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); fill(c, col, a)
    n = 180
    for i in range(n + 1):
        u = i / n
        yy = y - amp * fn(u)
        (c.move_to if i == 0 else c.line_to)(x0 + w * u, yy)
    c.stroke()


def panel(c, a, t, flip, mix, kind="low", lag=0.0, rows=(1, 1, 1)):
    """Three waveform rows: noise, anti-noise, what you hear. flip 0..1 turns the copy upside down."""
    if a <= 0: return
    x0, y0, w = 110, 985, 860
    rr(c, x0 - 20, y0 - 30, w + 40, 380, 26); fill(c, "#0F172A", 0.92 * a); c.fill_preserve()
    fill(c, "#334155", a); c.set_line_width(3); c.stroke()
    sp = t * 0.9

    def noise(u):
        if kind == "low":
            return math.sin(2 * math.pi * (3 * u - sp))
        return (0.55 * math.sin(2 * math.pi * (9 * u - 2.3 * sp)) + 0.45 * math.sin(2 * math.pi * (14 * u + 0.7 * sp))
                + 0.4 * math.sin(2 * math.pi * (5.5 * u - 3.1 * sp))) * (0.6 + 0.4 * math.sin(2 * math.pi * (1.3 * u - sp)))

    def anti(u):
        return noise(u - lag) * (1 - 2 * flip)

    def total(u):
        return noise(u) + mix * anti(u) + (1 - mix) * 0

    labels = (("NOISE", NOISE, noise), ("ANTI-NOISE", ANTI, anti), ("WHAT YOU HEAR", SUM, lambda u: 0.5 * total(u) if mix > 0 else 0.5 * noise(u)))
    for i, ((lab, col, fn), on) in enumerate(zip(labels, rows)):
        if on <= 0: continue
        y = y0 + 40 + i * 110
        text(c, lab, x0, y - 30, 22, col, "xbold", "left", a=a * on)
        c.set_line_width(1.5); fill(c, "#334155", a * on); c.move_to(x0, y + 10); c.line_to(x0 + w, y + 10); c.stroke()
        wave(c, x0, y + 10, w * on, 34, fn, col, a * on)


def heli(c, x, y, s, a, t):
    if a <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, s, s)
    c.set_line_width(10); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, "#94A3B8", a)
    blade = 230 * abs(math.cos(t * 20))
    c.move_to(-blade, -120); c.line_to(blade, -120); c.stroke()
    c.move_to(0, -120); c.line_to(0, -80); c.stroke()
    rr(c, -140, -80, 220, 130, 60); fill(c, "#475569", a); c.fill()
    rr(c, -120, -60, 90, 70, 30); fill(c, "#7DD3FC", a); c.fill()
    c.move_to(70, -40); c.line_to(260, -30); c.line_to(260, -10); c.line_to(70, 10); c.close_path(); fill(c, "#475569", a); c.fill()
    c.set_line_width(8); fill(c, "#94A3B8", a); c.move_to(-130, 80); c.line_to(60, 80); c.stroke()
    c.restore()


# ---------- the episode ----------
def draw(c, t):
    A = 1 - cta_amount(t)

    # ---- hook ----
    hook_title(c, t, "HOW DO HEADPHONES", "ERASE NOISE?", S("mic"))
    ha = (1 - ease(pr(t, S("mic") - 0.1, 0.45))) * A
    if ha > 0:
        k = back(pr(t, 0.05, 0.6))
        headphones(c, 640, 860, 1.0 * k, ha)
        jet(c, 200, 840, 0.9 * ease(pr(t, wt("hook", "jet") - 0.2, 0.4)), ha, t)
        fade = ease(pr(t, wt("hook", "fade") - 0.1, 0.8))
        for kk in range(4):
            ph = (t * 0.8 + kk / 4) % 1
            r = lerp(60, 420, ph)
            c.set_line_width(8); fill(c, NOISE, ha * (1 - ph) * (1 - 0.85 * fade) * ease(pr(t, wt("hook", "jet"), 0.4)))
            c.arc(270, 840, r, -0.5, 0.5); c.stroke()
        ad = pr(t, wt("hook", "add") - 0.1, 0.4)
        pill(c, "+ MORE SOUND = SILENCE", 540, 1240, 34, "#0F172A", CYAN, a=ha * ease(ad), sc=back(ad), pad=26, outline=CYAN)

    # ---- the cup + waveform panel (mic .. voices) ----
    ca = ease(pr(t, S("mic") - 0.1, 0.5)) * (1 - ease(pr(t, S("history") - 0.1, 0.4))) * A
    if ca > 0:
        out_mic = ease(pr(t, wt("mic", "microphone") - 0.2, 0.4)) * (1 - 0.6 * ease(pr(t, S("inside"), 0.4)))
        in_mic = ease(pr(t, wt("inside", "mic") - 0.2, 0.4)) * (1 - ease(pr(t, S("lows"), 0.4)))
        speaker = ease(pr(t, wt("flip", "plays") - 0.2, 0.4))
        cushion = ease(pr(t, wt("voices", "cushions") - 0.2, 0.4))
        noise_in = ease(pr(t, wt("mic", "noise") - 0.6, 0.6))
        leak = ease(pr(t, wt("inside", "leaks") - 0.2, 0.4)) * (1 - ease(pr(t, wt("inside", "correcting") - 0.1, 0.6)))
        leak = max(leak, 0.6 * ease(pr(t, wt("voices", "change") - 0.1, 0.4)) * (1 - cushion * 0.7))
        cup_section(c, ca, t, out_mic=out_mic, in_mic=in_mic, speaker=speaker, cushion=cushion, noise_in=noise_in,
                    anti_out=speaker, leak=leak)
        om = pr(t, wt("mic", "outside") - 0.2, 0.4) * (1 - ease(pr(t, S("flip"), 0.3)))
        pill(c, "OUTSIDE MIC", 860, 470, 28, "#0F172A", YEL, a=ca * ease(om), sc=back(om), pad=18, outline=YEL)
        im = pr(t, wt("inside", "inside") - 0.2, 0.4) * (1 - ease(pr(t, S("lows"), 0.3)))
        pill(c, "INSIDE MIC", 420, 470, 28, "#0F172A", YEL, a=ca * ease(im), sc=back(im), pad=18, outline=YEL)
        # waveform panel
        pa = ease(pr(t, wt("flip", "copy") - 0.3, 0.5))
        if pa > 0:
            flip = ease(pr(t, wt("flip", "flipped") - 0.1, 0.8))
            mix = ease(pr(t, wt("cancel", "peak") - 0.2, 1.0))
            kind = "voice" if t >= wt("voices", "voices") - 0.2 else "low"
            lag = 0.0
            if kind == "voice":
                lag = 0.03 * ease(pr(t, wt("voices", "change") - 0.3, 0.5))
            # small residual wobble while the inside mic corrects
            if S("inside") <= t < S("lows"):
                lag = 0.02 * (1 - ease(pr(t, wt("inside", "correcting") - 0.1, 0.8)))
            rows = (1, ease(pr(t, wt("flip", "copy") - 0.1, 0.5)), ease(pr(t, wt("cancel", "peak") - 0.3, 0.5)))
            panel(c, ca * pa, t, flip, mix, kind=kind, lag=lag, rows=rows)
        nz = pr(t, wt("cancel", "nothing") - 0.3, 0.4) * (1 - ease(pr(t, S("inside"), 0.3)))
        pill(c, "≈ SILENCE", 800, 1205, 28, "#052E2B", GREEN, a=ca * ease(nz), sc=back(nz), pad=18, outline=GREEN)
        lw_ = pr(t, wt("lows", "engine") - 0.2, 0.4) * (1 - ease(pr(t, S("voices"), 0.3)))
        pill(c, "ENGINE HUM: CANCELLED", 540, 455, 30, "#052E2B", GREEN, a=ca * ease(lw_), sc=back(lw_), pad=22, outline=GREEN)
        vc = pr(t, wt("voices", "voices") - 0.1, 0.4) * (1 - ease(pr(t, wt("voices", "cushions") - 0.3, 0.3)))
        pill(c, "VOICES: TOO FAST TO COPY", 540, 455, 30, "#450A0A", RED, a=ca * ease(vc), sc=back(vc), pad=22, outline=RED)
        cs = pr(t, wt("voices", "cushions") - 0.2, 0.4)
        pill(c, "CUSHIONS BLOCK THE REST", 540, 455, 30, "#0F172A", AMBER, a=ca * ease(cs), sc=back(cs), pad=22, outline=AMBER)

    # ---- history ----
    ya = ease(pr(t, S("history") - 0.1, 0.5)) * A
    if ya > 0:
        yr = pr(t, wt("history", "1950s") - 0.2, 0.4)
        c.save(); c.translate(540, 560); safe_scale(c, back(yr), back(yr))
        text(c, "1950s", 0, 40, 150, WHITE, "black", a=ya * ease(yr)); c.restore()
        heli(c, 330, 950, 0.85, ya * ease(pr(t, wt("history", "helicopter") - 0.2, 0.4)), t)
        jet(c, 800, 950, 0.9, ya * ease(pr(t, wt("history", "airplane") - 0.2, 0.4)), t)
        ck = pr(t, wt("history", "cockpits") - 0.2, 0.4)
        pill(c, "FIRST PATENTS: QUIETER COCKPITS", 540, 1215, 30, "#0F172A", CYAN, a=ya * ease(ck), sc=back(ck), pad=22, outline=CYAN)

    for lid, s, col in (("mic", "LISTEN", YEL), ("flip", "FLIP IT", CYAN), ("cancel", "CANCEL", GREEN), ("inside", "DOUBLE-CHECK", YEL),
                        ("lows", "WHAT IT'S GREAT AT", GREEN), ("voices", "WHAT SLIPS THROUGH", RED), ("history", "WHERE IT STARTED", PURPLE)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "jet") - 0.2, "rumble"), (wt("hook", "fade"), "rise"), (wt("hook", "add") - 0.1, "pop"),
            (wt("mic", "microphone") - 0.2, "pop"), (wt("mic", "noise") - 0.6, "ping"),
            (wt("flip", "copy") - 0.3, "blip"), (wt("flip", "flipped") - 0.1, "wake"), (wt("flip", "plays") - 0.2, "ping"),
            (wt("cancel", "peak") - 0.2, "rise"), (wt("cancel", "nothing") - 0.3, "success"),
            (wt("inside", "mic") - 0.2, "pop"), (wt("inside", "correcting") - 0.1, "ok"),
            (wt("lows", "engine") - 0.2, "resolve"), (wt("voices", "voices") - 0.1, "warn"), (wt("voices", "cushions") - 0.2, "pop"),
            (wt("history", "1950s") - 0.2, "pop"), (wt("history", "cockpits") - 0.2, "ok")]
