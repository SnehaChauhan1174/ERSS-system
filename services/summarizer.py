import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
import os
import json
import re

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

SYSTEM_PROMPT = """You are an ERSS (Emergency Response Support System) AI assistant.
Your job is to analyze emergency call transcripts and extract structured information.
Always respond with only valid JSON, no extra text, no markdown backticks."""

def format_transcript(merge_seg):
    lines = []
    for seg in merge_seg:
        lines.append(f"[{seg['start']:.1f}s] {seg['speaker']}: {seg['text']}")
    return "\n".join(lines)


def build_prompt(transcript_text):
    return f"""Analyze this emergency call transcript and extract information:

TRANSCRIPT:
{transcript_text}

Return ONLY this JSON structure with real values from the transcript:
{{
  "summary": "5-7 sentence paragraph covering what happened, exact location, casualties, ground situation, actions taken, what is still needed",
  "incident_type": "type of emergency",
  "location": "exact address or landmark mentioned",
  "casualties": "number and condition of victims or null",
  "caller_count": "number of distinct callers",
  "key_details": ["fact1", "fact2", "fact3"],
  "priority": "HIGH or MEDIUM or LOW",
  "recommended_response": "units to dispatch"
}}"""

def summarize(transcript_text):
    prompt = build_prompt(transcript_text)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this emergency call transcript:\n\n{prompt}"}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        raw = response.choices[0].message.content

        print("\n── RAW LLM RESPONSE ──")
        print(raw)


        try:
            return json.loads(raw)
        except:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
            return {"raw_response": raw}

    except Exception as e:
        print(f"LLM error: {e}")
        return {"error": str(e)}