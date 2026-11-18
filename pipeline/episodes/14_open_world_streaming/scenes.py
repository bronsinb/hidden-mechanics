"""Episode 14 (GTA 6 week #4, launch day): How open worlds have no loading screens (streaming + LOD)."""
from hm.core import *
from hm.props import *

DARK = "#0F172A"
PINK = "#F472B6"
STAGE = (60, 560, 1020, 1320)        # x0, y0, x1, y1 of the map viewport


def h(i, j, k=0):
    """Deterministic pseudo-random 0..1 per cell."""
    v = math.sin(i * 127.1 + j * 311.7 + k * 74.7) * 43758.5453
    return v - math.floor(v)


def cell_city(c, x, y, s, i, j, a, detail):
    """One city block at (x,y) size s. detail 0 = box only, 1 = windows."""
    if a <= 0: return
    pad = s * 0.12
    rr(c, x + pad * 0.5, y + pad * 0.5, s - pad, s - pad, s * 0.06); fill(c, "#1F2937", a); c.fill()
    if h(i, j, 9) < 0.18:                       # park
        rr(c, x + pad, y + pad, s - 2 * pad, s - 2 * pad, s * 0.08); fill(c, "#166534", a); c.fill()
        for k in range(3):
            c.arc(x + s * (0.3 + 0.2 * k), y + s * (0.35 + 0.15 * (k % 2)), s * 0.09, 0, 2 * math.pi); fill(c, "#22C55E", a); c.fill()
        return
    if h(i, j, 8) < 0.12:                       # water / canal
        rr(c, x + pad, y + pad, s - 2 * pad, s - 2 * pad, s * 0.08); fill(c, "#0E7490", a); c.fill()
        return
    n = 2 + int(h(i, j, 1) * 2)
    for k in range(n):
        bw = s * (0.28 + 0.2 * h(i, j, k + 2)); bh = s * (0.28 + 0.2 * h(i, j, k + 5))
        bx = x + pad + (s - 2 * pad - bw) * h(i, j, k + 11); by = y + pad + (s - 2 * pad - bh) * h(i, j, k + 17)
        col = ("#475569", "#64748B", "#334155", "#7C3AED")[int(h(i, j, k + 23) * 3.99)] if h(i, j, k + 29) < 0.85 else PINK
        rr(c, bx, by, bw, bh, s * 0.03); fill(c, col, a); c.fill()
        if detail > 0:
            for wi in range(3):
                for wj in range(3):
                    c.rectangle(bx + bw * (0.15 + 0.27 * wi), by + bh * (0.15 + 0.27 * wj), bw * 0.14, bh * 0.14)
                    fill(c, "#FDE68A" if h(i + wi, j + wj, k) < 0.5 else "#BAE6FD", 0.7 * a * detail); c.fill()
            c.rectangle(bx, by, bw, bh * 0.08); fill(c, WHITE, 0.25 * a * detail); c.fill()


def zoomed_out_map(c, a, t, memfit=0.0):
    if a <= 0: return
    n, s = 14, 50
    x0, y0 = 540 - n * s / 2, 520
    rr(c, x0 - 10, y0 - 10, n * s + 20, n * s + 20, 18); fill(c, "#0B1220", a); c.fill()
    for i in range(n):
        for j in range(n):
            cell_city(c, x0 + i * s, y0 + j * s, s, i, j, a, 0)
    # car blip
    cx, cy = x0 + 7.5 * s, y0 + 8.5 * s - 30 * math.sin(t * 0.6)
    glow(c, cx, cy, 40, YEL, 0.8 * a); c.arc(cx, cy, 10, 0, 2 * math.pi); fill(c, YEL, a); c.fill()
    return x0, y0, n * s


def memory_box(c, a, p, t):
    if a <= 0: return
    x, y, w, hh = 200, 1262, 600, 54
    text(c, "CONSOLE MEMORY", x, y - 18, 26, MUTED, "black", align="left", a=a)
    rr(c, x, y, w, hh, 16); fill(c, DARK, a); c.fill_preserve(); c.set_line_width(4); fill(c, WHITE, a); c.stroke()
    fw = w * min(p, 1.0)
    col = lerp_col(CYAN, RED, ease(cl((p - 0.7) / 0.3)))
    rr(c, x + 6, y + 6, max(fw - 12, 1), hh - 12, 11); fill(c, col, a); c.fill()
    if p > 1:
        over = (p - 1) * w
        shake = 4 * math.sin(t * 40)
        rr(c, x + w - 6 + shake, y + 6, over, hh - 12, 11); fill(c, RED, a * 0.9); c.fill()
        glow(c, x + w, y + hh / 2, 90, RED, 0.6 * a)


# ---------- zoomed-in streaming view ----------
S_ = 120                                    # cell size on screen
CARX, CARY = 540, 1010                       # car screen position


def player_world(t):
    """Car world position (cells) going north (negative y)."""
    t0 = S("stream") - 0.3
    if t < t0: return 0.0, 0.0
    v = 0.55
    y = -v * (t - t0)
    t1 = wt("speed", "move") - 0.3
    if t > t1:
        y -= 3.2 * (t - t1) ** 1.4               # accelerate hard
    return 0.0, y


def streaming_view(c, a, t, mode):
    """mode: dict with load radius, lag, lod, cone, unloaded style."""
    if a <= 0: return
    px, py = player_world(t)
    x0, y0, x1, y1 = STAGE
    c.save(); rr(c, x0, y0, x1 - x0, y1 - y0, 22); c.clip()
    c.rectangle(x0, y0, x1 - x0, y1 - y0); fill(c, "#0B1220", a); c.fill()
    lag = mode.get("lag", 0.0)
    ly = py + lag                               # where the loaded bubble is centred (lags behind when fast)
    R = mode.get("R", 2.2)
    lead = mode.get("lead", 0.0)
    for i in range(-5, 6):
        for j in range(int(math.floor(py)) - 6, int(math.floor(py)) + 6):
            sx = CARX + (i - px) * S_ - S_ / 2
            sy = CARY + (j - py) * S_ - S_ / 2
            if sy > y1 or sy + S_ < y0 or sx > x1 or sx + S_ < x0: continue
            dx, dy = i - px, j + 0.5 - (ly - lead)
            d = math.hypot(dx, dy * (0.8 if dy < 0 else 1.0))
            load = cl((R - d) / 0.6 + 0.5) if mode.get("stream", True) else 1.0
            # grid outline for unloaded space
            c.set_line_width(2); fill(c, "#1E293B", a)
            c.rectangle(sx + 2, sy + 2, S_ - 4, S_ - 4); c.stroke()
            if load > 0:
                dist_car = math.hypot(i - px, j + 0.5 - py)
                detail = 1.0 if dist_car < mode.get("lod_r", 99) else 0.0
                cell_city(c, sx, sy, S_, i, j, a * load, detail)
                if mode.get("lod_tint", 0) > 0 and detail == 0:
                    c.rectangle(sx + 4, sy + 4, S_ - 8, S_ - 8); c.set_source_rgba(*hexc(CYAN)[:3], 0.12 * a * mode["lod_tint"]); c.fill()
                if 0.05 < load < 0.95 and mode.get("flash", 0) > 0:
                    c.set_line_width(5); fill(c, GREEN if dy < 0 else RED, a * mode["flash"] * (1 - abs(load - 0.5) * 2))
                    c.rectangle(sx + 6, sy + 6, S_ - 12, S_ - 12); c.stroke()
            elif mode.get("placeholder", 0) > 0 and dy < 0 and d < R + 2.5:
                rr(c, sx + 10, sy + 10, S_ - 20, S_ - 20, 10); fill(c, "#334155", 0.6 * a * mode["placeholder"]); c.fill()
                text(c, "?", sx + S_ / 2, sy + S_ / 2 + 16, 44, MUTED, "black", a=a * mode["placeholder"])
    # loaded-zone ring
    if mode.get("ring", 0) > 0:
        ry_ = CARY + (ly - lead - py) * S_
        c.set_line_width(5); c.set_dash([18, 12]); fill(c, CYAN, a * mode["ring"])
        c.new_path(); c.arc(CARX, ry_, R * S_, 0, 2 * math.pi); c.stroke(); c.set_dash([])
    # LOD rings
    if mode.get("lod_ring", 0) > 0:
        c.set_line_width(4); fill(c, WHITE, 0.6 * a * mode["lod_ring"])
        c.new_path(); c.arc(CARX, CARY, mode["lod_r"] * S_, 0, 2 * math.pi); c.stroke()
    # prefetch cone
    if mode.get("cone", 0) > 0:
        ca = mode["cone"]
        c.move_to(CARX, CARY - 40); c.line_to(CARX - 260, CARY - 420); c.line_to(CARX + 260, CARY - 420); c.close_path()
        g = cairo.LinearGradient(0, CARY, 0, CARY - 420)
        g.add_color_stop_rgba(0, *hexc(GREEN)[:3], 0.0); g.add_color_stop_rgba(1, *hexc(GREEN)[:3], 0.35 * a * ca)
        c.set_source(g); c.fill()
    c.restore()
    # car
    sp = mode.get("speedlines", 0)
    if sp > 0:
        c.set_line_width(5); fill(c, WHITE, 0.5 * a * sp)
        for k in range(6):
            xx = CARX - 60 + k * 24; L = 60 + 60 * h(k, int(t * 10))
            c.move_to(xx, CARY + 60); c.line_to(xx, CARY + 60 + L); c.stroke()
    glow(c, CARX, CARY, 70, YEL, 0.5 * a)
    rr(c, CARX - 26, CARY - 46, 52, 92, 14); fill(c, YEL, a); c.fill()
    rr(c, CARX - 19, CARY - 26, 38, 22, 6); fill(c, "#0B1220", 0.8 * a); c.fill()
    rr(c, CARX - 19, CARY + 14, 38, 16, 6); fill(c, "#0B1220", 0.6 * a); c.fill()
    # frame
    rr(c, x0, y0, x1 - x0, y1 - y0, 22); c.set_line_width(4); fill(c, "#334155", a); c.stroke()


def loading_icon(c, x, y, a, crossed):
    if a <= 0: return
    rr(c, x - 200, y - 34, 400, 68, 18); fill(c, DARK, a); c.fill_preserve(); c.set_line_width(4); fill(c, MUTED, a); c.stroke()
    text(c, "LOADING...", x - 170, y + 12, 30, MUTED, "black", align="left", a=a)
    rr(c, x + 20, y - 12, 160, 24, 12); fill(c, "#334155", a); c.fill()
    rr(c, x + 20, y - 12, 50, 24, 12); fill(c, CYAN, a); c.fill()
    if crossed > 0:
        c.set_line_width(12); c.set_line_cap(cairo.LINE_CAP_ROUND); fill(c, RED, a)
        c.move_to(x - 220, y - 50); c.line_to(lerp(x - 220, x + 220, crossed), lerp(y - 50, y + 50, crossed)); c.stroke()


def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "HOW OPEN WORLDS HAVE", "NO LOADING SCREENS", S("memory"))

    out_a = A * ease(pr(t, 0.05, 0.5)) * (1 - ease(pr(t, S("chunks") - 0.2, 0.5)))
    in_a = A * ease(pr(t, S("chunks") - 0.1, 0.5))

    if out_a > 0:
        zoomed_out_map(c, out_a, t)
        if t < S("memory"):
            la = ease(pr(t, wt("hook", "loading") - 0.4, 0.4))
            loading_icon(c, 540, 1280, out_a * la, ease(pr(t, wt("hook", "screens") - 0.1, 0.4)))
            g = pr(t, wt("hook", "today") - 0.4, 0.4) * (1 - ease(pr(t, wt("hook", "how") - 0.2, 0.3)))
            pill(c, "GTA 6 LAUNCH DAY", 540, 470, 32, DARK, PINK, a=out_a * ease(g), sc=back(g), pad=22, outline=PINK)
        else:
            p = 1.25 * eio(pr(t, wt("memory", "world") - 0.2, 1.4))
            memory_box(c, out_a, p, t)
            wf = pr(t, wt("memory", "fit") - 0.2, 0.4) * (1 - ease(pr(t, wt("memory", "games") - 0.2, 0.3)))
            pill(c, "THE WHOLE MAP WON'T FIT", 540, 470, 30, "#450A0A", RED, a=out_a * ease(wf), sc=back(wf), pad=22, outline=RED)
            nl = pr(t, wt("memory", "load") - 0.2, 0.4)
            pill(c, "SO: NEVER LOAD IT ALL AT ONCE", 540, 470, 30, DARK, CYAN, a=out_a * ease(nl), sc=back(nl), pad=22, outline=CYAN)

    if in_a > 0:
        mode = {"R": 2.2}
        if t < S("stream"):
            sp = ease(pr(t, wt("chunks", "split") - 0.2, 0.6))
            mode.update({"stream": True, "R": lerp(9, 2.2, ease(pr(t, wt("chunks", "only") - 0.2, 0.8))), "ring": ease(pr(t, wt("chunks", "around") - 0.2, 0.4))})
            streaming_view(c, in_a, t, mode)
            ch = pr(t, wt("chunks", "chunks") - 0.2, 0.4) * (1 - ease(pr(t, wt("chunks", "only") - 0.2, 0.3)))
            pill(c, "THE MAP = A GRID OF CHUNKS", 540, 470, 30, DARK, CYAN, a=in_a * ease(ch), sc=back(ch), pad=22, outline=CYAN)
            km = pr(t, wt("chunks", "around") - 0.2, 0.4)
            pill(c, "ONLY NEARBY CHUNKS IN MEMORY", 540, 470, 30, DARK, CYAN, a=in_a * ease(km), sc=back(km), pad=22, outline=CYAN)
        elif t < S("lod"):
            mode.update({"ring": 1.0, "flash": 1.0})
            streaming_view(c, in_a, t, mode)
            ld = pr(t, wt("stream", "loads") - 0.2, 0.4) * (1 - ease(pr(t, wt("stream", "throws") - 0.3, 0.3)))
            pill(c, "AHEAD: STREAM IN FROM STORAGE", 540, 470, 28, "#052E2B", GREEN, a=in_a * ease(ld), sc=back(ld), pad=22, outline=GREEN)
            tw = pr(t, wt("stream", "throws") - 0.2, 0.4)
            pill(c, "BEHIND: THROWN AWAY", 540, 470, 30, "#450A0A", RED, a=in_a * ease(tw), sc=back(tw), pad=22, outline=RED)
        elif t < S("predict"):
            lr = lerp(9, 1.3, ease(pr(t, wt("lod", "simpler") - 0.3, 0.6)))
            mode.update({"R": 3.4, "lod_r": lr, "lod_ring": ease(pr(t, wt("lod", "simpler") - 0.2, 0.5)), "lod_tint": ease(pr(t, wt("lod", "fewer") - 0.2, 0.5))})
            streaming_view(c, in_a, t, mode)
            lp_ = pr(t, wt("lod", "simpler") - 0.2, 0.4)
            pill(c, "LEVEL OF DETAIL (LOD)", 540, 470, 30, DARK, CYAN, a=in_a * ease(lp_), sc=back(lp_), pad=22, outline=CYAN)
            nd = pr(t, wt("lod", "never") - 0.2, 0.4)
            text(c, "NEAR: FULL DETAIL", 540, 1180, 30, YEL, "black", a=in_a * ease(lp_), stroke=6)
            text(c, "FAR: SIMPLE BOXES", 540, 640, 30, CYAN, "black", a=in_a * ease(lp_), stroke=6)
        elif t < S("speed"):
            mode.update({"ring": 0.6, "lead": 0.8 * ease(pr(t, wt("predict", "fetch") - 0.3, 0.5)), "cone": ease(pr(t, wt("predict", "fetch") - 0.2, 0.5)), "flash": 0.6})
            streaming_view(c, in_a, t, mode)
            ss = pr(t, wt("predict", "ssds") - 0.3, 0.4) * (1 - ease(pr(t, wt("predict", "second") - 0.3, 0.3)))
            pill(c, "FAST SSD STORAGE", 540, 470, 30, DARK, WHITE, a=in_a * ease(ss), sc=back(ss), pad=22, outline=MUTED)
            sc_ = pr(t, wt("predict", "second") - 0.2, 0.4)
            pill(c, "FETCHED ~1 SECOND AHEAD", 540, 470, 30, "#052E2B", GREEN, a=in_a * ease(sc_), sc=back(sc_), pad=22, outline=GREEN)
        else:
            fast = ease(pr(t, wt("speed", "move") - 0.3, 1.0))
            px, py = player_world(t)
            t1 = wt("speed", "move") - 0.3
            lag = min(1.7, 3.2 * max(0.0, t - t1) ** 1.4 * 0.55) * fast
            mode.update({"ring": 1.0, "lag": lag, "placeholder": fast, "speedlines": fast})
            streaming_view(c, in_a, t, mode)
            st = pr(t, wt("speed", "speed") - 0.2, 0.4) * (1 - ease(pr(t, wt("speed", "load") - 0.3, 0.3)))
            pill(c, "SPEED = THE STRESS TEST", 540, 470, 30, DARK, AMBER, a=in_a * ease(st), sc=back(st), pad=22, outline=AMBER)
            lf = pr(t, wt("speed", "load") - 0.2, 0.4)
            pill(c, "LOAD FASTER THAN YOU ARRIVE", 540, 470, 30, "#450A0A", RED, a=in_a * ease(lf), sc=back(lf), pad=22, outline=RED)

    for lid, s, col in (("memory", "THE PROBLEM", RED), ("chunks", "THE CHUNKS", CYAN), ("stream", "THE STREAM", GREEN),
                        ("lod", "THE CHEAT", CYAN), ("predict", "THE HEAD START", GREEN), ("speed", "THE LIMIT", AMBER)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "today") - 0.4, "pop"), (wt("hook", "screens") - 0.1, "warn"),
            (wt("memory", "world") - 0.2, "rise"), (wt("memory", "fit") - 0.1, "low"), (wt("memory", "load") - 0.2, "blip"),
            (wt("chunks", "split") - 0.2, "tick"), (wt("chunks", "around") - 0.2, "ping"),
            (wt("stream", "loads") - 0.2, "blip"), (wt("stream", "throws") - 0.2, "blip"),
            (wt("lod", "simpler") - 0.2, "ping"), (wt("predict", "fetch") - 0.2, "rise"), (wt("predict", "second") - 0.2, "ok"),
            (wt("speed", "move") - 0.3, "rumble"), (wt("speed", "load") - 0.2, "warn")]
