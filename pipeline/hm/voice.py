"""Narration: script.json -> voice.wav + timeline.json (per-line and per-word timings)."""
import json, os, re
import numpy as np, soundfile as sf

TTS = os.environ.get("HM_TTS", "/home/claude/tts")
LEAD, GAP, TAIL = 0.30, 0.30, 0.9
PUNCT = set(".,!?;:—…\"“”'()")


def is_sound(p):
    return p.strip() != "" and p not in PUNCT


def make(ep):
    from kokoro_onnx import Kokoro
    cfg = json.load(open(f"{ep}/script.json"))
    k = Kokoro(f"{TTS}/kokoro-v11.onnx", f"{TTS}/voices-v1.0.bin")

    def word_times(text, timings, t0):
        words = text.split()
        cnt = []
        for w in words:
            ph = k.tokenizer.phonemize(re.sub(r"[^\w']", " ", w).strip() or w, "en-us")
            cnt.append(max(1, sum(1 for c in ph if is_sound(c))))
        sounds = [t for t in timings if is_sound(t.phoneme)]
        n, tot = len(sounds), sum(cnt)
        out, c = [], 0
        for w, m in zip(words, cnt):
            a = min(int(round(c / tot * n)), n - 1)
            b = max(a, min(int(round((c + m) / tot * n)) - 1, n - 1))
            out.append({"w": w, "s": round(t0 + sounds[a].start, 3), "e": round(t0 + sounds[b].end, 3)})
            c += m
        return out

    sr = 24000
    chunks = [np.zeros(int(LEAD * sr), dtype=np.float32)]
    t, timeline = LEAD, []
    for ln in cfg["lines"]:
        a, sr, tim = k.create_timed(ln["text"], voice=cfg.get("voice", "am_michael"),
                                    speed=cfg.get("speed", 1.08), lang="en-us")
        a = a.astype(np.float32)
        snd = [x for x in tim if is_sound(x.phoneme)]
        s0 = max(0.0, snd[0].start - 0.05)
        s1 = min(len(a) / sr, snd[-1].end + 0.12)
        a = a[int(s0 * sr):int(s1 * sr)]
        d = len(a) / sr
        timeline.append({"id": ln["id"], "text": ln["text"], "s": round(t, 3), "e": round(t + d, 3),
                         "words": word_times(ln["text"], tim, t - s0)})
        chunks += [a, np.zeros(int(GAP * sr), dtype=np.float32)]
        t += d + GAP
        print(f'  {ln["id"]:12s} {d:5.2f}s')
    chunks.append(np.zeros(int(TAIL * sr), dtype=np.float32))
    audio = np.concatenate(chunks)
    audio = audio / max(1e-6, np.abs(audio).max()) * 0.89
    sf.write(f"{ep}/voice.wav", audio, sr)
    total = len(audio) / sr
    json.dump({"total": round(total, 3), "lines": timeline}, open(f"{ep}/timeline.json", "w"), indent=1)
    print(f"  total {total:.2f}s")
    return total
