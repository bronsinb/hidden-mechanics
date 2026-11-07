"""Sound: ambient music bed + whooshes between lines + episode sound cues, mixed under the voice."""
import numpy as np, soundfile as sf
from . import core

SR = 48000
_rng = np.random.default_rng(7)


def _env(n, a=0.005, r=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / r)


def tone(f0, f1, dur, r=0.08, kind="sine"):
    n = int(dur * SR)
    f = np.linspace(f0, f1, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    w = np.sin(ph) if kind == "sine" else (2 / np.pi) * np.arcsin(np.sin(ph))
    return w * _env(n, 0.004, r)


def whoosh(dur=0.45):
    n = int(dur * SR)
    x = _rng.standard_normal(n)
    k = np.linspace(40, 6, n).astype(int)
    c = np.cumsum(np.concatenate([[0], x]))
    idx = np.arange(n)
    y = (c[idx + 1] - c[np.maximum(0, idx + 1 - k)]) / k
    return y * np.sin(np.linspace(0, np.pi, n)) ** 2


def chime(notes, step=0.07, r=0.35):
    out = np.zeros(int((step * len(notes) + 1.2) * SR))
    for i, f in enumerate(notes):
        s = tone(f, f, 1.2, r) + 0.3 * tone(f * 2, f * 2, 1.2, r * 0.6)
        j = int(i * step * SR)
        out[j:j + len(s)] += s
    return out


# Named sound cues an episode can place: (time_seconds, name)
CUES = {
    "pop":     lambda: (tone(900, 1500, 0.12, 0.05), 0.16),           # something appears
    "blip":    lambda: (tone(1200, 1200, 0.08, 0.03, "tri"), 0.10),   # data / small item
    "ping":    lambda: (tone(400, 260, 0.6, 0.25), 0.07),             # signal goes out
    "wake":    lambda: (np.concatenate([tone(700, 1400, 0.15, 0.06), tone(1400, 1800, 0.15, 0.06)]), 0.13),
    "ok":      lambda: (chime([784, 1175]), 0.10),                    # check / correct
    "success": lambda: (chime([523, 659, 784, 1047]), 0.13),          # payoff moment
    "rumble":  lambda: (tone(80, 120, 0.9, 0.35, "tri"), 0.25),       # engine / machine starts
    "warn":    lambda: (np.concatenate([tone(330, 330, 0.18, 0.08, "tri"), tone(247, 247, 0.3, 0.12, "tri")]), 0.16),
    "low":     lambda: (tone(300, 200, 0.3, 0.1, "tri"), 0.12),       # suspicious / villain
    "tick":    lambda: (tone(2000, 2000, 0.03, 0.01), 0.05),          # timer tick
    "rise":    lambda: (tone(200, 800, 0.5, 0.3), 0.06),              # build-up / reveal
    "resolve": lambda: (chime([392, 523, 659]), 0.11),
    "outro":   lambda: (chime([659, 784, 988, 1319], 0.06), 0.11),
}


def make(ep, cues=()):
    total = core.TOTAL
    N = int((total + 0.2) * SR)
    t = np.arange(N) / SR
    sfx = np.zeros(N)

    def add(t0, sig, g):
        i = int(t0 * SR)
        if i < 0 or i >= N: return
        sig = sig[: N - i]
        sfx[i:i + len(sig)] += sig * g

    # music bed: slow minor pad + soft pulse
    chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (196.0, 246.94, 293.66), (164.81, 207.65, 246.94)]
    pad = np.zeros(N)
    seg = 4.0
    for i in range(int(total / seg) + 2):
        ch = chords[i % 4]
        a, b = int(i * seg * SR), min(N, int(((i + 1) * seg + 1.0) * SR))
        if a >= N: break
        tt = t[a:b] - t[a]
        w = sum(np.sin(2 * np.pi * (f / 2 + d) * tt) + 0.25 * np.sin(2 * np.pi * (f + d) * tt) for f in ch for d in (-0.6, 0.6))
        pad[a:b] += w * np.minimum(1, tt / 1.2) * np.clip((seg + 1.0 - tt) / 1.2, 0, 1)
    pad *= (0.8 + 0.2 * np.sin(2 * np.pi * 0.11 * t))
    pad /= np.abs(pad).max()
    beat = np.zeros(N)
    for k, bt in enumerate(np.arange(0.3, total - 1.5, 0.5)):
        s = tone(55, 45, 0.25, 0.09)
        i = int(bt * SR)
        beat[i:i + len(s)] += s[: N - i] * (1.0 if k % 2 == 0 else 0.6)
    music = (pad * 0.10 + beat * 0.07) * np.minimum(1, t / 0.8) * np.clip((total + 0.2 - t) / 1.5, 0, 1)

    for lid in core.IDS[1:]:
        add(core.S(lid) - 0.15, whoosh(), 0.10)
    if "cta" in core.L:
        add(core.S("cta"), *CUES["outro"]())
    for t0, name in cues:
        sig, g = CUES[name]()
        add(t0, sig, g)

    voice, vsr = sf.read(f"{ep}/voice.wav")
    v = np.interp(np.arange(N) / SR, np.arange(len(voice)) / vsr, voice, right=0)
    out = v * 0.95 + music + sfx
    out = out / max(1.0, np.abs(out).max() / 0.95)
    sf.write(f"{ep}/mix.wav", np.stack([out, out], 1).astype(np.float32), SR)
