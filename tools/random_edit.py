import subprocess
import random
import sys
import uuid

def get_video_duration(video_path):
    """Récupère la durée de la vidéo en secondes avec ffprobe"""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return float(result.stdout.strip())

def generate_random_durations(total_duration, choices):
    """Génère une liste de durées aléatoires dont la somme est proche de total_duration"""
    durations = []
    remaining = total_duration

    while remaining > 0.1:
        d = random.choice(choices)
        if d > remaining:
            d = remaining
        durations.append(d)
        remaining -= d

    return durations

def generate_random_clips(video_path, total_duration, choices):
    duration = get_video_duration(video_path)

    clip_durations = generate_random_durations(total_duration, choices)

    input_args = []
    filter_complex_parts = []

    for i, clip_len in enumerate(clip_durations):
        t = random.uniform(0, max(0, duration - clip_len))
        input_args.extend(["-ss", str(t), "-t", str(clip_len), "-i", video_path])
        filter_complex_parts.append(f"[{i}:v:0][{i}:a:0]")

    filter_complex = (
        "".join(filter_complex_parts)
        + f"concat=n={len(clip_durations)}:v=1:a=1[outv][outa]"
    )

    random_id = uuid.uuid4().hex[:8]
    output_file = f"random_edit_{random_id}.mp4"

    cmd = [
        "ffmpeg", "-y",
		"-stats",
        "-loglevel", "error",
        *input_args,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "experimental",
        output_file
    ]

    subprocess.run(cmd)
    return output_file

def parse_choices(choices_str):
    """Convertit '1,1.5,2' en [1.0, 1.5, 2.0]"""
    try:
        return [float(c.strip()) for c in choices_str.split(",")]
    except ValueError:
        print("Erreur : choices doit être une liste de nombres séparés par des virgules.")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python random_edit.py <video.mp4> "
            "[total_duration] [choices]\n"
            "Exemple: python random_edit.py video.mp4 10 1,1.5,2"
        )
        sys.exit(1)

    video_path = sys.argv[1]
    total_duration = float(sys.argv[2]) if len(sys.argv) >= 3 else 10
    choices = parse_choices(sys.argv[3]) if len(sys.argv) >= 4 else [1, 1.5, 2]

    output_file = generate_random_clips(video_path, total_duration, choices)
    print(f"Montage aléatoire généré : {output_file}")

if __name__ == "__main__":
    main()
