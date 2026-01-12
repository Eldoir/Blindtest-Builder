import subprocess
import random
import sys
import uuid

def get_video_duration(video_path):
    """Récupère la durée de la vidéo en secondes avec ffprobe"""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", video_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return float(result.stdout.strip())

def generate_random_durations(total_duration=10, choices=[1, 1.5, 2]):
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

def generate_random_clips(video_path, total_duration=10):
    duration = get_video_duration(video_path)
    
    # Durées aléatoires pour les clips
    clip_durations = generate_random_durations(total_duration)
    
    input_args = []
    filter_complex_parts = []
    
    for i, clip_len in enumerate(clip_durations):
        t = random.uniform(0, max(0, duration - clip_len))
        input_args.extend(["-ss", str(t), "-t", str(clip_len), "-i", video_path])
        filter_complex_parts.append(f"[{i}:v:0][{i}:a:0]")
    
    filter_complex = "".join(filter_complex_parts) + f"concat=n={len(clip_durations)}:v=1:a=1[outv][outa]"
    
    # Générer un nom de fichier unique
    random_id = uuid.uuid4().hex[:8]
    output_file = f"random_edit_{random_id}.mp4"
    
    cmd = ["ffmpeg", "-y"] + input_args + ["-filter_complex", filter_complex,
                                           "-map", "[outv]", "-map", "[outa]",
                                           "-c:v", "libx264", "-c:a", "aac",
                                           "-strict", "experimental", output_file]
    
    subprocess.run(cmd)
    
    return output_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python random_edit.py <video.mp4> [total_duration_in_seconds]")
        sys.exit(1)
    
    video_path = sys.argv[1]
    # Paramètre optionnel : durée totale, défaut à 10
    total_duration = float(sys.argv[2]) if len(sys.argv) >= 3 else 10
    
    output_file = generate_random_clips(video_path, total_duration)
    print(f"Montage aléatoire généré : {output_file}")

if __name__ == "__main__":
    main()
