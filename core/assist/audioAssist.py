import os
import wave

import miniaudio

from core.assist.paths import AUDIO_DIR


def convert_all_progress():
    if not os.path.isdir(AUDIO_DIR):
        return

    mp3_files = sorted(
        f for f in os.listdir(AUDIO_DIR) if f.lower().endswith(".mp3")
    )
    total = len(mp3_files)

    for i, filename in enumerate(mp3_files, 1):
        mp3_path = os.path.join(AUDIO_DIR, filename)
        wav_path = os.path.join(AUDIO_DIR, filename[:-4] + ".wav")

        if os.path.exists(wav_path):
            os.remove(mp3_path)
            yield (i, total, f"skipping {filename}")
            continue

        yield (i, total, f"converting {filename}")
        audio = miniaudio.decode_file(mp3_path)
        with wave.open(wav_path, "w") as wf:
            wf.setnchannels(audio.nchannels)
            wf.setsampwidth(audio.sample_width)
            wf.setframerate(audio.sample_rate)
            wf.writeframes(audio.samples.tobytes())
        os.remove(mp3_path)
        yield (i, total, f"done {filename}")


def convert_all():
    list(convert_all_progress())
