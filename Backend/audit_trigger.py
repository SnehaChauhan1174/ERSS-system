import os
import json
from pathlib import Path
# FIXED: Pointing cleanly to the vocal_agent module
from sentiment_agent import vocal_graph, execute_agent_audit

def run_pipeline_trigger(json_file_path: str):
    path = Path(json_file_path)
    if not path.exists():
        raise FileNotFoundError(f"Missing pipeline JSON file at: {json_file_path}")

    print(f"Loading pre-processed JSON: {path.name}")

    with open(path, "r", encoding="utf-8") as f:
        pipeline_data = json.load(f)

    # Invoke your agent graph cleanly
    final_graph_state = vocal_graph.invoke({
        "audio_path":    pipeline_data.get("audio_path", "D:/InternshipProject/ERSS Project/Backend/audio/hindi_audio.mp3"),
        "transcript":    pipeline_data.get("transcript", []),
        "summary":       pipeline_data.get("summary", ""),
        "severity":      "",
        "score":         0.0,
        "justification": "",
        "adaptive_dimensions": {} # FIXED: Spelling aligned perfectly with VocalState definition
    })


    print(f"FINAL AUDIT COMPLETED FOR CALL: {pipeline_data.get('call_id', 'Unknown')}")

    print(f"Calculated Severity  : {final_graph_state['severity']}")
    print(f"Assigned Final Score : {final_graph_state['score']} / 10")

    # Check if dimensions exist (if adaptive track ran)
    if final_graph_state.get('adaptive_dimensions'):
        print("\n Dimension Breakdowns:")
        for metric, val in final_graph_state['adaptive_dimensions'].items():
            print(f"   - {metric.replace('_', ' ').title()}: {val}/10")

    print(f"\n Audit Justification:\n{final_graph_state['justification']}")


if __name__ == "__main__":
    # Ensure your mock input JSON exists or create a placeholder for test stability
    mock_file = "call_0623.json"
    if not os.path.exists(mock_file):
        sample_data = {
            "call_id": "call_0611",
            "audio_path": "D:/InternshipProject/ERSS Project/Backend/audio/real_audio1.wav",
            "summary": "जलमहल रोड, जयपुर पर एक गंभीर सड़क दुर्घटना हुई है जिसमें कई लोग घायल हैं और बाइक में आग लग गई है। ऑपरेटर ने स्थिति की गंभीरता को समझते हुए तुरंत शांत रहकर पूरी लोकेशन नोट की और एम्बुलेंस को रवाना किया।",
            "transcript": [
                {"speaker": "Caller", "start": 0.0, "end": 4.0, "text": "Help me, my kitchen is covered in thick black smoke!"},
                {"speaker": "Agent", "start": 4.5, "end": 10.0, "text": "(sighs firmly) Fine. Give me your exact home street address right now."}
            ]
        }
        with open(mock_file, "w") as f:
            json.dump(sample_data, f, indent=4)

    run_pipeline_trigger(mock_file)