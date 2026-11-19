"""Episode 15 (GTA 6 week #5): How game characters know where to go (road graph, navmesh, A*, flocking)."""
import heapq
import random
from hm.core import *
from hm.props import *

DARK = "#0F172A"
PINK = "#F472B6"

# ---------- city (top view) ----------
RX = (250, 540, 830)          # vertical road centres
RY = (720, 990, 1260)         # horizontal road centres
RW = 70                       # road width


def city(c, a):
    if a <= 0: return
    c.rectangle(40, 560, 1000, 780); fill(c, "#334155", a); c.fill()        # sidewalk base
    for x in RX:
        c.rectangle(x - RW / 2, 560, RW, 780); fill(c, "#1E293B", a); c.fill()
    for y in RY:
        c.rectangle(40, y - RW / 2, 1000, RW); fill(c, "#1E293B", a); c.fill()
    # blocks (buildings) inset from sidewalks
    xs = [40] + [x for x in RX] + [1040]
    ys = [560] + [y for y in RY] + [1340]
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            bx0 = xs[i] + (RW / 2 if i > 0 else 0) + 22
            bx1 = xs[i + 1] - (RW / 2 if i < len(xs) - 2 else 0) - 22
            by0 = ys[j] + (RW / 2 if j > 0 else 0) + 22
            by1 = ys[j + 1] - (RW / 2 if j < len(ys) - 2 else 0) - 22
            if bx1 - bx0 < 30 or by1 - by0 < 30: continue
            col = ("#475569", "#5B21B6", "#475569", "#0F766E")[(i * 3 + j) % 4]
            rr(c, bx0, by0, bx1 - bx0, by1 - by0, 10); fill(c, col, a); c.fill()
    c.set_line_width(4); c.set_dash([24, 18]); fill(c, "#64748B", 0.8 * a)
    for x in RX:
        c.move_to(x, 560); c.line_to(x, 1340); c.stroke()
    for y in RY:
        c.move_to(40, y); c.line_to(1040, y); c.stroke()
    c.set_dash([])


def traffic(c, a, t, n=10, question=0.0):
    if a <= 0: return
    for k in range(n):
        horiz = k % 2 == 0
        lane = (RY if horiz else RX)[k % 3]
        d = 1 if k % 4 < 2 else -1
        span = 1000 if horiz else 780
        u = ((t * (90 + 13 * k) * d / span) + k * 0.37) % 1
        if horiz:
            x = 40 + span * u; y = lane + (16 if d > 0 else -16)
            rr(c, x - 26, y - 13, 52, 26, 7)
        else:
            x = lane + (16 if d < 0 else -16); y = 560 + span * u
            rr(c, x - 13, y - 26, 26, 52, 7)
        fill(c, (AMBER, CYAN, PINK, WHITE, GREEN)[k % 5], a); c.fill()
        if question > 0 and k % 3 == 0:
            text(c, "?", x, y - 34, 40, YEL, "black", a=a * question, stroke=6)
    # pedestrians on sidewalks
    for k in range(18):
        lane = RY[k % 3] + (RW / 2 + 10) * (1 if k % 2 else -1)
        u = ((t * (30 + 4 * k) / 1000) * (1 if k % 3 else -1) + k * 0.19) % 1
        x = 40 + 1000 * u
        c.arc(x, lane, 7, 0, 2 * math.pi); fill(c, "#FDE68A", a); c.fill()


def road_graph(c, a, p):
    if a <= 0: return
    nodes = [(x, y) for x in RX for y in RY]
    c.set_line_width(6); fill(c, CYAN, a)
    k = 0
    for x in RX:
        for y0, y1 in zip(RY, RY[1:]):
            q = cl(p * 12 - k * 0.6); k += 1
            if q > 0: c.move_to(x, y0); c.line_to(x, lerp(y0, y1, q)); c.stroke()
    for y in RY:
        for x0, x1 in zip(RX, RX[1:]):
            q = cl(p * 12 - k * 0.6); k += 1
            if q > 0: c.move_to(x0, y); c.line_to(lerp(x0, x1, q), y); c.stroke()
    for i, (x, y) in enumerate(nodes):
        q = cl(p * 6 - i * 0.4)
        if q <= 0: continue
        glow(c, x, y, 30, CYAN, 0.6 * a * q)
        c.arc(x, y, 13 * back(q), 0, 2 * math.pi); fill(c, WHITE, a); c.fill()


def navmesh(c, a, p):
    """Triangles over the sidewalk strips."""
    if a <= 0: return
    k = 0
    c.set_line_width(2)
    for y in RY:
        for side in (-1, 1):
            yy0 = y + side * RW / 2
            yy1 = yy0 + side * 22
            xs = list(range(40, 1041, 70))
            for x0, x1 in zip(xs, xs[1:]):
                q = cl(p * 40 - k * 0.5); k += 1
                if q <= 0: continue
                for tri in (((x0, yy0), (x1, yy0), (x0, yy1)), ((x1, yy0), (x1, yy1), (x0, yy1))):
                    c.move_to(*tri[0]); c.line_to(*tri[1]); c.line_to(*tri[2]); c.close_path()
                    c.set_source_rgba(*hexc(GREEN)[:3], 0.35 * a * q); c.fill_preserve(); fill(c, GREEN, a * q); c.stroke()


# ---------- A* on a grid ----------
GX, GY, GC = 120, 600, 70
COLS, ROWS = 12, 9
WALLS = set()
for r in range(1, 7): WALLS.add((4, r))
for cc in range(6, 10): WALLS.add((cc, 5))
for r in range(2, 5): WALLS.add((8, r))
for r in range(6, 9): WALLS.add((2, r))
START, GOAL = (1, 4), (10, 2)


def astar():
    def h(n): return math.hypot(n[0] - GOAL[0], n[1] - GOAL[1])
    openh = [(h(START), 0.0, START)]
    came, g = {}, {START: 0.0}
    order = []
    seen = set()
    while openh:
        f, gc, n = heapq.heappop(openh)
        if n in seen: continue
        seen.add(n); order.append(n)
        if n == GOAL: break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            m = (n[0] + dx, n[1] + dy)
            if not (0 <= m[0] < COLS and 0 <= m[1] < ROWS) or m in WALLS: continue
            if dx and dy and ((n[0] + dx, n[1]) in WALLS or (n[0], n[1] + dy) in WALLS): continue
            ng = gc + math.hypot(dx, dy)
            if ng < g.get(m, 1e9):
                g[m] = ng; came[m] = n
                heapq.heappush(openh, (ng + h(m), ng, m))
    path = [GOAL]
    while path[-1] != START: path.append(came[path[-1]])
    return order, path[::-1], g


ORDER, PATH, GCOST = astar()


def cell_xy(n): return GX + n[0] * GC + GC / 2, GY + n[1] * GC + GC / 2


def astar_view(c, a, t, explored, path_p, scores=0.0):
    if a <= 0: return
    rr(c, GX - 14, GY - 14, COLS * GC + 28, ROWS * GC + 28, 18); fill(c, "#0B1220", a); c.fill()
    for i in range(COLS):
        for j in range(ROWS):
            x, y = GX + i * GC, GY + j * GC
            if (i, j) in WALLS:
                rr(c, x + 3, y + 3, GC - 6, GC - 6, 8); fill(c, "#475569", a); c.fill()
            else:
                rr(c, x + 3, y + 3, GC - 6, GC - 6, 8); fill(c, "#1E293B", a); c.fill()
    n_exp = int(len(ORDER) * explored)
    for k, n in enumerate(ORDER[:n_exp]):
        x, y = cell_xy(n)
        fresh = 1 - cl((n_exp - k) / 6)
        rr(c, x - GC / 2 + 3, y - GC / 2 + 3, GC - 6, GC - 6, 8)
        fill(c, lerp_col("#164E63", YEL, fresh), a); c.fill()
    if path_p > 0:
        c.set_line_width(12); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND); fill(c, GREEN, a)
        m = max(2, int(len(PATH) * path_p))
        c.move_to(*cell_xy(PATH[0])); [c.line_to(*cell_xy(n)) for n in PATH[1:m]]; c.stroke()
    if scores > 0:
        # one highlighted frontier cell with its g + h
        n = ORDER[min(len(ORDER) - 1, max(0, int(len(ORDER) * explored) - 1))]
        x, y = cell_xy(n)
        gx, gy = cell_xy(START); bx, by = cell_xy(GOAL)
        c.set_line_width(6); fill(c, AMBER, a * scores)
        c.move_to(gx, gy); c.line_to(x, y); c.stroke()
        c.set_dash([14, 10]); fill(c, PINK, a * scores); c.move_to(x, y); c.line_to(bx, by); c.stroke(); c.set_dash([])
    for n, lab, col in ((START, "A", AMBER), (GOAL, "B", PINK)):
        x, y = cell_xy(n)
        glow(c, x, y, 50, col, 0.6 * a)
        c.arc(x, y, 26, 0, 2 * math.pi); fill(c, col, a); c.fill()
        text(c, lab, x, y + 12, 32, DARK, "black", a=a)


# ---------- frame budget ----------
def frames_view(c, a, t, p):
    if a <= 0: return
    n = 8
    w = 105
    x0 = 540 - n * w / 2
    for i in range(n):
        x = x0 + i * w
        rr(c, x + 6, 760, w - 12, 300, 14); fill(c, "#1E293B", a); c.fill()
        text(c, f"F{i + 1}", x + w / 2, 740, 24, MUTED, "black", a=a)
        # rendering work (always there)
        rr(c, x + 16, 900, w - 32, 140, 8); fill(c, "#334155", a); c.fill()
        text(c, "DRAW", x + w / 2, 980, 18, MUTED, "black", a=a)
        # a slice of pathfinding work, one agent per frame
        q = cl(p * n - i)
        if q > 0:
            rr(c, x + 16, 780, w - 32, 100 * ease(q), 8); fill(c, YEL, a); c.fill()
            text(c, "PATH", x + w / 2, 840, 18, DARK, "black", a=a * ease(q))
    c.set_line_width(5); fill(c, YEL, a * p)
    c.move_to(x0 + 10, 1110); c.line_to(x0 + n * w - 10, 1110); c.stroke()


# ---------- boids ----------
_SIM = {}


def boids_sim():
    if "f" in _SIM: return _SIM["f"]
    random.seed(7)
    N = 34
    t0, t1 = S("flock") - 0.6, E("alive") + 1.2
    on_sep, on_ali, on_coh = wt("flock", "keep") - 0.2, wt("flock", "match") - 0.2, wt("flock", "stay") - 0.2
    pos = [[random.uniform(180, 900), random.uniform(640, 1240)] for _ in range(N)]
    vel = [[random.uniform(-1, 1) * 3, random.uniform(-1, 1) * 3] for _ in range(N)]
    frames = []
    steps = int((t1 - t0) * 30) + 2
    for s in range(steps):
        tt = t0 + s / 30
        sep, ali, coh = tt > on_sep, tt > on_ali, tt > on_coh
        newv = []
        for i in range(N):
            px, py = pos[i]; vx, vy = vel[i]
            ax = ay = 0.0
            cnt = 0; cx = cy = avx = avy = 0.0
            for j in range(N):
                if i == j: continue
                dx, dy = pos[j][0] - px, pos[j][1] - py
                d = math.hypot(dx, dy)
                if d < 170:
                    cnt += 1; cx += pos[j][0]; cy += pos[j][1]; avx += vel[j][0]; avy += vel[j][1]
                if sep and 0 < d < 55:
                    ax -= dx / d * (55 - d) * 0.06; ay -= dy / d * (55 - d) * 0.06
            if cnt:
                if ali: ax += (avx / cnt - vx) * 0.06; ay += (avy / cnt - vy) * 0.06
                if coh: ax += (cx / cnt - px) * 0.0025; ay += (cy / cnt - py) * 0.0025
            if not ali:
                ax += random.uniform(-0.6, 0.6); ay += random.uniform(-0.6, 0.6)
            # stay in the stage
            if px < 160: ax += 0.4
            if px > 920: ax -= 0.4
            if py < 620: ay += 0.4
            if py > 1260: ay -= 0.4
            vx += ax; vy += ay
            sp = math.hypot(vx, vy); mx = 4.2
            if sp > mx: vx, vy = vx / sp * mx, vy / sp * mx
            if sp < 1.5 and sp > 0: vx, vy = vx / sp * 1.5, vy / sp * 1.5
            newv.append([vx, vy])
        vel = newv
        pos = [[pos[i][0] + vel[i][0], pos[i][1] + vel[i][1]] for i in range(N)]
        frames.append(([p[:] for p in pos], [v[:] for v in vel]))
    _SIM["f"] = (t0, frames)
    return _SIM["f"]


def boids_view(c, a, t, ring=0.0, alive=0.0):
    if a <= 0: return
    t0, frames = boids_sim()
    k = max(0, min(len(frames) - 1, int((t - t0) * 30)))
    pos, vel = frames[k]
    rr(c, 120, 600, 840, 700, 22); fill(c, "#0B1220", a); c.fill()
    if alive > 0:
        glow(c, 540, 950, 380, GREEN, 0.18 * a * alive)
    for i, ((x, y), (vx, vy)) in enumerate(zip(pos, vel)):
        ang = math.atan2(vy, vx)
        if ring > 0 and i == 0:
            c.set_line_width(3); c.set_dash([10, 8]); fill(c, CYAN, a * ring)
            c.new_path(); c.arc(x, y, 55, 0, 2 * math.pi); c.stroke(); c.set_dash([])
        c.save(); c.translate(x, y); c.rotate(ang)
        col = YEL if i == 0 else lerp_col("#FDE68A", "#86EFAC", alive)
        c.move_to(18, 0); c.line_to(-12, -10); c.line_to(-6, 0); c.line_to(-12, 10); c.close_path(); fill(c, col, a); c.fill()
        c.restore()


def draw(c, t):
    A = 1 - cta_amount(t)
    hook_title(c, t, "HOW GAME CHARACTERS", "KNOW WHERE TO GO", S("map"))

    city_a = A * ease(pr(t, 0.05, 0.5)) * (1 - ease(pr(t, S("astar") - 0.2, 0.4)))
    grid_a = A * ease(pr(t, S("astar") - 0.1, 0.5)) * (1 - ease(pr(t, S("cheap") - 0.2, 0.4)))
    fr_a = A * ease(pr(t, S("cheap") - 0.1, 0.5)) * (1 - ease(pr(t, S("flock") - 0.2, 0.4)))
    boid_a = A * ease(pr(t, S("flock") - 0.1, 0.5))

    if city_a > 0:
        city(c, city_a)
        dim = ease(pr(t, wt("map", "hidden") - 0.2, 0.5))
        traffic(c, city_a * (1 - 0.6 * dim), t, question=ease(pr(t, wt("hook", "where") - 0.3, 0.3)) * (1 - dim))
        rg = eio(pr(t, wt("map", "roads") - 0.2, 1.6))
        road_graph(c, city_a, rg)
        nm = eio(pr(t, wt("map", "walkable") - 0.2, 2.0))
        navmesh(c, city_a, nm)
        hm = pr(t, wt("map", "hidden") - 0.2, 0.4) * (1 - ease(pr(t, wt("map", "roads") - 0.2, 0.3)))
        pill(c, "A HIDDEN MAP", 540, 470, 32, DARK, WHITE, a=city_a * ease(hm), sc=back(hm), pad=22, outline=MUTED)
        rp = pr(t, wt("map", "network") - 0.2, 0.4) * (1 - ease(pr(t, wt("map", "walkable") - 0.2, 0.3)))
        pill(c, "ROADS = POINTS + LINES", 540, 470, 30, DARK, CYAN, a=city_a * ease(rp), sc=back(rp), pad=22, outline=CYAN)
        np_ = pr(t, wt("map", "navmesh") - 0.3, 0.4)
        pill(c, "SIDEWALKS = NAVMESH", 540, 470, 30, "#052E2B", GREEN, a=city_a * ease(np_), sc=back(np_), pad=22, outline=GREEN)

    if grid_a > 0:
        if t < S("score"):
            ex = eio(pr(t, wt("astar", "searches") - 0.5, 1.4))
            pp = eio(pr(t, wt("astar", "best") - 0.2, 0.6))
            astar_view(c, grid_a, t, ex, pp)
            ap = pr(t, wt("astar", "star") - 0.3, 0.4)
            pill(c, "A* PATHFINDING", 540, 470, 32, DARK, YEL, a=grid_a * ease(ap), sc=back(ap), pad=22, outline=YEL)
        else:
            ex = 0.15 + 0.85 * eio(pr(t, wt("score", "explores") - 0.4, 1.8))
            sc_ = ease(pr(t, wt("score", "distance") - 0.3, 0.4)) * (1 - ease(pr(t, wt("score", "explores") - 0.3, 0.3)))
            pp = eio(pr(t, wt("score", "first") - 0.1, 0.6))
            astar_view(c, grid_a, t, ex if t > wt("score", "explores") - 0.4 else 0.15, pp, scores=sc_)
            g = pr(t, wt("score", "distance") - 0.2, 0.4)
            h_ = pr(t, wt("score", "guess") - 0.2, 0.4)
            c.save()
            text(c, "DISTANCE SO FAR", 330, 1330, 28, AMBER, "black", a=grid_a * ease(g) * (1 - ease(pr(t, wt("score", "explores") - 0.3, 0.3))), stroke=6)
            text(c, "+  GUESS LEFT", 760, 1330, 28, PINK, "black", a=grid_a * ease(h_) * (1 - ease(pr(t, wt("score", "explores") - 0.3, 0.3))), stroke=6)
            c.restore()
            sf = pr(t, wt("score", "scores") - 0.2, 0.4) * (1 - ease(pr(t, wt("score", "explores") - 0.3, 0.3)))
            pill(c, "SCORE = SO FAR + GUESS LEFT", 540, 470, 30, DARK, YEL, a=grid_a * ease(sf), sc=back(sf), pad=22, outline=YEL)
            mp = pr(t, wt("score", "promising") - 0.3, 0.4)
            pill(c, "BEST-LOOKING PATHS FIRST", 540, 470, 30, "#052E2B", GREEN, a=grid_a * ease(mp), sc=back(mp), pad=22, outline=GREEN)

    if fr_a > 0:
        p = eio(pr(t, wt("cheap", "spread") - 0.3, 1.6))
        frames_view(c, fr_a, t, p)
        ef = pr(t, wt("cheap", "every") - 0.3, 0.4) * (1 - ease(pr(t, wt("cheap", "spread") - 0.3, 0.3)))
        pill(c, "NOT EVERY FRAME", 540, 470, 32, "#450A0A", RED, a=fr_a * ease(ef), sc=back(ef), pad=22, outline=RED)
        sw = pr(t, wt("cheap", "spread") - 0.2, 0.4)
        pill(c, "WORK SPREAD ACROSS FRAMES", 540, 470, 30, DARK, YEL, a=fr_a * ease(sw), sc=back(sw), pad=22, outline=YEL)

    if boid_a > 0:
        alive = ease(pr(t, wt("alive", "alive") - 0.6, 0.6))
        boids_view(c, boid_a, t, ring=ease(pr(t, wt("flock", "keep") - 0.2, 0.4)) * (1 - ease(pr(t, S("alive"), 0.4))), alive=alive)
        rules = [("1 · KEEP YOUR DISTANCE", "keep", CYAN), ("2 · MATCH DIRECTION", "match", AMBER), ("3 · STAY WITH THE GROUP", "stay", GREEN)]
        cur = max([i for i, (_, ww, _) in enumerate(rules) if t >= wt("flock", ww) - 0.2] or [-1])
        if cur >= 0:
            lab, w, col = rules[cur]
            q = pr(t, wt("flock", w) - 0.2, 0.4)
            fade = 1 - ease(pr(t, wt("alive", "alive") - 0.6, 0.4))
            pill(c, lab, 540, 1345, 26, DARK, col, a=boid_a * ease(q) * fade, sc=back(q), pad=18, outline=col)
        sr = pr(t, wt("flock", "simple") - 0.2, 0.4) * (1 - ease(pr(t, wt("alive", "alive") - 0.6, 0.3)))
        pill(c, "FLOCKING: 3 SIMPLE RULES", 540, 470, 30, DARK, WHITE, a=boid_a * ease(sr), sc=back(sr), pad=22, outline=MUTED)
        al = pr(t, wt("alive", "alive") - 0.4, 0.4)
        pill(c, "A CROWD THAT LOOKS ALIVE", 540, 470, 30, "#052E2B", GREEN, a=boid_a * ease(al), sc=back(al), pad=22, outline=GREEN)

    for lid, s, col in (("map", "THE HIDDEN MAP", CYAN), ("astar", "THE SEARCH", YEL), ("score", "THE TRICK", YEL),
                        ("cheap", "THE BUDGET", AMBER), ("flock", "THE CROWD", GREEN), ("alive", "THE RESULT", GREEN)):
        scene_label(c, t, lid, s, col)


def SFX():
    return [(wt("hook", "where") - 0.3, "blip"), (wt("map", "hidden") - 0.2, "low"), (wt("map", "roads") - 0.2, "rise"),
            (wt("map", "navmesh") - 0.3, "ping"), (wt("astar", "star") - 0.3, "pop"), (wt("astar", "searches") - 0.5, "rise"),
            (wt("astar", "best") - 0.2, "success"), (wt("score", "distance") - 0.3, "tick"), (wt("score", "guess") - 0.2, "tick"),
            (wt("score", "explores") - 0.4, "rise"), (wt("cheap", "spread") - 0.3, "blip"),
            (wt("flock", "keep") - 0.2, "ping"), (wt("flock", "match") - 0.2, "ping"), (wt("flock", "stay") - 0.2, "ping"),
            (wt("alive", "alive") - 0.6, "resolve")]
