"""Dolce Vista reel builder for Betty's Italy footage (1080x1920, 30 fps)."""
import json, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SR, XF = 1080, 1920, 30, 44100, 0.5
ROOT = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(ROOT, *a)
for d in ("seg", "layers", "stills", "out", "audio"):
    os.makedirs(P(d), exist_ok=True)

# Dolce Vista palette
CREAM = (247, 239, 227); TRAV = (217, 195, 165); GOLD = (233, 168, 76); TERRA = (138, 74, 43)
TEAL = (31, 111, 120); TWI = (35, 51, 92); LANTERN = (244, 194, 107); ESP = (59, 42, 34)
BASIL = (46, 125, 79); ROSSO = (200, 55, 45)
CLAY = (200, 121, 74); LAGOON = (127, 183, 178); MAT = (255, 251, 244)
GROUNDS = {"teal": TEAL, "terracotta": TERRA, "golden": GOLD, "clay": CLAY, "travertine": TRAV, "lagoon": LAGOON, "twilight": TWI, "cream": CREAM}
CARDS = {"twilight": (TWI, LANTERN), "teal": (TEAL, LANTERN), "terracotta": (TERRA, GOLD), "espresso": (ESP, GOLD)}
ENDS = {
    "cream": dict(bg=CREAM, ring=CLAY, quote=TEAL, kicker=TERRA, sub=(110, 90, 76)),
    "twilight": dict(bg=TWI, ring=LANTERN, quote=CREAM, kicker=LANTERN, sub=(214, 204, 188)),
    "terracotta": dict(bg=TERRA, ring=GOLD, quote=CREAM, kicker=CREAM, sub=(240, 222, 200)),
    "teal": dict(bg=TEAL, ring=LANTERN, quote=CREAM, kicker=CREAM, sub=(220, 236, 232)),
}

def font(kind, size, wght):
    path = {"serif_i": "fonts/CormorantGaramond-Italic[wght].ttf",
            "serif": "fonts/CormorantGaramond[wght].ttf",
            "sans": "fonts/Jost[wght].ttf"}[kind]
    f = ImageFont.truetype(P(path), size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f

GRADES = {
    "travertino": "eq=contrast=0.95:saturation=0.9:brightness=0.012,colorbalance=rs=0.03:gs=0.01:bs=-0.03:rm=0.035:gm=0.01:bm=-0.035,curves=all='0/0.05 0.5/0.52 1/0.98',noise=alls=4:allf=t",
    "canale": "eq=contrast=1.05:saturation=1.1,colorbalance=rs=-0.03:gs=0.0:bs=0.035:rm=0.02:bm=-0.01,curves=all='0/0.02 1/1'",
    "oro": "eq=saturation=1.06:contrast=1.03,colorbalance=rs=0.06:gs=0.02:bs=-0.06:rm=0.05:bm=-0.05:rh=0.03:bh=-0.04",
    "memoria": "eq=saturation=0.72:contrast=1.03:brightness=-0.01,colorbalance=rs=0.03:bs=-0.03:rm=0.02:bm=-0.02,curves=all='0/0.04 1/0.97',vignette=angle=PI/4.5",
}

def run(cmd):
    r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:]); raise SystemExit(1)

# ---------- stills (graded) ----------
def graded_still(src, look, at=None):
    """src: photo name like '2' or 'rome@7.5' (frame from master)."""
    key = f"{src.replace('@','_')}_{look}.png"
    out = P("stills", key)
    if not os.path.exists(out):
        if "@" in src:
            clip, t = src.split("@")
            run(["ffmpeg", "-v", "error", "-y", "-ss", t, "-i", P("masters", f"{clip}_rt.mp4"), "-frames:v", "1",
                 "-vf", GRADES[look].replace(",noise=alls=4:allf=t", ""), out])
        else:
            run(["ffmpeg", "-v", "error", "-y", "-i", P("src", f"{src}.jpg"), "-vf",
                 GRADES[look].replace(",noise=alls=4:allf=t", ""), out])
    return Image.open(out).convert("RGB")

def ease(u):
    return u * u * (3 - 2 * u)

def frames_to_mp4(frames_iter, n, out):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "fast",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for fr in frames_iter:
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()

def photo_seg(out, src, look, dur, z0=1.0, z1=1.08, c0=(0.5, 0.5), c1=(0.5, 0.5)):
    img = graded_still(src, look)
    iw, ih = img.size
    base = max(W / iw, H / ih)  # output px per source px at zoom 1 (cover)
    n = int(round(dur * FPS))
    def gen():
        for i in range(n):
            u = ease(i / max(1, n - 1))
            z = z0 + (z1 - z0) * u
            s = 1 / (base * z)  # source px per output px
            vw, vh = W * s, H * s
            cx = c0[0] + (c1[0] - c0[0]) * u; cy = c0[1] + (c1[1] - c0[1]) * u
            x0 = min(max(cx * iw - vw / 2, 0), iw - vw); y0 = min(max(cy * ih - vh / 2, 0), ih - vh)
            yield img.transform((W, H), Image.AFFINE, (s, 0, x0, 0, s, y0), Image.BICUBIC)
    frames_to_mp4(gen(), n, out)

def arch_mask(w, h):
    m = Image.new("L", (w * 2, h * 2), 0)
    d = ImageDraw.Draw(m)
    r = w
    d.ellipse([0, 0, w * 2, w * 2], fill=255)
    d.rounded_rectangle([0, w, w * 2, h * 2], radius=8, fill=255)
    return m.resize((w, h), Image.LANCZOS)

def wrap_fit(text, kind, size, wght, maxw, minsize=40):
    while True:
        f = font(kind, size, wght)
        lines = text.split("\n")
        if all(f.getlength(l) <= maxw for l in lines) or size <= minsize:
            return f, lines, size
        size -= 2

def draw_centered(d, lines, f, cy, fill, lh=1.12, shadow=None):
    size = f.size
    total = lh * size * len(lines)
    y = cy - total / 2
    for l in lines:
        w = f.getlength(l)
        x = (W - w) / 2
        if shadow:
            d.text((x, y), l, font=f, fill=shadow)
        d.text((x, y), l, font=f, fill=fill)
        y += lh * size
    return cy - total / 2, cy + total / 2

def endcard_seg(out, src, look, dur, quote, kicker="BETTY WHITEMAN", sub=None, theme="cream"):
    T = ENDS[theme]
    img = graded_still(src, look)
    aw, ah = 620, 820
    mask = arch_mask(aw, ah)
    bg = Image.new("RGB", (W, H), T["bg"])
    d = ImageDraw.Draw(bg)
    ax, ay = (W - aw) // 2, 250
    # fine rule frame around arch
    fr = arch_mask(aw + 28, ah + 28)
    ring = Image.new("RGB", fr.size, T["ring"])
    inner = arch_mask(aw + 24, ah + 24)
    ringmask = Image.fromarray(np.clip(np.array(fr, dtype=int) - np.pad(np.array(inner, dtype=int), 2), 0, 255).astype("uint8"))
    bg.paste(ring, (ax - 14, ay - 14), ringmask)
    # tricolore mini rule
    ry = ay + ah + 60
    for i, col in enumerate((BASIL, CREAM, ROSSO)):
        d.rectangle([W / 2 - 54 + i * 36, ry, W / 2 - 54 + (i + 1) * 36, ry + 4], fill=col)
    if T["bg"] == CREAM:
        d.rectangle([W / 2 - 18, ry, W / 2 + 18, ry + 4], outline=(205, 183, 151))
    fq, lines, _ = wrap_fit(quote, "serif_i", 74, 500, 900)
    top, bot = draw_centered(d, lines, fq, ry + 60 + 0.56 * 74 * len(lines) * 1.12, T["quote"], lh=1.14)
    fk = font("sans", 28, 500)
    k = kicker
    # tracked caps
    def tracked(text, y, f, fill, tr=0.3):
        sp = f.size * tr
        widths = [f.getlength(c) for c in text]
        tot = sum(widths) + sp * (len(text) - 1)
        x = (W - tot) / 2
        for c, w in zip(text, widths):
            d.text((x, y), c, font=f, fill=fill); x += w + sp
    if sub:
        sl = sub.split("\n")
        for li, line in enumerate(sl):
            tracked(line, bot + 44 + li * 40, font("sans", 24, 400), T["sub"], 0.22)
        tracked(k, bot + 60 + len(sl) * 40 + 16, fk, T["kicker"])
    else:
        tracked(k, bot + 56, fk, T["kicker"])
    iw, ih = img.size
    n = int(round(dur * FPS))
    base = max(aw / iw, ah / ih)
    def gen():
        for i in range(n):
            u = ease(i / max(1, n - 1)); z = 1.0 + 0.07 * u
            s = 1 / (base * z); vw, vh = aw * s, ah * s
            x0 = (iw - vw) / 2; y0 = (ih - vh) / 2
            ph = img.transform((aw, ah), Image.AFFINE, (s, 0, x0, 0, s, y0), Image.BICUBIC)
            fr_ = bg.copy(); fr_.paste(ph, (ax, ay), mask)
            yield fr_
    frames_to_mp4(gen(), n, out)

def video_seg(out, clip, a, b, look, speed="rt"):
    master = P("masters", f"{clip}_{'slow3' if speed == 'slow' else 'rt'}.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-i", master, "-t", str(b - a), "-an",
         "-vf", f"{GRADES[look]},setpts=PTS-STARTPTS,fps={FPS},format=yuv420p",
         "-c:v", "libx264", "-crf", "16", "-preset", "fast", out])

def frame_bg(path, ground, label):
    g = GROUNDS[ground]
    bg = Image.new("RGB", (W, H), g)
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rectangle([132, 322, 972, 1568], fill=120)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    bg.paste(Image.new("RGB", (W, H), (30, 20, 15)), (0, 0), sh)
    d = ImageDraw.Draw(bg)
    d.rectangle([120, 300, 960, 1540], fill=MAT)
    f = font("sans", 26, 500)
    sp = 26 * 0.34
    widths = [f.getlength(c) for c in label]
    tot = sum(widths) + sp * (len(label) - 1)
    x = (W - tot) / 2
    for c, w in zip(label, widths):
        d.text((x, 1468), c, font=f, fill=TERRA); x += w + sp
    for i, col in enumerate((BASIL, MAT, ROSSO)):
        d.rectangle([W / 2 - 36 + i * 24, 1512, W / 2 - 36 + (i + 1) * 24, 1515], fill=col)
    d.rectangle([W / 2 - 12, 1512, W / 2 + 12, 1515], outline=(205, 183, 151))
    bg.save(path)

def frame_seg(out, inner_file, ground, label):
    bgp = out.replace(".mp4", "_bg.png")
    frame_bg(bgp, ground, label)
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", bgp, "-i", inner_file, "-filter_complex",
         "[1:v]scale=760:1351,crop=760:1100,setsar=1[v];[0:v][v]overlay=160:340:shortest=1,fps=30,format=yuv420p",
         "-c:v", "libx264", "-crf", "16", "-preset", "fast", out])

# ---------- text layers ----------
def layer_hook(out, kicker, text):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # soft espresso scrim band behind the hook for legibility
    sc = np.zeros((H, W), dtype=float)
    y = np.arange(H)[:, None]
    sc[:] = np.exp(-((y - 960) / 360.0) ** 2) * 0.62
    scrim = Image.fromarray((sc * 255).astype("uint8"))
    im.paste(Image.new("RGBA", (W, H), ESP + (255,)), (0, 0), scrim)
    f, lines, size = wrap_fit(text, "serif_i", 120, 700, 990)
    total = 1.08 * size * len(lines)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    draw_centered(gd, lines, f, 960 + 24, (20, 12, 8, 200), lh=1.08)
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    im = Image.alpha_composite(im, glow)
    d = ImageDraw.Draw(im)
    top, bot = draw_centered(d, lines, f, 960 + 24, CREAM + (255,), lh=1.08)
    fk = font("sans", 30, 500)
    sp = 30 * 0.32
    widths = [fk.getlength(c) for c in kicker]
    tot = sum(widths) + sp * (len(kicker) - 1)
    x = (W - tot) / 2; ky = top - 70
    for c, w in zip(kicker, widths):
        d.text((x, ky), c, font=fk, fill=LANTERN + (255,)); x += w + sp
    d.rectangle([W / 2 - 40, bot + 34, W / 2 + 40, bot + 36], fill=LANTERN + (255,))
    im.save(out)

def layer_card(out, text, small=None, cy=1290, style="twilight"):
    PANEL, RULE = CARDS[style]
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f, lines, size = wrap_fit(text, "serif_i", 70, 500, 840)
    lh = 1.12
    th = lh * size * len(lines) + (60 if small else 0)
    pw, ph = 940, th + 84
    x0, y0 = (W - pw) / 2, cy - ph / 2
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rectangle([x0, y0, x0 + pw, y0 + ph], fill=PANEL + (232,))
    pd.rectangle([x0, y0, x0 + pw, y0 + 3], fill=RULE + (255,))
    im = Image.alpha_composite(im, panel)
    d = ImageDraw.Draw(im)
    draw_centered(d, lines, f, y0 + 42 + lh * size * len(lines) / 2 + 6, CREAM + (255,), lh=lh)
    if small:
        fs = font("sans", 30, 300)
        w = fs.getlength(small)
        d.text(((W - w) / 2, y0 + ph - 74), small, font=fs, fill=CREAM + (255,))
    im.save(out)

def layer_place(out, name):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = font("sans", 34, 500)
    sp = 34 * 0.36
    widths = [f.getlength(c) for c in name]
    tot = sum(widths) + sp * (len(name) - 1)
    x = (W - tot) / 2; y = 380
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    xx = x
    for c, w in zip(name, widths):
        gd.text((xx, y + 2), c, font=f, fill=(0, 0, 0, 210)); xx += w + sp
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    im = Image.alpha_composite(im, glow)
    pill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle([(W - tot) / 2 - 34, y - 22, (W + tot) / 2 + 34, y + 76], radius=8, fill=TWI + (215,))
    im = Image.alpha_composite(im, pill); d = ImageDraw.Draw(im)
    for c, w in zip(name, widths):
        d.text((x, y), c, font=f, fill=CREAM + (255,)); x += w + sp
    d.rectangle([W / 2 - 30, y + 58, W / 2 + 30, y + 60], fill=LANTERN + (255,))
    im.save(out)

# ---------- audio ----------
def read_audio(path, start=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-i", path]
    if dur: cmd += ["-t", str(dur)]
    cmd += ["-map", "0:a:0", "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).reshape(-1, 2).astype(float) / 32768

def loop_to(a, n, xf=0.4):
    x = int(xf * SR)
    out = a.copy()
    while len(out) < n:
        fade = np.linspace(0, 1, x)[:, None]
        out[-x:] = out[-x:] * (1 - fade) + a[:x] * fade
        out = np.concatenate([out, a[x:]])
    return out[:n]

def env_fade(n, fi, fo):
    e = np.ones(n)
    fi, fo = int(fi * SR), int(fo * SR)
    if fi: e[:fi] = np.linspace(0, 1, fi)
    if fo: e[-fo:] = np.linspace(1, 0, fo)
    return e[:, None]

def build_audio(job, starts, durs, total, out):
    n = int(total * SR)
    mix = np.zeros((n, 2))
    music_gain = np.full(n, job.get("music_level", 0.85))
    if job["sound"] == "natural":
        music_gain[:] = job.get("bed", 0.16)
        for seg, st, du in zip(job["segs"], starts, durs):
            nat = seg.get("nat")
            if not nat:
                continue
            clip, mode = nat[0], nat[1]
            if mode == "sync":  # real-speed audio matching the picture
                a = read_audio(P("src", f"{clip}.mov"), seg["a"], du)
            else:  # real ambience from the same clip, extended under slow motion / stills
                a = loop_to(read_audio(P("src", f"{clip}.mov")), int(du * SR))
            rms = np.sqrt((a ** 2).mean()) + 1e-9
            a = a / rms * 0.09 * nat[2] if len(nat) > 2 else a / rms * 0.09
            a = a[: int(du * SR)] * env_fade(len(a[: int(du * SR)]), XF, XF)
            s = int(st * SR); e = min(n, s + len(a))
            mix[s:e] += a[: e - s]
    if job.get("music"):
        m = read_audio(P("music", job["music"] + ".wav"), job.get("music_start", 0), total + 1)[:n]
        if len(m) < n:
            m = np.concatenate([m, np.zeros((n - len(m), 2))])
        mix += m * music_gain[:, None]
    mix *= env_fade(n, 0.03, 1.6)
    peak = np.abs(mix).max() + 1e-9
    if peak > 0.95: mix *= 0.95 / peak
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())

# ---------- assembly ----------
def build(job):
    vid = job["id"]
    segfiles, durs = [], []
    for i, s in enumerate(job["segs"]):
        f = P("seg", f"{vid}_{i:02d}.mp4")
        if s["t"] == "video":
            video_seg(f, s["clip"], s["a"], s["b"], s["look"], s.get("speed", "rt"))
            durs.append(s["b"] - s["a"])
        elif s["t"] == "photo":
            photo_seg(f, s["src"], s["look"], s["dur"], s.get("z0", 1.0), s.get("z1", 1.08),
                      tuple(s.get("c0", (0.5, 0.5))), tuple(s.get("c1", (0.5, 0.5))))
            durs.append(s["dur"])
        elif s["t"] == "frame":
            inn = s["inner"]; tmp = P("seg", f"{vid}_{i:02d}_inner.mp4")
            if inn["t"] == "video":
                video_seg(tmp, inn["clip"], inn["a"], inn["b"], inn["look"], inn.get("speed", "rt"))
            else:
                photo_seg(tmp, inn["src"], inn["look"], inn["dur"], inn.get("z0", 1.0), inn.get("z1", 1.08),
                          tuple(inn.get("c0", (0.5, 0.5))), tuple(inn.get("c1", (0.5, 0.5))))
            frame_seg(f, tmp, s["ground"], s["label"])
            durs.append(0)
        elif s["t"] == "end":
            endcard_seg(f, s["src"], s["look"], s["dur"], s["quote"], sub=s.get("sub"), theme=s.get("theme", job.get("end", "cream")))
            durs.append(s["dur"])
        segfiles.append(f)
    durs = [float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                 capture_output=True, text=True).stdout) for f in segfiles]
    starts, t = [], 0.0
    for d in durs:
        starts.append(t); t += d - XF
    total = t + XF
    # text layers
    layers = []
    hk = P("layers", f"{vid}_hook.png"); layer_hook(hk, job["kicker"], job["hook"])
    layers.append((hk, 0.0, job.get("hook_end", 3.4), False))
    for j, c in enumerate(job.get("cards", [])):
        f = P("layers", f"{vid}_card{j}.png")
        if c.get("place"):
            layer_place(f, c["text"])
        else:
            layer_card(f, c["text"], c.get("small"), style=c.get("style", job.get("card", "twilight")))
        si = c["seg"]
        a = starts[si] + c.get("da", 0.35) + (0 if si == 0 else XF * 0.5)
        b = starts[si] + durs[si] - c.get("db", 0.3) - (0 if si == len(durs) - 1 else XF * 0.5)
        if c.get("a") is not None: a = c["a"]
        if c.get("b") is not None: b = c["b"]
        layers.append((f, a, b, True))
    # filter graph
    inputs = []
    for f in segfiles:
        inputs += ["-i", f]
    for f, a, b, _ in layers:
        inputs += ["-loop", "1", "-t", f"{total:.3f}", "-i", f]
    aud = P("audio", f"{vid}.wav")
    build_audio(job, starts, durs, total, aud)
    inputs += ["-i", aud]
    fc = []
    ns = len(segfiles)
    for i in range(ns):
        fc.append(f"[{i}:v]settb=AVTB,fps={FPS},format=yuv420p,setsar=1[s{i}]")
    prev = "s0"
    for i in range(1, ns):
        off = starts[i]
        fc.append(f"[{prev}][s{i}]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]")
        prev = f"x{i}"
    for k, (f, a, b, fade_in) in enumerate(layers):
        idx = ns + k
        fl = f"[{idx}:v]format=rgba"
        if fade_in:
            fl += f",fade=t=in:st={a:.3f}:d=0.45:alpha=1"
        fl += f",fade=t=out:st={b - 0.4:.3f}:d=0.4:alpha=1[l{k}]"
        fc.append(fl)
        fc.append(f"[{prev}][l{k}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[o{k}]")
        prev = f"o{k}"
    fc.append(f"[{prev}]format=yuv420p[vout]")
    out = P("out", f"{vid}.mp4")
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[vout]",
         "-map", f"{ns + len(layers)}:a", "-t", f"{total:.3f}", "-c:v", "libx264", "-crf", "21", "-preset", "medium",
         "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", out])
    return {"id": vid, "file": out, "duration": round(total, 2), "segments": len(segfiles),
            "starts": [round(s, 2) for s in starts], "durs": [round(d, 2) for d in durs]}

if __name__ == "__main__":
    jobs = json.load(open(P("jobs.json")))
    sel = sys.argv[1:]
    res = []
    for j in jobs:
        if sel and j["id"] not in sel:
            continue
        r = build(j); print(json.dumps(r)); res.append(r)
