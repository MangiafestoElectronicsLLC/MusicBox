# MusicBox
# MusicBox – YouTube to MP3 (Batocera Intros)

MusicBox is a small tool to turn YouTube videos into MP3 files, optimized for Batocera intro / menu music.

- **Tkinter desktop app**: Dark mode, optional batch mode, drag‑and‑drop (Windows with `tkinterdnd2`), trim, normalize, progress bar.
- **Streamlit web app**: Simple web UI, batch processing, download buttons.

> Use only with your own content or copyright‑free videos. Downloading copyrighted material without permission may violate YouTube’s Terms of Service and local laws.

---

## Features

- **Single or batch mode**
  - Single URL mode by default.
  - Optional batch mode: multiple URLs, one per line.
- **Trim for Batocera intros**
  - Default 35 seconds, configurable 5–120 seconds.
- **Normalize volume**
  - Uses FFmpeg's `loudnorm` filter for more consistent loudness.
- **Dark mode desktop UI**
  - Modern look with progress bar + status messages.
- **Drag‑and‑drop (desktop app)**
  - Drag `.txt` file with URLs or links (on supported setups).
  - Requires `tkinterdnd2` on Windows.

---

## Requirements

- Python 3.10+ (tested for Python 3.13 compatibility – no `pydub` / `audioop`).
- FFmpeg installed and in your system `PATH`.
- Internet connection for downloading from YouTube.

---

## Installation

```bash
git clone https://github.com/your-username/MusicBox.git
cd MusicBox
