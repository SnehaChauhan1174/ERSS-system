import json
import time
from pathlib import Path

ROOT_DIR   = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "output"

def slow_print(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def print_section(title):

    slow_print(f"  {title}")


def main():

    slow_print("   ERSS — EMERGENCY RESPONSE SUPPORT SYSTEM")
    slow_print("   INCIDENT SUMMARY")

    time.sleep(1)

    # load latest output JSON
    files = sorted(OUTPUT_DIR.glob("*.json"))
    latest = files[-1]
    print(f"[ Loading: {latest.name} ]\n")
    time.sleep(0.5)

    with open(latest) as f:
        data = json.load(f)

    summary = data.get("summary", {})

    # ── Incident Summary ──────────────────────────────────
    print_section("INCIDENT SUMMARY")
    print()
    slow_print(f"  {summary.get('summary', 'N/A')}", delay=0.02)

    time.sleep(0.5)
    print()
    slow_print(f"  Incident Type : {summary.get('incident_type')}")
    time.sleep(0.2)
    slow_print(f"  Location      : {summary.get('location')}")
    time.sleep(0.2)
    slow_print(f"  Casualties    : {summary.get('casualties')}")
    time.sleep(0.2)
    slow_print(f"  Priority      : {summary.get('priority')}")
    time.sleep(0.2)
    slow_print(f"  Callers       : {summary.get('caller_count')}")
    time.sleep(0.2)
    slow_print(f"  Response      : {summary.get('recommended_response')}")

    time.sleep(0.3)
    print("\n  Key Details:")
    for detail in summary.get('key_details', []):
        time.sleep(0.2)
        slow_print(f"    -> {detail}")


    slow_print("  Summary Complete")


if __name__ == "__main__":
    main()