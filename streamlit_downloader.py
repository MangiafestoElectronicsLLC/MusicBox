import os
import tempfile
import subprocess

import streamlit as st
import yt_dlp


def run_ffmpeg(input_path, output_path, trim_seconds=None, normalize=False):
    cmd = ["ffmpeg", "-y", "-i", input_path]

    if trim_seconds is not None:
        cmd += ["-t", str(trim_seconds)]

    if normalize:
        cmd += ["-af", "loudnorm"]

    cmd.append(output_path)

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def download_and_process_audio(
    url,
    output_folder,
    trim_seconds=None,
    normalize=False,
):
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
        processed_path = os.path.join(output_folder, f"{title}_processed.mp3")
        run_ffmpeg(
            input_path=mp3_path,
            output_path=processed_path,
            trim_seconds=trim_seconds,
            normalize=normalize,
        )
        os.replace(processed_path, mp3_path)

    return mp3_path, title


def main():
    st.set_page_config(page_title="MusicBox - YouTube to MP3", page_icon="🎵", layout="centered")

    st.title("MusicBox - YouTube to MP3")
    st.caption("Use only with your own or copyright‑free content.")

    st.markdown("Paste one or more YouTube links (one per line):")
    urls_text = st.text_area(
        "YouTube URLs",
        height=150,
        placeholder="https://youtube.com/...\nhttps://youtube.com/...",
    )

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        trim_enabled = st.checkbox("Trim intro", value=True)
    with col2:
        trim_seconds = st.number_input(
            "Trim length (seconds)",
            min_value=5,
            max_value=120,
            value=35,
            step=1,
        )
    with col3:
        normalize_enabled = st.checkbox("Normalize volume", value=True)

    urls = [u.strip() for u in urls_text.splitlines() if u.strip()]

    if st.button("Download MP3s"):
        if not urls:
            st.error("Please enter at least one YouTube URL.")
            return

        with st.spinner("Downloading and processing..."):
            results = []
            with tempfile.TemporaryDirectory() as tmpdir:
                total = len(urls)
                progress = st.progress(0)
                for i, url in enumerate(urls, start=1):
                    try:
                        mp3_path, title = download_and_process_audio(
                            url=url,
                            output_folder=tmpdir,
                            trim_seconds=trim_seconds if trim_enabled else None,
                            normalize=normalize_enabled,
                        )
                        results.append((title, mp3_path))
                    except Exception as e:
                        st.warning(f"Error for {url}: {e}")
                    progress.progress(i / total)

                if not results:
                    st.error("No files were successfully downloaded.")
                    return

                st.success(f"Completed {len(results)} download(s).")

                for title, mp3_path in results:
                    with open(mp3_path, "rb") as f:
                        st.download_button(
                            label=f"Download {title}.mp3",
                            data=f,
                            file_name=f"{title}.mp3",
                            mime="audio/mpeg",
                        )


if __name__ == "__main__":
    main()
