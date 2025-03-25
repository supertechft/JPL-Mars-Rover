#  Copyright (c) 2024. Jet Propulsion Laboratory. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pyaudio
import sounddevice
import wave


def recording(audio_path: str):
    # Create an interface to PortAudio and setup values
    port_audio = pyaudio.PyAudio()  
    chunk = 1024
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    sample_rate = 44100
    seconds = 5

    # print('Recording')

    stream = port_audio.open(format=sample_format,
                    channels=channels,
                    rate=sample_rate,
                    frames_per_buffer=chunk,
                    input=True,
                    input_device_index=1)

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
    wf = wave.open(audio_path, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(port_audio.get_sample_size(sample_format))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()