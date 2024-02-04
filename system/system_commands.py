import subprocess
import requests

def uptime():
    return(subprocess.check_output("uptime").decode('utf-8'))

def ip():
    return("IP: " + requests.get('https://ifconfig.me').text)

def fortune():
    result = subprocess.run(["fortune -a"], shell=True, capture_output=True, text=True)
    return result.stdout

def audio_to_wav(file_path):
    result = subprocess.run([f"ffmpeg -y -hide_banner -loglevel error -i {file_path} /tmp/voice_file.wav"], shell=True, capture_output=True, text=True)
    return result.stdout


if __name__ == "__main__":
    print(uptime())
    print(ip())
    print(fortune())
    audio_to_wav("/tmp/voice_file.ogg")