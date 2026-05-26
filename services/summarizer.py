import json
import re
import ollama

def format_transcript(merge_seg):
    lines=[]
    for seg in merge_seg:
        lines.append(f"[{seg['start']:.1f}s] {seg['speaker']}: {seg['text']}")
    return "\n".join(lines)

def build_prompt(transcript_text):
    return f"""
You are an Emergency Response Support System (ERSS) AI assistant.
Analyze the following emergency call transcript and extract structured information.

TRANSCRIPT:
{transcript_text}

Return ONLY a JSON object with these exact fields, no extra text:
{{
  "summary": "A thorough but concise paragraph (5-7 sentences) covering: what happened, where exactly, how many people involved, current situation on ground, what has already been done, and what is still needed. Write it as if briefing a dispatcher who has zero context.",
  "incident_type": "type of emergency",
  "location": "exact address or landmark",
  "casualties": "number and condition of victims or null",
  "caller_count": "number of distinct callers",
  "key_details": ["important", "facts", "list"],
  "priority": "HIGH or MEDIUM or LOW",
  "recommended_response": "units to dispatch"
}}

Rules:
- summary must be the most detailed field
- summary must include: incident type, location, casualties, ground situation, actions taken
- Only use information explicitly in the transcript
- If information not mentioned, use null
- Return only valid JSON
"""

def summarize(transcript_text):
    prompt = build_prompt(transcript_text)

    try:
        # ── using ollama locally ──────────────────────────
        response = ollama.chat(
            model="llama3.2:1b",
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response["message"]["content"]

    except Exception as e:
        print(f"LLM error: {e}")
        return {"error": str(e)}

    # parse JSON from response
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