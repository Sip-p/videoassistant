
from pathlib import Path
import yt_dlp
from pydub import AudioSegment


# =========================================================
# 1. PROJECT PATHS AND FFMPEG CONFIGURATION
# =========================================================

# Project structure:
# videoassistant/
#   ffmpeg/
#     ffmpeg-9.0.2-essentials_build/
#       bin/
#         ffmpeg.exe
#         ffprobe.exe
#   utils/
#     audioprocessor.py

BASE_DIR = Path(__file__).resolve().parents[1]

FFMPEG_DIR = (
    BASE_DIR
    / "ffmpeg"
    / "ffmpeg-9.0.2-essentials_build"
    / "bin"
)

FFMPEG_EXE = FFMPEG_DIR / "ffmpeg.exe"
FFPROBE_EXE = FFMPEG_DIR / "ffprobe.exe"

if not FFMPEG_EXE.exists():
    raise FileNotFoundError(f"FFmpeg not found: {FFMPEG_EXE}")

if not FFPROBE_EXE.exists():
    raise FileNotFoundError(f"FFprobe not found: {FFPROBE_EXE}")

AudioSegment.converter = str(FFMPEG_EXE)
AudioSegment.ffprobe = str(FFPROBE_EXE)

print("FFmpeg configured successfully!")


# =========================================================
# 2. DOWNLOAD DIRECTORY
# =========================================================

DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_DIR = DOWNLOAD_DIR / "chunks"
CHUNK_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# 3. DOWNLOAD YOUTUBE AUDIO
# =========================================================

def download_youtube_audio(url: str) -> str:

    output_path = str(DOWNLOAD_DIR / "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,

        # Pass the correct FFmpeg directory to yt-dlp
        "ffmpeg_location": str(FFMPEG_DIR),

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],

        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(url, download=True)

        raw_filename = Path(ydl.prepare_filename(info))

        filename = raw_filename.with_suffix(".wav")

    if not filename.exists():
        raise FileNotFoundError(
            f"Expected downloaded WAV file not found: {filename}"
        )

    print(f"Audio downloaded: {filename}")

    return str(filename)


# =========================================================
# 4. CONVERT AUDIO/VIDEO TO WAV
# =========================================================

def convert_audio_to_wav(input_path: str) -> str:
    """
    Convert an audio or video file into:
    - WAV format
    - Mono channel
    - 16 kHz sample rate
    """

    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path = input_path.with_name(
        input_path.stem + "_converted.wav"
    )

    audio = AudioSegment.from_file(str(input_path))

    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)

    audio.export(str(output_path), format="wav")

    print(f"Converted audio: {output_path}")

    return str(output_path)


# =========================================================
# 5. SPLIT AUDIO INTO CHUNKS
# =========================================================

def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list[str]:
    """
    Split WAV audio into smaller chunks.

    Default chunk duration: 10 minutes.
    """

    wav_path = Path(wav_path)

    if not wav_path.exists():
        raise FileNotFoundError(f"WAV file not found: {wav_path}")

    if chunk_minutes <= 0:
        raise ValueError("chunk_minutes must be greater than zero")

    audio = AudioSegment.from_wav(str(wav_path))

    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):

        chunk = audio[start:start + chunk_ms]

        chunk_path = CHUNK_DIR / f"{wav_path.stem}_chunk_{i}.wav"

        chunk.export(str(chunk_path), format="wav")

        chunks.append(str(chunk_path))

        print(f"Created chunk {i + 1}: {chunk_path.name}")

    return chunks


# =========================================================
# 6. PROCESS INPUT (YOUTUBE URL OR LOCAL FILE)
# =========================================================

def process_input(source: str) -> list[str]:
    """
    Accept either:
    1. YouTube URL
    2. Local audio/video file

    Returns a list of processed WAV chunk paths.
    """

    source = source.strip()

    if source.startswith(("http://", "https://")):

        print(f"Downloading audio from URL: {source}")

        wav_path = download_youtube_audio(source)

    else:

        print("Detected local file. Converting to WAV...")

        wav_path = convert_audio_to_wav(source)

    print("Chunking audio...")

    chunks = chunk_audio(wav_path)

    print(f"Created {len(chunks)} chunks successfully.")

    return chunks


# =========================================================
# 7. TEST THE AUDIO PROCESSOR
# =========================================================

if __name__ == "__main__":

    youtube_url = "https://youtu.be/Ty8gcCKuwNI?si=8kXaRR3icyWwBjww"

    chunks = process_input(youtube_url)

    print("\nFinal generated chunks:")

    for chunk in chunks:
        print(chunk)
