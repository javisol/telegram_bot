# Telegram Bot

## Load env vars
```bash
set -o allexport;source .env;set +o allexport
```

## Speech to Text using Google
### Requirements
Audio must be in wav format. Convert it with:
```bash
ffmpg -i voice_file voice_file.wav
```