## issue come in setup of pyannote.audio file
  - pyannote.audio uses TorchCodec as its primary library for audio decoding and I/O. The pipeline heavily relies on it to efficiently handle audio files via FFmpeg
  - Because pyannote.audio relies on this specific dependency, changes in the underlying PyTorch libraries can sometimes lead to segmentation faults or library incompatibilities
  - [ Your Audio File ] 
       │
       ▼
┌───────────────┐
│    FFmpeg     │  ◄── (Demuxes, decompresses, and resamples to 16kHz mono)
└───────┬───────┘
       │ (C++ Pointer)
       ▼
┌───────────────┐
│  TorchCodec   │  ◄── (Wraps the raw bits into a PyTorch-friendly structure)
└───────┬───────┘
       │ 
       ▼
[ PyTorch Tensor ] ──► Passed into Pyannote AI Pipeline
```
RuntimeError(RuntimeError: Could not load libtorchcodec. Likely causes: 1. FFmpeg is not properly installed in your environment. We support versions 4, 5, 6, 7, and 8, and we attempt to load libtorchcodec for each of those versions. Errors for versions not installed on your system are expected; only the error for your installed FFmpeg version is relevant. On Windows, ensure you've installed the "full-shared" version which ships DLLs. 2. The PyTorch version (2.12.0+cpu) is not compatible with this version of TorchCodec. Refer to the version compatibility table: https://github.com/pytorch/torchcodec?tab=readme-ov-file#installing-torchcodec. 3. Another runtime dependency; see exceptions below. The following exceptions were raised as we tried to load libtorchcodec: [start of libtorchcodec loading traceback]FFmpeg version 8:Traceback (most recent call last): File "D:\InternshipProject\ERSS Project\.venv\Lib\site-packages\torch\_ops.py", line 1509, in load_library ctypes.CDLL(path) File "C:\Users\sneha\AppData\Local\Programs\Python\Python312\Lib\ctypes\__init__.py", line 379, in __init__ self._handle = _dlopen(self._name, mode) ^^^^^^^^^^^^^^^^^^^^^^^^^FileNotFoundError: Could not find module 'D:\InternshipProject\ERSS Project\.venv\Lib\site-
```
### About the error :
Since you are running Windows, torchcodec cycles through versions 4 to 8 looking for a matching, installed FFmpeg library. Because it cannot find any, it throws a FileNotFoundError for the .dll hooks.

### How i solved it :
Solution 1: Bypass TorchCodec entirely i can bypass torchaudio.load's attempt to use TorchCodec by switching the backend module or using a traditional backend like soundfile.Option A: Tell Torchaudio to use the soundfile backend
But in this solution i get to know Torchaudio also used Torchcodec internally, and that;s why same error.
Now next option i got is to use soundfile like this:
```
wave = AudioSegment.from_mp3(audio_path)
wave.export(output_file,format="wav")

# load audio
audio_data, sample_rate = sf.read("audio/test_audio.wav",dtype="float32")
```
Installs:
```
pip install openai-whisper
pip install ffmpeg-python
pip install pyannote.audio
pip install torchcodec
pip install soundfile
pip install pydub

```
### what was the issue with torchcodec:
on windows there are strict path handling, so when there is a library path issue like happened in case of torchcodec with pytorch, then it didnt handle it which is not the case with linux and macOS
as they have this builtin package manager which handle such path and library issues.
on windows we need to mannually configure
The strict version matching table applies to everyone. But while a Linux or Mac user can usually just type ```pip install torchcodec``` and have it work instantly, a Windows user has to manually configure their operating system's architecture just to get it to boot.



### 28th may
for a screen recording task to refine the output, i have tested on some other versions of merger file( i thought merger logicmight be boken)
so from chatgpt idea, 
- segmenting word wise and then combining words on basis of pyannote segments
- but as whisper segments rae still accurate than pyannote segmnets due to less accurate speake labeling thats why the statemnets
  got broke in mid and also separate got merge incorrectly.
  ```
  "diarized_transcript": [
    {
      "speaker": "SPEAKER_00",
      "start": 0.5800000000000014,
      "end": 2.02,
      "text": "I wrote 911, where's your"
    },
    {
      "speaker": "SPEAKER_01",
      "start": 2.02,
      "end": 14.52,
      "text": "emergency? Yeah, this is from I had a little girl that fell on the ball and I think she's unconscious right now. Okay, what address? It's 8 -826 East Florida Avenue."
    },
  ```
  this output was using the segment by word logic which yu cans ee how the ``` emergency``` of pevious seg,ent got merged with next segment
  as pyannote changed label mid way
  thats why keeping whisper first logic is really more viable as we have some cedibility from whsiper first rather than pyannote first.

 ## Insight from this:
 - going with whisper first logic only
 - keep diarization same, can see in diarize.py pipeline ``` diarization pipeline -> mp3 to wav -> prepare_audio(resampling, etc) -> main processing```
      - output observation from using pyannote:
          - works bad on noisy audio
          - can label inconsistently like first speaker as 03 or sec as 01 ( we can correc this by a post preocessing in chain to correct the labels):
               ```
               {
                  "start": 0.6200000000000006,
                  "end": 2.3,
                  "speaker": "SPEAKER_01",
                  "text": "I wrote 911, where's your emergency?"
                },
                {
                  "start": 2.98,
                  "end": 9.24,
                  "speaker": "SPEAKER_03",
                  "text": "Yeah, this is from I had a little girl that fell on the ball and I think she's unconscious"
                },
                {
                  "start": 9.24,
                  "end": 9.74,
                  "speaker": "SPEAKER_03",
                  "text": "right now."
                },
               ```
            - can spearate midway and also can merge diff speakers ( will give smae label)
            - get better result on good qaulity audio
            - 1600kHz resampled.
- merger logic, already explained ( written by me only ) can see in merger.py

### 30th may
### working on hindi transcription:
- tested on hindi audio with faster whisper also more parameters included in whisper.transcribe()
    - observation of output:
       - bad words in hindi transcribe
       - good in english translation
       ```
       "start": 0.0,
        "end": 3.08,
        "speaker": "SPEAKER_01",
        "text": "अपने 911 मुड़ क्या आप आप कल इन कैस छिती है।"
        },
        {
          "start": 3.08,
          "end": 5.72,
          "speaker": "SPEAKER_00",
          "text": "जी जी में आप यह एक accident होगा है।"
        },
        {
          "start": 6.48,
          "end": 10.08,
          "speaker": "SPEAKER_00",
          "text": "आगे रोड पे गाडी चल रही तो और एक दम से पीचे गाडी में तक्र मार दिया।"
       ```
  - solution i thought :
      that we can do translation in hindi after english translation (which is really done accuaret by faster whisper) using LLM.

  ## next tried to understand the whisper parameters and how we can tune sepecific to erss
    ```
    segments, info = model.transcribe(
        audio_path,
        language="hi",
        task="translate",
        word_timestamps=True,
        beam_size=5,
        temperature=0.0,
        condition_on_previous_text=False,  # keep this
        no_speech_threshold=0.6,           # keep this
        vad_filter=True,
        vad_parameters=dict(
            threshold=0.45,               # back to gentler value
            min_silence_duration_ms=500,
        ),
        initial_prompt="यह एक emergency call है। Hindi और English mix में conversation है। accident, location, road, police, ambulance.",
        compression_ratio_threshold=2.4
    )
    ```

     - language to get whisper telling beforehand what language to expect
     - task can be "translate" or "transcribe"
     - beam_size and temperature : whisper to consider multiple candidates and randomness in predicting token( not only highest probabbility)
         respectively.
       ```
             beam_size
            Beam search width. Whisper generates multiple candidate transcripts in parallel and picks the best one. beam_size=1 is greedy (fastest, worst). beam_size=5 keeps 5 candidates at once.
            Your value: 5 — good balance.
            Range: 1 (fastest, least accurate) → 10 (slowest, most accurate).
            Tune up to: 8 or 10 if accuracy is more important than speed — for offline batch processing of call recordings.
            Tune down to: 1 or 2 only if doing real-time live transcription where speed is critical.
            temperature
            Randomness in token selection. 0.0 = always pick the highest probability token (deterministic). Higher values introduce randomness — useful when the model is stuck but can cause hallucination.
            Your value: 0.0 — deterministic, consistent output. Right for ERSS.
            Whisper's default behaviour: starts at 0.0, automatically increases if output looks bad (high compression ratio or low confidence) — called temperature fallback.
            Never set above 0.2 for ERSS — higher values cause random wrong words in critical information like addresses and names.
        ```

       ### vad parameters:
          - ```vad filter:True``` this remove noise before the whisper treats them
          - ```
            vad_parameters=dict(
            threshold=0.45,               # back to gentler value
            min_silence_duration_ms=500,
            ```
            in this i observe the behaviour in my output itself
            threshold: if val exceeds threshold then take it as silence
            min silence duration tells for how much min silence time it will treat as silence in between, if val crosses threshold then it vad cuts the segment
            observation in my code:
            1. without this prarameter:
                 ```
                  [55.3s-56.8s]: Yeah, she's 12 years.        ← cut here (short pause)
                  [57.0s-57.6s]: She's not breathing.          ← cut here (short pause)
                  [57.9s-58.6s]: She's not doing anything.     ← cut here (short pause)
                  [58.7s-59.6s]: She is not breathing.
                 ```
            2. with parameter set to 500:
                 ```
                  [55.2s-58.7s]: Yeah. She's 12 years. She's not breathing. She's not doing anything.
                  [58.7s-59.6s]: She is not breathing?
                 ```

                 this pool_save_audio in actual, it is same as second output all three segments were by same speaker
               and next dispatcher asked she is not breathing? in a question tone which is also recognized in second output but not in first output
               why?
                ### The actual mechanism
               Whisper's decoder uses the previous segment's text as context when predicting the next token — including punctuation tokens.
               Longer, richer previous context = better punctuation prediction.
               So the 500ms VAD merging didn't just help accuracy of words — it accidentally gave Whisper more context window to predict punctuation correctly too.
               This is a side effect you want to keep. It means your VAD params are doing triple duty:
                | Effect of 500ms VAD | How
               | --- | --- | 
                | Fewer hallucinations  | Less silence for Whisper to confuse|
                | Better word accuracy  |       More context per segment|
               | Better punctuation     |       Richer prior context for decoder|
               
  
  
    
    

               
   




