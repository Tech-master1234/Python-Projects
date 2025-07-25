import os
import speech_recognition as sr
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from pydub.silence import split_on_silence
from langdetect import detect
import translators as ts
import argparse
import sys

def extract_audio(video_path):
    """Extracts audio from a video file and saves it as a WAV file."""
    try:
        print("Extracting audio...")
        video = VideoFileClip(video_path)
        audio_path = "temp_audio.wav"
        video.audio.write_audiofile(audio_path)
        return audio_path
    except Exception as e:
        print(f"Error extracting audio: {e}")
        sys.exit(1)

def transcribe_audio(audio_path):
    """Transcribes the audio file to text."""
    r = sr.Recognizer()
    sound = AudioSegment.from_wav(audio_path)
    chunks = split_on_silence(sound,
        min_silence_len = 500,
        silence_thresh = sound.dBFS-14,
        keep_silence=500
    )

    full_text = ""
    print("Transcribing audio...")
    for i, audio_chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join("audio_chunks", f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")

        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            try:
                text = r.recognize_google(audio_listened)
                full_text += text + " "
            except sr.UnknownValueError as e:
                print("Error: ", str(e))
            except Exception as e:
                print("Error: ", str(e))

    return full_text

def create_srt(video_path, target_language='en'):
    """Creates subtitles in SRT format."""
    audio_path = extract_audio(video_path)
    if not audio_path:
        return

    if not os.path.exists("audio_chunks"):
        os.makedirs("audio_chunks")

    full_text = transcribe_audio(audio_path)
    if not full_text:
        print("Could not transcribe audio.")
        return

    try:
        source_language = detect(full_text)
        print(f"Detected language: {source_language}")
    except Exception as e:
        print(f"Could not detect language: {e}")
        source_language = "en" # Assume english

    if source_language != target_language:
        print(f"Translating to {target_language}...")
        translated_text = ts.translate_text(full_text, to_language=target_language, from_language=source_language)
    else:
        translated_text = full_text

    subtitle_file_name = os.path.splitext(os.path.basename(video_path))[0] + f".{target_language}.srt"
    with open(subtitle_file_name, "w", encoding="utf-8") as f:
        # Simple SRT generation, assuming one line for the whole text.
        # For more accurate timing, a more sophisticated approach is needed.
        f.write("1\n")
        f.write("00:00:00,000 --> 00:05:00,000\n") # Placeholder timestamp
        f.write(translated_text + "\n")

    print(f"Subtitles saved to {subtitle_file_name}")

    # Cleanup
    os.remove(audio_path)
    for file in os.listdir("audio_chunks"):
        os.remove(os.path.join("audio_chunks", file))
    os.rmdir("audio_chunks")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate subtitles for a video.")
    parser.add_argument("video_path", help="Path to the video file.")
    parser.add_argument("-lang", "--language", help="Target language for subtitles (e.g., 'en', 'es', 'fr').", default="en")
    args = parser.parse_args()

    if not os.path.exists(args.video_path):
        print(f"Error: Video file not found at {args.video_path}")
        sys.exit(1)

    create_srt(args.video_path, args.language)