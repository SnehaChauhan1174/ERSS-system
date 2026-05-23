import whisper

model = whisper.load_model("base")

audio_path = r"D:\InternshipProject\ERSS Project\audio\corona_aircrash.mp3"


text = model.transcribe(audio=audio_path)
# print(type(text))

for key,value in text.items():
    print(f"{key}")
    print(type(value))

print(type(text["segments"][0]))

print("each seg structure")
for seg in text["segments"]:
    for key,value in seg.items():
        print(f"{key}")
        print(type(value))
    break

for seg in text["segments"]:
    start = seg["start"]
    end = seg["end"]
    text = seg["text"]
    print(f"[{start}s-{end}s]:{text}")












