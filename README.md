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
  * **transition** (_str_): a path to a video that will be prepended to *every* clip during the video.
    * A timer will be displayed at the center of the video, counting down to 0 (its initial value depends on the duration of the transition video).
    * Also the number of the clip will be displayed in the top left corner.
  * **output** (_str_): a path to the final video, built by this program.
  * **clips** (_List[Clip]_): a list of clips (see below).
* Optional
  * **intro** (_str_): a path to a video that will be prepended at the very beginning of the final video.
  * **outro** (_str_): a path to a video that will be appended at the very end of the final video.
  * **font** (_str_): a path to a font file (usually .ttf or .otf) to use for the texts on the final video. If not specified, a default font will be chosen depending on the platform:
      * Windows: Arial
      * MacOS: Arial
      * Linux: DejaVuSans-Bold, or LiberationSans-Bold if not found

### Clip
* **title** (_str_): displayed on screen when the clip is revealed (after the transition).
* **video** (_Stream_): see below.
* **audio** (_Stream_): see below.

### Stream
* **src** (_str_): a path to the source file.
* **start** (_float_): the start position to crop the stream (in seconds).
* **end** (_float_): the end position to crop the stream (in seconds).

## Next steps
* Also display clip number on clip
* Add text on clip (title, should be in config file)
* Add cross fade transitions
  * Make it optional
* Ask to replace if output file already exists