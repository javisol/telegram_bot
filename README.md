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

## Docker
### Build docker image
```bash
docker build -t "telegram_bot:0.1" .
```
### Run docker image
```bash
docker run -d -e TOKEN="" -e CAL_URL="" -e CAL_USER="" -e CAL_PASS="" --name telegram_bot telegram_bot:0.1 
```
