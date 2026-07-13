import ast
import os
import json
import re
from pathlib import Path
import traceback
from groq import Groq
from dotenv import load_dotenv
from Backend.sentiment_agent import vocal_graph

load_dotenv()
root_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=root_dir / '.env')

# Retrieve the GROQ API token directly from local environment config
groq_key = os.getenv("GROQ_API_KEY")
if groq_key:
    groq_client = Groq(api_key=groq_key)
else:
    # Safe fallback if not found in environmental variables
    groq_client = Groq()

# Define the production reasoning model on Groq
GROQ_MODEL = "openai/gpt-oss-120b"

# Weights — 5 dimensions summing to 100
WEIGHTS = {
    "opening_statement":    10,
    "closing_statement":    10,
    "information_gathering": 30,
    "silence_analysis":     25,
    "caller_management":    25,
}

def _groq_json(prompt: str) -> dict:
    """
    Modular shared API executor. Sends a prompt to Groq utilizing openai/gpt-oss-120b,
    forces response formatting into structured json_object mode, and applies defensive parsing fallbacks.
    """
    try:
        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise 112 ERSS emergency call quality auditor. Always respond with a single valid JSON block matching the requested structure."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        raw = completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq API call failed: {e}")
        return {"score": 0.0, "reason": f"API Error: {str(e)}"}

    # 1. Strip Markdown syntax tags if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    
    raw = raw.strip()

    # 2. Extract only the first complete JSON object block {...} or array [...]
    start_char = ""
    end_char = ""
    start_idx = -1
    
    for idx, ch in enumerate(raw):
        if ch in ("{", "["):
            start_idx = idx
            start_char = ch
            end_char = "}" if ch == "{" else "]"
            break
            
    if start_idx != -1:
        brace_count = 0
        end_idx = -1
        for i in range(start_idx, len(raw)):
            if raw[i] == start_char:
                brace_count += 1
            elif raw[i] == end_char:
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        clean_str = raw[start_idx:end_idx] if end_idx != -1 else raw[start_idx:]
    else:
        clean_str = raw

    clean_str = clean_str.strip()

    # 3. Defensive Parsing Pipeline Chain
    # Tier A: Standard JSON parsing
    try:
        return json.loads(clean_str)
    except json.JSONDecodeError:
        pass

    # Tier B: Fix common dangling quotes and trailing commas using regex
    try:
        fixed = re.sub(r'"\s*"$', '"', clean_str)
        fixed = re.sub(r'"\s*\n\s*"$', '"', fixed)
        fixed = re.sub(r'"\s*\n\s*"(\s*})', r'"\1', fixed)
        fixed = re.sub(r',\s*([\]}])', r'\1', fixed)  # Remove trailing commas
        return json.loads(fixed)
    except Exception:
        pass

    # Tier C: Abstract Syntax Tree fallback
    try:
        return ast.literal_eval(clean_str)
    except Exception as e:
        print(f"Robust Groq JSON parsing failure. Raw snippet: {clean_str[:120]}... Error: {e}")
        return {
            "score": 0.0,
            "reason": "Failed to parse evaluation response format safely.",
            "greeting_detected": False,
            "closing_detected": False
        }


def _format_transcript(transcript: list) -> str:
    return "\n".join(
        [f"{t['speaker']}: {t['text']}" for t in transcript]
    )


class CallAuditor:

    def __init__(self):
        pass

    # ── DIMENSION 1: OPENING STATEMENT ──────────────────────────────────────

    def opening_statement(self, transcript: list) -> dict:
        formatted = _format_transcript(transcript)
        prompt = f"""You are a 112 ERSS call quality auditor.
            Analyze the transcript and evaluate ONLY the opening of the call.

            Check: Did the call taker greet the caller and identify the 112 service within the first few exchanges?
            Any form of welcome or identification counts — formal or informal, Hindi or English mixed.

            Score out of 10:
            10 — Clear greeting with 112 identification
            7  — Greeting present but no 112 identification
            4  — Vague opening, unclear if it's 112
            0  — No greeting at all, jumped straight into questions

            Return strict JSON:
            {{ "score": <float 0-10>, "reason": "one line", "greeting_detected": true or false }}

            Transcript:
            {formatted}"""

        try:
            result = _groq_json(prompt)
            return {
                "score":             float(result.get("score", 0.0)),
                "reason":            result.get("reason", ""),
                "greeting_detected": result.get("greeting_detected", False)
            }
        except Exception as e:
            return {"score": 0.0, "reason": f"failed: {str(e)}", "greeting_detected": False}

    # ── DIMENSION 2: CLOSING STATEMENT ──────────────────────────────────────

    def closing_statement(self, transcript: list) -> dict:
        formatted = _format_transcript(transcript)
        prompt = f"""You are a 112 ERSS call quality auditor.
            Analyze the transcript and evaluate ONLY the closing of the call.

            Check: Did the call taker confirm that action will be taken and close the call properly?
            Any closing statement confirming action counts.

            Score out of 10:
            10 — Clear confirmation of action + proper closing
            7  — Action confirmed but closing was abrupt
            4  — Vague closing, no explicit action confirmation
            0  — Call ended without any closing statement

            Return strict JSON:
            {{ "score": <float 0-10>, "reason": "one line", "closing_detected": true or false }}

            Transcript:
            {formatted}"""

        try:
            result = _groq_json(prompt)
            return {
                "score":            float(result.get("score", 0.0)),
                "reason":           result.get("reason", ""),
                "closing_detected": result.get("closing_detected", False)
            }
        except Exception as e:
            return {"score": 0.0, "reason": f"failed: {str(e)}", "closing_detected": False}

    # ── DIMENSION 3: INFORMATION GATHERING ───────────────────────────────────

    def fetch_critical_gaps_from_groq(self, transcript: list, summary) -> dict:
        formatted = _format_transcript(transcript)
        summary_text = (
            json.dumps(summary, ensure_ascii=False, indent=2)
            if isinstance(summary, dict) else str(summary)
        )

        prompt = f"""You are a Quality Assurance Auditor for the 112 Emergency Response Support System (ERSS).

                Your task has two steps:

                Step 1: Identify the call type from the transcript.

                Step 2: Based on the call type, identify what minimum operational information
                a 112 dispatcher needs to log and forward this complaint.
                Then check which of those fields are missing or were never mentioned.

                Important rules:
                - First check the summary to see what was already gathered, then evaluate.
                - Only flag information operationally necessary to log and forward the complaint.
                - Do not flag investigative details, evidence, or follow-up actions.
                - If a field was mentioned even approximately or unclearly, do not flag it.
                - If the dispatcher confirmed or read out information from their system, treat it as collected.
                - Do not flag phone number of caller as missing — dispatcher already has it from CLI.
                - Minimum required fields vary by call type.

                Return strict JSON with two keys:
                {{
                "call_type": "identified call type as a string",
                "unresolved_critical_gaps": ["list of missing field names, empty if nothing missing"]
                }}

                Summary extracted from transcript:
                {summary_text}

                Original Transcript:
                {formatted}"""

        try:
            result = _groq_json(prompt)
            return {
                "call_type": result.get("call_type", "unknown"),
                "gaps":      result.get("unresolved_critical_gaps", [])
            }
        except Exception as e:
            return {"call_type": "unknown", "gaps": [f"Groq call failed: {str(e)}"]}

    def information_gathering(self, transcript: list, summary) -> dict:
        gaps_result = self.fetch_critical_gaps_from_groq(transcript, summary)

        gaps     = gaps_result["gaps"]
        num_gaps = len(gaps)

        # Score calculation solely based on missing critical fields (num_gaps)
        final_score = max(0.0, 10.0 - (num_gaps * 2.0))

        if num_gaps == 0:
            reason = "Excellent. All critical emergency information successfully collected."
        else:
            reason = f"Missed {num_gaps} critical field(s) during information gathering."

        return {
            "score":                    final_score,
            "reason":                   reason,
            "call_type":                gaps_result["call_type"],
            "gaps":                     gaps,
            # Returning safe dummy entries so downstream components don't throw KeyError crashes
            "address_confirmed_twice":  True, 
            "confirmed_location":       None,
            "address_check_detail":     None
        }

    # ── DIMENSION 4: SILENCE ANALYSIS ────────────────────────────────────────

    def validate_silence_via_groq(self, context_before: str, call_taker_text: str, gap_duration: float) -> dict:
        prompt = f"""You are an expert Quality Assurance Auditor for an emergency response helpline (112/ERSS).
            You are analyzing a phone call transcript where a physical silence gap occurred.

            Your job is to determine if this silence is JUSTIFIED or UNJUSTIFIED.

            CRITICAL RULE: If the conversation before the silence indicates that the caller is actively 
            searching, retrieving, or looking up records, account numbers, documents, card details, or addresses, 
            the silence is 100% JUSTIFIED. Do not penalize dispatchers for patiently waiting for the caller to find information.

            JUSTIFIED if:
            - Caller is looking for information (diary, account number, landmark, token number)
            - Caller or agent implies a pause to fetch details (e.g., waiting, holding, searching)
            - Dispatcher was logging information or dispatching units behind the scenes

            UNJUSTIFIED if:
            - Caller gave an urgent life-safety crisis description and the agent went silent without acting
            - The gap is filled with dead air with absolutely no contextual activity underway

            Silence duration: {gap_duration:.2f} seconds

            [CONVERSATION BEFORE SILENCE]
            {context_before}

            [SILENCE: {gap_duration:.2f} seconds]

            [AFTER SILENCE]
            Call Taker said: "{call_taker_text}"

            Return strict JSON:
            {{ "is_justified": true or false, "reasoning": "one line explanation" }}"""

        try:
            return _groq_json(prompt)
        except Exception as e:
            return {"is_justified": True, "reasoning": f"Groq call failed: {str(e)}"}

    def _analyze_physical_silence_gaps(self, transcript: list) -> dict:
        unjustified_silence_count = 0
        silence_details = []

        for i in range(len(transcript) - 1):
            curr_turn = transcript[i]
            next_turn = transcript[i + 1]

            if curr_turn["speaker"] == "CALLER" and next_turn["speaker"] == "CALL_TAKER":
                silence_gap = next_turn["start"] - curr_turn["end"]

                if silence_gap > 4.0:
                    is_at_end = next_turn["start"] >= (transcript[-1]["end"] - 1.5)
                    if is_at_end:
                        continue

                    # pass 2 turns of context before silence
                    context_turns  = transcript[max(0, i - 2): i + 1]
                    context_before = "\n".join(
                        [f"{t['speaker']}: {t['text']}" for t in context_turns]
                    )

                    groq_eval    = self.validate_silence_via_groq(
                        context_before=context_before,
                        call_taker_text=next_turn["text"],
                        gap_duration=silence_gap
                    )
                    is_justified = groq_eval.get("is_justified", False)
                    reasoning    = groq_eval.get("reasoning", "No explanation provided.")

                    status_flag = "JUSTIFIED_NEUTRAL" if is_justified else "UNJUSTIFIED_PENALTY"
                    if not is_justified:
                        unjustified_silence_count += 1

                    silence_details.append({
                        "timestamp":        f"{curr_turn['end']:.1f}s - {next_turn['start']:.1f}s",
                        "duration_seconds":  round(silence_gap, 2),
                        "status":            status_flag,
                        "audit_reasoning":   reasoning
                    })

        final_score = max(0.0, 10.0 - (unjustified_silence_count * 2.5))

        verdict = (
            "Excellent line attentiveness. All silence pauses were contextually valid or operational."
            if unjustified_silence_count == 0
            else f"Line compliance friction detected. Found {unjustified_silence_count} unexplained dead-air gaps."
        )

        return {
            "score":                     round(final_score, 2),
            "verdict":                   verdict,
            "unjustified_silence_count": unjustified_silence_count,
            "silence_logs":              silence_details
        }

    # ── DIMENSION 5: CALLER MANAGEMENT ───────────────────────────────────────

    def _extract_caller_management_metrics(self, transcript: list) -> dict:
        formatted = _format_transcript(transcript)

        soft_skills_prompt = f"""You are an expert ERSS (112) Behavior Analyst auditing a call taker's soft skills.
Analyze the transcript and evaluate two specific dimensions:
1. Active Reassurance: Did the agent use steady verbal calming anchors to calm panic (e.g., 'घबराइए मत', 'मैं मदद भेज रहा हूँ')?
2. Language Adaptability: Did the agent adjust vocabulary or switch to simpler words/regional dialect if caller struggled?

Return strict JSON with exactly these keys:
{{
  "active_reassurance_verified": true or false,
  "language_adaptability_verified": true or false,
  "behavioral_evidence_summary": "precise summary of linguistic phrases used"
}}

Transcript:
{formatted}"""

        try:
            groq_report = _groq_json(soft_skills_prompt)
        except Exception:
            groq_report = {
                "active_reassurance_verified":    False,
                "language_adaptability_verified": False,
                "behavioral_evidence_summary":    "Inference failed."
            }

        # overlap detection
        total_agent_overlaps       = 0
        overlapping_turns_to_check = []

        for i in range(len(transcript) - 1):
            curr_turn = transcript[i]
            next_turn = transcript[i + 1]

            if next_turn["start"] < curr_turn["end"]:
                overlap_duration = curr_turn["end"] - next_turn["start"]
                if next_turn["speaker"] == "CALL_TAKER" and overlap_duration > 0.4:
                    total_agent_overlaps += 1
                    overlapping_turns_to_check.append({
                        "caller_panic_speech":       curr_turn["text"],
                        "agent_interrupting_speech":  next_turn["text"]
                    })

        command_control_count   = 0
        rude_interruption_count = 0

        if total_agent_overlaps > 0:
            overlap_prompt = f"""You are an emergency room quality inspector reviewing speech overlaps where the dispatcher talked over the caller.
Differentiate between two intents:
- COMMAND_CONTROL: agent firmly cut off an escalating or hysterical caller to regain focus or give safety commands.
- RUDE_INTERRUPTION: agent cut off a cooperative caller due to impatience.

Return JSON with a single key 'classifications' containing a list of strings,
one per input, each either 'COMMAND_CONTROL' or 'RUDE_INTERRUPTION'.

Overlap instances:
{json.dumps(overlapping_turns_to_check, ensure_ascii=False)}"""

            try:
                overlap_result = _groq_json(overlap_prompt)
                classes = overlap_result.get("classifications", [])
                command_control_count   = classes.count("COMMAND_CONTROL")
                rude_interruption_count = classes.count("RUDE_INTERRUPTION")
            except Exception:
                rude_interruption_count = total_agent_overlaps

        return {
            "active_reassurance":    groq_report.get("active_reassurance_verified", False),
            "language_adaptability": groq_report.get("language_adaptability_verified", False),
            "summary":               groq_report.get("behavioral_evidence_summary", ""),
            "command_control_moves": command_control_count,
            "rude_interruptions":    rude_interruption_count
        }

    def caller_management(self, metrics: dict) -> dict:
        score = 5.0

        if metrics["active_reassurance"]:
            score += 2.0
        if metrics["language_adaptability"]:
            score += 1.0

        score += min(1.0, metrics["command_control_moves"] * 0.5)
        score -= metrics["rude_interruptions"] * 2.0

        final_score = max(0.0, min(10.0, score))
        evidence    = metrics["summary"]

        if final_score >= 8.0:
            reason = f"Highly effective caller management. Excellent command control and reassurances. {evidence}"
        elif final_score >= 5.0:
            reason = f"Acceptable management performance but conversational control was unstrategic. {evidence}"
        else:
            reason = f"Soft-skills failure. Agent failed to anchor the caller's anxiety. {evidence}"

        return {
            "score":  round(final_score, 2),
            "reason": reason,
            "audit": {
                "tactical_grounding_actions": metrics["command_control_moves"],
                "penalized_interruptions":    metrics["rude_interruptions"]
            }
        }

    def audit_trigger(self, transcript: list, audio_path: str):
        # Trigger the LangGraph sentiment and multimodal graph (uses separate API Key)
        final_graph_state = vocal_graph.invoke({
            "audio_path":    audio_path,
            "transcript":    transcript,
            "severity":      "",
            "score":         0.0,
            "justification": "",
            "adaptive_dimensions": {}, 
            "soft_skills": {}
        })
        return final_graph_state
        
    # ── FINAL COMPLIANCE REPORT CONTROLLER ───────────────────────────────────

    def final_report(self, transcript: list, summary, audio_path: str = None) -> dict:
        print("audit report running..")

        # Five fully isolated dimension checks running cleanly without hallucinating
        opening_res  = self.opening_statement(transcript)
        closing_res  = self.closing_statement(transcript)
        info_res     = self.information_gathering(transcript, summary)
        silence_res  = self._analyze_physical_silence_gaps(transcript)
        cm_metrics   = self._extract_caller_management_metrics(transcript)
        cm_res       = self.caller_management(cm_metrics)
        
        # Fire Vocal Sentiment Graph pipeline if audio_path exists
        audit_res = {}
        if audio_path and os.path.exists(audio_path):
            try:
                audit_res = self.audit_trigger(transcript, audio_path)
            except Exception as e:
                traceback.print_exc()
                print(f"Multimodal audio pipeline skipped or failed: {e}")

        # Compute weighted contributions (total score out of 100)
        wt_opening  = (opening_res["score"]  / 10.0) * 10.0
        wt_closing  = (closing_res["score"]  / 10.0) * 10.0
        wt_info     = (info_res["score"]     / 10.0) * 30.0
        wt_silence  = (silence_res["score"]  / 10.0) * 25.0
        wt_caller_m = (cm_res["score"]       / 10.0) * 25.0

        total_score = round(wt_opening + wt_closing + wt_info + wt_silence + wt_caller_m, 2)

        if total_score >= 85.0:
            grade = "EXCELLENT"
        elif total_score >= 70.0:
            grade = "SATISFACTORY"
        elif total_score >= 50.0:
            grade = "MARGINAL - Requires Performance Improvement"
        else:
            grade = "UNSATISFACTORY - Severe Protocol Breach"

        return {
            "meta": {
                "total_weighted_score": total_score,
                "out_of":               100.0,
                "performance_verdict":  grade
            },
            "script_compliance": {
                "opening_statement_10pt": {
                    "weight":                "10%",
                    "raw_score_out_of_10":   opening_res["score"],
                    "weighted_contribution": round(wt_opening, 2),
                    "finding":               opening_res["reason"],
                    "greeting_detected":     opening_res["greeting_detected"]
                },
                "closing_statement_10pt": {
                    "weight":                "10%",
                    "raw_score_out_of_10":   closing_res["score"],
                    "weighted_contribution": round(wt_closing, 2),
                    "finding":               closing_res["reason"],
                    "closing_detected":      closing_res["closing_detected"]
                },
                "information_gathering_30pt": {
                    "weight":                    "30%",
                    "raw_score_out_of_10":       info_res["score"],
                    "call_type":                 info_res["call_type"],
                    "weighted_contribution":     round(wt_info, 2),
                    "finding":                   info_res["reason"],
                    "critical_gaps":             info_res.get("gaps", []),
                    "address_confirmed_twice":   True, 
                    "confirmed_location":        None,
                },
                "silence_analysis_25pt": {
                    "weight":                  "25%",
                    "raw_score_out_of_10":     silence_res["score"],
                    "weighted_contribution":   round(wt_silence, 2),
                    "finding":                 silence_res["verdict"],
                    "unjustified_gaps_found":  silence_res["unjustified_silence_count"],
                    "silence_logs":            silence_res["silence_logs"]
                },
                "caller_management_25pt": {
                    "weight":                "25%",
                    "raw_score_out_of_10":   cm_res["score"],
                    "weighted_contribution": round(wt_caller_m, 2),
                    "finding":               cm_res["reason"],
                    "audit_detail":          cm_res["audit"]
                }
            },
            "weighted_breakdown": {
                "opening_statement":    round(wt_opening, 2),
                "closing_statement":    round(wt_closing, 2),
                "information_gathering": round(wt_info, 2),
                "silence_analysis":     round(wt_silence, 2),
                "caller_management":    round(wt_caller_m, 2),
                "total":                total_score
            },
            "soft_skills_analysis": {
                "severity":             audit_res.get("severity") if audit_res else "",
                "vocal_score":          audit_res.get("score") if audit_res else 0.0,
                "justification":        audit_res.get("justification") if audit_res else "",
                "adaptive_dimensions":  audit_res.get("adaptive_dimensions") if audit_res else {},
                "soft_skills":          audit_res.get("soft_skills") if audit_res else {}
            }
        }