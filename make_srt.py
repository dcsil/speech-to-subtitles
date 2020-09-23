# Adapted from https://stackoverflow.com/questions/62554058/subtitles-captions-with-microsoft-azure-speech-to-text-in-python
# Adapted from solution from "sathya_vijayakumar-MSFT" under https://creativecommons.org/licenses/by-sa/4.0/
#
import azure.cognitiveservices.speech as speechsdk
import datetime
import json
import os
import srt
import sys
import time

from loguru import logger
from dotenv import load_dotenv
load_dotenv()

path = os.getcwd()
audio_filename = sys.argv[1]

filename = os.path.basename(audio_filename)
filename_without_ext = os.path.splitext(filename)[0]
subtitle_output = os.path.join(path, "subtitles", filename_without_ext + ".srt")

# Add your variables to your .env file: https://speech.microsoft.com
speech_key, service_region = os.getenv("AZURE_SPEECH_KEY"), os.getenv("AZURE_SPEECH_REGION")
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

def get_speech_recognizer(audio_filename):
    logger.info("Loading speech recognizer from " + audio_filename)
    audio_input = speechsdk.audio.AudioConfig(filename=audio_filename)
    speech_config.speech_recognition_language="en-US"
    speech_config.request_word_level_timestamps()
    speech_config.enable_dictation()
    speech_config.output_format = speechsdk.OutputFormat(1)
    return speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

#https://docs.microsoft.com/en-us/python/api/azure-cognitiveservices-speech/azure.cognitiveservices.speech.recognitionresult?view=azure-python
def handle_final_result(evt):
    import json
    all_results.append(evt.result.text) 
    results = json.loads(evt.result.json)
    transcript.append(results['DisplayText'])
    confidence_list_temp = [item.get('Confidence') for item in results['NBest']]
    max_confidence_index = confidence_list_temp.index(max(confidence_list_temp))
    words.extend(results['NBest'][max_confidence_index]['Words'])

def stop_cb(evt):
    logger.info('CLOSING on {}'.format(evt))
    speech_recognizer.stop_continuous_recognition()
    global done
    done= True

def convertduration(t):
    x = t / 10000
    return int((x / 1000)), (x % 1000)

def create_subtitles_and_transcript(speech_to_text_response):
    #3 Seconds
    bin = 3.0
    duration = 0 
    transcriptions = []
    transcript = ""
    index, prev = 0,0
    wordstartsec, wordstartmicrosec=0,0
    for i in range(len(speech_to_text_response)):
        # Forms the sentence until the bin size condition is met
        transcript = transcript + " " + speech_to_text_response[i]["Word"]

        # Checks whether the elapsed duration is less than the bin size
        if(int((duration / 10000000)) < bin): 
            wordstartsec, wordstartmicrosec = convertduration(speech_to_text_response[i]["Offset"])
            duration = duration + speech_to_text_response[i]["Offset"] - prev
            prev = speech_to_text_response[i]["Offset"]
            # transcript = transcript + " " + speech_to_text_response[i]["Word"]
        else : 
            index = index + 1
            #transcript = transcript + " " + speech_to_text_response[i]["Word"]
            transcriptions.append(
                srt.Subtitle(
                    index,
                    datetime.timedelta(0, wordstartsec, wordstartmicrosec),
                    datetime.timedelta(0, wordstartsec + bin, 0),
                    transcript
                )
            )
            duration = 0 
            #logger.info(transcript)
            transcript = ""


    transcriptions.append(
        srt.Subtitle(
            index,
            datetime.timedelta(0, wordstartsec, wordstartmicrosec),
            datetime.timedelta(0, wordstartsec+bin, 0),
            transcript
        )
    )
    subtitles = srt.compose(transcriptions)
    logger.info("Outputting subtitles to " + subtitle_output)
    with open(subtitle_output, "w") as f:
        f.write(subtitles)

done = False
all_results = []
results = []
transcript = []
words = []

speech_recognizer = get_speech_recognizer(audio_filename)
speech_recognizer.recognized.connect(handle_final_result) 

# Connect callbacks to the events fired by the speech recognizer
# Basically just logging  
speech_recognizer.recognizing.connect(lambda evt: logger.info('RECOGNIZING: {}'.format(evt)))
speech_recognizer.recognized.connect(lambda evt: logger.info('RECOGNIZED: {}'.format(evt)))
speech_recognizer.session_started.connect(lambda evt: logger.info('SESSION STARTED: {}'.format(evt)))
speech_recognizer.session_stopped.connect(lambda evt: logger.info('SESSION STOPPED {}'.format(evt)))
speech_recognizer.canceled.connect(lambda evt: logger.info('CANCELED {} {}'.format(evt, evt.cancellation_details)))

# stop continuous recognition on either session stopped or canceled events
speech_recognizer.session_stopped.connect(stop_cb)
speech_recognizer.canceled.connect(stop_cb)

# Add in phrases to recognize
phrase_list_grammar = speechsdk.PhraseListGrammar.from_recognizer(speech_recognizer)
phrase_list = open(os.path.join(path, "phrases.txt"), "r")
phrases = phrase_list.read().split("\n")
for phrase in phrases:
    phrase_list_grammar.addPhrase(phrase)

# Actually Run
speech_recognizer.start_continuous_recognition()

while not done:
    time.sleep(.5)

logger.info("logger.infoing all results:")
logger.info(all_results)
create_subtitles_and_transcript(words)
