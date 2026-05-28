import json
from datetime import datetime
from services import summarizer
from services import diarize
from services import merger3
from pathlib import Path
import whisper

ROOT_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = ROOT_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

def save_output(
        audio_path,
        whis_words,
        merge_seg,
        summary
):

    audio_name = Path(audio_path).stem

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    out_file = (
            OUTPUT_DIR
            / f"{audio_name}_{timestamp}.json"
    )

    output = {
        "metadata": {
            "audio_file": str(audio_path),
            "processed_at": timestamp,
        },

        "summary": summary,

        "diarized_transcript": merge_seg,

        "whisper_words": whis_words,
    }

    with open(
            out_file,
            "w",
            encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"\nOutput saved to: {out_file}")

    return out_file


def main():

    # ─────────────────────────────────────
    # WHISPER
    # ─────────────────────────────────────

    whisper_model = whisper.load_model("base")

    audio_path = (
        r"D:\InternshipProject\ERSS Project"
        r"\audio\pool_save_2mins.mp3"
    )

    wav_path = (
        r"D:\InternshipProject\ERSS Project"
        r"\audio\test_audio8.wav"
    )

    result = whisper_model.transcribe(
        audio_path,
        word_timestamps=True
    )

    # extract WORDS instead of segments
    whis_words = []

    for seg in result["segments"]:

        if "words" not in seg:
            continue

        for word in seg["words"]:

            whis_words.append({
                "word": word["word"].strip(),
                "start": word["start"],
                "end": word["end"]
            })

    print("\nWHISPER WORDS \n")

    for word in whis_words:

        print(
            f"[{word['start']:.2f}s-"
            f"{word['end']:.2f}s] "
            f"{word['word']}"
        )

    # ─────────────────────────────────────
    # PYANNOTE
    # ─────────────────────────────────────

    diarization_pipeline = (
        diarize.load_diarization_pipeline()
    )

    diarize.convert_mp3_to_wav(
        audio_path,
        wav_path
    )

    audio_inp = diarize.prepare_audio(
        wav_path
    )

    pyann_seg = diarize.diarize_audio(
        diarization_pipeline,
        audio_inp
    )

    print("\nPYANNOTE RESULT\n")

    for seg in pyann_seg:

        print(
            f"[{seg['start']:.2f}s-"
            f"{seg['end']:.2f}s] "
            f"{seg['speaker']}"
        )

    # ─────────────────────────────────────
    # MERGE
    # ─────────────────────────────────────

    merge_seg = merger3.merge_whisper_first(
        whis_words,
        pyann_seg
    )

    merge_seg = merger3.combine_same_speaker_segments(
        merge_seg,
        max_gap=2.0
    )

    print("\nFINAL TRANSCRIPT\n")

    for seg in merge_seg:

        print(
            f"[{seg['start']:.2f}s-"
            f"{seg['end']:.2f}s] "
            f"{seg['speaker']}: "
            f"{seg['text']}"
        )

    # ─────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────

    transcript_text = (
        summarizer.format_transcript(
            merge_seg
        )
    )

    summary = summarizer.summarize(
        transcript_text
    )

    print("\nERSS INCIDENT SUMMARY\n")

    print(
        f"SUMMARY:\n"
        f"{summary.get('summary')}\n"
    )

    print(
        f"Incident Type : "
        f"{summary.get('incident_type')}"
    )

    print(
        f"Location      : "
        f"{summary.get('location')}"
    )

    print(
        f"Casualties    : "
        f"{summary.get('casualties')}"
    )

    print(
        f"Priority      : "
        f"{summary.get('priority')}"
    )

    print(
        f"Callers       : "
        f"{summary.get('caller_count')}"
    )

    print(
        f"Response      : "
        f"{summary.get('recommended_response')}"
    )

    print("\nKey Details:")

    for detail in summary.get(
            'key_details',
            []
    ):

        print(f"  - {detail}")

    # ─────────────────────────────────────
    # SAVE OUTPUT
    # ─────────────────────────────────────

    save_output(
        audio_path,
        whis_words,
        merge_seg,
        summary
    )


if __name__ == "__main__":
    main()