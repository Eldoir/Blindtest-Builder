from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json

@dataclass
class Stream:
    src: Path
    start: float = field(default=0)

    def __post_init__(self):
        self.src = Path(self.src)

@dataclass
class Clip:
    title: str
    audio: Stream
    video: Stream
    year: Optional[float] = None

@dataclass
class Config:
    transition: Path
    output: Path
    clip_duration: float
    clips: list[Clip]
    font: Optional[Path] = None
    intro: Optional[Path] = None
    outro: Optional[Path] = None
    shuffle_clips: bool = field(default = False)

    def __post_init__(self):
        self.transition = Path(self.transition)
        self.output = Path(self.output)
        if self.font is not None:
            self.font = Path(self.font)
        if self.intro is not None:
            self.intro = Path(self.intro)
        if self.outro is not None:
            self.outro = Path(self.outro)

def load_config(path: str) -> Config:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    clips = []
    for c in data.get("clips", []):
        video = Stream(**c["video"])
        audio = Stream(**c["audio"])
        clip = Clip(title=c["title"], video=video, audio=audio, year=c["year"])
        clips.append(clip)

    return Config(
        font=data.get("font"),
        intro=data.get("intro"),
        outro=data.get("outro"),
        transition=data["transition"],
        output=data["output"],
        clip_duration=data["clip_duration"],
        clips=clips,
        shuffle_clips=data["shuffle_clips"]
    )