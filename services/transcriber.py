import whisper

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    return model.transcribe(audio=audio_path)

def load_segments(whisper_result):
    segm = []
    for seg in whisper_result["segments"]:
        start    = seg["start"]
        end      = seg["end"]
        seg_text = seg["text"]
        segm.append({
            "start": start,
            "end":   end,
            "text":  seg_text
        })
    return segm