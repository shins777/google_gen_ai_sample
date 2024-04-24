# Copyright 2024 shins777@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

from google.cloud import aiplatform
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.cloud import translate
from google.cloud import texttospeech
from google.cloud.texttospeech import SynthesizeSpeechResponse

from listen import MicrophoneStream

from rag.search import RAG


PROJECT_ID="ai-hangsik"
LOCATION ="asia-northeast3"

class VoiceTranslation():

    def __init__(self):
        
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        #print(f"Version : {aiplatform.__version__}")

        VoiceTranslation.stt_client = SpeechClient()
        VoiceTranslation.trans_client = translate.TranslationServiceClient()
        VoiceTranslation.tts_client = texttospeech.TextToSpeechClient()

    def interpret(self, source_lang_code:str, target_lang_code:str, lang_options)->dict:

        print("Start to listen")
        
        #MicrophoneStream.receive_q.queue.clear()
        question = MicrophoneStream.receive_q.get()
        print(f"Data:Recieved : {question}")

      
        rag = RAG()
        received_str = rag.process(question)

        print(f"final_outcome:{received_str}")

        # https://cloud.google.com/text-to-speech/docs/voices?hl=ko

        translated_dict = {}
        translated_dict[source_lang_code] = received_str


        # 모든 Target 언어에 대해서 Translation.
        for lang in lang_options:
            #print(f"Source : {source_lang_code}, Target : {lang[1]}")

            # 만일 Source, target 언어가 동일하면 skip. 
            if source_lang_code == lang[1]:
                continue

            translated_str = self.translate_text(received_str, source_lang_code,lang[1])
            translated_dict[lang[0]] = translated_str

        translated_dict['question'] = question

        # Audio 생성 로직 - for only target 언어에 대해서만. 음성을 만들어야 하므로.
        targeted_translated_str = self.translate_text(received_str,source_lang_code,target_lang_code)
        targeted_generated_audio = self.text_to_speech(targeted_translated_str,target_lang_code)
        
        with open("output.mp3", "wb") as out:
            # Write the response to the output file.
            out.write(targeted_generated_audio.audio_content)
            print('Audio content written to file "output.mp3"')

        return translated_dict

    def speech_to_text(self, language_code:str, content:bytes,) -> str:
        
        LOCATION="global"

        try:
            config = cloud_speech.RecognitionConfig(
                auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
                language_codes=[language_code],
                model="long",
            )

            request = cloud_speech.RecognizeRequest(
                recognizer=f"projects/{PROJECT_ID}/locations/{LOCATION}/recognizers/_",
                config=config,
                content=content,
            )

            # Transcribes the audio into text
            response = VoiceTranslation.stt_client.recognize(request=request)
            outcome_stt = response.results[0].alternatives[0].transcript

            print(f"[speech_to_text] outcome_stt : {outcome_stt}")

        except Exception as e:
            print(f"[translate_text] An error occurred: {e}")

        return outcome_stt

    def translate_text(self, text: str, source_lang_code: str, target_lang_code:str) -> str:

        LOCATION="global"

        try:
            parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"

            response = VoiceTranslation.trans_client.translate_text(
                request={
                    "parent": parent,
                    "contents": [text],
                    "mime_type": "text/plain",  # mime types: text/plain, text/html
                    "source_language_code": source_lang_code,
                    "target_language_code": target_lang_code,
                }
            )

            # Display the translation for each input text provided
            for translation in response.translations:
                print(f"Translated text: {translation.translated_text}")

        except Exception as e:
            print(f"[translate_text] An error occurred: {e}")

        #return response
        return response.translations[0].translated_text
    

    def text_to_speech(self, text:str,language_code:str ) -> SynthesizeSpeechResponse:
        response = None
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)

            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code, 
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = VoiceTranslation.tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
        except Exception as e:
            print(f"[text_to_speech] An error occurred: {e}")
    
        return response

 

    def record_until_silence(self):
        try:
            
            print("Recording...")

            t1 = time.time()
            
            #display(Javascript(RECORD))
            
            t2 = time.time()

            s = output.eval_js('recordUntilSilence()')
            b = b64decode(s.split(',')[1])
            #audio = AudioSegment.from_file(BytesIO(b))

            t3 = time.time()

            outcome_stt = self.speech_to_text(language_code="ko-KR", 
                                        content=b)

            t4 = time.time()

            outcome_trans = self.translate_text(text=outcome_stt, 
                                        source_lang_code="ko-KR", 
                                        target_lang_code="en-US")

            t5 = time.time()

            outcome_tts = self.text_to_speech(text=outcome_trans,
                                        language_code="en-US" )

            t6 = time.time()


            # The response's audio_content is binary.
            with open("output.mp3", "wb") as out:
                # Write the response to the output file.
                out.write(outcome_tts.audio_content)
                print('Audio content written to file "output.mp3"')

            t7 = time.time()

            print(f"display: {t2-t1}s")
            print(f"audio building: {t3-t2}s")
            print(f"stt: {t4-t3}s")
            print(f"translation: {t5-t4}s")
            print(f"tts: {t6-t5}s")
            print(f"build audio: {t7-t6}s")

        except Exception as e:
            print(f"An error occurred: {e}")