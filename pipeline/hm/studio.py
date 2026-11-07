"""Hidden Mechanics: one command per step.

  python3 -m hm.studio voice  EP_DIR            # script.json -> voice.wav, timeline.json
  python3 -m hm.studio stills EP_DIR t1 t2 ...  # check frames -> EP_DIR/frames/f_<t>.png + sheet.jpg
  python3 -m hm.studio video  EP_DIR            # full render + sound -> EP_DIR/final.mp4 and upload.mp4 (<10 MB)
  python3 -m hm.studio fit    EP_DIR            # just remake upload.mp4 from final.mp4
  python3 -m hm.studio thumb  EP_DIR t          # one frame as thumbnail.jpg (1080x1920)

EP_DIR holds script.json and scenes.py. scenes.py defines draw(c, t) and may define
SFX(): a list of (seconds, cue_name) using names from hm.mix.CUES.
"""
import sys, os, math, subprocess, importlib.util, json
import cairo
from . import core

PROCS = 2


def load_scenes(ep):
    core.load_timeline(f"{ep}/timeline.json")
    spec = importlib.util.spec_from_file_location("episode_scenes", f"{ep}/scenes.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _surface():
    return cairo.ImageSurface(cairo.FORMAT_ARGB32, core.W, core.H)


def stills(ep, times):
    mod = load_scenes(ep)
    os.makedirs(f"{ep}/frames", exist_ok=True)
    paths = []
    for t in times:
        s = _surface()
        core.frame(cairo.Context(s), float(t), mod.draw)
        p = f"{ep}/frames/f_{float(t):05.2f}.png"
        s.write_to_png(p)
        paths.append(p)
    try:
        from PIL import Image
        for n in range(0, len(paths), 4):
            sheet = Image.new("RGB", (2160, 960))
            for j, p in enumerate(paths[n:n + 4]):
                sheet.paste(Image.open(p).convert("RGB").resize((540, 960)), (j * 540, 0))
            sheet.save(f"{ep}/frames/sheet{n // 4}.jpg", quality=88)
    except ImportError:
        pass
    print("\n".join(paths))


def render_part(ep, f0, f1, out):
    mod = load_scenes(ep)
    s = _surface()
    tmp = out[:-4] + ".part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
                           "-s", f"{core.W}x{core.H}", "-r", str(core.FPS), "-i", "-", "-c:v", "libx264",
                           "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        core.frame(cairo.Context(s), f / core.FPS, mod.draw)
        s.flush()
        ff.stdin.write(bytes(s.get_data()))
    ff.stdin.close()
    if ff.wait() != 0: sys.exit("ffmpeg failed")
    os.replace(tmp, out)


def video(ep):
    mod = load_scenes(ep)
    frames = math.ceil(core.TOTAL * core.FPS)
    os.makedirs(f"{ep}/parts", exist_ok=True)
    cuts = [round(frames * i / PROCS) for i in range(PROCS + 1)]
    procs = [subprocess.Popen([sys.executable, "-m", "hm.studio", "_part", ep, str(cuts[i]), str(cuts[i + 1]),
                               f"{ep}/parts/p{i}.mp4"], cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
             for i in range(PROCS)]
    if any(p.wait() != 0 for p in procs): sys.exit("render failed")
    with open(f"{ep}/parts/list.txt", "w") as fh:
        for i in range(PROCS): fh.write(f"file 'p{i}.mp4'\n")
    from . import mix
    mix.make(ep, mod.SFX() if hasattr(mod, "SFX") else [])
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{ep}/parts/list.txt",
                    "-i", f"{ep}/mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", f"{ep}/final.mp4"], check=True)
    fit_for_upload(ep)
    print(f"{ep}/final.mp4 + {ep}/upload.mp4", round(core.TOTAL, 2), "s")


def fit_for_upload(ep, limit=9_500_000):
    """Chrome's file attach takes at most 10 MB: write upload.mp4 under the limit (flat animation compresses well)."""
    for crf in (22, 24, 26, 28, 30):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{ep}/final.mp4", "-c:v", "libx264", "-preset", "medium",
                        "-crf", str(crf), "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart",
                        f"{ep}/upload.mp4"], check=True)
        if os.path.getsize(f"{ep}/upload.mp4") <= limit:
            print(f"upload.mp4 crf {crf}: {os.path.getsize(f'{ep}/upload.mp4') / 1e6:.1f} MB")
            return
    sys.exit("could not get upload.mp4 under the size limit")


def thumb(ep, t):
    mod = load_scenes(ep)
    s = _surface()
    core.frame(cairo.Context(s), float(t), mod.draw)
    s.write_to_png(f"{ep}/thumbnail.png")
    from PIL import Image
    Image.open(f"{ep}/thumbnail.png").convert("RGB").save(f"{ep}/thumbnail.jpg", quality=90)


if __name__ == "__main__":
    cmd, ep = sys.argv[1], sys.argv[2].rstrip("/")
    if cmd == "voice":
        from . import voice
        voice.make(ep)
    elif cmd == "stills": stills(ep, sys.argv[3:])
    elif cmd == "video": video(ep)
    elif cmd == "thumb": thumb(ep, sys.argv[3])
    elif cmd == "fit": fit_for_upload(ep)
    elif cmd == "_part": render_part(ep, int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else: sys.exit(__doc__)
