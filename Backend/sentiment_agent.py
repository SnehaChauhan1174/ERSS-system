import os
import json
import time
from pathlib import Path
from google.genai.errors import ServerError, APIError
from pydantic import BaseModel,Field
from typing import Optional, Dict, List, Any
from groq import Groq
from dotenv import load_dotenv
from typing import TypedDict, Literal
from google import genai
from google.genai import types
from langgraph.graph import StateGraph, END
import re

load_dotenv()

root_dir = Path(__file__).resolve().parent.parent
env_path = root_dir / '.env'

vocal_key = os.getenv("GEMINI_KEY_VOCAL")
gemini_client = genai.Client(api_key=vocal_key)


class VocalState(TypedDict):
    audio_path:str
    transcript:List[Dict[str,Any]]
    severity:str
    score:float
    justification:str
    adaptive_dimensions:dict
    soft_skills:dict

def get_severity(state:VocalState)->dict:
    system_prompt = """
        You are a 112 ERSS call classifier.
        Your task is NOT to classify incident category.

        Your task is to determine whether the dispatcher needed
        to prioritize life-saving intervention.
        Return:

            ACTIVE_CRISIS:
            - road accident happening now
            - medical emergency
            - fire
            - assault in progress
            - kidnapping
            - suicide threat
            - active violence
            
            NON_ACTIVE_INCIDENT:
            - cyber fraud already completed
            - old complaint
            - follow-up request
            - property dispute
            - administrative complaint
            - information request
            
        Return JSON:
        {
                "severity":"ACTIVE_CRISIS or NON_ACTIVE_INCIDENT",
                "call_type":"short description",
                "reasoning":"one sentence"
        }
    """
    formatted_transcript = format_transcript_segments(state["transcript"])
  
    response = gemini_client.models.generate_content(
        model="gemini-3.5-flash",
        contents=f"Call transcript:\n{formatted_transcript}",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0.0
        )
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except Exception:
     
        result = {"severity": "NON_ACTIVE_INCIDENT", "call_type": "unknown"}

    severity = result.get("severity", "ROUTINE")
    print(f"   --> Triage Verdict: {severity} | Type: {result.get('call_type')}")

    return {"severity": severity}


def format_transcript_segments(segments: List[Dict[str, Any]]) -> str:
    """Converts the JSON segments into a beautiful structured text timeline for LLM tracking."""
    formatted_lines = []
    for seg in segments:
        line = f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['speaker']}: {seg['text']}"
        formatted_lines.append(line)
    return "\n".join(formatted_lines)

def severity_router(state:VocalState)->Literal["adaptive_compliance","rigid_compliance"]:

    if state["severity"]=="ACTIVE_CRISIS":
        print("routing to [adaptive compliance track] (high severity)")
        return "adaptive_compliance"

    else:
        print("routing to [rigid compliance track] (routine severity)")
        return "rigid_compliance"

def upload_audio(audio_path:str):
    print("uploading audio")
    uploaded=gemini_client.files.upload(
        file=audio_path,
        config=types.UploadFileConfig(mime_type="audio/wav")
    )
    waited=0
    while uploaded.state.name=="PROCESSING":
        time.sleep(2)
        waited+=2
        uploaded=gemini_client.files.get(name=uploaded.name)
        if waited>=180:
            raise TimeoutError("gemini processing imed out")
    print("raw audio wave loaded")
    return uploaded

def cleanup_audio(uploaded_file):
    gemini_client.files.delete(name=uploaded_file.name)
    print("temp cloud cleaned up")


class SoftSkills(BaseModel):
    tone: str
    argument: str
    enthusiasm_willingness: str


class VocalAuditSchema(BaseModel):
    score: float = Field(..., description="Score between 0 and 10")
    soft_skills: SoftSkills
    justification: str

def call_gemini_multimodal(uploaded_file,system_prompt:str,transcript:str)->dict:
    """
        executes audio processing so the model can listen to pitch, freq and vloume

    """
    retries = 3
    delay = 4 # Initial wait time in seconds

    for attempt in range(retries):
        try:
            resp = gemini_client.models.generate_content(
                model="gemini-3.5-flash",
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(
                                file_data=types.FileData(
                                    file_uri=uploaded_file.uri,
                                    mime_type="audio/wav"
                                )
                            ),
                            types.Part(text=f"{system_prompt}\n\nCall transcript text for reference:\n{transcript}")
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=VocalAuditSchema,
                    temperature=0.0
                )
            )

            return json.loads(resp.text)
    

        except (ServerError, APIError) as e:
            if "503" in str(e) and attempt < retries - 1:
                print(f" High demand detected. Retrying in {delay}s... (Attempt {attempt + 1}/{retries})")
                time.sleep(delay)
                delay *= 2 # Double the wait time for the next attempt
            else:
                raise e 

def adaptive_compliance_node(state:VocalState)->dict:
    # this checker evaluated the actual vocal behavior, empathy, and tone of how the agent handled the crisis
    # even though we compromoise on strict procedural script like skipping greeting or policy stt
    # but taking an immediate action suring high severity crisis,
    # indicators ofr poor perfomrnace-- an impateint sigh, dismissive tone, or complete panic from the agent

    print("adaptive node running(ACTIVE_CRISIS...")
    trans_text = format_transcript_segments(state["transcript"])


    system_prompt=(
        "You are a specialized Quality Assurance Auditor executing an [Adaptive Behavioral Compliance Check] "
        "for a high-severity emergency 112 call. Your job is to listen to how the operator responds emotionally to the crisis.\n\n"
        
        "THE ADAPTIVE RULE (What we compromise):\n"
        "Because this is a high-severity crisis, do NOT penalize the operator for skipping greeting templates, "
        "dropping official script lines, speaking quickly, or firmly cutting off a screaming caller to gather a location. "
        "This is 'Productive Urgency' and is completely acceptable.\n\n"
        
        "THE NON-NEGOTIABLE BASELINE (What we NEVER compromise):\n"
        "Even under extreme pressure, the underlying behavioral layer must remain professional and supportive. "
        "You must strictly fail and penalize the operator if you detect any of these critical behavioral deficits:\n"
        "1. IGNORANCE/INDIFFERENCE: An audible sigh of frustration, an unresponsive or robotic cold tone, or ignoring an explicit plea for help.\n"
        "2. AGGRESSION: Sounding hostile, matching the caller's anger, arguing, or shouting defensively.\n"
        "3. PANIC: The agent losing emotional control, stuttering out of fear, or screaming back at the caller instead of acting as an anchor.\n\n"


        "SCORING TARGETS:\n"
        "9-10: Perfect control — fast/urgent but collaborative and calm. Caller was anchored.\n"
        "7-8:  Good — controlled delivery, minor conversational friction.\n"
        "5-6:  Acceptable — urgency present but minor emotional mismanagement.\n"
        "1-4:  Failed — clear signs of aggression, complete panic, or emotional indifference.\n\n"
        "Evaluate whether the operator balanced speed with foundational sympathy and control.\n"
        "Return strict JSON:\n"

        "{\n"
        ' "score": <0-10>,\n'
        ' "dimensions": {\n'
        '   "vocal_calmness": <0-10>,\n'
        '   "reassurance": <0-10>,\n'
        '   "conversational_control": <0-10>,\n'
        '   "productive_urgency": <0-10>,\n'
        '   "emotional_stability": <0-10>\n'
        ' },\n' 
        ' "soft_skills":{' 
        '   "tone": "Good or Ok or Poor — Good means empathetic and calming, Ok means neutral/professional, Poor means cold/rude/dismissive",\n'
        '   "argument": "Good or Ok or Poor — Good means zero aggression and stayed composed under pressure, Ok means minor friction, Poor means matched caller aggression or argued",\n'
        '   "enthusiasm_willingness": "Good or Ok or Poor — Good means fully engaged and proactive, Ok means did the job without energy, Poor means showed signs of ignorance or indifference"\n'
        '},\n'
        ' "justification": "detailed explanation"\n'
        "}"
        # "Return strict JSON:\n"
        # "{\n"
        # "  \"score\": <float 0-10>,\n"
        # "  \"productive_urgency_detected\": <true/false>,\n"
        # "  \"critical_deficit_detected\": <true/false>,\n"
        # "  \"deficit_type\": \"IGNORANCE or AGGRESSION or PANIC or none\",\n"
        # "  \"justification\": \"comprehensive audit commentary assessing script deviations vs underlying behavioral control\"\n"
        # "}"
    )
    uploaded=upload_audio(state["audio_path"])
    try:
        result=call_gemini_multimodal(uploaded,system_prompt,trans_text)
    except Exception as e:
        print(f"Error in compliance node: {e}")
        # Provide a safe fallback dictionary if the call fails
        result = {
            "score": 5.0,
            "dimensions": {},
            "soft_skills": {"tone": "Ok", "argument": "Ok", "enthusiasm_willingness": "Ok"},
            "justification": "Failed to generate audit."
        }
    finally:
        cleanup_audio(uploaded)

    print(f"   --> Adaptive Score: {result.get('score')}/10")

    return {
        "score": float(result.get("score", 5.0)),
        "justification": result.get("justification", ""),
        "adaptive_dimensions":result.get("dimensions", {}),
        "soft_skills":         result.get("soft_skills", {
            "tone":                   "Ok",
            "argument":               "Ok",
            "enthusiasm_willingness": "Ok"
        })
    }


def rigid_compliance_node(state:VocalState)->dict:
    print("rigid compliance checker running")
    system_prompt = (
        "You are a Senior Quality Assurance Auditor conducting a RIGID VOCAL BEHAVIOR REVIEW "
        "for a NON-ACTIVE administrative 112 emergency helpline call.\n\n"

        "CONTEXT:\n"
        "This is not a life-threatening crisis. The caller is reporting a completed incident "
        "or following up on a prior complaint. Because there is no active emergency, "
        "the dispatcher has no excuse for impatience or rushed vocal behavior. "
        "Evaluate ONLY what you hear in the voice — tone, pacing, patience, and emotional response.\n\n"

        "DO NOT evaluate greeting scripts or closing statements — those are assessed separately.\n\n"

        "LISTEN AND EVALUATE THESE THREE VOCAL DIMENSIONS:\n\n"

        "1. PATIENCE AND LISTENING QUALITY\n"
        "   Did the dispatcher's voice sound patient and engaged throughout?\n"
        "   Reward: steady measured pacing, no audible rushing, calm tone even when caller repeats.\n"
        "   Penalize: audibly faster speech when caller is slow, sighing, clipped short responses "
        "that signal impatience.\n"
        "   Note: a gentle vocal redirect when caller goes off-topic is acceptable.\n\n"

        "2. ACKNOWLEDGMENT TONE\n"
        "   When the caller expressed frustration, did the dispatcher's voice soften or warm up?\n"
        "   Reward: vocal warmth, slower pacing, empathetic tone shifts when caller is distressed.\n"
        "   Penalize: monotone robotic delivery that ignores caller's emotional state, "
        "continuing at the same mechanical pace regardless of what the caller expressed.\n\n"

        "3. COMMUNICATION CLARITY\n"
        "   Was the dispatcher's speech clear, measured, and easy to follow?\n"
        "   Reward: consistent clear articulation, appropriate pauses.\n"
        "   Penalize: mumbling, speaking too fast for a non-urgent call, "
        "or giving instructions in a clipped dismissive tone.\n\n"

        "SCORING GUIDE (out of 10):\n"
        "9-10: Warm, patient, and clear throughout. Vocal behavior matches the non-urgent context.\n"
        "7-8:  Mostly professional, minor vocal impatience in one area.\n"
        "5-6:  Noticeable rushed or cold vocal delivery in two or more areas.\n"
        "3-4:  Consistently impatient or robotic tone, caller frustration ignored vocally.\n"
        "1-2:  Dismissive, cold, or audibly hostile vocal behavior throughout.\n\n"

        "Return strict JSON:\n"
        "{\n"
        "  \"score\": <float 0-10>,\n"
        "  \"dimensions\": {\n"
        "    \"patience_and_listening\": <0-10>,\n"
        "    \"acknowledgment_tone\": <0-10>,\n"
        "    \"communication_clarity\": <0-10>\n"
        "  },\n"
        "  \"soft_skills\": {\n"
        "    \"tone\": \"Good or Ok or Poor — Good means warm and empathetic throughout, Ok means neutral/professional, Poor means cold/robotic/dismissive\",\n"
        "    \"argument\": \"Good or Ok or Poor — Good means stayed fully composed and never challenged the caller, Ok means minor impatience, Poor means sounded frustrated or dismissive toward the caller's complaint\",\n"
        "    \"enthusiasm_willingness\": \"Good or Ok or Poor — Good means genuinely engaged and helpful, Ok means adequate but flat, Poor means showed visible disinterest or ignored caller frustration\"\n"
        "  },\n"
        "  \"justification\": \"detailed breakdown citing specific vocal moments heard in the audio\"\n"
        "}"
    )
    trans_text = format_transcript_segments(state["transcript"])
    uploaded = upload_audio(state["audio_path"])
    try:
        result = call_gemini_multimodal(uploaded, system_prompt, trans_text)
    except Exception as e:
        print(f"Error in compliance node: {e}")
        # Provide a safe fallback dictionary if the call fails
        result = {
            "score": 5.0,
            "dimensions": {},
            "soft_skills": {"tone": "Ok", "argument": "Ok", "enthusiasm_willingness": "Ok"},
            "justification": "Failed to generate audit."
        }
    finally:
        cleanup_audio(uploaded)

    print(f"rigid compliance result: {result.get('score')}/10")
    return {
        "score":         float(result.get("score", 5.0)),
        "justification": result.get("justification", ""),
        "adaptive_dimensions": result.get("dimensions", {}),
        "soft_skills":         result.get("soft_skills", {
            "tone":                   "Ok",
            "argument":               "Ok",
            "enthusiasm_willingness": "Ok"
        })
    }

graph=StateGraph(VocalState)

graph.add_node("get_severity",get_severity)
graph.add_node("adaptive_compliance",adaptive_compliance_node)
graph.add_node("rigid_compliance",rigid_compliance_node)
graph.set_entry_point("get_severity")

graph.add_conditional_edges(
    "get_severity",
    severity_router,
    {
        "adaptive_compliance": "adaptive_compliance",
        "rigid_compliance":    "rigid_compliance"
    }
)
graph.add_edge("adaptive_compliance",END)
graph.add_edge("rigid_compliance",END)

vocal_graph=graph.compile()




