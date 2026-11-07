"""Episode 01: How your car knows where your key is."""
from hm.core import *
from hm.props import *

# ---------- the scenes ----------
CAM_MAIN = (540, 840, 1.0)
CAM_RELAY = (250, 1100, 0.55)
HOUSE_POS = (810, 790)
DEV_A = (412, 1112)
DEV_B = (598, 985)
KEY_HOUSE = (715, 938)

def sc(id_): return S(id_)

def draw(c, t):

    # --- camera / car placement ---
    rel = eio(pr(t, S("relay"), 1.1))
    cam = (lerp(CAM_MAIN[0], CAM_RELAY[0], rel), lerp(CAM_MAIN[1], CAM_RELAY[1], rel), lerp(CAM_MAIN[2], CAM_RELAY[2], rel))
    intro = eout(pr(t, 0, 0.7))
    cam = (cam[0], cam[1] + (1 - intro) * 260, cam[2] * (0.85 + 0.15 * intro))
    cta = cta_amount(t)
    scene_a = 1 - cta

    # x-ray: on for hook back seat, antennas onward
    xray = ease(pr(t, wt("hook", "sitting"), 0.4))

    # hazard flash at unlock (normal), and at relay unlock
    def flashes(t0):
        d = t - t0
        if d < 0 or d > 1.2: return 0
        return max(0, math.sin(d / 1.2 * 4 * math.pi)) if d < 1.2 else 0
    flash = max(flashes(wt("result", "unlocks")), flashes(wt("relay", "house", end=True) + 0.1))
    lights = ease(pr(t, wt("result", "engine"), 0.4)) * (1 - ease(pr(t, S("relay"), 0.4)))

    car(c, cam[0], cam[1], cam[2], xray=xray, flash=flash, lights=lights, alpha=scene_a)

    # --- antennas & bubbles ---
    pop_t = {"dl": wt("antennas", "door"), "dr": wt("antennas", "door") + 0.12,
             "cab": wt("antennas", "cabin"), "tr": wt("antennas", "trunk")}
    bub_t0 = wt("bubbles", "sends")
    for k, p in ANT.items():
        sp = to_screen(cam, p)
        ap = back(pr(t, pop_t[k], 0.35))
        # bubbles
        bg = eout(pr(t, bub_t0 + 0.12 * list(ANT).index(k), 0.9))
        ba = bg * scene_a
        if t > S("relay"):
            keep = 1.0 if k == "dr" else 1 - ease(pr(t, S("relay"), 0.5))
            ba *= keep
            # relay: dr bubble only shows once the relay starts
            if k == "dr": ba *= 0.35 + 0.65 * ease(pr(t, wt("relay", "relay"), 0.4))
        if t > S("uwb"):
            ba *= 1 - ease(pr(t, S("uwb"), 0.5)) * 0.6
        R = BUB_R * cam[2] * bg
        if k == "cab":
            def clipf(cc, cam=cam):
                x0, y0 = to_screen(cam, (-124, -78)); rr(cc, x0, y0, 248 * cam[2], 258 * cam[2], 34 * cam[2])
            bubble(c, sp[0], sp[1], R * 1.4, CYAN, ba, t, clip=clipf)
        else:
            bubble(c, sp[0], sp[1], R, CYAN, ba, t)
        da = scene_a * (1 if t < S("relay") else (1 if k == "dr" else 1 - ease(pr(t, S("relay"), 0.5))))
        antenna_dot(c, sp[0], sp[1], ap * cam[2] * 1.2, CYAN, da)
        # labels during antennas scene
        la = ease(pr(t, pop_t[k] + 0.1, 0.3)) * (1 - ease(pr(t, S("bubbles") + 0.6, 0.4)))
        if la > 0:
            off = {"dl": (-150, -110), "dr": (150, -110), "cab": (0, -150), "tr": (0, 120)}[k]
            if k == "cab": off = (0, -0)
            lpos = (sp[0] + off[0], sp[1] + off[1])
            if k == "cab": lpos = (sp[0], sp[1] + 70)
            pill(c, ANT_LABEL[k], lpos[0], lpos[1], 30, "#0F172A", CYAN, a=la, sc=back(la), pad=18, outline=CYAN)

    # 1-2 m scale bar
    sb = ease(pr(t, wt("bubbles", "meter") - 0.3, 0.4)) * (1 - ease(pr(t, S("wake") + 0.3, 0.3)))
    if sb > 0:
        p = to_screen(cam, ANT["dr"])
        scale_bar(c, (p[0], p[1] + 0), (p[0] + BUB_R * cam[2], p[1]), "1–2 m", sb)

    # --- hook ---
    if t < S("antennas") + 0.5:
        ha = 1 - ease(pr(t, S("antennas") - 0.1, 0.4))
        t1 = back(pr(t, 0.05, 0.45)); t2 = back(pr(t, 0.25, 0.45))
        c.save(); c.translate(540, 250); safe_scale(c, t1, t1)
        text(c, "HOW DOES YOUR CAR", 0, 0, 74, WHITE, "black", a=ha, stroke=0)
        c.restore()
        c.save(); c.translate(540, 345); safe_scale(c, t2, t2)
        text(c, "KNOW WHERE YOUR KEY IS?", 0, 0, 66, YEL, "black", a=ha)
        c.restore()
        # key outside (pocket) then inside back seat
        k1 = back(pr(t, wt("hook", "pocket") - 0.2, 0.4)) * (1 - ease(pr(t, wt("hook", "sitting"), 0.3)))
        if k1 > 0:
            keyfob(c, 205, 900, 0.95 * k1, 0.4, t)
            pill(c, "OUTSIDE", 205, 1035, 30, "#0F172A", WHITE, a=k1 * ha, sc=k1, pad=18, outline=MUTED)
        k2 = back(pr(t, wt("hook", "back"), 0.4))
        if k2 > 0:
            kp = to_screen(cam, (40, 128))
            keyfob(c, kp[0], kp[1], 0.75 * k2, 0.4, t, alpha=ha)
            pill(c, "INSIDE", kp[0], kp[1] - 120, 30, "#0F172A", WHITE, a=k2 * ha, sc=k2, pad=18, outline=MUTED)
        q = back(pr(t, wt("hook", "how"), 0.35)) * ha
        if q > 0:
            c.save(); c.translate(860, 640); safe_scale(c, q, q); c.rotate(0.12 * math.sin(t * 6))
            glow(c, 0, -40, 140, YEL, 0.35)
            text(c, "?", 0, 0, 200, YEL, "black", stroke=18)
            c.restore()

    # --- scene label pills ---
    labels = [("antennas", "THE ANTENNAS", CYAN), ("bubbles", "RADIO BUBBLES", CYAN), ("wake", "THE HANDSHAKE", AMBER),
              ("locate", "FINDING THE KEY", AMBER), ("result", "UNLOCK & START", GREEN), ("relay", "THE RELAY ATTACK", RED),
              ("uwb", "THE FIX: ULTRA-WIDEBAND", PURPLE)]
    for lid, s, col in labels:
        scene_label(c, t, lid, s, col)

    # --- key path (main) ---
    KEY_START = (120, 1300)
    KEY_DOOR = (250, 905)
    in_cab = eio(pr(t, wt("result", "inside"), 0.9))
    kcab = to_screen(cam, (-62, 10))
    key_enter = eout(pr(t, S("wake") - 0.1, 1.3))
    kp = lp(lp(KEY_START, KEY_DOOR, key_enter), kcab, in_cab)
    key_a = ease(pr(t, S("wake") - 0.15, 0.3)) * (1 - ease(pr(t, S("relay"), 0.5)))
    awake = ease(pr(t, wt("wake", "wakes"), 0.3))
    if key_a > 0:
        zzz(c, kp[0] + 10, kp[1] - 50, t, key_a * (1 - awake))
        keyfob(c, kp[0], kp[1], lerp(0.85, 0.62, in_cab), awake, t, alpha=key_a)

    # signal lines + panel
    meas = ease(pr(t, wt("wake", "measures"), 0.4)) * (1 - ease(pr(t, S("result") - 0.1, 0.3)))
    lines_a = ease(pr(t, wt("wake", "measures"), 0.4)) * (1 - ease(pr(t, wt("result", "inside"), 0.4)))
    strengths = {"dl": 5, "cab": 2, "tr": 1, "dr": 1}
    if lines_a > 0:
        for k in ("dl", "cab", "tr"):
            ap = to_screen(cam, ANT[k])
            st = strengths[k]
            pulse = 0.5 + 0.5 * math.sin(t * 8) if t > wt("locate", "compares") else 1
            rgb = hexc(CYAN)
            c.set_line_width(2 + st * 2.2 * (0.8 + 0.4 * pulse)); c.set_dash([6, 10], -t * 40)
            c.set_source_rgba(rgb[0], rgb[1], rgb[2], lines_a * (0.25 + 0.15 * st))
            c.move_to(*kp); c.line_to(*ap); c.stroke(); c.set_dash([])
    if meas > 0:
        px, py = 590, 300
        a = meas
        c.save(); c.translate(px, py)
        rr(c, 0, 0, 440, 210, 26); fill(c, "#0F172A", 0.92 * a); c.fill_preserve()
        fill(c, CYAN, 0.6 * a); c.set_line_width(3); c.stroke()
        text(c, "SIGNAL STRENGTH", 30, 46, 26, MUTED, "xbold", "left", a=a)
        for i, (k, nm) in enumerate((("dl", "Driver door"), ("cab", "Cabin"), ("tr", "Trunk"))):
            yy = 98 + i * 46
            text(c, nm, 30, yy, 30, WHITE, "bold", "left", a=a)
            f = int(round(strengths[k] * ease(pr(t, wt("wake", "measures") + 0.2 * i, 0.6))))
            bars(c, 290, yy + 6, 5, f, CYAN if strengths[k] >= 3 else "#7DD3FC", a, w=20, gap=7, h0=10, step=6)
        c.restore()

    # reply: waves + code chips
    rep = ease(pr(t, wt("wake", "answers") - 0.1, 0.3)) * (1 - ease(pr(t, wt("locate", "compares"), 0.4)))
    if rep > 0:
        tgt = to_screen(cam, ANT["dl"])
        ang = math.atan2(tgt[1] - kp[1], tgt[0] - kp[0])
        waves(c, kp[0], kp[1], ang, AMBER, t, rep, r0=60, r1=150)
        cs = wt("wake", "secret")
        for i, code in enumerate(("7F3A", "91C2", "E04B")):
            ph = pr(t, cs + i * 0.25, 0.9)
            if 0 < ph < 1:
                p = lp(kp, to_screen(cam, (-20, -140)), eio(ph))
                pill(c, code, p[0], p[1], 26, AMBER, "#0B1220", a=rep * (1 - pr(ph, 0.8, 0.2)), pad=12, weight="mono")
    # code check badge
    ck = pr(t, wt("locate", "checks"), 0.5)
    cka = ease(ck) * (1 - ease(pr(t, wt("result", "unlocks") - 0.2, 0.3)))
    if cka > 0:
        c.save(); c.translate(300, 405); s_ = back(ck); safe_scale(c, s_, s_)
        rr(c, -200, -38, 400, 76, 38); fill(c, "#052E2B", cka); c.fill_preserve()
        fill(c, GREEN, cka); c.set_line_width(3); c.stroke()
        text(c, "CODE MATCHES", -30, 12, 34, GREEN, "xbold", a=cka)
        check(c, 140, 0, 36, GREEN, cka, lw=8, p=pr(t, wt("locate", "checks") + 0.2, 0.4))
        c.restore()
    # locate pin
    loc = pr(t, wt("locate", "exactly"), 0.4)
    la = ease(loc) * (1 - ease(pr(t, wt("result", "unlocks") - 0.1, 0.3)))
    if la > 0:
        r = 70 + 12 * math.sin(t * 6)
        c.set_line_width(5); fill(c, AMBER, la); c.arc(kp[0], kp[1], r, 0, 2 * math.pi); c.stroke()
        pill(c, "OUTSIDE · DRIVER DOOR", 265, 765, 30, "#0F172A", AMBER, a=la, sc=back(loc), pad=20, outline=AMBER)

    # unlock lock icon
    ul = pr(t, wt("result", "unlocks") - 0.05, 0.5)
    ua = ease(pr(t, wt("result", "unlocks") - 0.25, 0.25)) * (1 - ease(pr(t, wt("result", "inside") + 0.2, 0.3)))
    if ua > 0:
        glow(c, 540, 340, 160, GREEN, 0.35 * ua)
        lock_icon(c, 540, 350, 1.3, eout(ul), GREEN, ua)
        text(c, "UNLOCKED", 540, 472, 44, GREEN, "black", a=ua * ease(ul))
    # engine start
    es = pr(t, wt("result", "engine") - 0.15, 0.4)
    ea = ease(es) * (1 - ease(pr(t, S("relay"), 0.4)))
    if ea > 0:
        c.save(); c.translate(540, 410); s_ = back(es); safe_scale(c, s_, s_)
        glow(c, 0, 0, 190, GREEN, 0.45 * ea * (0.75 + 0.25 * math.sin(t * 7)))
        c.arc(0, 0, 90, 0, 2 * math.pi); fill(c, "#052E2B", ea); c.fill_preserve()
        fill(c, GREEN, ea); c.set_line_width(7); c.stroke()
        c.set_line_width(9); c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.arc(0, 4, 36, -math.pi / 2 + 0.6, -math.pi / 2 - 0.6 + 2 * math.pi); c.stroke()
        c.move_to(0, -40); c.line_to(0, -6); c.stroke()
        text(c, "ENGINE START", 0, 140, 36, GREEN, "black", a=ea)
        c.restore()
    # cabin bubble highlight when key inside
    if in_cab > 0 and t < S("relay") + 0.4:
        cp = to_screen(cam, ANT["cab"])
        glow(c, cp[0], cp[1], 160, CYAN, 0.35 * in_cab * (1 - ease(pr(t, S("relay"), 0.4))))

    # ---------- relay ----------
    ra = ease(pr(t, S("relay") + 0.4, 0.6)) * scene_a
    if ra > 0:
        hs = back(pr(t, S("relay") + 0.4, 0.7))
        house(c, HOUSE_POS[0], HOUSE_POS[1], 0.95 * hs, ra)
        text(c, "YOUR HOUSE", HOUSE_POS[0], HOUSE_POS[1] - 225, 34, MUTED, "xbold", a=ra * (1 - ease(pr(t, S("uwb"), 0.4))))
        text(c, "DRIVEWAY", CAM_RELAY[0], 1330, 34, MUTED, "xbold", a=ra * rel)
        # key inside house
        hk_awake = ease(pr(t, wt("relay", "key"), 0.3))
        keyfob(c, KEY_HOUSE[0], KEY_HOUSE[1] + 4, 0.55, hk_awake, t, alpha=ra,
               badge="UWB", badge_a=ease(pr(t, wt("uwb", "ultra"), 0.4)))
        if hk_awake < 1: zzz(c, KEY_HOUSE[0], KEY_HOUSE[1] - 40, t, ra * (1 - hk_awake))
        # devices
        th = wt("relay", "thieves")
        fix = ease(pr(t, wt("uwb", "fake"), 0.4))
        dA = back(pr(t, th, 0.4)); dB = back(pr(t, th + 0.25, 0.4))
        act = ease(pr(t, wt("relay", "relay"), 0.3)) * (1 - fix)
        drp = to_screen(cam, ANT["dr"])
        # beams: car bubble -> A -> B, B bubble -> key
        b1 = eio(pr(t, wt("relay", "relay"), 0.5))
        b2 = eio(pr(t, wt("relay", "bubble"), 0.8))
        beam_a = ra * (1 - fix * 0.8)
        dashed_beam(c, DEV_A, DEV_B, RED, t, beam_a * act, b2)
        bb = ease(pr(t, wt("relay", "key") - 0.5, 0.5))
        bubble(c, DEV_B[0], DEV_B[1], 150 * bb, RED, beam_a * bb * act, t)
        # reply back
        rb = pr(t, wt("relay", "inside"), 1.0)
        if 0 < rb < 1:
            for path in ((KEY_HOUSE, DEV_B), (DEV_B, DEV_A), (DEV_A, drp)):
                pass
            pts = [KEY_HOUSE, DEV_B, DEV_A, drp]
            seg = min(2, int(rb * 3)); f = rb * 3 - seg
            p = lp(pts[seg], pts[seg + 1], eio(f))
            glow(c, p[0], p[1], 50, AMBER, 0.9 * ra)
            pill(c, "7F3A", p[0], p[1], 24, AMBER, "#0B1220", a=ra, pad=10, weight="mono")
        device(c, DEV_A[0], DEV_A[1], 0.9 * dA, ra, t, act)
        device(c, DEV_B[0], DEV_B[1], 0.9 * dB, ra, t, act)
        if fix > 0:
            cross(c, DEV_A[0], DEV_A[1] - 10, 70, RED, fix * ra, 12)
            cross(c, DEV_B[0], DEV_B[1] - 10, 70, RED, fix * ra, 12)
        # relay unlock warning
        ru = pr(t, wt("relay", "house", end=True) - 0.05, 0.4)
        rua = ease(ru) * (1 - ease(pr(t, wt("uwb", "time") - 0.6, 0.3)))
        if rua > 0:
            lock_icon(c, CAM_RELAY[0], 820, 1.15, eout(ru), RED, rua)
            pill(c, "RELAY ATTACK!", 540, 380, 50, "#450A0A", RED, a=rua, sc=back(ru), pad=34, outline=RED)
            text(c, "Car thinks the key is right there", 540, 480, 32, WHITE, "semi", a=rua)

    # ---------- UWB ----------
    ua2 = ease(pr(t, wt("uwb", "time") - 0.35, 0.35)) * scene_a
    if ua2 > 0 and t >= S("uwb") - 0.1:
        drp = to_screen(cam, ANT["dr"])
        # timer bar
        tt0 = wt("uwb", "time")
        tp = pr(t, tt0, wt("uwb", "fake") - tt0 - 0.1)
        pts = [drp, DEV_A, DEV_B, KEY_HOUSE, DEV_B, DEV_A, drp]
        if 0 < tp < 1:
            seg = min(len(pts) - 2, int(tp * (len(pts) - 1))); f = tp * (len(pts) - 1) - seg
            p = lp(pts[seg], pts[seg + 1], f)
            glow(c, p[0], p[1], 60, PURPLE, ua2)
            c.arc(p[0], p[1], 10, 0, 2 * math.pi); fill(c, "#EDE9FE", ua2); c.fill()
        lt = pr(t, wt("uwb", "light") - 0.1, 0.4)
        pa = ua2 * (1 - ease(lt))
        # stopwatch panel
        bx, by, bw = 110, 300, 860
        rr(c, bx, by, bw, 190, 26); fill(c, "#0F172A", 0.92 * pa); c.fill_preserve()
        fill(c, PURPLE, 0.6 * pa); c.set_line_width(3); c.stroke()
        text(c, "SIGNAL TRAVEL TIME", bx + 30, by + 50, 28, MUTED, "xbold", "left", a=pa)
        thr = 0.32
        fillp = tp if t < wt("uwb", "fake") else 1.0
        over = fillp > thr
        rr(c, bx + 30, by + 80, bw - 60, 40, 20); fill(c, "#1E293B", pa); c.fill()
        if fillp > 0:
            rr(c, bx + 30, by + 80, max(40, (bw - 60) * fillp), 40, 20)
            fill(c, RED if over else PURPLE, pa); c.fill()
        tx = bx + 30 + (bw - 60) * thr
        fill(c, WHITE, pa); c.set_line_width(4); c.move_to(tx, by + 70); c.line_to(tx, by + 130); c.stroke()
        text(c, "max for a key that's close", tx, by + 165, 27, WHITE, "semi", a=pa)
        fk = pr(t, wt("uwb", "fake"), 0.4)
        if fk > 0:
            pill(c, "TOO FAR — STAYS LOCKED", 540, 555, 40, "#052E2B", GREEN, a=ua2 * ease(fk), sc=back(fk), pad=30, outline=GREEN)
            lock_icon(c, CAM_RELAY[0], 820, 1.15, 0, GREEN, ua2 * ease(fk))
        if lt > 0:
            la_ = ua2 * ease(lt)
            c.save(); c.translate(540, 360); s_ = back(lt); safe_scale(c, s_, s_)
            glow(c, 0, 0, 380, YEL, 0.18 * la_)
            text(c, "YOU CAN'T FAKE", 0, -10, 76, WHITE, "black", a=la_)
            text(c, "THE SPEED OF LIGHT", 0, 80, 76, YEL, "black", a=la_)
            c.restore()



def SFX():
    cues = []
    for w, n, d in (("door", 0, 0), ("door", 0, 0.12), ("cabin", 0, 0), ("trunk", 0, 0)):
        cues.append((wt("antennas", w, n) + d, "pop"))
    cues += [(wt("bubbles", "sends") + 0.12 * i, "ping") for i in range(4)]
    cues.append((wt("wake", "wakes"), "wake"))
    cues += [(wt("wake", "secret") + 0.25 * i, "blip") for i in range(3)]
    cues += [(wt("locate", "checks") + 0.2, "ok"), (wt("result", "unlocks"), "success"), (wt("result", "engine"), "rumble"),
             (wt("relay", "thieves"), "low"), (wt("relay", "house", end=True), "warn")]
    tt0, tf = wt("uwb", "time"), wt("uwb", "fake")
    t = tt0
    while t < tf: cues.append((t, "tick")); t += 0.18
    cues += [(tf, "resolve"), (wt("uwb", "light"), "rise")]
    return cues
