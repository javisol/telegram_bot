import sys
import speech_recognition as sr

def speech_to_text_from_file(file_path) -> str:
    recognizer = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        # Adjust for ambient noise if necessary
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.record(source)

    try:
        return recognizer.recognize_google(audio, language="es-ES")

    except sr.UnknownValueError:
        print("Google Web Speech API could not understand audio")

    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech API; {e}")

    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error number of parameters: an audio file must be provided")
        exit(1)

    file_path = sys.argv[1] 
    print(speech_to_text_from_file(file_path))