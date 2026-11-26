"""Episode 22: How store security gates catch you (acousto-magnetic + RF tags), Black Friday."""
from hm.core import *
from hm.props import *

DARK = "#0F172A"
GATE = "#CBD5E1"
ALLOY = "#E2E8F0"
MAG = "#475569"
BURST = "#38BDF8"
RING = AMBER


def gates(c, a, t, alarm=0.0, waves=0.0):
    if a <= 0: return
    for gx in (230, 850):
        rr(c, gx - 40, 640, 80, 600, 30); fill(c, "#334155", a); c.fill()
        rr(c, gx - 28, 660, 56, 560, 22); fill(c, GATE, 0.15 * a); c.fill()
        if alarm > 0:
            on = 0.5 + 0.5 * math.sin(t * 18)
            glow(c, gx, 700, 120, RED, 0.8 * a * alarm * on)
            rr(c, gx - 28, 660, 56, 80, 22); fill(c, RED, a * alarm * on); c.fill()
    rr(c, 150, 1240, 780, 20, 8); fill(c, "#1E293B", a); c.fill()
    if waves > 0:
        for k in range(4):
            ph = (t * 1.2 + k / 4) % 1
            for gx, d in ((230, 1), (850, -1)):
                r = 40 + 280 * ph
                c.set_line_width(5); fill(c, BURST, a * waves * (1 - ph))
                c.new_path(); c.arc(gx, 940, r, (0 if d > 0 else math.pi) - 0.6, (0 if d > 0 else math.pi) + 0.6); c.stroke()


def bag(c, x, y, a, tag_glow=0.0):
    if a <= 0: return
    rr(c, x - 90, y - 110, 180, 200, 16); fill(c, "#F472B6", a); c.fill()
    c.set_line_width(10); fill(c, "#9D174D", a); c.new_path(); c.arc(x, y - 110, 50, math.pi, 2 * math.pi); c.stroke()
    text(c, "SALE", x, y + 10, 44, WHITE, "black", a=a)
    if tag_glow > 0:
        glow(c, x + 60, y + 60, 50, RING, 0.9 * a * tag_glow)
    rr(c, x + 30, y + 44, 60, 30, 6); fill(c, WHITE, a); c.fill()


def label_exploded(c, a, t, sep, vib=0.0, mag_on=1.0, show_alloy=0.0, show_mag=0.0):
    """The security sticker with its two strips pulled apart by `sep`."""
    if a <= 0: return
    cx, cy = 540, 940
    # sticker
    rr(c, cx - 300, cy - 110, 600, 220, 18); fill(c, "#F8FAFC", a * (1 - sep)); c.fill()
    text(c, "SECURITY LABEL", cx, cy - 70, 24, "#64748B", "black", a=a * (1 - sep))
    # alloy resonator strip (top)
    ay = cy - 20 - 150 * sep
    amp = 14 * vib * math.sin(t * 40)
    c.save(); c.translate(cx, ay)
    if vib > 0:
        glow(c, 0, 0, 260, RING, 0.35 * a * vib)
    c.move_to(-240, -10)
    for i in range(0, 25):
        x = -240 + 20 * i
        c.line_to(x, -10 + amp * math.sin(math.pi * i / 24))
    c.line_to(240, 10)
    for i in range(24, -1, -1):
        x = -240 + 20 * i
        c.line_to(x, 10 + amp * math.sin(math.pi * i / 24))
    c.close_path(); fill(c, lerp_col(ALLOY, RING, vib * 0.6), a); c.fill()
    c.restore()
    # bias magnet (bottom)
    my = cy + 30 + 150 * sep
    rr(c, cx - 240, my - 14, 480, 28, 6); fill(c, MAG, a); c.fill()
    if mag_on > 0:
        rr(c, cx - 240, my - 14, 240, 28, 6); fill(c, RED, a * mag_on); c.fill()
        rr(c, cx, my - 14, 240, 28, 6); fill(c, "#3B82F6", a * mag_on); c.fill()
        text(c, "N", cx - 200, my + 10, 22, WHITE, "black", a=a * mag_on)
        text(c, "S", cx + 200, my + 10, 22, WHITE, "black", a=a * mag_on)
    else:
        for k in range(16):
            ang = (k * 2.39) % (2 * math.pi)
            x = cx - 220 + k * 29
            c.set_line_width(4); fill(c, "#94A3B8", a)
            c.move_to(x - 9 * math.cos(ang), my - 9 * math.sin(ang)); c.line_to(x + 9 * math.cos(ang), my + 9 * math.sin(ang)); c.stroke()
    if show_alloy > 0:
        text(c, "ALLOY: VIBRATES IN A MAGNETIC FIELD", cx, ay - 50, 26, RING, "black", a=a * show_alloy, stroke=6)
    if show_mag > 0:
        text(c, "MAGNET: TUNES IT", cx, my + 70, 28, "#93C5FD", "black", a=a * show_mag, stroke=6)


def scope(c, a, t, p, ring_on=1.0, beep=0.0):
    """Timeline: transmit bursts, and the tag ringing in the gaps."""
    if a <= 0: return
    x0, x1, y = 110, 970, 960
    rr(c, x0 - 20, 680, x1 - x0 + 40, 520, 24); fill(c, "#0B1220", a); c.fill()
    text(c, "GATE SENDS", x0, 730, 24, BURST, "black", align="left", a=a)
    text(c, "TAG RINGS BACK", x0, 1170, 24, RING, "black", align="left", a=a * ring_on)
    period = 220
    xe = lerp(x0, x1, p)
    for k in range(5):
        bx = x0 + k * period
        if bx > xe: break
        # burst
        c.save(); c.rectangle(bx, 760, min(70, xe - bx), 180); c.clip()
        c.set_line_width(3); fill(c, BURST, a)
        c.move_to(bx, y - 60)
        for i in range(0, 71, 2):
            c.line_to(bx + i, y - 60 + 50 * math.sin(i * 1.2))
        c.stroke(); c.restore()
        # ring-down in the gap
        if ring_on > 0:
            gx0 = bx + 70
            c.save(); c.rectangle(gx0, 960, max(0, min(period - 70, xe - gx0)), 220); c.clip()
            c.set_line_width(4); fill(c, RING, a * ring_on)
            c.move_to(gx0, y + 90)
            for i in range(0, period - 70, 2):
                env = 60 * math.exp(-i / 55)
                c.line_to(gx0 + i, y + 90 + env * math.sin(i * 0.9))
            c.stroke(); c.restore()
    if beep > 0:
        c.save(); c.translate(780, 640); safe_scale(c, back(beep), back(beep)); c.rotate(-0.12)
        text(c, "BEEP!", 0, 30, 100, RED, "black", a=a * ease(beep), stroke=12)
        c.restore()


def checkout_pad(c, a, t, swipe):
    if a <= 0: return
    rr(c, 160, 1150, 760, 120, 24); fill(c, "#1E293B", a); c.fill()
    rr(c, 360, 1170, 360, 80, 16); fill(c, "#334155", a); c.fill()
    text(c, "DEACTIVATOR", 540, 1222, 28, CYAN, "black", a=a)
    glow(c, 540, 1210, 200, CYAN, 0.4 * a * swipe)


def rf_tag(c, a, t, zap):
    if a <= 0: return
    cx, cy = 540, 920
    rr(c, cx - 230, cy - 230, 460, 460, 24); fill(c, "#F8FAFC", a); c.fill()
    c.set_line_width(8); fill(c, COPPER if False else "#B45309", a)
    for k in range(6):
        s = 190 - k * 26
        c.rectangle(cx - s, cy - s, 2 * s, 2 * s); c.stroke()
    # capacitor plates
    rr(c, cx - 50, cy - 20, 100, 16, 4); fill(c, "#334155", a); c.fill()
    rr(c, cx - 50, cy + 8, 100, 16, 4); c.fill()
    text(c, "COIL", cx, cy - 210 - 30, 28, "#F59E0B", "black", a=a, stroke=6)
    text(c, "CAPACITOR", cx, cy + 280, 28, WHITE, "black", a=a, stroke=6)
    if zap > 0:
        glow(c, cx, cy, 160, YEL, 0.9 * a * (1 - zap * 0.5))
        c.set_line_width(7); fill(c, YEL, a * (1 - zap * 0.6))
        for k in range(6):
            ang = k * math.pi / 3 + 0.3
            c.move_to(cx, cy)
            for j in range(1, 5):
                r = j * 30
                c.line_to(cx + r * math.cos(ang) + 10 * (-1) ** j, cy + r * math.sin(ang) + 10 * (-1) ** (j + 1))
            c.stroke()


def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "HOW STORE GATES", "KNOW YOU DIDN'T PAY", S("strip"))

    gate_a = A * ease(pr(t, 0.05, 0.5)) * (1 - ease(pr(t, S("strip") - 0.2, 0.4)))
    lab_a = A * (ease(pr(t, S("strip") - 0.1, 0.5)) * (1 - ease(pr(t, S("listen") - 0.2, 0.4)))
                 + ease(pr(t, S("deact") - 0.1, 0.5)) * (1 - ease(pr(t, S("rf") - 0.2, 0.4))))
    sc_a = A * ease(pr(t, S("listen") - 0.1, 0.5)) * (1 - ease(pr(t, S("deact") - 0.2, 0.4)))
    rf_a = A * ease(pr(t, S("rf") - 0.1, 0.5))

    if gate_a > 0:
        bx = lerp(-150, 540, eio(pr(t, 0.3, 3.4)))
        alarm = ease(pr(t, wt("hook", "pay") - 0.3, 0.3))
        gates(c, gate_a, t, alarm=alarm, waves=1.0)
        bag(c, bx, 1080, gate_a, tag_glow=alarm)
        bf = pr(t, wt("hook", "black") - 0.2, 0.4) * (1 - ease(pr(t, wt("hook", "ever") - 0.2, 0.3)))
        pill(c, "BLACK FRIDAY", 540, 470, 34, DARK, YEL, a=gate_a * ease(bf), sc=back(bf), pad=24, outline=YEL)

    if lab_a > 0:
        if t < S("listen"):
            sep = ease(pr(t, wt("strip", "two") - 0.3, 0.6))
            vib = ease(pr(t, wt("ring", "vibrating") - 0.3, 0.4))
            label_exploded(c, lab_a, t, sep, vib=vib, show_alloy=ease(pr(t, wt("strip", "alloy") - 0.3, 0.4)),
                           show_mag=ease(pr(t, wt("strip", "magnet") - 0.3, 0.4)))
            if t > S("ring") - 0.2:
                bw = ease(pr(t, wt("ring", "bursts") - 0.3, 0.4))
                for k in range(3):
                    ph = (t * 1.6 + k / 3) % 1
                    c.set_line_width(6); fill(c, BURST, lab_a * bw * (1 - ph))
                    c.new_path(); c.arc(540, 700, 40 + 260 * ph, 0.35 * math.pi, 0.65 * math.pi); c.stroke()
                kz = pr(t, wt("ring", "fifty") - 0.3, 0.4) * (1 - ease(pr(t, wt("ring", "tuning") - 0.4, 0.3)))
                pill(c, "BURSTS AT ~58 kHz", 540, 470, 32, DARK, BURST, a=lab_a * ease(kz), sc=back(kz), pad=22, outline=BURST)
                tf = pr(t, wt("ring", "tuning") - 0.3, 0.4)
                pill(c, "RINGS LIKE A TUNING FORK", 540, 470, 30, DARK, RING, a=lab_a * ease(tf), sc=back(tf), pad=22, outline=RING)
            else:
                ts = pr(t, wt("strip", "two") - 0.2, 0.4)
                pill(c, "TWO HIDDEN METAL STRIPS", 540, 470, 30, DARK, WHITE, a=lab_a * ease(ts), sc=back(ts), pad=22, outline=MUTED)
        else:
            sw = ease(pr(t, wt("deact", "swipes") - 0.3, 0.6))
            dm = ease(pr(t, wt("deact", "demagnetizes") - 0.2, 0.5))
            label_exploded(c, lab_a, t, 1.0, vib=0.0, mag_on=1 - dm, show_mag=0)
            checkout_pad(c, lab_a, t, sw)
            dp = pr(t, wt("deact", "demagnetizes") - 0.2, 0.4) * (1 - ease(pr(t, wt("deact", "quiet") - 0.3, 0.3)))
            pill(c, "MAGNET SCRAMBLED", 540, 470, 32, DARK, CYAN, a=lab_a * ease(dp), sc=back(dp), pad=22, outline=CYAN)
            qp = pr(t, wt("deact", "quiet") - 0.2, 0.4)
            pill(c, "TAG GOES QUIET · NO BEEP", 540, 470, 30, "#052E2B", GREEN, a=lab_a * ease(qp), sc=back(qp), pad=22, outline=GREEN)

    if sc_a > 0:
        p = eio(pr(t, S("listen") - 0.1, 3.0))
        scope(c, sc_a, t, p, ring_on=ease(pr(t, wt("listen", "ringing") - 0.6, 0.4)), beep=pr(t, wt("listen", "beep") - 0.3, 0.4))
        hp = pr(t, wt("listen", "hears") - 0.3, 0.4)
        pill(c, "THE GATE LISTENS BETWEEN BURSTS", 540, 470, 28, DARK, RING, a=sc_a * ease(hp), sc=back(hp), pad=22, outline=RING)

    if rf_a > 0:
        zap = pr(t, wt("rf", "fried") - 0.3, 0.6)
        rf_tag(c, rf_a, t, zap)
        mh = pr(t, wt("rf", "megahertz") - 0.4, 0.4)
        pill(c, "RF TAGS: TUNED TO 8.2 MHz", 540, 470, 30, DARK, "#F59E0B", a=rf_a * ease(mh) * (1 - ease(pr(t, wt("rf", "fried") - 0.3, 0.3))), sc=back(mh), pad=22, outline="#F59E0B")
        fr = pr(t, wt("rf", "fried") - 0.2, 0.4)
        pill(c, "CHECKOUT: SHORTED OUT", 540, 470, 30, "#450A0A", YEL, a=rf_a * ease(fr), sc=back(fr), pad=22, outline=YEL)

    for lid, s, col in (("strip", "THE TAG", WHITE), ("ring", "THE PING", BURST), ("listen", "THE CATCH", RING),
                        ("deact", "THE CHECKOUT", GREEN), ("rf", "THE OTHER KIND", "#F59E0B")):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "black") - 0.2, "pop"), (wt("hook", "pay") - 0.3, "warn"),
            (wt("strip", "two") - 0.3, "blip"), (wt("strip", "alloy") - 0.3, "tick"), (wt("strip", "magnet") - 0.3, "tick"),
            (wt("ring", "bursts") - 0.3, "ping"), (wt("ring", "tuning") - 0.3, "ping"),
            (wt("listen", "ringing") - 0.6, "rise"), (wt("listen", "beep") - 0.3, "warn"),
            (wt("deact", "swipes") - 0.3, "blip"), (wt("deact", "quiet") - 0.2, "ok"),
            (wt("rf", "coil") - 0.3, "tick"), (wt("rf", "fried") - 0.3, "pop")]
