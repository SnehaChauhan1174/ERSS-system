import time

AUDIO_PATH = "/content/drive/MyDrive/hindi_audio.mp3"

# ── CELL 4: config ────────────────────────────
MODEL_ID       = "collabora/faster-whisper-medium-hindi"
LANGUAGE       = "hi"
CHUNK_DURATION = 15
OVERLAP        = 2


# ── CELL 5: load model ────────────────────────
print(f"Loading: {MODEL_ID}")
t0    = time.time()
model = WhisperModel(MODEL_ID, device="cuda", compute_type="float16")
print(f"Loaded in {round(time.time()-t0, 2)}s")


# ── CELL 6: load audio ────────────────────────
def load_audio(path, target_sr=16000):
    waveform, sr = torchaudio.load(path)
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    if sr != target_sr:
        resampler = torchaudio.transforms.Resample(
            orig_freq=sr, new_freq=target_sr
        )
        waveform = resampler(waveform)
    return waveform.squeeze().numpy().astype(np.float32), target_sr

audio, sr      = load_audio(AUDIO_PATH)
total_duration = len(audio) / sr
print(f"Duration: {round(total_duration, 1)}s")


CHUNK_DURATION = 15
OVERLAP        = 2
LANGUAGE       = "hi"

# ── prep ──────────────────────────────────────
chunk_samples   = int(CHUNK_DURATION * sr)
overlap_samples = int(OVERLAP * sr)
step_samples    = chunk_samples - overlap_samples

all_segments   = []
latencies      = []
start_sample   = 0
call_start     = time.time()
last_chunk_end = 0.0
previous_text  = "यह एक 112 emergency call है। dispatcher और caller Hindi में बात कर रहे हैं। accident, ambulance, location, road, police."

print(f"\nlive transcription — {MODEL_ID}")


while start_sample < len(audio):
    end_sample     = min(start_sample + chunk_samples, len(audio))
    chunk          = audio[start_sample:end_sample]
    chunk_start    = start_sample / sr
    chunk_end      = end_sample   / sr
    chunk_duration = chunk_end - chunk_start

    if chunk_duration < 2.0:
        start_sample += step_samples
        continue

    # real time pacing
    elapsed = time.time() - call_start
    wait    = chunk_start - elapsed
    if wait > 0:
        time.sleep(wait)

    t_start = time.time()

    # transcribe
    segments, _ = model.transcribe(
        chunk,
        language=LANGUAGE,
        task="transcribe",
        beam_size=5,
        best_of=5,
        temperature=0.0,
        condition_on_previous_text=False,
        no_speech_threshold=0.6,
        vad_filter=True,
        vad_parameters=dict(
            threshold=0.45,
            min_silence_duration_ms=300,
        ),
        repetition_penalty=1.1,
        suppress_blank=True,
        initial_prompt=previous_text,
    )

    # collect segments
    whis_seg = []
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        abs_start = round(chunk_start + seg.start, 2)
        abs_end   = round(chunk_start + seg.end,   2)
        whis_seg.append({
            "start": abs_start,
            "end":   abs_end,
            "text":  text
        })

    # remove overlap with previous chunk
    whis_seg = [
        s for s in whis_seg
        if s["start"] >= last_chunk_end - 2.0   # more tolerance
    ]

    # update context
    if whis_seg:
        previous_text  = " ".join([s["text"] for s in whis_seg])[-200:]
        last_chunk_end = whis_seg[-1]["end"]

    latency = round(time.time() - t_start, 3)
    latencies.append(latency)

    # print live
    if whis_seg:
        for seg in whis_seg:
            print(f"[{seg['start']:.1f}s-{seg['end']:.1f}s] | {latency}s | {seg['text']}")
        all_segments.extend(whis_seg)
    else:
        print(f"[{chunk_start:.1f}s-{chunk_end:.1f}s] | {latency}s | <silence>")

    start_sample += step_samples


def dedup(segments):
    if not segments:
        return segments
    cleaned = [segments[0]]
    for seg in segments[1:]:
        prev        = cleaned[-1]
        overlap     = min(seg["end"], prev["end"]) - max(seg["start"], prev["start"])
        overlap_ratio = overlap / max((seg["end"] - seg["start"]), 0.01)
        if overlap_ratio > 0.5:
            continue
        cleaned.append(seg)
    return cleaned

all_segments = dedup(all_segments)

