"""Episode 07: How GPS finds you (and why it needs Einstein)."""
from hm.core import *
from hm.props import *

EARTH_C, EARTH_R = (540, 2500), 1290      # top of the Earth at y = 1210
PHONE = (540, 1185)
SATS = [(190, 560), (540, 470), (890, 560), (370, 780)]
MAP = (110, 500, 860, 760)                 # x, y, w, h
YOU = (560, 880)


# ---------- props ----------
def earth(c, a):
    if a <= 0: return
    cx, cy = EARTH_C
    glow(c, cx, cy - EARTH_R + 10, 500, CYAN, 0.18 * a)
    c.arc(cx, cy, EARTH_R, 0, 2 * math.pi)
    g = cairo.LinearGradient(0, cy - EARTH_R, 0, cy - EARTH_R + 300)
    g.add_color_stop_rgba(0, *hexc("#1D4ED8")[:3], a); g.add_color_stop_rgba(1, *hexc("#0B1220")[:3], a)
    c.set_source(g); c.fill()
    c.save(); c.arc(cx, cy, EARTH_R, 0, 2 * math.pi); c.clip()
    for (x, y, rx, ry) in ((260, 1250, 160, 40), (700, 1240, 210, 50), (980, 1290, 120, 40)):
        c.save(); c.translate(x, y); safe_scale(c, rx, ry); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
        fill(c, "#16A34A", 0.75 * a); c.fill()
    c.restore()
    c.set_line_width(4); fill(c, "#7DD3FC", 0.6 * a); c.arc(cx, cy, EARTH_R, 0, 2 * math.pi); c.stroke()


def small_phone(c, x, y, s, a, glow_=0.0):
    if a <= 0: return
    if glow_ > 0: glow(c, x, y, 90 * s, YEL, 0.5 * glow_ * a)
    rr(c, x - 22 * s, y - 40 * s, 44 * s, 80 * s, 10 * s); fill(c, "#0F172A", a); c.fill_preserve()
    fill(c, "#CBD5E1", a); c.set_line_width(3); c.stroke()
    rr(c, x - 16 * s, y - 32 * s, 32 * s, 60 * s, 6 * s); fill(c, "#38BDF8", a); c.fill()


def satellite(c, x, y, s, a, t, clock=0.0, col=CYAN):
    if a <= 0: return
    c.save(); c.translate(x, y); safe_scale(c, s, s); c.rotate(0.1 * math.sin(t * 0.8 + x))
    for sx in (-1, 1):
        rr(c, sx * 40 + (-90 if sx < 0 else 0), -22, 90, 44, 4); fill(c, "#1D4ED8", a); c.fill()
        c.set_line_width(2); fill(c, "#60A5FA", a)
        for k in range(1, 4):
            xx = sx * 40 + (-90 if sx < 0 else 0) + k * 22
            c.move_to(xx, -22); c.line_to(xx, 22); c.stroke()
    rr(c, -34, -34, 68, 68, 10); fill(c, "#E2E8F0", a); c.fill()
    rr(c, -34, -34, 68, 68, 10); fill(c, col, 0.25 * a); c.fill()
    c.set_line_width(5); fill(c, "#94A3B8", a); c.move_to(0, 34); c.line_to(0, 56); c.stroke()
    c.arc(0, 62, 9, 0, 2 * math.pi); fill(c, "#94A3B8", a); c.fill()
    c.restore()
    if clock > 0:
        cx, cy = x + 58 * s, y - 52 * s
        c.arc(cx, cy, 22, 0, 2 * math.pi); fill(c, "#0F172A", clock * a); c.fill_preserve(); fill(c, AMBER, clock * a); c.set_line_width(3); c.stroke()
        ang = t * 4
        c.set_line_width(3); c.move_to(cx, cy); c.line_to(cx + 14 * math.sin(ang), cy - 14 * math.cos(ang)); c.stroke()


def pulse(c, p, q, prog, col, a):
    if a <= 0 or not (0 < prog < 1): return
    x, y = lp(p, q, prog)
    glow(c, x, y, 34, col, 0.9 * a)
    c.arc(x, y, 8, 0, 2 * math.pi); fill(c, WHITE, a); c.fill()


def city_map(c, a):
    if a <= 0: return
    x, y, w, h = MAP
    rr(c, x, y, w, h, 30); fill(c, "#111827", 0.95 * a); c.fill_preserve(); fill(c, "#334155", a); c.set_line_width(3); c.stroke()
    c.save(); rr(c, x, y, w, h, 30); c.clip()
    c.set_line_width(10); fill(c, "#1F2937", a)
    for k in range(1, 8):
        c.move_to(x + k * w / 8, y); c.line_to(x + k * w / 8 + 40, y + h); c.stroke()
    for k in range(1, 7):
        c.move_to(x, y + k * h / 7); c.line_to(x + w, y + k * h / 7 - 30); c.stroke()
    c.set_line_width(26); fill(c, "#1E3A8A", 0.6 * a)
    c.move_to(x, y + h * 0.75); c.curve_to(x + w * 0.3, y + h * 0.6, x + w * 0.6, y + h * 0.95, x + w, y + h * 0.8); c.stroke()
    c.restore()


def range_circle(c, center, r, prog, col, a):
    if a <= 0 or prog <= 0: return
    x, y, w, h = MAP
    c.save(); rr(c, x, y, w, h, 30); c.clip()
    c.set_line_width(5); c.set_dash([16, 10]); fill(c, col, a)
    c.arc(center[0], center[1], r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * prog); c.stroke(); c.set_dash([])
    c.restore()
    c.arc(center[0], center[1], 9, 0, 2 * math.pi); fill(c, col, a); c.fill()


def big_clock(c, x, y, r, a, ang, col, label):
    if a <= 0: return
    c.arc(x, y, r, 0, 2 * math.pi); fill(c, "#0F172A", 0.95 * a); c.fill_preserve(); fill(c, col, a); c.set_line_width(6); c.stroke()
    for k in range(12):
        aa = k * math.pi / 6
        c.set_line_width(4); fill(c, "#64748B", a)
        c.move_to(x + (r - 18) * math.sin(aa), y - (r - 18) * math.cos(aa)); c.line_to(x + (r - 6) * math.sin(aa), y - (r - 6) * math.cos(aa)); c.stroke()
    c.set_line_width(8); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, col, a)
    c.move_to(x, y); c.line_to(x + (r - 30) * math.sin(ang), y - (r - 30) * math.cos(ang)); c.stroke()
    c.arc(x, y, 10, 0, 2 * math.pi); fill(c, col, a); c.fill()
    text(c, label, x, y + r + 50, 28, col, "xbold", a=a)


# ---------- the episode ----------
def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "HOW DOES GPS", "KNOW WHERE YOU ARE?", S("sats"))

    # ---- space view: hook, sats, time, delay ----
    sa = A * ease(pr(t, 0.05, 0.5)) * (1 - ease(pr(t, S("meet") - 0.1, 0.4)))
    if sa > 0:
        earth(c, sa)
        small_phone(c, PHONE[0], PHONE[1], 1.2, sa, glow_=ease(pr(t, wt("hook", "listens") - 0.2, 0.4)))
        nos = pr(t, wt("hook", "sending") - 0.1, 0.4) * (1 - ease(pr(t, S("sats"), 0.3)))
        pill(c, "NOTHING SENT UP", 540, 1060, 30, "#0F172A", WHITE, a=sa * ease(nos), sc=back(nos), pad=20, outline=MUTED)
        n_sats = 3
        for i, (x, y) in enumerate(SATS[:n_sats]):
            k = back(pr(t, wt("sats", "satellites") - 0.3 + 0.15 * i, 0.5)) if t < S("sats") + 3 else 1.0
            k = max(k, back(pr(t, 0.4 + 0.2 * i, 0.5)) if t < S("sats") else k)
            clk = ease(pr(t, wt("sats", "atomic") - 0.2, 0.4))
            satellite(c, x, y + 8 * math.sin(t * 1.3 + i), 0.9 * k, sa, t, clock=clk)
        # signals raining down from the start (listening), clocked pulses during "time"
        on = ease(pr(t, wt("hook", "listens") - 0.3, 0.4))
        for i, (x, y) in enumerate(SATS[:n_sats]):
            for kk in range(2):
                ph = (t * 0.6 + i * 0.27 + kk * 0.5) % 1
                pulse(c, (x, y + 40), PHONE, ph, AMBER, sa * on)
        alt = pr(t, wt("sats", "twenty") - 0.2, 0.4) * (1 - ease(pr(t, S("time"), 0.3)))
        if alt > 0:
            fill(c, WHITE, sa * ease(alt)); c.set_line_width(3); c.set_dash([10, 8])
            c.move_to(1000, 560); c.line_to(1000, 1180); c.stroke(); c.set_dash([])
            pill(c, "20,200 KM", 870, 870, 30, "#0F172A", WHITE, a=sa * ease(alt), sc=back(alt), pad=18, outline=MUTED)
        ts = pr(t, wt("time", "time") - 0.2, 0.4) * (1 - ease(pr(t, S("delay"), 0.3)))
        pill(c, "\"IT'S 10:04:31.0000000 · I'M HERE\"", 540, 1000, 26, "#0F172A", AMBER, a=sa * ease(ts), sc=back(ts), pad=20, outline=AMBER)
        dl = pr(t, wt("delay", "late") - 0.2, 0.4)
        if dl > 0:
            rr(c, 160, 930, 760, 150, 26); fill(c, "#0F172A", 0.94 * sa * ease(dl)); c.fill_preserve()
            fill(c, AMBER, 0.7 * sa * ease(dl)); c.set_line_width(3); c.stroke()
            text(c, "TRAVEL TIME  ≈ 0.07 s", 540, 985, 34, WHITE, "black", a=sa * ease(dl))
            sl = ease(pr(t, wt("delay", "speed") - 0.2, 0.4))
            text(c, "× SPEED OF LIGHT = DISTANCE", 540, 1045, 30, YEL, "xbold", a=sa * sl)

    # ---- map view: meet, four ----
    ma = A * ease(pr(t, S("meet") - 0.1, 0.5)) * (1 - ease(pr(t, S("twist") - 0.1, 0.4)))
    if ma > 0:
        city_map(c, ma)
        centers = [(260, 640), (900, 620), (420, 1220), (900, 1190)]
        cols = [CYAN, PURPLE, GREEN, AMBER]
        for i, cen in enumerate(centers):
            r = math.hypot(YOU[0] - cen[0], YOU[1] - cen[1])
            if i == 0: start = wt("meet", "distance") - 0.2
            elif i < 3: start = wt("meet", "add") - 0.2 + 0.5 * (i - 1)
            else: start = wt("four", "four") - 0.2
            range_circle(c, cen, r, eout(pr(t, start, 0.9)), cols[i], ma)
        hit = ease(pr(t, wt("meet", "meet") - 0.2, 0.4))
        if hit > 0:
            glow(c, YOU[0], YOU[1], 70, YEL, 0.6 * ma * hit)
            small_phone(c, YOU[0], YOU[1], 1.0, ma * hit)
        yh = pr(t, wt("meet", "spot") - 0.3, 0.4) * (1 - ease(pr(t, S("four"), 0.3)))
        pill(c, "YOU ARE HERE", 540, 1330, 30, "#052E2B", GREEN, a=ma * ease(yh), sc=back(yh), pad=22, outline=GREEN)
        ce = pr(t, wt("four", "cheap") - 0.3, 0.4)
        if ce > 0:
            c.save(); c.translate(540, 1330); safe_scale(c, back(ce), back(ce))
            rr(c, -300, -38, 600, 76, 38); fill(c, "#0F172A", ma); c.fill_preserve(); fill(c, AMBER, ma); c.set_line_width(3); c.stroke()
            text(c, "4TH SATELLITE FIXES YOUR CLOCK", -20, 11, 28, AMBER, "xbold", a=ma)
            check(c, 255, 0, 30, AMBER, ma, lw=7, p=pr(t, wt("four", "clock") - 0.1, 0.4))
            c.restore()

    # ---- twist: clocks run faster up there ----
    wa = A * ease(pr(t, S("twist") - 0.1, 0.5)) * (1 - ease(pr(t, S("fix") + 1.8, 0.4)))
    if wa > 0:
        run = max(0.0, t - S("twist"))
        big_clock(c, 290, 800, 170, wa, run * 2.0, CYAN, "GROUND")
        big_clock(c, 790, 800, 170, wa, run * 2.0 * (1 + 0.25 * ease(pr(t, wt("twist", "faster") - 0.2, 0.6))), AMBER, "SATELLITE")
        satellite(c, 790, 560, 0.55, wa, t)
        fs = pr(t, wt("twist", "thirty") - 0.2, 0.4)
        if fs > 0:
            c.save(); c.translate(540, 1150); safe_scale(c, back(fs), back(fs))
            text(c, "+38 µs / DAY", 0, 30, 96, YEL, "black", a=wa * ease(fs), stroke=10)
            c.restore()
        ft = pr(t, wt("twist", "faster") - 0.2, 0.4) * (1 - ease(pr(t, wt("twist", "thirty") - 0.3, 0.3)))
        pill(c, "WEAKER GRAVITY → TIME RUNS FASTER", 540, 1150, 28, "#0F172A", AMBER, a=wa * ease(ft), sc=back(ft), pad=20, outline=AMBER)

    # ---- fix: drift, then tuned slow ----
    fa = A * ease(pr(t, S("fix") + 1.6, 0.5))
    if fa > 0:
        city_map(c, fa)
        dr = ease(pr(t, wt("fix", "drift") - 0.1, 1.6)) * (1 - ease(pr(t, wt("fix", "tuned") - 0.1, 0.8)))
        x0, y0 = YOU
        x1, y1 = lerp(x0, 880, dr), lerp(y0, 600, dr)
        small_phone(c, x0, y0, 1.0, fa)
        if dr > 0.02:
            c.set_line_width(6); c.set_dash([14, 10]); fill(c, RED, fa); c.move_to(x0, y0); c.line_to(x1, y1); c.stroke(); c.set_dash([])
            glow(c, x1, y1, 60, RED, 0.7 * fa); c.arc(x1, y1, 14, 0, 2 * math.pi); fill(c, RED, fa); c.fill()
            pill(c, "≈ 11 KM OFF PER DAY", 540, 1330, 30, "#450A0A", RED, a=fa * ease(pr(t, wt("fix", "eleven") - 0.2, 0.4)), pad=22, outline=RED)
        tn = pr(t, wt("fix", "tuned") - 0.1, 0.4)
        if tn > 0:
            c.save(); c.translate(540, 1330); safe_scale(c, back(tn), back(tn))
            rr(c, -330, -40, 660, 80, 40); fill(c, "#052E2B", fa); c.fill_preserve(); fill(c, GREEN, fa); c.set_line_width(3); c.stroke()
            text(c, "10.22999999543 MHz", -30, 13, 34, GREEN, "mono", a=fa)
            check(c, 285, 0, 32, GREEN, fa, lw=7, p=pr(t, wt("fix", "slow") - 0.1, 0.4))
            c.restore()
            text(c, "CLOCKS SET SLOW BEFORE LAUNCH", 540, 1250, 26, GREEN, "xbold", a=fa * ease(tn))

    for lid, s, col in (("sats", "THE SATELLITES", CYAN), ("time", "THE SIGNAL", AMBER), ("delay", "THE MEASUREMENT", YEL),
                        ("meet", "THE CIRCLES", PURPLE), ("four", "WHY FOUR", AMBER), ("twist", "THE TWIST", YEL), ("fix", "EINSTEIN'S FIX", GREEN)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "sending") - 0.1, "low"), (wt("hook", "listens") - 0.2, "ping"),
            (wt("sats", "satellites") - 0.3, "pop"), (wt("sats", "satellites") - 0.15, "pop"), (wt("sats", "satellites"), "pop"),
            (wt("sats", "twenty") - 0.2, "blip"), (wt("sats", "atomic") - 0.2, "tick"),
            (wt("time", "time") - 0.2, "blip"), (wt("delay", "late") - 0.2, "pop"), (wt("delay", "speed") - 0.2, "rise"),
            (wt("meet", "distance") - 0.2, "ping"), (wt("meet", "add") - 0.2, "ping"), (wt("meet", "add") + 0.3, "ping"),
            (wt("meet", "meet") - 0.2, "success"), (wt("four", "four") - 0.2, "ping"), (wt("four", "clock") - 0.1, "ok"),
            (wt("twist", "twist") - 0.2, "warn"), (wt("twist", "thirty") - 0.2, "pop"),
            (wt("fix", "drift") - 0.1, "low"), (wt("fix", "tuned") - 0.1, "resolve")]
