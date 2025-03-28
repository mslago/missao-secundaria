from pydub import AudioSegment

audiofile = "audiofile.wav"
audiofileduration = AudioSegment.from_file(audiofile).duration_seconds
audiofileduration = int(audiofileduration)  # Convert to milliseconds

for x in range(1, audiofileduration):
    print(f"Splitting audio file at {x} seconds")
    start_time = x * 1000  # Convert to milliseconds
    end_time = (x + 1) * 1000  # Convert to milliseconds
    split_audio = AudioSegment.from_file(audiofile)[start_time:end_time]
    split_audio.export(f"audiofileat{x}.wav", format="wav")