"""Clean B-roll pack: graded shots, no text. Video shots keep their real sound; photo shots are silent."""
import json, os, subprocess, sys
sys.argv = [sys.argv[0]]
import build as B
P = B.P
TR, CA = "travertino", "canale"
shots = [
 ("B01", "Venice canal from the bridge (slow motion)", "Venezia", ("video", "venice", 0.0, 5.7, CA, "slow")),
 ("B02", "Venetian stone rail, close (slow motion)", "Venezia", ("video", "venice", 6.0, 9.2, CA, "slow")),
 ("B03", "Gondola at the canal-side table", "Venezia", ("photo", "10", CA, 7.0, (.3, .5), (.58, .5), 1.0, 1.06)),
 ("B04", "St. Mark's astronomical clock", "Venezia", ("photo", "6", CA, 7.0, (.5, .45), (.5, .45), 1.0, 1.15)),
 ("B05", "Basilica di San Marco mosaic", "Venezia", ("photo", "8", TR, 6.0, (.45, .35), (.5, .55), 1.08, 1.0)),
 ("B06", "Clock tower, Piazza San Marco", "Venezia", ("photo", "9", CA, 6.0, (.55, .65), (.55, .4), 1.18, 1.18)),
 ("B07", "Betty in Piazza San Marco", "Venezia", ("photo", "7", TR, 6.0, (.6, .45), (.6, .45), 1.0, 1.1)),
 ("B08", "Walking toward the Colosseum (slow motion)", "Roma", ("video", "rome", 12.0, 24.5, TR, "slow")),
 ("B09", "Basilica of Maxentius and the camera's shadow (slow motion)", "Roma", ("video", "rome", 0.0, 7.4, TR, "slow")),
 ("B10", "Walking toward the Colosseum (real time, natural sound)", "Roma", ("video", "rome", 4.0, 8.2, TR, "rt")),
 ("B11", "The Forum under the clouds", "Pompeii", ("photo", "2", TR, 8.0, (.25, .5), (.72, .5), 1.0, 1.0)),
 ("B12", "Ruins and restoration scaffolding", "Pompeii", ("photo", "1", TR, 7.0, (.3, .45), (.65, .45), 1.0, 1.04)),
 ("B13", "Arches along the wall", "Pompeii", ("photo", "5", TR, 6.0, (.5, .45), (.5, .33), 1.0, 1.12)),
 ("B14", "Street and the house of L. Volusius Faustus", "Pompeii", ("photo", "4", TR, 6.0, (.22, .5), (.55, .5), 1.0, 1.04)),
]
out = []
for sid, title, place, spec in shots:
    tmp = P("broll", f"{sid}_v.mp4"); fin = P("broll", f"{sid}.mp4")
    if spec[0] == "video":
        _, clip, a, b, look, speed = spec
        B.video_seg(tmp, clip, a, b, look, speed)
        if speed == "rt":
            B.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-ss", str(a), "-t", str(b - a), "-i", P("src", f"{clip}.mov"),
                   "-map", "0:v", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", fin])
            sound = "natural sound"
        else:
            B.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-movflags", "+faststart", fin])
            sound = "silent"
    else:
        _, src, look, dur, c0, c1, z0, z1 = spec
        B.photo_seg(tmp, src, look, dur, z0, z1, c0, c1)
        B.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-movflags", "+faststart", fin])
        sound = "silent"
    os.remove(tmp)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", fin], capture_output=True, text=True).stdout)
    B.run(["ffmpeg", "-v", "error", "-y", "-ss", str(min(1.0, dur / 2)), "-i", fin, "-frames:v", "1", "-vf", "scale=540:-1", "-q:v", "4", P("broll", f"{sid}.jpg")])
    out.append({"id": sid, "title": title, "place": place, "sound": sound, "duration": round(dur, 1), "size": os.path.getsize(fin)})
    print(json.dumps(out[-1]), flush=True)
json.dump(out, open(P("broll", "manifest.json"), "w"), indent=1)
