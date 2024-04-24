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

import os
import sys


directory = os.getcwd()
# Append sys path to refer utils.
sys.path.append(directory+"/src")

# https://b.corp.google.com/issues/324447032
os.environ["GRPC_DNS_RESOLVER"] = "native"

from controller import Controller
import constant as env

prod = False
controller = Controller(prod)

st.set_page_config(layout="wide")
st.subheader("지식 정보 검색 서비스")
st.markdown("VertexAI Search + Gemini 1.5 Pro")

question_list = None
contexts_list = None 
verified_context_list = None
final_prompt = None
final_outcome = None
execution_stat = None

# Set up sidebar with various options
with st.sidebar.expander("Configuration", expanded=True):

    Controller.project_id = st.text_input(label='Project ID', value =env.project_id)
    Controller.region = st.text_input(label='Region', value =env.region)
    Controller.q_type = st.selectbox('질문유형',('복합질문', '단순질문'))
    Controller.search_url = st.text_area(label='Vertex AI Search', value =env.search_url,height=200)
    #Controller.num_search = st.number_input('Search pages',min_value=1,max_value=5, value=env.num_search)

with st.container(height=40, border=False):
    prompt = st.chat_input("질문을 입력해주세요.")

col1, col2 = st.columns(2)

with col1:
    tab1,tab2 = col1.tabs(["검색 결과","최종 Prompt"])
    with tab1:
        with st.container(height=1000, border=False):
            if prompt:
                with st.container(height=800, border=False):

                    with st.expander("질문 내용", expanded=True):
                        st.write(prompt)

                    if Controller.q_type =="복합질문":
                        mixed_question = True
                    else:
                        mixed_question = False

                    condition = {
                        "mixed_question" : mixed_question,
                        "detailed_return" : True
                    }

                    splitted_questions, contexts_list, verified_context_list, final_prompt, final_outcome, execution_stat = controller.response(prompt, condition)

                    if condition['mixed_question']: 
                        with st.expander("질문 재작성", expanded=True):
                            for question in splitted_questions:
                                st.write(question)       

                    with st.expander("최종 처리결과", expanded=True):
                        with st.empty():

                            st.write(final_outcome)
    with tab2:
        with st.container(height=600, border=False):
            with st.expander("최종 Prompt", expanded=True):
                st.write(final_prompt)

with col2:

    tab1, tab2, tab3 = col2.tabs(["요약 검색정보", "상세 검색정보", "검색 통계"],)

    with tab1:

        with st.container(height=1000, border=False):
            if verified_context_list != None:
                for verified_context in verified_context_list:
                    if verified_context != None:

                        question = verified_context['result']['question']
                        reference = verified_context['result']['uri']
                        pageSpan = verified_context['result']['pageSpan']
                        
                        title = f"{question}-[{reference}]-[{pageSpan}]"

                        content = verified_context['result']['content']

                        with st.expander(title, expanded=False):
                            st.write(content)

    with tab2:
        with st.container(height=1000, border=False):
            if contexts_list != None:
                for context in contexts_list:
                    if context != None:
                        question = context['result']['question']
                        content = context['result']['content']
                        pageSpan = context['result']['pageSpan']

                        reference = context['result']['uri']
                        
                        title = f"{question}-[{reference}]-[{pageSpan}]"

                        with st.expander(title, expanded=False):
                            st.write(reference)
                            st.write(content)

    with tab3:
        with st.expander("처리 시간", expanded=True):
            if execution_stat != None:

                q_split = execution_stat['time_question_splitter']
                a_seach = execution_stat['time_ai_search']
                c_veri = execution_stat['time_context_verifier']
                l_req = execution_stat['llm_request']
                total = round((q_split + a_seach + c_veri + l_req), 3)

                st.write(f"질문 재작성 : {q_split} seconds")
                st.write(f"컨텍스트 검색 : {a_seach} seconds")
                st.write(f"컨텍스트 검증 : {c_veri} seconds")
                st.write(f"최종 추론 요청 : {l_req} seconds")
                st.write(f"전체 처리 시간 : {total} seconds")

        with st.expander("검색 결과", expanded=True):
            if execution_stat != None:
                st.write(f"검색된 전체 세그먼트 개수 : {execution_stat['num_total_searched']}")
                st.write(f"전체 중에 검증된 세그먼트 개수 : {execution_stat['num_verified_contexts']}")
