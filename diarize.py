import warnings
import torch
from pyannote.audio import Pipeline
import whisper
import ffmpeg
from pydub import AudioSegment
import os
import soundfile as sf
# import faster_whisper import WhisperModel

warnings.filterwarnings("ignore", category=UserWarning, module="pyannote.audio")

HF_TOKEN = os.getenv("HF_TOKEN")

whisper_model = whisper.load_model("base")
# whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    token = HF_TOKEN
)
audio_path = r"D:\InternshipProject\ERSS Project\audio\corona_aircrash.mp3"
output_file = "audio/test_audio.wav"

result = whisper_model.transcribe(audio_path, word_timestamps=True)

print("whisper result")
for seg in result["segments"]:
    start = round(seg["start"],1)
    end = round(seg["end"],1)
    text = seg["text"].strip()
    print(f"[{start}s-{end}s]:{text}")


wave = AudioSegment.from_mp3(audio_path)
wave.export(output_file,format="wav")

# load audio
audio_data, sample_rate = sf.read("audio/test_audio.wav",dtype="float32")

# soundfile returns (time, channels) → convert to (channels, time)
if audio_data.ndim == 1:
    # mono already
    waveform = torch.tensor(audio_data).unsqueeze(0)  # shape: (1, time)
else:
    # stereo → convert to mono
    audio_data = audio_data.mean(axis=1)
    waveform = torch.tensor(audio_data).unsqueeze(0)

# if sample_rate!=16000:
#     resampler=


audio_inp={
    "waveform":waveform,
    "sample_rate":sample_rate
}
diarization = pipeline(audio_inp)

speaker_seg=[]
annotation = diarization.speaker_diarization
print("pyannote result")
for turn,_,speaker in annotation.itertracks(yield_label =True):
    speaker_seg.append({
        "speaker":speaker,
        "start":turn.start,
        "end":turn.end
    })
    print(f"[{turn.start:.1f}s-{turn.end:.1f}] {speaker}")

def find_speaker(word_start,word_end,seg):
    overlaps={}
    for s in seg:
        overlap=max(0,min(word_end,s["end"]) - max(word_start,s["start"]))
        if overlap>0:
            overlaps[s["speaker"]]=overlaps.get(s["speaker"],0)+overlap
    return max(overlaps, key=overlaps.get) if overlaps else "UNKNOWN"

final = []
current_speaker, current_text, current_start = None, [], None

for segment in result["segments"]:
    for word in segment["words"]:
        speaker = find_speaker(word["start"], word["end"], speaker_seg)
        if speaker != current_speaker:
            if current_speaker:
                final.append({
                    "speaker": current_speaker,
                    "start": current_start,
                    "text": " ".join(current_text).strip()
                })
            current_speaker = speaker
            current_text = [word["word"]]
            current_start = word["start"]
        else:
            current_text.append(word["word"])


if current_speaker:
    final.append({
        "speaker": current_speaker,
        "start": current_start,
        "text": " ".join(current_text).strip()
    })

print("both whisper and pyannoe result")
for entry in final:
    print(f"[{entry['start']:.1f}s] {entry['speaker']}: {entry['text']}")

# print(type(diarization))
# print(dir(diarization))

# annotation = diarization.speaker_diarization
# for turn,_,speaker in annotation.itertracks(yield_label =True):
#     print(f"[{turn.start:.1f}s-{turn.end:.1f}] {speaker}")







