# Prerequisites
* Python 3.x
* [FFmpeg](https://www.ffmpeg.org/)

# How to Use
Run _generate_video.py_.

## Config
The config should be in a file named _config.json_ next to the python file.\
There is an example in this repo.\
Here are the possible fields for this config (all paths are **relative** to the config file):

* Mandatory
  * `transition` (_str_): a path to a video that will be prepended to *every* clip during the video.
    * A timer will be displayed at the center of the video, counting down to 0 (its initial value depends on the duration of the transition video).
    * Also the number of the clip will be displayed in the top left corner.
  * `output` (_str_): a path to the final video, built by this program.
  * `clip_duration` (_float_): the duration of each clip on screen when revealed.
  * `clips` (_List[Clip]_): a list of clips (see below).
* Optional
  * `intro` (_str_): a path to a video that will be prepended at the very beginning of the final video.
  * `outro` (_str_): a path to a video that will be appended at the very end of the final video.
  * `font` (_str_): a path to a font file (usually .ttf or .otf) to use for the texts on the final video. If not specified, the default font will be:
      * Windows: _Arial_
      * MacOS: _Arial_
      * Linux: _DejaVuSans-Bold_, or _LiberationSans-Bold_ if not found
  * `shuffle_clips` (_bool_): if true, clips will be randomly shuffled before generating the video.

### Clip
* Mandatory
  * `title` (_str_): displayed at the bottom center of the screen, 2s after the clip is revealed (after the transition).
  * `video` (_Stream_): see below.
  * `audio` (_Stream_): see below.
* Optional
  * `year` (_int_): displayed below the title if given.

### Stream
* Mandatory
  * `src` (_str_): a path to the source file.
* Optional
  * `start` (_float_): the stream will start at that timestamp (in seconds). 0 if not specified.

## Notes
* For each clip, the part of the audio that will be played will be exactly `transition` + `clip_duration`.
  * For example, if the `transition` video lasts 10s and the `clip_duration` is `5`, the audio will play for 15s.
* The program will abort if any video cannot fit in the timeline.
  * When that's the case, you can either start the video sooner (by reducing the `start` value), or reduce the `clip_duration`.
  * For example, if you have a video file that lasts 30s, and set its `start` to `25`, the maximum value for `clip_duration` will be `5`.
* The same goes for audio: if your `transition` lasts 10s, your `clip_duration` is `5` and you defined a `start` value of `3` for some audio file, that audio should be at least 18s long (it will play for 15s, from 00:03 to 00:18).
* To make my life easier, the folders below are ignored. This allows me to have my source files close to the code to keep short paths and everything is in the same place. You can do the same!
  * `assets/`: I put my _intro_, _outro_, and _transition_ files here, as well as some editing files, like an Adobe Premiere Pro project, and also a text file containing the rules of my blind tests, and some notes, whatever.
  * `clips/`: I put my audio and video files here.
  * `output/`: I put the output files of the program here.

# Next steps
* Add "enabled" flag in Clip class (true by default) and make it work
* Shrink clip title if too long
* Add (optional) cross fade transitions...
* ...or forget about cross fade transitions
  * And display a timer on clip 3s before next transition instead
  * Audio cross-fade can still be performed later on using an editing tool