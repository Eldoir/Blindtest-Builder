import subprocess
import logging
import time

import utils
import serialization
from DrawTextBuilder import DrawTextBuilder

def build_ffmpeg_command(config: serialization.Config):
    """Build a single FFmpeg command to create the entire video"""

    # Build input list
    inputs = []
    input_map = {}
    input_idx = 0
    
    # Add intro if exists
    if config.intro is not None and config.intro.exists():
        inputs.extend(["-i", str(config.intro)])
        input_map['intro'] = input_idx
        input_idx += 1
    
    # Add transition (used multiple times)
    inputs.extend(["-i", str(config.transition)])
    input_map['transition'] = input_idx
    input_idx += 1
    
    clips = list(map(lambda x: x, config.clips))

    # Add all video clips
    for clip in clips:
        inputs.extend(["-i", str(clip.video.src)])
        input_map[f'video_{clip}'] = input_idx
        input_idx += 1
    
    # Add all audio clips
    for clip in clips:
        inputs.extend(["-i", str(clip.audio.src)])
        input_map[f'audio_{clip}'] = input_idx
        input_idx += 1
    
    # Add outro if exists
    if config.outro is not None and config.outro.exists():
        inputs.extend(["-i", str(config.outro)])
        input_map['outro'] = input_idx
        input_idx += 1
    
    video_streams = []
    audio_streams = []

    # Add intro video/audio if exists
    if 'intro' in input_map:
        video_streams.append(f"[{input_map['intro']}:v]")
        audio_streams.append(f"[{input_map['intro']}:a]")
    
    filter_parts = []
    font_file = utils.determine_font_file(config)
    if font_file is None:
        logging.warning("Could not find a suitable font for texts. This can lead to unexpected results on the final output.")
    font_file = utils.escape_filter_string(str(font_file))
    transition_duration = utils.get_media_duration(config.transition)

    # Process each clip
    for i, clip in enumerate(clips, start=1):
        # Check that video is long enough
        clip_video_end = clip.video.start + config.clip_duration
        video_duration = utils.get_media_duration(clip.video.src)
        if clip_video_end > video_duration:
            raise ValueError(
                f"Video for '{clip.title}' is too short: {video_duration}s "
                f"(need at least {clip_video_end}s)"
            )
        
        # Check that audio is long enough
        clip_audio_end = clip.audio.start + transition_duration + config.clip_duration
        audio_duration = utils.get_media_duration(clip.audio.src)
        if clip_audio_end > audio_duration:
            raise ValueError(
                f"Audio for '{clip.title}' is too short: {audio_duration}s "
                f"(need at least {clip_audio_end}s)"
            )
        
        full_duration = transition_duration + config.clip_duration
        # Validate audio duration
        if audio_duration < full_duration - 0.01:  # 0.01s tolerance
            raise ValueError(
                f"Audio for '{clip.title}' is too short: {audio_duration}s "
                f"(need at least {full_duration}s)"
            )
        
        transition_idx = input_map['transition']
        video_idx = input_map[f'video_{clip}']
        audio_idx = input_map[f'audio_{clip}']
        
        text_builder = (
            DrawTextBuilder()
            .fontfile(font_file)
            .fontsize(255)
            .fontcolor("white")
            .borderw(4)
        )

        clip_number_text = (text_builder
            .text(f"#{i}")
            .x(20).y(20)
            .build()
        )

        timer_text = (text_builder
            .text(f"%{{eif\\:max(0\\,ceil({transition_duration}-t))\\:d}}")
            .centered()
            .build()
        )

        # Create transition with overlays
        trans_label = f"trans{i}"
        filter_parts.append(
            f"[{transition_idx}:v]"
            f"{clip_number_text},"
            f"{timer_text}"
            f"[{trans_label}]"
        )
        
        clip_title_text = (text_builder
            .text(clip.title)
            .fontsize(155)
            .centered_x()
            .bottom_y(20)
            .enable(f"between(t, 2, {clip_video_end})") # show after 2s and for the rest of the clip
            .build())

        # Trim video clip
        video_label = f"v{i}"
        filter_parts.append(
            f"[{video_idx}:v]"
            f"trim=start={clip.video.start}:end={clip_video_end},"
            f"setpts=PTS-STARTPTS,"
            f"{clip_number_text},"
            f"{clip_title_text}"
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
            f"atrim=start={clip.audio.start}:end={clip_audio_end},"
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
        "ffmpeg",
        "-stats",
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
        str(config.output)
    ]
    
    return cmd

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    config = serialization.load_config("config.json")
    
    if not config.transition.exists():
        logging.error(f'Transition video not found at {config.transition}')
        return
    
    logging.info(f"Building video with {len(config.clips)} clips...")
    
    try:
        cmd = build_ffmpeg_command(config)
        
        # logging.debug(" ".join(cmd))
        
        start = time.perf_counter()
        subprocess.run(cmd, check=True)
        end = time.perf_counter()
        logging.info(f"Video created in {end - start:.1f}s at: {config.output}")
        
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg failed: {e}")
    except Exception as e:
        logging.error(f"{e}")

if __name__ == "__main__":
    main()