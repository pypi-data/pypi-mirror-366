# 🎬 ytmagic

`ytmagic` is a simple command-line tool that lets anyone download videos or extract audio from **YouTube, Instagram, Facebook, TikTok, X, and more** using [yt-dlp](https://github.com/yt-dlp/yt-dlp) — no technical knowledge needed.

It works on **Linux**, **macOS**, and **Windows**.

---

## 🧠 What Can It Do?

- ✅ Download full video with best quality
- 🎧 Download **audio only** and convert it to MP3
- 📥 Choose specific video quality like 360p, 720p, 1080p
- 📁 Save to custom folder or default to `~/Downloads`

---

## 🔧 Installation

Make sure you have **Python 3.7+**, `ffmpeg`, and `pip/pipx` installed.

Then install `ytmagic` globally using `pipx`:

```bash
pipx install ytmagic
```

Or for local testing (developer mode):

```bash
git clone https://github.com/owais-shafi/Yt_Magic.git
cd ytmagic
pipx install --force --editable .
```

✅ Now you can use the `ytmagic` command from anywhere in your terminal.

---

## 🎯 How to Use

Basic command format:

```bash
ytmagic [options] URL
```

### 🔤 Examples

```bash
ytmagic https://youtu.be/example1
# ▶️ Downloads best video+audio to ~/Downloads

ytmagic https://youtu.be/example2 -q 720
# ⬇️ Downloads 720p video

ytmagic https://youtu.be/example3 -a
# 🎵 Downloads and converts audio to MP3

ytmagic -a https://youtu.be/example4 -p ~/Music
# 🎧 Downloads MP3 and saves it in ~/Music
```

---

## ⚙️ Command-Line Options

| Option             | Description                                                             |
| ------------------ | ----------------------------------------------------------------------- |
| `url` (positional) | Video URL (YouTube, Instagram, Facebook, TikTok, etc.)                  |
| `-q`, `--quality`  | Video quality: `360`, `480`, `720`, `1080`, or `best` (default: `best`) |
| `-p`, `--path`     | Folder to save downloaded file (default: `~/Downloads`)                 |
| `-a`, `--audio`    | Download audio only and convert to MP3 (requires FFmpeg)                |

---

## 📦 Dependencies

To use the `-a` (audio-only MP3) option, `ffmpeg` must be installed on your system.

### ✅ Install `ffmpeg`:

- **Linux (Debian/Ubuntu):**

  ```bash
  sudo apt install ffmpeg
  ```

- **Linux (Arch):**

  ```bash
  sudo pacman -S ffmpeg
  ```

- **macOS (with Homebrew):**

  ```bash
  brew install ffmpeg
  ```

- **Windows (with Chocolatey):**

  ```bash
  choco install ffmpeg
  ```

- Or [download manually](https://www.gyan.dev/ffmpeg/builds/) and add it to your system PATH.

---

## 📂 Default Output Folder

If no path is given using `-p`, ytmagic saves all downloads to:

```bash
~/Downloads
```

---

## 💡 Tip

You can combine options! For example:

```bash
ytmagic -a -q best -p ~/Music https://youtu.be/example
```

This downloads the best audio, converts it to MP3, and saves it in your Music folder.

## To upgrade ytmagic:

```bash
pipx upgrade ytmagic
```

---

## 👨‍🔧 Built With

- [Python](https://www.python.org/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org/)

---

## 📜 License

MIT License — free for personal or commercial use.
