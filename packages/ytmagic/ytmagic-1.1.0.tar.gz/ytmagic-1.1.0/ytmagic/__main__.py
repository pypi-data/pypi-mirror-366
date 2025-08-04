#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path
from yt_dlp import YoutubeDL
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.console import Console

console = Console()

quality_map = {
    "360": "bestvideo[height<=360]+bestaudio/best[height<=360]",
    "480": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "720": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "best": "bestvideo+bestaudio/best"
}

def download_video(url, quality, download_path, audio_only=False):
    output_template = os.path.join(download_path, "%(title)s.%(ext)s")

    format_string = "bestaudio/best" if audio_only else quality_map.get(quality, quality_map["best"])

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("Downloading...", start=False)

        def hook(d):
            if d['status'] == 'downloading' and not progress.tasks[task].started:
                progress.start_task(task)
            if d['status'] == 'finished':
                progress.update(task, description="Processing...")
                console.print(f"\n✅ [bold green]Download complete:[/bold green] {d['filename']}")

        ydl_opts = {
            'format': format_string,
            'quiet': True,
            'progress_hooks': [hook],
            'outtmpl': output_template,
            'noplaylist': True,
            'merge_output_format': 'mp4' if not audio_only else None,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }] if audio_only else [],
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            console.print(f"❌ [bold red]Error:[/bold red] {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="🎥 Download videos or extract audio from YouTube, Instagram, Facebook, TikTok, X (Twitter), and more — easily and fast.",
        epilog="""
Examples:
  ytmagic -v or ytmagic --version                  # Show Current version
  ytmagic https://youtu.be/example1                # Best video+audio(saved into Downloads folder)
  ytmagic https://youtu.be/example1 -q 360         # Download 360p
  ytmagic https://youtu.be/example2 -q 720         # Download 720p
  ytmagic https://youtu.be/example3 -a             # Download and convert to MP3
  ytmagic -a https://youtu.be/exapmple4 -p ~/Music # Audio to custom folder
  
  Author: Owais shafi
  Username: @Meowahaha
  To upgrade ytmagic, run: pipx upgrade ytmagic
  For more details, visit: https://pypi.org/project/ytmagic/
              """,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("url", help="Video URL to download")
    parser.add_argument("-q", "--quality", default="best", choices=quality_map.keys(),
                        help="Video quality: 360, 480, 720, 1080, best")
    parser.add_argument("-p", "--path", default=str(Path.home() / "Downloads"),
                        help="Download location (default: ~/Downloads)")
    parser.add_argument("-a", "--audio", action="store_true",
                        help="Download audio only and convert to MP3")
    parser.add_argument("-v", "--version", action="version", version="ytmagic 1.1.0",
                        help="Show the version of ytmagic")


    args = parser.parse_args()
    download_video(args.url, args.quality, args.path, audio_only=args.audio)

if __name__ == "__main__":
    main()