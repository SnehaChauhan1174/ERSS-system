import json
from datetime import datetime
from services import summarizer
from services import diarize
from services import merger
from pathlib import Path
import whisper

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def save_output(audio_path, whis_seg, merge_seg, summary):

    # use audio filename as base for output filename
    audio_name = Path(audio_path).stem   # e.g. "detroit_911_1"
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file   = OUTPUT_DIR / f"{audio_name}_{timestamp}.json"

    output = {
        "metadata": {
            "audio_file": str(audio_path),
            "processed_at": timestamp,
        },
        "summary": summary,
        "diarized_transcript": merge_seg,
        "whisper_segments": whis_seg,

    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nOutput saved to: {out_file}")
    return out_file


def main():
    whisper_model = whisper.load_model("base")
    audio_path = r"D:\InternshipProject\ERSS Project\audio\hindi_audio.mp3"
    wav_path   = r"D:\InternshipProject\ERSS Project\audio\test_audio9.wav"


    result   = whisper_model.transcribe(
        audio_path,
        word_timestamps=True,
        language="hi",
        task="transcribe" )

    print(f"Detected language: {result['language']}")


    whis_seg = []
    for seg in result["segments"]:
        whis_seg.append({
            "start": seg["start"],
            "end":   seg["end"],
            "text":  seg["text"].strip()
        })

    print("WHISPER RESULT")
    for seg in whis_seg:
        print(f"[{round(seg['start'],1)}s-{round(seg['end'],1)}s]: {seg['text']}")

    # ── Pyannote ──────────────────────────────────────────
    diarization_pipeline = diarize.load_diarization_pipeline()
    diarize.convert_mp3_to_wav(audio_path, wav_path)
    audio_inp  = diarize.prepare_audio(wav_path)
    pyann_seg  = diarize.diarize_audio(diarization_pipeline, audio_inp)

    print("\nPYANNOTE RESULT (first 5)")
    print(pyann_seg[:5])


    merge_seg = merger.merge_whisper_first(whis_seg, pyann_seg)
    # merge_seg = merger.combine_same_speaker_segments(
    #     merge_seg,
    #     max_gap=2.0
    # )

    print("\nFINAL TRANSCRIPT")
    for seg in merge_seg:
        print(f"[{seg['start']}s-{seg['end']}s] {seg['speaker']}: {seg['text']}")

    transcript_text = summarizer.format_transcript(merge_seg)
    summary = summarizer.summarize(transcript_text)

    print("\nerss incident summary\n")
    print(f"SUMMARY:\n{summary.get('summary')}\n")
    print(f"Incident Type : {summary.get('incident_type')}")
    print(f"Location      : {summary.get('location')}")
    print(f"Casualties    : {summary.get('casualties')}")
    print(f"Priority      : {summary.get('priority')}")
    print(f"Callers       : {summary.get('caller_count')}")
    print(f"Response      : {summary.get('recommended_response')}")
    print(f"\nKey Details:")
    for detail in summary.get('key_details', []):
        print(f"  - {detail}")


    save_output(audio_path, whis_seg, merge_seg, summary)

if __name__ == "__main__":
    main()