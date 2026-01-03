import random
import json
import subprocess
from pathlib import Path

# =========================
# PATHS
# =========================
BASE = Path("assets/finance_psychology")
CLIPS = list((BASE / "clips").glob("*.mp4"))
MUSIC = list((BASE / "music").glob("*.m4a"))

SETS_FILE = BASE / "sets.txt"

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

MANIFEST = Path("manifest.json")
used = set(json.loads(MANIFEST.read_text()).get("used", [])) if MANIFEST.exists() else set()

# =========================
# LOAD SETS
# =========================
def load_sets():
    sets = []
    for i, line in enumerate(SETS_FILE.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        if "|" not in line:
            raise ValueError(f"Invalid format at line {i}: missing '|'")

        hook, body = map(str.strip, line.split("|", 1))
        if not hook or not body:
            raise ValueError(f"Invalid set at line {i}: empty hook/body")

        sets.append({
            "id": f"set_{i}",
            "hook": hook,
            "body": body
        })
    return sets

SETS = load_sets()

# =========================
# HELPERS
# =========================
def pick_unused_set():
    random.shuffle(SETS)
    for s in SETS:
        if s["id"] not in used:
            return s
    raise RuntimeError("No unused text sets left")

def pick_unused(items):
    random.shuffle(items)
    for i in items:
        if i.name not in used:
            return i
    raise RuntimeError("No unused assets left")

def escape_text(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace("'", "\\'")
            .replace("%", "\\%")
    )

def text_filters(hook: str, body: str) -> str:
    hook = escape_text(hook)
    body = escape_text(body)

    return (
        # HOOK (boxed)
        "drawtext="
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        f"text='{hook}':"
        "fontcolor=white:"
        "fontsize=min(h*0.06\\,52):"
        "box=1:"
        "boxcolor=black@0.45:"
        "boxborderw=12:"
        "x=(w-text_w)/2:"
        "y=h*0.18"
        ","
        # BODY (clean)
        "drawtext="
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        f"text='{body}':"
        "fontcolor=white:"
        "fontsize=min(h*0.05\\,44):"
        "line_spacing=6:"
        "x=(w-text_w)/2:"
        "y=h*0.28"
    )

# =========================
# MAIN
# =========================
def generate_one(index: int):
    clip = pick_unused(CLIPS)
    music = pick_unused(MUSIC)
    text_set = pick_unused_set()

    out = OUTPUT / f"short_{index}.mp4"
    filters = text_filters(text_set["hook"], text_set["body"])

    cmd = [
        "ffmpeg", "-y",
        "-i", str(clip),
        "-i", str(music),
        "-filter_complex", filters,
        "-map", "0:v",
        "-map", "1:a",
        "-shortest",
        "-c:v", "libx264",
        "-preset", "slow",
        "-profile:v", "high",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "aac",
        "-b:a", "128k",
        str(out)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("FFmpeg failed")

    # mark everything as used
    used.update([
        clip.name,
        music.name,
        text_set["id"]
    ])

    return {
        "video": str(out),
        "hook": text_set["hook"],
        "body": text_set["body"]
    }

# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    GENERATED_COUNT = 3  # <-- change how many Shorts per run

    results = []
    for i in range(1, GENERATED_COUNT + 1):
        results.append(generate_one(i))

    MANIFEST.write_text(json.dumps({"used": sorted(used)}, indent=2))
    print(json.dumps(results, indent=2))
