"""Original royalty-free music for Betty's Italy reels, synthesized from scratch with numpy.
Three tracks: dolce (hopeful piano + strings), memoria (reflective, Pompeii), passeggiata (light mandolin/guitar).
"""
import numpy as np, wave, sys, os

SR = 44100
rng = np.random.default_rng(7)

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)

def piano(f, dur, vel=0.5):
    n = int(SR * (dur + 2.5))
    t = np.arange(n) / SR
    out = np.zeros(n)
    for h in range(1, 9):
        fh = f * h * np.sqrt(1 + 0.0004 * h * h)
        if fh > 16000:
            break
        amp = (1.0 / h ** 1.3) * vel
        dec = np.exp(-t * (0.9 + 0.55 * h) * (f / 440) ** 0.3)
        out += amp * dec * np.sin(2 * np.pi * fh * t + rng.uniform(0, 6.28))
    att = np.minimum(1, t / 0.004)
    rel = np.where(t > dur, np.exp(-(t - dur) * 6), 1.0)
    return out * att * rel

def pluck(f, dur, vel=0.5, bright=0.5):
    N = max(2, int(round(SR / f)))
    total = int(SR * (dur + 1.5))
    y = np.zeros(total + N + 1)
    burst = rng.uniform(-1, 1, N)
    # soften burst for warmer tone
    burst = np.convolve(burst, np.ones(int(2 + (1 - bright) * 6)) / (2 + (1 - bright) * 6), mode="same")
    y[1:N + 1] = burst
    decay = 0.996
    k = 1
    while (k + 1) * N + 1 <= len(y):
        s = k * N + 1
        y[s:s + N] = decay * 0.5 * (y[s - N:s] + y[s - N - 1:s - 1])
        k += 1
    y = y[1:total + 1]
    t = np.arange(len(y)) / SR
    rel = np.where(t > dur, np.exp(-(t - dur) * 8), 1.0)
    return y * rel * vel

def tremolo_mandolin(f, dur, vel=0.3, rate=11):
    out = np.zeros(int(SR * (dur + 1.2)))
    step = 1 / rate
    t0 = 0
    i = 0
    while t0 < dur:
        v = vel * (0.85 + 0.15 * (i % 2))
        p = pluck(f, step * 1.2, v, bright=0.8) + 0.5 * pluck(f * 1.003, step * 1.2, v * 0.6, bright=0.8)
        s = int(t0 * SR)
        e = min(len(out), s + len(p))
        out[s:e] += p[:e - s]
        t0 += step
        i += 1
    return out

def pad(freqs, dur, vel=0.12):
    n = int(SR * (dur + 1.5))
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            ff = f * 2 ** (det / 12)
            ph = rng.uniform(0, 6.28)
            # soft saw: a few harmonics
            for h in range(1, 7):
                out += (1 / h) * np.sin(2 * np.pi * ff * h * t + ph * h) * (0.7 ** h)
    env = np.minimum(1, t / 0.9) * np.where(t > dur, np.exp(-(t - dur) * 2.5), 1.0)
    return out * env * vel / (len(freqs) * 3)

def add(buf, sig, t):
    s = int(t * SR)
    e = min(len(buf), s + len(sig))
    if e > s:
        buf[s:e] += sig[:e - s]

def reverb(x, secs=2.6, wet=0.28, seed=3):
    r = np.random.default_rng(seed)
    n = int(SR * secs)
    t = np.arange(n) / SR
    outs = []
    for ch in range(2):
        ir = r.normal(0, 1, n) * np.exp(-t * 6.9 / secs)
        ir[: int(0.012 * SR)] = 0
        ir /= np.sqrt((ir ** 2).sum())
        L = len(x) + n
        nfft = 1 << (L - 1).bit_length()
        y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]
        outs.append((1 - wet) * x + wet * y * 0.9)
    return np.stack(outs, 1)

def lowpass(x, cutoff):
    nfft = 1 << (len(x) - 1).bit_length()
    X = np.fft.rfft(x, nfft)
    f = np.fft.rfftfreq(nfft, 1 / SR)
    X *= 1 / np.sqrt(1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, nfft)[: len(x)]

def master(st, fade_in=0.05, fade_out=3.0):
    st = st / (np.abs(st).max() + 1e-9) * 0.89
    n = len(st)
    env = np.ones(n)
    fi = int(fade_in * SR); fo = int(fade_out * SR)
    env[:fi] = np.linspace(0, 1, fi)
    env[-fo:] = np.linspace(1, 0, fo) ** 1.5
    return st * env[:, None]

def write(path, st):
    d = (np.clip(st, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(d.tobytes())

# chord helpers (midi roots)
def triad(root, minor=False):
    return [root, root + (3 if minor else 4), root + 7]

def dolce(length=48):
    bpm = 76; beat = 60 / bpm; bar = beat * 4
    buf = np.zeros(int(SR * (length + 4)))
    padbuf = np.zeros_like(buf)
    # D major: D A Bm G | D A G A
    prog = [(62, False), (57, False), (59, True), (55, False), (62, False), (57, False), (55, False), (57, False)]
    melody = {  # bar index -> list of (beat offset, midi, dur beats)
        2: [(0, 78, 1.5), (1.5, 76, 0.5), (2, 74, 2)],
        3: [(0, 74, 1), (1, 76, 1), (2, 71, 2)],
        4: [(0, 74, 1.5), (1.5, 73, 0.5), (2, 69, 2)],
        5: [(0, 73, 2), (2, 76, 2)],
        6: [(0, 78, 1.5), (1.5, 79, 0.5), (2, 81, 2)],
        7: [(0, 79, 1), (1, 78, 1), (2, 76, 2)],
        8: [(0, 78, 3)],
        10: [(0, 78, 1.5), (1.5, 76, 0.5), (2, 74, 2)],
        11: [(0, 74, 1), (1, 76, 1), (2, 79, 2)],
        12: [(0, 78, 2), (2, 76, 2)],
        13: [(0, 74, 4)],
    }
    nbars = int(length / bar) + 1
    for b in range(nbars):
        root, mn = prog[b % 8]
        tr = triad(root, mn)
        t0 = b * bar
        add(buf, piano(midi(root - 12), bar, 0.42), t0)
        arp = [tr[0], tr[1], tr[2], tr[1] + 12, tr[2] + 12, tr[1] + 12, tr[2], tr[1]]
        for i, n in enumerate(arp):
            add(buf, piano(midi(n), beat * 0.9, 0.22 + 0.04 * (i == 0)), t0 + i * beat / 2)
        if b >= 1:
            add(padbuf, pad([midi(x) for x in tr], bar, 0.16), t0)
        for off, n, d in melody.get(b, []):
            add(buf, piano(midi(n), d * beat, 0.38), t0 + off * beat)
    mix = buf + lowpass(padbuf, 1800)
    return master(reverb(mix[: int(SR * length)], 2.8, 0.3))

def memoria(length=48):
    bpm = 60; beat = 60 / bpm; bar = beat * 4
    buf = np.zeros(int(SR * (length + 4)))
    padbuf = np.zeros_like(buf)
    # A minor F C G | Am F C E
    prog = [(57, True), (53, False), (60, False), (55, False), (57, True), (53, False), (60, False), (52, False)]
    melody = {
        1: [(0, 76, 2), (2, 74, 1), (3, 72, 1)],
        2: [(0, 72, 3), (3, 71, 1)],
        3: [(0, 71, 4)],
        5: [(0, 76, 2), (2, 77, 1), (3, 76, 1)],
        6: [(0, 79, 3), (3, 77, 1)],
        7: [(0, 76, 2), (2, 75, 2)],   # leading into E
        8: [(0, 76, 4)],
        9: [(0, 81, 2), (2, 79, 2)],
        10: [(0, 76, 4)],
        11: [(0, 74, 2), (2, 72, 2)],
    }
    nbars = int(length / bar) + 1
    for b in range(nbars):
        root, mn = prog[b % 8]
        tr = triad(root, mn)
        if b % 8 == 7:
            tr = [52, 56, 59]  # E major
        t0 = b * bar
        add(buf, piano(midi(root - 12), bar * 1.2, 0.35), t0)
        for i, n in enumerate([tr[0], tr[2], tr[1] + 12, tr[2]]):
            add(buf, piano(midi(n), beat * 1.6, 0.17), t0 + i * beat)
        add(padbuf, pad([midi(x) for x in tr] + [midi(tr[0] - 12)], bar, 0.2), t0)
        for off, n, d in melody.get(b, []):
            add(buf, piano(midi(n), d * beat, 0.33), t0 + off * beat)
    mix = buf + lowpass(padbuf, 1400)
    return master(reverb(mix[: int(SR * length)], 3.4, 0.36))

def passeggiata(length=40):
    bpm = 104; beat = 60 / bpm; bar = beat * 4
    buf = np.zeros(int(SR * (length + 4)))
    # G major: G D Em C | G D C D
    prog = [(55, False), (50, False), (52, True), (48, False), (55, False), (50, False), (48, False), (50, False)]
    mel = [
        [(0, 74, 1), (1, 71, 1), (2, 74, 1), (3, 79, 1)],
        [(0, 78, 2), (2, 74, 2)],
        [(0, 76, 1), (1, 79, 1), (2, 83, 2)],
        [(0, 81, 1), (1, 79, 1), (2, 76, 2)],
        [(0, 74, 1), (1, 79, 1), (2, 83, 1), (3, 81, 1)],
        [(0, 81, 2), (2, 78, 2)],
        [(0, 76, 1), (1, 79, 1), (2, 81, 1), (3, 79, 1)],
        [(0, 78, 4)],
    ]
    nbars = int(length / bar) + 1
    for b in range(nbars):
        root, mn = prog[b % 8]
        tr = triad(root, mn)
        t0 = b * bar
        # guitar: bass on 1 and 3, chord strums on 2 and 4 + eighth arpeggio
        add(buf, pluck(midi(root - 12), beat * 1.8, 0.55, 0.4), t0)
        add(buf, pluck(midi(root - 5), beat * 1.8, 0.45, 0.4), t0 + 2 * beat)
        for k in (1, 3):
            for j, n in enumerate(tr):
                add(buf, pluck(midi(n), beat * 0.9, 0.22, 0.6), t0 + k * beat + j * 0.012)
        for j, n in enumerate([tr[0] + 12, tr[1] + 12, tr[2], tr[1] + 12]):
            add(buf, pluck(midi(n), beat * 0.4, 0.1, 0.7), t0 + (j * 2 + 1) * beat / 2)
        if b >= 2:
            for off, n, d in mel[b % 8]:
                add(buf, tremolo_mandolin(midi(n), d * beat * 0.95, 0.16), t0 + off * beat)
        # soft shaker on eighths
        for e in range(8):
            nz = rng.normal(0, 1, int(0.05 * SR)) * np.exp(-np.arange(int(0.05 * SR)) / (0.012 * SR))
            nz = nz - lowpass(nz, 5000)
            add(buf, nz * (0.015 if e % 2 else 0.022), t0 + e * beat / 2)
    return master(reverb(lowpass(buf[: int(SR * length)], 5500), 1.8, 0.2))

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name, fn in [("dolce", dolce), ("memoria", memoria), ("passeggiata", passeggiata)]:
        write(os.path.join(out, name + ".wav"), fn())
        print("wrote", name)
