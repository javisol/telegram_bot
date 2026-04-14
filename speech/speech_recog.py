import sys
import logging
import speech_recognition as sr

logger = logging.getLogger(__name__)


def speech_to_text_from_file(file_path: str) -> str:
    """Convert audio file to text using Google Speech Recognition.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Transcribed text string
        
    Raises:
        sr.UnknownValueError: When the audio is not understood
        sr.RequestError: When the API request fails
    """
    recognizer = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        # Adjust for ambient noise if necessary
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.record(source)

    try:
        return recognizer.recognize_google(audio, language="es-ES")
    except sr.UnknownValueError:
        logger.warning(f"Google Web Speech API could not understand audio: {file_path}")
        return "Google Web Speech API could not understand audio"
    except sr.RequestError as e:
        logger.error(f"Could not request results from Google Web Speech API; {e}")
        return f"Could not request results from Google Web Speech API; {e}"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error number of parameters: an audio file must be provided")
        sys.exit(1)

    file_path = sys.argv[1]
    print(speech_to_text_from_file(file_path))
