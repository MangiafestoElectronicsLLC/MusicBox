import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import yt_dlp
from pydub import AudioSegment, effects

# Try to enable drag-and-drop via tkinterdnd2 (optional)
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    TK_DND_AVAILABLE = True
except ImportError:
    TK_DND_AVAILABLE = False
    TkinterDnD = tk.Tk  # fallback to normal Tk


# ---------- CONFIG DEFAULTS ----------

DEFAULT_TRIM_SECONDS = 35  # for Batocera intros


# ---------- CORE DOWNLOAD / PROCESSING LOGIC ----------

def download_and_process_audio(
    url,
    output_folder,
    trim_seconds=None,
    normalize=False,
    progress_callback=None,
):
    """
    Download a single YouTube URL as MP3, optionally trim and normalize.

    progress_callback: function(message: str) called with status updates.
    """
    if progress_callback:
        progress_callback(f"Downloading: {url}")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "noprogress": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "audio")
        mp3_path = os.path.join(output_folder, f"{title}.mp3")

    if not os.path.exists(mp3_path):
        raise FileNotFoundError(f"MP3 file not found after download: {mp3_path}")

    if trim_seconds is not None or normalize:
        if progress_callback:
            progress_callback("Processing audio...")

        audio = AudioSegment.from_file(mp3_path)

        if trim_seconds is not None:
            max_ms = int(trim_seconds * 1000)
            if len(audio) > max_ms:
                audio = audio[:max_ms]

        if normalize:
            audio = effects.normalize(audio)

        audio.export(mp3_path, format="mp3")

    if progress_callback:
        progress_callback("Done")


# ---------- TKINTER GUI APP ----------

class YoutubeMp3DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube to MP3 Downloader")
        self.root.geometry("650x480")
        self.root.resizable(False, False)

        self.apply_dark_mode()

        self.output_folder = tk.StringVar()
        self.batch_mode = tk.BooleanVar(value=False)
        self.trim_enabled = tk.BooleanVar(value=True)
        self.normalize_enabled = tk.BooleanVar(value=True)
        self.trim_seconds = tk.IntVar(value=DEFAULT_TRIM_SECONDS)

        self.create_widgets()

    def apply_dark_mode(self):
        bg = "#121212"
        fg = "#f0f0f0"
        accent = "#1f6feb"

        self.root.configure(bg=bg)

        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(
            "TLabel",
            background=bg,
            foreground=fg,
        )
        style.configure(
            "TButton",
            background=accent,
            foreground="#ffffff",
            padding=6,
        )
        style.map("TButton", background=[("active", "#2386f5")])
        style.configure(
            "TCheckbutton",
            background=bg,
            foreground=fg,
        )
        style.configure(
            "Horizontal.TProgressbar",
            background=accent,
            troughcolor="#333333",
            bordercolor="#333333",
            lightcolor=accent,
            darkcolor=accent,
        )

    def create_widgets(self):
        pad_x = 15
        pad_y = 5

        # URL input / batch input
        url_frame = ttk.LabelFrame(self.root, text="YouTube links")
        url_frame.pack(fill="x", padx=pad_x, pady=pad_y)

        self.single_url_entry = tk.Entry(url_frame, width=80, bg="#1e1e1e", fg="#f0f0f0", insertbackground="#f0f0f0")
        self.single_url_entry.pack(fill="x", padx=8, pady=4)

        self.batch_text = tk.Text(url_frame, height=6, width=80, bg="#1e1e1e", fg="#f0f0f0", insertbackground="#f0f0f0")
        self.batch_text.pack(fill="both", padx=8, pady=4)
        self.batch_text.pack_forget()  # start hidden

        # Drag and drop hint
        if TK_DND_AVAILABLE:
            hint = "Tip: Drag YouTube links or .txt file with URLs into the window."
        else:
            hint = "Drag-and-drop not available (install tkinterdnd2 to enable)."
        self.dd_hint_label = ttk.Label(self.root, text=hint)
        self.dd_hint_label.pack(fill="x", padx=pad_x, pady=(0, pad_y))

        # Batch mode toggle
        options_frame = ttk.Frame(self.root)
        options_frame.pack(fill="x", padx=pad_x, pady=pad_y)

        batch_check = ttk.Checkbutton(
            options_frame,
            text="Batch mode (multiple links, one per line)",
            variable=self.batch_mode,
            command=self.toggle_batch_mode,
        )
        batch_check.grid(row=0, column=0, sticky="w", padx=(0, 20))

        # Trim & normalize options
        trim_check = ttk.Checkbutton(
            options_frame,
            text="Trim for Batocera intro",
            variable=self.trim_enabled,
        )
        trim_check.grid(row=1, column=0, sticky="w", pady=(4, 0))

        trim_seconds_label = ttk.Label(options_frame, text="Trim length (seconds):")
        trim_seconds_label.grid(row=1, column=1, sticky="e", padx=(20, 4))

        trim_spin = tk.Spinbox(
            options_frame,
            from_=5,
            to=120,
            textvariable=self.trim_seconds,
            width=5,
            bg="#1e1e1e",
            fg="#f0f0f0",
            insertbackground="#f0f0f0",
        )
        trim_spin.grid(row=1, column=2, sticky="w")

        norm_check = ttk.Checkbutton(
            options_frame,
            text="Normalize audio volume",
            variable=self.normalize_enabled,
        )
        norm_check.grid(row=2, column=0, sticky="w", pady=(4, 0))

        # Output folder
        folder_frame = ttk.LabelFrame(self.root, text="Output folder")
        folder_frame.pack(fill="x", padx=pad_x, pady=pad_y)

        folder_row = ttk.Frame(folder_frame)
        folder_row.pack(fill="x", padx=8, pady=4)

        self.folder_label = ttk.Label(folder_row, text="No folder selected")
        self.folder_label.pack(side="left", fill="x", expand=True)

        folder_btn = ttk.Button(folder_row, text="Choose folder", command=self.choose_folder)
        folder_btn.pack(side="right")

        # Progress + status
        progress_frame = ttk.LabelFrame(self.root, text="Progress")
        progress_frame.pack(fill="x", padx=pad_x, pady=pad_y)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            length=400,
            style="Horizontal.TProgressbar",
        )
        self.progress_bar.pack(fill="x", padx=8, pady=4)

        self.status_label = ttk.Label(progress_frame, text="Idle")
        self.status_label.pack(fill="x", padx=8, pady=(0, 4))

        # Download button
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=pad_x, pady=(pad_y, 12))

        self.download_button = ttk.Button(
            button_frame,
            text="Download MP3",
            command=self.on_download_clicked,
        )
        self.download_button.pack(side="right")

        # Drag-and-drop binding
        if TK_DND_AVAILABLE:
            self.setup_drag_and_drop()

    def toggle_batch_mode(self):
        if self.batch_mode.get():
            self.single_url_entry.pack_forget()
            self.batch_text.pack(fill="both", padx=8, pady=4)
        else:
            self.batch_text.pack_forget()
            self.single_url_entry.pack(fill="x", padx=8, pady=4)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)
            self.folder_label.config(text=folder)

    def setup_drag_and_drop(self):
        # Root must be an instance of TkinterDnD.Tk to support DND_FILES
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.handle_drop)

    def handle_drop(self, event):
        data = event.data.strip()

        # Windows: {path1} {path2}; on other OS sometimes different formatting
        paths = self.root.splitlist(data)

        urls = []

        for p in paths:
            p = p.strip()
            if not p:
                continue
            if os.path.isfile(p) and p.lower().endswith(".txt"):
                # Treat file as list of URLs
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                urls.append(line)
                except Exception as e:
                    messagebox.showerror("Error reading file", str(e))
            else:
                # Might be a URL string
                urls.append(p)

        if urls:
            self.batch_mode.set(True)
            self.toggle_batch_mode()
            self.batch_text.delete("1.0", "end")
            self.batch_text.insert("1.0", "\n".join(urls))

    def on_download_clicked(self):
        folder = self.output_folder.get().strip()
        if not folder:
            messagebox.showerror("Error", "Please choose an output folder.")
            return

        if self.batch_mode.get():
            raw_text = self.batch_text.get("1.0", "end").strip()
            urls = [line.strip() for line in raw_text.splitlines() if line.strip()]
        else:
            url = self.single_url_entry.get().strip()
            urls = [url] if url else []

        if not urls:
            messagebox.showerror("Error", "Please enter at least one YouTube link.")
            return

        trim_seconds = self.trim_seconds.get() if self.trim_enabled.get() else None
        normalize_audio = self.normalize_enabled.get()

        self.download_button.config(state="disabled")
        self.progress_bar["value"] = 0
        self.status_label.config(text="Starting download...")

        threading.Thread(
            target=self.run_batch_download,
            args=(urls, folder, trim_seconds, normalize_audio),
            daemon=True,
        ).start()

    def run_batch_download(self, urls, folder, trim_seconds, normalize_audio):
        total = len(urls)
        completed = 0

        def progress_callback(msg):
            self.update_status(msg)

        try:
            for url in urls:
                self.update_status(f"Processing {url}")
                try:
                    download_and_process_audio(
                        url=url,
                        output_folder=folder,
                        trim_seconds=trim_seconds,
                        normalize=normalize_audio,
                        progress_callback=progress_callback,
                    )
                    completed += 1
                except Exception as e:
                    self.update_status(f"Error: {e}")
                    # Continue with next URL

                pct = int((completed / total) * 100)
                self.update_progress(pct)

            self.update_status(f"Completed {completed}/{total} downloads.")
        finally:
            self.download_button.config(state="normal")

    def update_progress(self, value):
        self.progress_bar["value"] = value

    def update_status(self, message):
        self.status_label.config(text=message)


def main():
    # If tkinterdnd2 is available, use its Tk class for DND support
    if TK_DND_AVAILABLE:
        root = TkinterDnD()
    else:
        root = TkinterDnD()
    app = YoutubeMp3DownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
