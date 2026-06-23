
# ERSS Call Audit System

## Overview

The **ERSS Call Audit System** is an AI-powered quality assessment framework designed for emergency response calls.

The system automatically processes recorded emergency conversations, generates structured transcripts, identifies speaker roles, extracts critical operational information, and evaluates dispatcher performance against predefined ERSS quality standards.

---

## Objectives

- Automatic Hindi call transcription
- Speaker diarization
- Role identification (Caller / Call Taker)
- Information extraction
- Incident summarization
- Automated dispatcher auditing
- Performance scoring and reporting

---

## System Pipeline

```text
Audio Call
    ↓
Audio Preprocessing
    ↓
Faster-Whisper Large-v2 Hindi ASR
    ↓
Pyannote Speaker Diarization
    ↓
Transcript-Diarization Merge
    ↓
Role Identification Engine
    ↓
Entity & Information Extraction
    ↓
Incident Summary Generation
    ↓
Audit Engine
    ↓
Quality Report
````

---

## Technologies Used

### Speech Processing

* Faster-Whisper Large-v2 (Hindi ASR)
* Pyannote Audio
* TorchAudio

### Natural Language Processing (NLP)

* Sentence Transformers
* Groq LLM API
* Llama 3.3 70B

### Backend

* Python
* JSON-based reporting

---

## Audit Dimensions

### Protocol Adherence

Measures whether the dispatcher followed the required ERSS call-handling procedures.

### Information Gathering

Evaluates whether critical dispatch-related information was collected during the call.

### Communication Quality

Assesses clarity, professionalism, tone, and conversational structure.

### Caller Management

Evaluates reassurance, panic handling, empathy, and call control.

### Silence Analysis

Detects prolonged and unexplained periods of silence during the conversation.

---

## Current Features

* Hindi speech transcription
* Speaker diarization
* Speaker role identification
* Structured information extraction
* Incident summarization
* Automated audit scoring
* JSON report generation

---

## Future Work

* Sentiment analysis
* Audio-based stress detection
* Multi-call agent performance dashboard
* Real-time audit assistance
* Fine-tuned ERSS evaluation models

---

## Project Status

*  Module 1: Speech Processing
*  Module 2: Audit Engine (In Progress)
*  Module 3: Dashboard/UI (In Development)

---

## Author

**Sneha Chauhan**
AIML Student
ERSS Call Quality Audit Project

```
```
