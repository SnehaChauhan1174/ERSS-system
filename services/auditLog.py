import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import json
import re

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

AUDIT_PROMPT =  """You are a senior ERSS (Emergency Response Support System) quality auditor.
Evaluate the call taker's performance from this transcript and return ONLY valid JSON.

Score each dimension 1–10. For each, provide:
- score (int 1–10)
- what happened the evidence with your suggestion like " operator's responses are confusing, indicating a need for improvement in communication quality
 basically justifying your rating.
- passed (true/false) passed is true if score >= 7, false if score < 7

Also flag critical failures — any of these = automatic fail regardless of score:
- Did not obtain caller location or any critical information which is necessary to dispatch and to get the situation
- Did not dispatch any emergency unit
- Disconnected an active emergency call
- Gave wrong medical advice or being in very unserious tone

Return this exact structure, nothing else:
{
  
  "call_taker_id": "<take that label from transcripts in which the speaker is starting with salutation like saying 112 or asking about situation>",
  "dimensions": {
    "protocol_adherence":    {"score": 0, "reason": "", "passed": false},
    "information_gathering": {"score": 0, "reason": "", "passed": false},
    "dispatch_accuracy":     {"score": 0, "reason": "", "passed": false},
    "caller_management":     {"score": 0, "reason": "", "passed": false},
    "communication":         {"score": 0, "reason": "", "passed": false},
    "confirmations":         {"score": 0, "reason": "", "passed": false}
  },
  "critical_failures": [],
  "strengths": [],
  "improvement_areas": [],
  "overall_comment": ""
}"""

def audit_call(transcript_text: str, groq_client: Groq) -> dict:
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": AUDIT_PROMPT},
            {"role": "user",   "content": f"Transcript:\n{transcript_text}"}
        ],
        temperature=0.1,
        max_tokens=1500
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    result = json.loads(raw)

    # Compute weighted score
    # weighted = 0.0
    # for dim, cfg in DIMENSIONS.items():
    #     score = result["dimensions"][dim]["score"]
    #     weighted += score * cfg["weight"]
    #
    # result["weighted_score"] = round(weighted, 2)
    # result["grade"] = _grade(weighted, bool(result["critical_failures"]))

    # simple average — no weights
    scores = [data["score"] for data in result["dimensions"].values()]
    avg = sum(scores) / len(scores)

    result["overall_score"] = round(avg, 2)
    return result

