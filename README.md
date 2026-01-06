# Prerequisites

* Python
* [FFmpeg](https://www.ffmpeg.org/)

# How to Use

Run _generate_video.py_.

## Considerations

* Clips must be in a _clips/_ folder.
* Each clip must be made of a .mp4 and a .mp3 file named the same way.
  * For example: _Cuphead.mp4_ and _Cuphead.mp3_.
* Timestamps for clips go in _clips_config.json_.
* The output file goes into the _output/_ folder and is named _blind_test.mp4_.

## Special assets
You can insert some special assets into the timeline.\
These assets must be in an _assets/_ folder.\
They will be ignored if not present.

* _intro.mp4_ will be prepended at the very beginning of the video.
* _transition.mp4_ will be prepended to *every* clip during the video.
  * For now the transition duration is 10 seconds.
  * A timer will be displayed at the center of the video, counting down from 10 to 0.
  * Also the number of the clip will be displayed in the top left corner.
* _outro.mp4_ will be appended at the very end of the video.

## Next steps
* Adjust audio during transitions (wrong right now)
* Add cross fade transitions
  * Make it optional
* Put python constants in a config file
* Ask to replace if output file already exists