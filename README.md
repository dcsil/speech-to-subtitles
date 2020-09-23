# Subtitles

Converts video to subtitles to be added to videos. Uses Azure Speech To Text.

Results are not perfect, but are a great start.

## How to Run

1. Setup an Azure account: https://speech.microsoft.com
2. Obtain a speech API key
3. Create a .env file by running `cp .env.example .env`, replace the example data with the data you made in (2)
4. Install Python 3 and Pip 3. Run `pip install -r requirements.txt`
5. 2 options to run:
  - Run `python make_srt.py PATH_TO_WAV` (requires 16bit .wav files)
  - Run `./aud_conv PATH_TO_VIDEO` which will use `ffmpeg` to extract 16 bit WAV audio and then converts it
6. Subtitles will be output to `subtitles` folder

_Install ffmpeg with `brew install ffmpeg` on Mac, `sudo apt update && sudo apt install ffmpeg` on Ubuntu 18.04+, and from https://ffmpeg.org/download.html for Windows_

### Optional

You can add phrases (one per line), to give the speech to text converter a hint into what you're saying, in `phrases.txt`
