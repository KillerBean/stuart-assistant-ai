import speech_recognition as sr
import sounddevice as sd
import whisper

from tmp_file_handler import TempFileHandler

# Initialize recognizer and microphone
TMP_FILE = "tmp/temp_audio.wav"
tmp_file_handler = TempFileHandler(TMP_FILE)
r = sr.Recognizer()

# Define the keyword to stop listening
# You can change this to any keyword you want
# For example, "stop listening" or "exit"
# This keyword will be used to stop the listening loop
keyword = "parar de ouvir"


def print_device_info():
    print("Available audio input devices:")
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"{idx}: {device['name']}")


def select_input_device():
    print_device_info()
    device_index = int(input("Select the input device index: "))
    sd.default.device = device_index
    print(f"Selected device: {sd.query_devices(device_index)['name']}")

def set_input_device_by_name(name):
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if name.lower() in device['name'].lower() and device['max_input_channels'] > 0:
            sd.default.device = idx
            print(f"Selected device: {device['name']}")
            return
    print(f"No input device found with name containing '{name}'")
    exit(1)

def record_from_mic():
    while True:
        try:
            with sr.Microphone() as source:
                print("Say something...")
                audio = r.listen(source)  # Listen for the first phrase and extract it into audio data
                print("Audio captured, processing...")
                audio_wav = audio.get_wav_data()  # Convert audio to WAV format
                # Recognize speech using Whisper
                model = whisper.load_model("base")  # Load the Whisper model
                # Save the audio to a temporary file for Whisper processing
                with open(TMP_FILE, "wb") as file:
                    file.write(audio_wav)
                    audio_wav = whisper.audio.load_audio(TMP_FILE)  # Load audio for Whisper

                result = model.transcribe(audio_wav, language="pt", fp16=False)
                text = result['text']
                print(f"You said: {text}")
                if keyword in text.lower():
                    print("Keyword detected! Stopping listening.")
                    break
                # 
                # print("Recognizing with google...")
                # text = r.recognize_google(audio, language="pt-BR") # Using Google Speech Recognition
                # print(f"You said: {text}")
                # if keyword in text.lower():
                #     print("Keyword detected! Stopping listening.")
                #     break
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Speech Recognition service; {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            tmp_file_handler.cleanup_temp_file()
    
def output_text(text):
    print(f"Output: {text}")

# TODO: set the device name you want to use
# TODO: you can also implement a way to select the device from the command line
# TODO: listen all the time and output the text when the keyword is detected

def main():
    # select_input_device()
    text = record_from_mic()
    output_text(text)

if __name__ == "__main__":
    main()



# with sr.Microphone() as source:
#     print("Say something...")
#     while True:
#         tmp_file_path = tmp_file_handler.get_temp_file_path()
#         try:
#             r.adjust_for_ambient_noise(source, 1)  # Adjust for ambient noise
#             audio = r.listen(source)  # Listen for the first phrase and extract it into audio data
#             print("Audio captured, processing...")
#             audio_wav = audio.get_wav_data()  # Convert audio to WAV format
#             print("Recognizing with Whisper...")
#             # Recognize speech using Whisper
#             model = whisper.load_model("base")  # Load the Whisper model
#             # audio_wav = audio.get_wav_data()  # Convert audio to WAV format
#             print("Saving audio to temporary file...")
#             # Note: Whisper expects audio in a specific format, so we save it as WAV
#             # Save the audio to a temporary file for Whisper processing
#             with open(tmp_file_path, "wb") as file:
#                 file.write(audio_wav)
#                 print("Audio data written to temp_audio.wav")
#                 audio_wav = whisper.audio.load_audio(tmp_file_path)  # Load audio for Whisper

#             ###
#             ### o modelo whisper funciona, mas o reconhecimento com google 
#             ### é mais rápido e preciso para o português
#             ### o modelo do google detecta somente se a palavra chave for dita em português
#             ### o modelo whisper detecta a palavra chave mesmo se for dita em inglês
#             ### multilingue, mas é mais lento e menos preciso
#             ### só usar o whisper se for usar para outros idiomas
#             ###
            
#             # result = model.transcribe(audio_wav, language="pt", fp16=False)
#             # text = result['text']
#             # print(f"You said: {text}")
#             # if keyword in text.lower():
#             #     print("Keyword detected! Stopping listening.")
#             #     break
#             print("Recognizing with google...")
#             text = r.recognize_google(audio, language="pt-BR") # Using Google Speech Recognition
#             print(f"You said: {text}")
#             if keyword in text.lower():
#                 print("Keyword detected! Stopping listening.")
#                 break
        
#         except sr.WaitTimeoutError:
#             print("Listening timed out while waiting for phrase to start")
#         except sr.UnknownValueError:
#             print("Could not understand audio")
#         except sr.RequestError as e:
#             print(f"Could not request results from Speech Recognition service; {e}")
#         except Exception as e:
#             print(f"An error occurred: {e}")
#         finally:
#             tmp_file_handler.cleanup_temp_file()

    