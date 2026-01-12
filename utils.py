from pathlib import Path
import subprocess
from typing import Callable, Iterable, TypeVar

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
        return r"C:\Windows\Fonts\Arial.ttf"
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
    s = s.replace("\\", "\\\\") # for windows paths
    s = s.replace(":", "\\:")
    s = s.replace("'", "'\\''")
    return s

T = TypeVar("T")
def reduce_to_single(
        items: Iterable[T],
        predicate: Callable[[T], bool]
) -> list[T]:
    """Returns an array with the first item matching the predicate,
    or the entire array if no items match the predicate."""
    for item in items:
        if predicate(item):
            return [item]
    return list(items)
