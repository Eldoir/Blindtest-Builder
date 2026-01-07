import subprocess
import os
import json
import tempfile
from pathlib import Path

# ---------------- CONFIG ---------------- #

ASSETS_DIR = Path("assets")
INTRO_FILEPATH = ASSETS_DIR / Path("intro.mp4")
OUTRO_FILEPATH = ASSETS_DIR / Path("outro.mp4")
TRANSITION_FILEPATH = ASSETS_DIR / Path("transition.mp4")

CLIPS_DIR = Path("clips")

OUTPUT_DIR = Path("output")
OUTPUT = OUTPUT_DIR / "blind_test.mp4"

CONFIG_FILE = Path("clips_config.json")
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    CLIP_CONFIG = json.load(f)

# --------------------------------------- #

def get_video_duration(path):
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return float(result.stdout.strip())

def run(cmd):
    subprocess.run(cmd, check=True)

def cut_and_mux(clip_name, idx, tmpdir):
    video_in = CLIPS_DIR / f"{clip_name}.mp4"
    audio_in = CLIPS_DIR / f"{clip_name}.mp3"

    v_start, v_end = CLIP_CONFIG[clip_name]["video"]
    a_start, a_end = CLIP_CONFIG[clip_name]["audio"]

    video_cut = tmpdir / f"{clip_name}_v.mp4"
    audio_cut = tmpdir / f"{clip_name}_a.wav"
    out_clip = tmpdir / f"{clip_name}_final.mp4"

    # Cut video
    run([
        "ffmpeg", "-y",
        "-ss", str(v_start), "-to", str(v_end),
        "-i", str(video_in),
        "-c:v", "libx264",
        "-an",
        str(video_cut)
    ])

    # Cut audio
    run([
        "ffmpeg", "-y",
        "-ss", str(a_start), "-to", str(a_end),
        "-i", str(audio_in),
        "-c:a", "pcm_s16le",
        str(audio_cut)
    ])

    # Mux audio + video
    run([
        "ffmpeg", "-y",
        "-i", str(video_cut),
        "-i", str(audio_cut),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(out_clip)
    ])

    return out_clip

def make_transition(idx, tmpdir, transition_duration):
    out = tmpdir / f"TRANSITION_FILEPATH_{idx}.mp4"

    run([
        "ffmpeg", "-y",
        "-i", str(TRANSITION_FILEPATH),
        "-vf",
         (
            # Clip number (top-left)
            f"drawtext=text='#{idx}':"
            "x=20:y=20:fontsize=256:fontcolor=white,"
            
            # Countdown timer (center)
            "drawtext="
            "text='%{eif\\:max(0\\,ceil(" + str(transition_duration) + "-t))\\:d}':"
            "x=(w-text_w)/2:"
            "y=(h-text_h)/2:"
            "fontsize=255:"
            "fontcolor=white:"
            "borderw=4"
        ),
        "-c:v", "libx264",
        "-c:a", "copy",
        str(out)
    ])

    return out

def concat_videos(video_list, output):
    inputs = []
    filter_parts = []

    for i, v in enumerate(video_list):
        inputs += ["-i", str(v)]
        filter_parts.append(f"[{i}:v:0][{i}:a:0]")

    filter_complex = "".join(filter_parts) + f"concat=n={len(video_list)}:v=1:a=1[outv][outa]"

    run([
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-c:a", "aac",
        output
    ])


def main():
    with tempfile.TemporaryDirectory() as td:
        tmpdir = Path(td)
        timeline = []

        if INTRO_FILEPATH.exists():
            timeline.append(INTRO_FILEPATH)

        clips = list(CLIP_CONFIG.keys())

        transition_duration: float = None
        if TRANSITION_FILEPATH.exists():
            transition_duration = get_video_duration(TRANSITION_FILEPATH) # in seconds, used for timer

        for i, clip_name in enumerate(clips, start=1):
            if transition_duration is not None:
                transition = make_transition(i, tmpdir, transition_duration)
                timeline.append(transition)

            final_clip = cut_and_mux(clip_name, i, tmpdir)
            timeline.append(final_clip)

        if OUTRO_FILEPATH.exists():
            timeline.append(OUTRO_FILEPATH)

        concat_videos(timeline, OUTPUT)

if __name__ == "__main__":
    main()
