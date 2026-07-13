
import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8001"

def process_audio_file(uploaded_file, call_taker_id: str) -> dict:
   
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/transcribe",
            files={"file": (uploaded_file.name, uploaded_file.getvalue(), "audio/wav")},
            data={"call_taker_id": call_taker_id.strip()},
            timeout=300
        )
        if resp.status_code != 200:
            st.error(f"Backend error: {resp.text}")
            return {}
        return resp.json()

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Make sure FastAPI is running on port 8001.")
        return {}
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return {}