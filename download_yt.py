import argparse
from yt_dlp import YoutubeDL

def download_media(url, audio_only=False, output_path="%(title)s.%(ext)s"):
    if audio_only:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
    else:
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
            "outtmpl": output_path,
            "merge_output_format": "mp4"
        }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def main():
    parser = argparse.ArgumentParser(
        description="Télécharger une vidéo YouTube (MP4) ou uniquement l'audio (MP3) avec yt-dlp"
    )
    parser.add_argument("url", type=str, help="URL de la vidéo YouTube à télécharger")
    parser.add_argument(
        "-a", "--audio",
        action="store_true",
        help="Télécharger uniquement l'audio"
    )

    args = parser.parse_args()
    download_media(args.url, audio_only=args.audio)

if __name__ == "__main__":
    main()
