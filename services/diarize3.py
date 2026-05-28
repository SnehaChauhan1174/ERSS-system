import numpy as np
import torch
from pyannote.audio import Pipeline
import whisper
from pydub import AudioSegment
import os
import soundfile as sf
import scipy.signal as scs

HF_TOKEN = os.getenv("HF_TOKEN")


def load_diarization_pipeline():
    return Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=HF_TOKEN
    )


def convert_mp3_to_wav(inp_path, out_path):
    audio = AudioSegment.from_mp3(inp_path)
    audio.export(out_path, format="wav")


def prepare_audio(wav_path):
    audio_data, sample_rate = sf.read(wav_path, dtype="float32")
    print(f"Original sample rate: {sample_rate}Hz")
    print(f"Original shape:       {audio_data.shape}")
    print(f"Original dtype:       {audio_data.dtype}")

    # Step 1 — Convert to mono
    if audio_data.ndim > 1:
        audio_data = audio_data.mean(axis=1)

    # Step 2 — Resample to 16kHz if needed
    if sample_rate != 16000:
        num_samples = int(len(audio_data) * 16000 / sample_rate)
        audio_data  = scs.resample(audio_data, num_samples)
        sample_rate = 16000
        print(f"Resampled to: {sample_rate}Hz")

    # Step 3 — Ensure float32 numpy array
    audio_data = np.array(audio_data, dtype=np.float32)

    # Step 4 — Convert to tensor (shape: [1, N])
    waveform = torch.from_numpy(audio_data).unsqueeze(0)

    print(f"Waveform shape: {waveform.shape}")   # should be (1, N)
    print(f"Waveform dtype: {waveform.dtype}")   # should be torch.float32

    return {
        "waveform":    waveform,
        "sample_rate": sample_rate
    }


def diarize_audio(pipeline, audio_input):
    """
    Run pyannote diarization.

    pyannote.audio 4.x:  pipeline() returns a DiarizeOutput object.
                         The Annotation lives at output.speaker_diarization.
                         Iterate with: for turn, speaker in output.speaker_diarization

    pyannote.audio 3.x:  pipeline() returns an Annotation directly.
                         Iterate with: for turn, _, speaker in output.itertracks(yield_label=True)

    This function handles both versions automatically.
    """
    output = pipeline(audio_input)

    speaker_segments = []

    print("\nPYANNOTE RESULT\n")

    # ── pyannote 4.x ──────────────────────────────────────
    if hasattr(output, "speaker_diarization"):
        for turn, speaker in output.speaker_diarization:
            speaker_segments.append({
                "speaker": speaker,
                "start":   turn.start,
                "end":     turn.end
            })
            print(f"  [{turn.start:.2f}s - {turn.end:.2f}s]  {speaker}")

    # ── pyannote 3.x ──────────────────────────────────────
    else:
        for turn, _, speaker in output.itertracks(yield_label=True):
            speaker_segments.append({
                "speaker": speaker,
                "start":   turn.start,
                "end":     turn.end
            })
            print(f"  [{turn.start:.2f}s - {turn.end:.2f}s]  {speaker}")

    print(f"\nTotal diarized segments: {len(speaker_segments)}")
    unique = set(s["speaker"] for s in speaker_segments)
    print(f"Unique speakers found:   {len(unique)} → {sorted(unique)}")

    return speaker_segments