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





