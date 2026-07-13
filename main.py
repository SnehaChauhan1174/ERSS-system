import json
import os
import time
import traceback
import requests
from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from typing import List,Dict,Any
from pydantic import BaseModel
from call_auditor import CallAuditor
from dotenv import load_dotenv
from groq import Groq
from Backend.sentiment_agent import vocal_graph
from pathlib import Path
# from audit_engine import CallAuditor
from datetime import datetime
from fastapi import BackgroundTasks

audit_output_dir=Path("storage/audits")
transcript_dir=Path("storage/transcripts")
audio_dir=Path("storage/audio")
counter_file=Path("storage/call_counter.txt")
if not counter_file.exists():
    counter_file.write_text("0")

transcript_dir.mkdir(parents=True,exist_ok=True)
audit_output_dir.mkdir(parents=True,exist_ok=True)

load_dotenv()

app=FastAPI(title="112 ERSS")

COLAB_URL = "https://eliminate-silt-liability.ngrok-free.dev"

auditor=CallAuditor()

class TranscribeReq(BaseModel):
    audio_path:str

class SingleAuditRequest(BaseModel):
    call_id:str

class AudioInputRequest(BaseModel):
    call_id:str
    audio_path:str
    transcript:List[Dict[str, Any]]


# function to generate call id
def generate_call_id():
    curr=int(counter_file.read_text())
    curr+=1
    counter_file.write_text(str(curr))
    today=datetime.now().strftime("%d-%m-%Y")
    return f"CALL_{today}_{curr:04d}"

def run_audit_task(call_id:str):
    call_file = transcript_dir / f"{call_id}.json"
    try:
        with open(call_file, "r", encoding="utf-8") as f:
            call_data = json.load(f)

        print(f"[audit bg] running audit for {call_id}")
        audit_report = auditor.final_report(
            transcript=call_data["transcript"],
            summary=call_data["summary"],
            audio_path=call_data["audio_path"]
        )
        report_data = {
            "call_id": call_id,
            "call_taker_id": call_data.get("call_taker_id", "CT-Unknown"),
            "audit_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "audio_file":    call_data.get("audio_file", ""),
            "audit_report": audit_report,
        }
        report_path = audit_output_dir / f"{call_id}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)
        print(f"[audit bg] saved report to {report_path}")
    except Exception as e:
        print(f"[audit bg] FAILED for {call_id}: {e}")
        traceback.print_exc()



@app.post("/api/transcribe",summary="module 1- audio transcription & summary")
async def local_transcribe( background_tasks: BackgroundTasks, file:UploadFile=File(...),
                           call_taker_id:str=Form(default="CT-Unknown")):
    call_id=generate_call_id()

    # save audio locally first
    audio_save_path=audio_dir/file.filename
    audio_dir.mkdir(parents=True, exist_ok=True)
    file_bytes=await file.read()
    with open(audio_save_path,"wb") as af:
        af.write(file_bytes)

    colab_endpoint=f"{COLAB_URL}/transcribe_and_summarize"
    try:
        
        files={
            "file":(file.filename,file_bytes,file.content_type)
        }
        resp=requests.post(colab_endpoint,files=files,timeout=300)
        if resp.status_code!=200:
            raise HTTPException(status_code=resp.status_code,detail=resp.text)
        
        result = resp.json()
        transcript=result["transcript"]
        summary=result["summary"]

        complete_call_data={
            "call_id":call_id,
            "call_taker_id":call_taker_id,
            "audio_file":file.filename,
            "audio_path":str(audio_save_path),
            "created_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "transcript": transcript,
            "summary": summary,
        }

        save_path=transcript_dir/f"{call_id}.json"
        print("Saving file to:", save_path.resolve())
        with open(save_path,"w",encoding="utf-8") as f:
            json.dump(complete_call_data,f,indent=4,ensure_ascii=False)
        print("Saved successfully.")

        background_tasks.add_task(run_audit_task,call_id)
        return{
            "status": "success",
            "call_id": call_id,
            "call_taker_id": call_taker_id,
            "transcript":transcript,
            "summary": summary,
        }
    except Exception as e:
        raise HTTPException(status_code=503,detail=f"failed to reach colab: {str(e)}")

@app.post("/api/audit")
async def audit_run(call_id:str, file:UploadFile=File(...)):
    call_file = transcript_dir / f"{call_id}.json"
    try:
        with open(call_file, "r", encoding="utf-8") as f:
            call_data = json.load(f)

        print(f"[audit bg] running audit for {call_id}")
        audit_report = auditor.final_report(
            transcript=call_data["transcript"],
            summary=call_data["summary"],
            audio_path=call_data["audio_path"]
        )
        report_data = {
            "call_id": call_id,
            "call_taker_id": call_data.get("call_taker_id", "CT-Unknown"),
            "audit_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "audio_file":    call_data.get("audio_file", ""),
            "audit_report": audit_report,
        }
        report_path = audit_output_dir / f"{call_id}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)
        print(f"[audit bg] saved report to {report_path}")
    except Exception as e:
        print(f"[audit bg] FAILED for {call_id}: {e}")
        traceback.print_exc()
