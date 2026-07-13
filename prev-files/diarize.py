import numpy as np
import torch
from pyannote.audio import Pipeline
import whisper
from pydub import AudioSegment
import os
import soundfile as sf
# import faster_whisper import WhisperModel
import scipy.signal as scs

HF_TOKEN = os.getenv("HF_TOKEN")

def load_diarization_pipeline():
    return Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=HF_TOKEN
    )

def convert_mp3_to_wav(inp_path,out_path):
    audio = AudioSegment.from_mp3(inp_path)
    audio.export(out_path,format="wav")


def prepare_audio(wav_path):
    audio_data, sample_rate = sf.read(wav_path, dtype="float32")
    print(f"Original sample rate: {sample_rate}Hz")
    print(f"Original shape: {audio_data.shape}")
    print(f"Original dtype: {audio_data.dtype}")

    # Step 1 — Convert to mono
    if audio_data.ndim > 1:
        audio_data = audio_data.mean(axis=1)

    # Step 2 — Resample to 16kHz
    if sample_rate != 16000:
        num_samples = int(len(audio_data) * 16000 / sample_rate)
        audio_data = scs.resample(audio_data, num_samples)  # returns numpy array
        sample_rate = 16000
        print(f"Resampled to: {sample_rate}Hz")

    # Step 3 — Ensure numpy array before converting to tensor
    audio_data = np.array(audio_data, dtype=np.float32)

    # Step 4 — Convert to tensor correctly
    waveform = torch.from_numpy(audio_data).unsqueeze(0)

    print(f"Waveform shape: {waveform.shape}")            # should be (1, N)
    print(f"Waveform dtype: {waveform.dtype}")            # should be torch.float32

    return {
        "waveform": waveform,
        "sample_rate": sample_rate
    }
    # audio_data, sample_rate = sf.read(
    #     wav_path,
    #     dtype="float32"
    # )
    # print(f"Original sample rate: {sample_rate}Hz")
    #
    # # if audio_data.ndim == 1:
    # #     waveform = torch.tensor(audio_data).unsqueeze(0)
    # #
    # # else:
    # #     audio_data = audio_data.mean(axis=1)
    # #     waveform = torch.tensor(audio_data).unsqueeze(0)
    #
    # if audio_data.ndim>1:
    #     audio_data=audio_data.mean(axis=1)
    # if sample_rate!=16000:
    #     num_sample=int(len(audio_data)*16000/sample_rate)
    #     audio_data=scs.resample(audio_data,num_sample)
    #     sample_rate=16000
    # waveform=torch.tensor(audio_data).unsqueeze(0).float
    #
    # return {
    #     "waveform": waveform,
    #     "sample_rate": sample_rate
    # }


# def diarize_audio(pipeline, audio_input):
#     diarization = pipeline(audio_input)  # ✅ this IS the annotation
#
#     speaker_segments = []
#     for turn, _, speaker in diarization.itertracks(yield_label=True):  # ✅ direct
#         speaker_segments.append({
#             "speaker": speaker,
#             "start":   turn.start,
#             "end":     turn.end
#         })
#     return speaker_segments
def diarize_audio(pipeline, audio_input):

    diarization = pipeline(audio_input)

    annotation = diarization.speaker_diarization

    speaker_segments = []

    print("\nPYANNOTE RESULT\n")

    for turn, _, speaker in annotation.itertracks(yield_label=True):

        speaker_segments.append({
            "speaker": speaker,
            "start": turn.start,
            "end": turn.end
        })

        print(
            f"[{turn.start:.1f}s-{turn.end:.1f}s] {speaker}"
        )

    return speaker_segments








