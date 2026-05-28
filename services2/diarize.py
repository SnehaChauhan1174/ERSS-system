import json
import time
import argparse
from pathlib import Path

# services2/ is one level inside the project root
ROOT_DIR   = Path(__file__).resolve().parent.parent   # goes up from services2/ to project root
OUTPUT_DIR = ROOT_DIR / "output"

def slow_print(text, delay=0.04):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def main():
    parser = argparse.ArgumentParser(description="ERSS Diarization Viewer")
    parser.add_argument(
        "--file", "-f",
        type=str,
        default=None,
        help="JSON filename inside the output/ folder (e.g. call_001.json). "
             "If omitted, the latest file is used."
    )
    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=0.04,
        help="Per-character print delay in seconds (default: 0.04). "
             "Lower = faster, higher = slower."
    )
    args = parser.parse_args()

    slow_print("  ERSS — EMERGENCY RESPONSE SUPPORT SYSTEM", delay=args.delay)
    slow_print("  CALL DIARIZATION & TRANSCRIPTION", delay=args.delay)

    time.sleep(1)

    # Resolve which file to load
    if args.file:
        target = OUTPUT_DIR / args.file
        if not target.exists():
            print(f"[ERROR] File not found: {target}")
            return
    else:
        files = list(OUTPUT_DIR.glob("*.json"))
        if not files:
            print("[ERROR] No JSON files found in output/")
            return
        target = max(files, key=lambda f: f.stat().st_mtime)  # newest by modified time

    print(f"[ Loading: {target.name} ]\n")
    time.sleep(0.5)

    with open(target) as f:
        data = json.load(f)

    merge_seg = data["diarized_transcript"]

    print("  SPEAKER-SEPARATED TRANSCRIPT")
    time.sleep(0.5)

    for seg in merge_seg:
        line = f"  [{seg['start']:.1f}s - {seg['end']:.1f}s]  {seg['speaker']}:  {seg['text']}"
        slow_print(line, delay=args.delay)
        time.sleep(0.08)

    print()
    slow_print("  Diarization Complete", delay=args.delay)


if __name__ == "__main__":
    main()