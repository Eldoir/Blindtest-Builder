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
    single: bool = field(default=False)

@dataclass
class Config:
    transition: Path
    output: Path
    clip_duration: float
    clips: list[Clip]
    font: Optional[Path] = None
    intro: Optional[Path] = None
    outro: Optional[Path] = None
    shuffle_clips: bool = field(default=False)

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
        clips.append(Clip(
            # Mandatory
            title=c["title"],
            video=video,
            audio=audio,
            # Optional
            **{key: c[key] for key in ("year", "single") if key in c}
        ))

    return Config(
        # Mandatory
        transition=data["transition"],
        output=data["output"],
        clip_duration=data["clip_duration"],
        clips=clips,
        # Optional
        **{key: data[key] for key in (
            "font",
            "intro",
            "outro",
            "shuffle_clips"
        ) if key in data}
    )