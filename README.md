# MusicBox
# YouTube to MP3 Downloader (Batocera Intro Helper)

A small toolkit to download audio from YouTube as MP3 files, optimized for Batocera intro / menu music.

- Desktop app: Tkinter GUI with dark mode, batch mode, drag‑and‑drop (optional), trim + normalize
- Web app: Streamlit interface with batch support and per-file download buttons

> Use only with your own content or copyright‑free videos. Downloading copyrighted material without permission may violate YouTube's Terms of Service.

---

## Features

- **Single or batch mode**  
  - Paste one URL or multiple (one per line)  
  - Batch mode is optional; you can keep using single‑URL mode

- **Auto-trim for Batocera intros**  
  - Default: `35` seconds  
  - Customizable from `5–120` seconds  
  - Trims from the start of the audio

- **Auto-normalize volume**  
  - Uses `pydub.effects.normalize`  
  - Helps keep intro/menu audio consistent in loudness

- **Dark mode Tkinter UI**  
  - Styled with `ttk`  
  - Progress bar + status messages

- **Drag-and-drop support (Tkinter app)**  
  - Drag a `.txt` file with URLs into the window  
  - Or drag URLs (platform-dependent)  
  - Requires `tkinterdnd2` (on Windows)

- **Streamlit version**  
  - Simple web UI  
  - Multi-URL support  
  - Produces per-file download buttons

---

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/your-username/yt-mp3-downloader.git
cd yt-mp3-downloader
