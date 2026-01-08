import subprocess
import json
import logging
from pathlib import Path

# ---------------- CONFIG ---------------- #
ASSETS_DIR = Path("assets")
INTRO_PATH = ASSETS_DIR / "intro.mp4"
OUTRO_PATH = ASSETS_DIR / "outro.mp4"
TRANSITION_PATH = ASSETS_DIR / "transition.mp4"
CLIPS_DIR = Path("clips")
OUTPUT_DIR = Path("output")
OUTPUT_PATH = OUTPUT_DIR / "blind_test.mp4"
CONFIG_PATH = Path("clips_config.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CLIP_CONFIG = json.load(f)

def get_video_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path)
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    return float(result.stdout.strip())

def determine_font_file() -> str:
    """Determine font path based on OS"""
    import platform
    system = platform.system()
    
    if system == "Windows":
        font_file = "C:/Windows/Fonts/arial.ttf"
    elif system == "Darwin":  # macOS
        font_file = "/System/Library/Fonts/Supplemental/Arial.ttf"
    else:  # Linux
        # Try common locations
        possible_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
        font_file = None
        for f in possible_fonts:
            if Path(f).exists():
                font_file = f
                break
        if not font_file:
            font_file = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    return font_file

def escape_filter_string(s: str) -> str:
    """Escape special characters for FFmpeg filter strings"""
    # For Windows paths and filter strings, we need to escape colons and backslashes
    # Convert backslashes to forward slashes first (FFmpeg prefers this)
    s = s.replace("\\", "/")
    # Then escape colons and single quotes
    s = s.replace(":", "\\:")
    s = s.replace("'", "'\\''")
    return s

def build_ffmpeg_command():
    """Build a single FFmpeg command to create the entire video"""
    
    transition_duration = get_video_duration(TRANSITION_PATH)
    clips = list(CLIP_CONFIG.keys())
    
    # Build input list
    inputs = []
    input_map = {}
    input_idx = 0
    
    # Add intro if exists
    if INTRO_PATH.exists():
        inputs.extend(["-i", str(INTRO_PATH)])
        input_map['intro'] = input_idx
        input_idx += 1
    
    # Add transition (used multiple times)
    inputs.extend(["-i", str(TRANSITION_PATH)])
    input_map['transition'] = input_idx
    input_idx += 1
    
    # Add all video clips
    for clip_name in clips:
        video_path = CLIPS_DIR / f"{clip_name}.mp4"
        inputs.extend(["-i", str(video_path)])
        input_map[f'video_{clip_name}'] = input_idx
        input_idx += 1
    
    # Add all audio clips
    for clip_name in clips:
        audio_path = CLIPS_DIR / f"{clip_name}.mp3"
        inputs.extend(["-i", str(audio_path)])
        input_map[f'audio_{clip_name}'] = input_idx
        input_idx += 1
    
    # Add outro if exists
    if OUTRO_PATH.exists():
        inputs.extend(["-i", str(OUTRO_PATH)])
        input_map['outro'] = input_idx
        input_idx += 1
    
    font_file = escape_filter_string(determine_font_file())
    
    # Build filter complex
    filter_parts = []
    video_streams = []
    audio_streams = []
    
    # Add intro video/audio if exists
    if 'intro' in input_map:
        video_streams.append(f"[{input_map['intro']}:v]")
        audio_streams.append(f"[{input_map['intro']}:a]")
    
    # Process each clip
    for i, clip_name in enumerate(clips, start=1):
        v_start, v_end = CLIP_CONFIG[clip_name]["video"]
        a_start, a_end = CLIP_CONFIG[clip_name]["audio"]
        
        video_duration = v_end - v_start
        audio_duration = a_end - a_start
        full_duration = transition_duration + video_duration
        
        # Validate audio duration
        if audio_duration < full_duration - 0.01:  # 0.01s tolerance
            raise ValueError(
                f"Audio for {clip_name} is too short: {audio_duration}s "
                f"(need at least {full_duration}s)"
            )
        
        transition_idx = input_map['transition']
        video_idx = input_map[f'video_{clip_name}']
        audio_idx = input_map[f'audio_{clip_name}']
        
        # Create transition with overlays
        trans_label = f"trans{i}"
        filter_parts.append(
            f"[{transition_idx}:v]"
            f"drawtext="
            f"fontfile='{font_file}':"
            f"text='#{i}':"
            f"x=20:y=20:"
            f"fontsize=256:"
            f"fontcolor=white,"
            f"drawtext="
            f"fontfile='{font_file}':"
            f"text='%{{eif\\:max(0\\,ceil({transition_duration}-t))\\:d}}':"
            f"x=(w-text_w)/2:"
            f"y=(h-text_h)/2:"
            f"fontsize=255:"
            f"fontcolor=white:"
            f"borderw=4"
            f"[{trans_label}]"
        )
        
        # Trim video clip
        video_label = f"v{i}"
        filter_parts.append(
            f"[{video_idx}:v]"
            f"trim=start={v_start}:end={v_end},"
            f"setpts=PTS-STARTPTS"
            f"[{video_label}]"
        )
        
        # Concatenate transition + video
        concat_label = f"concat{i}"
        filter_parts.append(
            f"[{trans_label}][{video_label}]"
            f"concat=n=2:v=1:a=0"
            f"[{concat_label}]"
        )
        
        video_streams.append(f"[{concat_label}]")
        
        # Trim and pad audio to exact duration
        audio_label = f"a{i}"
        filter_parts.append(
            f"[{audio_idx}:a]"
            f"atrim=start={a_start}:end={a_end},"
            f"asetpts=PTS-STARTPTS,"
            f"atrim=duration={full_duration},"
            f"apad=whole_dur={full_duration}"
            f"[{audio_label}]"
        )
        
        audio_streams.append(f"[{audio_label}]")
    
    # Add outro video/audio if exists
    if 'outro' in input_map:
        video_streams.append(f"[{input_map['outro']}:v]")
        audio_streams.append(f"[{input_map['outro']}:a]")
    
    # Final concatenation
    n_segments = len(video_streams)
    filter_parts.append(
        f"{''.join(video_streams)}"
        f"concat=n={n_segments}:v=1:a=0[outv]"
    )
    filter_parts.append(
        f"{''.join(audio_streams)}"
        f"concat=n={n_segments}:v=0:a=1[outa]"
    )
    
    filter_complex = ";".join(filter_parts)
    
    # Build final command
    cmd = [
        "ffmpeg", "-y",
        "-loglevel", "error",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "medium",  # adjust: ultrafast, fast, medium, slow
        "-crf", "23",         # quality: lower = better (18-28 range)
        "-c:a", "aac",
        "-b:a", "192k",
        str(OUTPUT_PATH)
    ]
    
    return cmd

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )
    
    if not TRANSITION_PATH.exists():
        logging.error(f'Transition video not found at {TRANSITION_PATH}')
        return
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    logging.info(f"Building video with {len(CLIP_CONFIG)} clips...")
    
    try:
        cmd = build_ffmpeg_command()
        
        # logging.debug(" ".join(cmd))
        
        subprocess.run(cmd, check=True)
        logging.info(f"Video created at: {OUTPUT_PATH}")
        
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg failed: {e}")
    except Exception as e:
        logging.error(f"Exception: {e}")

if __name__ == "__main__":
    main()