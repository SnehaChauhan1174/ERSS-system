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

    ### 4th june
    Till now i have tried for different hindi model approaches, used hindi fine tuned model ```collabara/faster-whisper-hindi-medium``` and saw result quite good but still not segmenting good way trabscription was good although.
  now we are moving to live transcription 





## 7th june
so we have used fatser whisper hindi model and we get quite an accurate output for the live trnascription happening in chunks batch not the live streaming 
now suppose we are taking 15s chunks then what will happen whisper will listen first 15s and then start processing it will take some time lime 2 3 4s which get printed as latency in output so the total time takn for that part will be 15+2.5s=17.5s

the next 15s of audio is already being recorded/buffered while you're processing the previous one
hey yu said that 15 s audio is lready buffered

In a real live system, here's how it actually works
You'd have two threads running in parallel:
Thread 1 (recording):     continuously writes mic audio to a buffer
Thread 2 (processing):    reads chunks from that buffer and transcribes

Timeline:
t=0s    Recording starts
t=15s   Processing thread picks up first 15s chunk → sends to Whisper
t=15s   Recording thread is ALREADY capturing second 15s (t=15 to t=30)
t=17.5s Whisper finishes → prints output for chunk 1
t=28s   Processing thread picks up chunk 2 (t=13 to t=28, with overlap)
t=30.5s Whisper finishes → prints output for chunk 2
While Whisper takes 2.5s to process chunk 1, the mic is independently capturing chunk 2. They don't block each other because they're separate threads.

now in our code its not a live streaming its alreayd fully loaded audio

The audio is fully loaded upfront
pythonaudio, sr = librosa.load("emergency_call.wav")
This one line loads the entire audio file into a numpy array in memory. All 53 seconds, right there. Nothing is being recorded. Nothing is streaming. It's just a big array of numbers.

The chunking loop
pythonstart_sample = 0

while start_sample < len(audio):
    end_sample = min(start_sample + chunk_samples, len(audio))
    chunk      = audio[start_sample:end_sample]
    chunk_start = start_sample / sr   # e.g. 0.0, 13.0, 26.0
This is just slicing the array. chunk_samples = 15 * sr, so you're cutting out 15-second windows. Nothing live about this yet.

This is the line that creates the illusion
pythonelapsed = time.time() - call_start
wait    = chunk_start - elapsed
if wait > 0:
    time.sleep(wait)
Walk through it concretely:
Chunk 2 starts at 13.0s in the audio.
You start processing it at t=2.5s real time (just finished chunk 1).
elapsed = 2.5s
wait    = 13.0 - 2.5 = 10.5s
→ code sleeps for 10.5 seconds
So the code literally pauses and does nothing for 10.5 seconds — simulating that you're "waiting for the audio to arrive." Then it wakes up and processes chunk 2 instantly (since the array is already in memory).
That sleep is the entire trick. It's not live. It's a timed replay.

Why it prints output at realistic intervals
Because of that sleep, chunk 1 output appears at ~17.5s, chunk 2 at ~30.5s, chunk 3 at ~43.5s — which feels like a real call being transcribed in real time. But underneath, you're just sleeping and then slicing a numpy array.

What real live would look like
pythonimport sounddevice as sd
from queue import Queue

audio_queue = Queue()

def recording_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())   # mic pushes audio in real time

# start recording in background
sd.InputStream(callback=recording_callback, samplerate=16000).start()

# processing loop reads from queue
while True:
    chunk = collect_from_queue(audio_queue, seconds=15)
    segments = model.transcribe(chunk, ...)
    print(segments)
Here the mic is genuinely filling the queue while your loop is processing. No sleep, no simulation. That's the real version — and that's what you'd build for actual deployment.
Your current code is a clean demo harness. It's the right way to test before you have real audio infrastructure.

my understanding:
ok so it is like as chunk 1 was alrady there so 15 sec were never passed and just 2s processin times takes place and thus it stopped 13s such that it feels like it listened whole 15 s first and then pcessed ti and then go to chunk2

next doubt:
now one thing see as in output yu can see it is breaking t good times
like i want to ask like it takes 15s right and yah we are giving it intila prompt for context as it is a trnasformer
but still like 15 s chunk can be anything so how it is knowing to break where and also like if a sentecne mid break in 15s and contuining in next how it is handling that

1. How Whisper knows where to break segments
Whisper is not breaking on 15s boundaries. It's breaking on speech patterns it learned during training.
Whisper was trained on massive amounts of audio-transcript pairs. From that training it learned that segments end at:

silence (even 300ms)
natural sentence completion patterns
breath pauses

The thing doing this detection in your code is this:
pythonvad_filter=True,
vad_parameters=dict(
    threshold=0.45,
    min_silence_duration_ms=300,
)
VAD = Voice Activity Detection. Before Whisper even touches the audio, VAD scans the 15s chunk and marks regions as speech vs silence. Whisper then treats silence boundaries as segment boundaries.
So the 15s chunk comes in → VAD finds 4 silence gaps → Whisper produces 4 segments. The 15s is just the container. Segmentation happens inside based on the audio content.

2. Mid-sentence break across chunks — how it's handled
This is where initial_prompt does the work.
Say a sentence starts at 13.5s and ends at 15.8s. Your chunk ends at 15s, so Whisper only hears the first half. Two things happen:
In chunk 1: Whisper hears an incomplete sentence. Because of how it was trained, it will either complete it naturally (it predicts likely endings) or cut it at the last clean word before the chunk ends.
In chunk 2 (starts at 13s due to 2s overlap): This chunk actually contains 13s-28s, so it re-includes those last 2 seconds. That's the overlap doing its job — the sentence that was mid-cut is now fully present in chunk 2.
Chunk 1:  |----0s-----------15s----|
Chunk 2:          |----13s-----------28s----|
                  ↑ overlap re-captures this
And initial_prompt gives Whisper the last 200 chars of previous output as context:
pythonprevious_text = " ".join([s["text"] for s in whis_seg])[-200:]
So when chunk 2 starts, Whisper already knows what was said before — it's not starting blind. This is the transformer attention working on the prompt, biasing the decoder toward continuation rather than a fresh start.

The dedup step then cleans the overlap
Because chunk 2 re-transcribes 13-15s that chunk 1 already covered, you'd get duplicate segments. This removes them:
pythonwhis_seg = [
    s for s in whis_seg
    if s["start"] >= last_chunk_end - 2.0
]
Only keep segments that start after where the last chunk ended (with 2s tolerance). So the repeated 13-15s gets dropped from chunk 2's output.

So to summarize the full flow
15s chunk arrives
→ VAD finds silence gaps → marks segment boundaries
→ initial_prompt gives conversation context
→ Whisper decodes each segment using both audio + context
→ 2s overlap ensures mid-sentence cuts are re-captured in next chunk
→ dedup removes the re-captured overlap from output









  
  
    
    

               
   




