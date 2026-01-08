from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json

@dataclass
class Stream:
    src: Path
    start: float
    end: float

    def __post_init__(self):
        self.src = Path(self.src)

@dataclass
class Clip:
    title: str
    audio: Stream
    video: Stream

@dataclass
class Config:
    transition: Path
    output: Path
    clips: list[Clip]
    intro: Optional[Path] = None
    outro: Optional[Path] = None

    def __post_init__(self):
        self.transition = Path(self.transition)
        self.output = Path(self.output)
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
        clip = Clip(title=c["title"], video=video, audio=audio)
        clips.append(clip)

    return Config(
        intro=data.get("intro"),
        outro=data.get("outro"),
        transition=data["transition"],
        output=data["output"],
        clips=clips
    )