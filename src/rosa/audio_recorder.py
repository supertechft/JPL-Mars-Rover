import pyaudio
import os
import sounddevice  # Hides ALSA warnings
import wave


def Record(audio_path: str):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    
    # Create an interface to PortAudio and setup values
    port_audio = pyaudio.PyAudio()
    chunk = 1024
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    sample_rate = 44100
    seconds = 5

    # print('Recording')

    stream = port_audio.open(
        format=sample_format,
        channels=channels,
        rate=sample_rate,
        frames_per_buffer=chunk,
        input=True,
        input_device_index=1,
    )

    frames = []  # Initialize array to store frames

    # Store data in chunks for the defined time in seconds
    for i in range(0, int(sample_rate / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream and PortAudio interface
    stream.stop_stream()
    stream.close()
    port_audio.terminate()

    # print('Finished recording')

    # Save the recorded data as a WAV file
    wf = wave.open(audio_path, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(port_audio.get_sample_size(sample_format))
    wf.setframerate(sample_rate)
    wf.writeframes(b"".join(frames))
    wf.close()
