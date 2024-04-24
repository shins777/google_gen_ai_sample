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

import streamlit as st
import threading
import os
import sys

directory = os.getcwd()
# Append sys path to refer utils.
sys.path.append(directory+"/src")

import listen
from listen import MicrophoneStream
from process import VoiceTranslation

# https://b.corp.google.com/issues/324447032
os.environ["GRPC_DNS_RESOLVER"] = "native"

st.set_page_config(layout="wide")
st.subheader("구글 Cloud Translation을 활용한 실시간 통역, 번역 서비스")
st.markdown("통역, 번역 데모는 주로 아시아권 언어를 대상으로 구성되었습니다.  실시간 통역 서비스 데모를 테스트 하기 위해서는 마이크와 스피거를 사용해야 합니다.")

vo_tran = VoiceTranslation()

class ListenThread(threading.Thread):
    def __init__(self, stop_event):
        super(ListenThread, self).__init__()
        self.stop_event = stop_event    

    def run(self):
        listen.process(self.stop_event)

def looper_control(state, stop_event):
    if state == 'start':
        t = ListenThread(stop_event=stop_event)
        t.start()
    elif state == 'stop':
        stop_event.set()

# Initialize session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""

# Define function to get user input
def get_text():

    input_text = st.text_area("You: ", st.session_state["input"], key="input",
                            placeholder="Your AI assistant here! Ask me anything ...", 
                            label_visibility='hidden')
    return input_text


source_lang_options = (['한국어','ko-KR'],
            ['영어','en-US'],
            ['일본어','ja-JP'],
            ['베트남어','vi-VN'],
            ['말레이시아어','ms-MY'],
            ['인도네시아어','id-ID'],
            ['필리핀어','fil-PH'])

target_lang_options = (['한국어','ko-KR'],
            ['영어','en-US'],
            ['일본어','ja-JP'],
            ['베트남어','vi-VN'],
            ['말레이시아어','ms-MY'],
            ['인도네시아어','id-ID'],
            ['캄보디아','km-KH'],
            ['필리핀어','fil-PH'])

cont = st.container(height=700, border=True)
tab1, tab2 = cont.tabs(["실시간 음성 통역","실시간 대화"],)

with tab1 : 

    i_src, i_tgt = st.columns(2)
    i_source_lang = i_src.selectbox(label = '원본 음성 언어', options = source_lang_options)
    i_target_lang = i_tgt.selectbox(label = '타겟 음성 언어', options = target_lang_options)

    if st.button('연결시작...'):
                
        MicrophoneStream.receive_q.queue.clear()

        stop_thread_event = threading.Event()
        looper_control('start', stop_thread_event)

        if i_source_lang[1]==i_target_lang[1]:
                st.warning('통역을 위해서 원본 음성언어와 타겟 음성 언어를 다르게 설정해주세요.', icon="⚠️")
        else:

            with st.status("청취중...", expanded=True) as status:

                translated_dict = vo_tran.interpret(source_lang_code = i_source_lang[1],
                                                    target_lang_code = i_target_lang[1],
                                                    lang_options = target_lang_options
                                                    )
                st.write(translated_dict)

                from playsound import playsound
                playsound('output.mp3')  

                status.update(label="통역 완료!", state="complete", expanded=True)
                
                looper_control('stop', stop_thread_event)


with tab2 : 

    target_lang = tab2.selectbox(label='언어선택',options = target_lang_options)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    MicrophoneStream.receive_q.queue.clear()

    stop_thread_event = threading.Event()
    looper_control('start', stop_thread_event)
    

    translated_dict = None

    if st.button('상담시작...'):

        with st.status("상담중...", expanded=True) as status:

            col1, col2 = st.columns(2)


            translated_dict = vo_tran.interpret(source_lang_code = "ko-KR",
                                                target_lang_code = target_lang[1],
                                                lang_options = target_lang_options
                                                )
            print(translated_dict)

            with col1:

                st.chat_message("user").markdown(translated_dict['question'])
                st.session_state.messages.append({"role": "user", "content": translated_dict['question']})

                context_str =f"{translated_dict[target_lang[0]]} ({translated_dict['ko-KR']})"

                with st.chat_message("assistant"):
                    st.markdown(context_str)

                st.session_state.messages.append({"role": "assistant", "content": context_str })
            with col2:
                st.write(translated_dict)

            from playsound import playsound
            playsound('output.mp3')  
            
            looper_control('stop', stop_thread_event)

            status.update(label="상담 완료!", state="complete", expanded=True)
