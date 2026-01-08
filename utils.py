from pathlib import Path
import subprocess
import serialization

def get_media_duration(path: Path) -> float:
    """Get duration of any media file (video or audio) using ffprobe"""
    result = subprocess.run(
        [
            "ffprobe", 
            "-v", "error",
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

def determine_font_file(config: serialization.Config) -> str | None:
    if config.font is not None:
        return str(config.font)

    # Determine font path based on OS
    import platform
    system = platform.system()
    
    # Windows
    if system == "Windows":
        return "C:/Windows/Fonts/arial.ttf"
    # MacOS
    if system == "Darwin":
        return "/System/Library/Fonts/Supplemental/Arial.ttf"
    # Linux
    possible_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for f in possible_fonts:
        if Path(f).exists():
            return f
        
    return None

def escape_filter_string(s: str) -> str:
    """Escape special characters for FFmpeg filter strings"""
    # For Windows paths and filter strings, we need to escape colons and backslashes
    # Convert backslashes to forward slashes first (FFmpeg prefers this)
    s = s.replace("\\", "/")
    # Then escape colons and single quotes
    s = s.replace(":", "\\:")
    s = s.replace("'", "'\\''")
    return s
