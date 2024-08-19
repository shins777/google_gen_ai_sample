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
import ast
import requests
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from operator import is_not
from functools import partial

import vertexai
import google
import google.oauth2.credentials
import google.auth.transport.requests
from google.oauth2 import service_account

from vertexai.language_models import TextGenerationModel
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models

import logging

logging.basicConfig(
  format = '%(asctime)s:%(levelname)s:%(message)s',
  #datefmt = '%Y-%m-%d: %I:%M:%S %p',
  level = logging.INFO
)

import rag.constant as env

class Controller():
    """
    Vertex AI 서치 후에 결과 처리 Flow.
    
        1. 복잡한 질문에 대해서 여러개로 분류한다. 
        2. 각각에 질문에 대해서 Vertex AI Search를 통해서 검색한다.
        3. 검색된 결과를 Verify 과정을 통해서 필요한 context만 정리한다.
        4. Verified 된 Context 만 Final context 구성해서 최종 결과를 LLM에 요청한다. 
    """
    
    gemini_model = None
    credentials = None

    project_id = env.project_id
    region = env.region
    q_type = None
    search_url = env.search_url
    num_search = 0

    # Langchain verbose
    # globals.set_verbose(False)

    def __init__(self, prod:bool ):

        # Logger setting. 
        if env.logging == "INFO": logging.getLogger().setLevel(logging.INFO)
        else: logging.getLogger().setLevel(logging.DEBUG)

        # if prod = False, use svc account.
        if not prod:
            
            # the location of service account in Cloud Shell.
            Controller.credentials = service_account.Credentials.from_service_account_file(
                env.svc_acct_file, 
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
        else:
            # Use default auth in Cloud Run env. 
            Controller.credentials, project_id = google.auth.default()

        # Initialize Vertex AI env with the credentials. 
        vertexai.init(project=Controller.project_id, location=Controller.region, credentials = Controller.credentials )

        logging.info(f"[Controller][__init__] Controller.credentials  : {Controller.credentials}")
        logging.info(f"[Controller][__init__] Controller.gemini_model  : {Controller.gemini_model}")
        logging.info(f"[Controller][__init__] Initialize Controller done!")

    def response(self, question:str, condition:dict ):
        """
        Controller to execute the RAG processes.
        """

        logging.info(f"[Controller][response] Start response : {condition}")

        splitted_questions, contexts_list, verified_context_list, final_contexts, execution_stat = self.search(question, condition)

        t1 = time.time()

        final_prompt = f"""
        
        당신은 지식을 검색해서 상담해주는 AI 어시스턴트입니다.
        아래 <Question> 에 대한 답변을 할 때 반드시 <Context> 내에 있는 내용만을 참고해서 단계적으로 추론 후 요약해서 답변해주세요.
        답변할 때 결론을 먼저 언급하고, 그 뒤에 이유를 최대한 상세하게 정리해서 근거를 가지고 답해주세요. 
        답변 포맷은 아래와 같이 해주세요.
        1. 답변 요약
        2. 이유 또는 참조 근거
        3. 기타 고려사항
    
        <Context> 
            {final_contexts} 
        
        </Context>
        
        <Question> 
            {question} 
        </Question>

        """

        # gemini is more concise to answer as of Mar 12, 2024.
        final_outcome = self.call_gemini(final_prompt, env.gemini_1_5_pro)

        logging.debug(f"[Controller][response] final_prompt : {final_prompt}")

        t2 = time.time()

        execution_stat['llm_request'] = round((t2-t1), 3)

        logging.debug(f"[Controller][response] Final_outcome : {final_outcome}")
        logging.info(f"[Controller][response] Elapsed time : {execution_stat}")

        if condition['detailed_return']:
            return splitted_questions, contexts_list, verified_context_list, final_prompt, final_outcome, execution_stat
        else:
            return final_outcome

    def search(self, question:str, condition:dict ):
        """
        Controller to execute the RAG processes.

        1. Call flow for mixed question:
            question_splitter --> search_chunks
        2. Call flow for singuar question: 
            search_chunks
        
        - quesiton : user query.
        - mixed_question : complex and composite questions 
        - detailed : return more detailed information.

        """
        
        mixed_question = condition['mixed_question']

        splitted_questions = None
        final_contexts = None

        t1 = time.time()

        if mixed_question:
            
            logging.info(f"[Controller][search] Mixed Question Processing Start! : {question}")

            # Question split for the composite question which contains several questions in a sentence.
            splitted_questions = self.question_splitter(question)
            # 원래의 질문도 추가함.
            splitted_questions.append(question)

            t2 = time.time()

            # Parallel processing to reduce the latency for the Vertex AI Search. 
            with ThreadPoolExecutor(max_workers=10) as executor:
                searched_contexts = executor.map(self.search_chunks, splitted_questions )

            searched_list = [context for context in searched_contexts]

            logging.info(f"[Controller][search] len(searched_list) : {len(searched_list)}")
            logging.debug(f"[Controller][search] searched_list : {searched_list}")

        else:
    
            logging.info(f"[Controller][search] Simple Question Processing Start! : {question}")
            
            t2 = time.time()            

            # Search contexts from the question directly in the different way which one question is searched. 
            contexts = self.search_chunks(question )
            searched_list = [contexts]

            logging.info(f"[Controller][search] len(searched_list) : {len(searched_list)}")
            logging.debug(f"[Controller][search] searched_list : {searched_list}")

        t3 = time.time()

        question_list =[]

        for context in searched_list:
            question_list.append(context['result']['question'])

        logging.debug(f"[Controller][search] question_list : {question_list}")
        logging.debug(f"[Controller][search] searched_list : {searched_list}")

        # 만일 복합 질문 형태가 아니면 검색결과를 그대로 사용.
        if not mixed_question:
            verified_context_list = searched_list
        # 복합 질문인 경우에는 Verification 과정을 처리.
        else:
            # Context Verification for the each contex searched from the Vertex AI Search.
            with ThreadPoolExecutor(max_workers=10) as executor:
                verified_contexts = executor.map(self.context_verifier, searched_list, question_list)

            verified_context_list_org = [context for context in verified_contexts]
            verified_context_list = list(filter(partial(is_not, None), verified_context_list_org))

        logging.debug(f"[Controller][search] verified_contexts : {verified_context_list}")

        # Build the final context consolidated from verified contexts.
        final_contexts = ""
        for context in verified_context_list:
            if context != None:
                final_contexts = final_contexts + "\n[content] : " + context['result']['content']

        logging.debug(f"[Controller][search] final_contexts : {final_contexts}")

        t4 = time.time()

        execution_stat = {}
        execution_stat['time_question_splitter'] = round((t2-t1), 3)
        execution_stat['time_ai_search'] = round((t3-t2), 3)
        execution_stat['time_context_verifier'] = round((t4-t3), 3)

        execution_stat['num_total_searched'] = len(searched_list)
        execution_stat['num_verified_contexts'] = len(verified_context_list)

        #elapsed_time = f"question_splitter[{t2-t1}] : ai_search {t3-t2}] : context_verifier [{t4-t3}] : Total search time : {t4-t1} "
        logging.info(f"[Controller][search] Elapsed time : {execution_stat}")

        logging.debug(f"[Controller][search] Final_outcome : {final_contexts}")

        return splitted_questions, searched_list, verified_context_list, final_contexts, execution_stat


    def question_splitter(self, question :str )->list:

        prompt = PromptTemplate.from_template("""
            당신을 정확한 검색을 위한 질문 생성기 입니다.
            아래 [Question]에 답하기 위한 사실을 검색할 목적으로, [Question]을 기반으로 3가지 질문을 만들어 주세요.
            답변 형태는 반드시 아래와 같은 리스트 포맷으로 답해주세요.
                                              
            [Question] : {question}
            답변 포맷 : ["질문1", "질문2", "질문3"]

        """)

        prompt = prompt.format(question=question)

        questions = self.call_gemini(prompt, env.gemini_1_5_pro)

        # 질문개수를 1차적으로 2개로 셋팅함.
        num_q = 3
        
        print(f"questions : {questions}")
        q_list = []
        
        try:
            q_list = ast.literal_eval(questions)

        # Handling for exception when splitting mixed question.
        except Exception as e:
            logging.info(f"[Controller][question_splitter] Splitting failed")
            for i in range(num_q):
                q_list.append(question)            

        logging.info(f"[Controller][question_verifier] Generated Question List : {q_list}")

        return q_list 

    # https://github.com/shins777/google_gen_ai_sample/blob/main/notebook/03.grounding/ai_search/Vertex%20AI%20Search%20-%20Chunk%20REST.ipynb
    def search_chunks(self, question:str)->str:

        logging.info(f"[Controller][search_chunks] Search Start! : {question}")

        request = google.auth.transport.requests.Request()
        Controller.credentials.refresh(request)

        headers = {
            "Authorization": "Bearer "+ Controller.credentials.token,
            "Content-Type": "application/json"
        }
        
        query_dic ={
            "query": question,
            "page_size": str(env.num_search),
            "offset": 0,
            "contentSearchSpec":{
                    "searchResultMode" : "CHUNKS",
                    "chunkSpec" : {
                        "numPreviousChunks" : 1,
                        "numNextChunks" : 1
                    }              
            },
        }

        data = json.dumps(query_dic)
        data=data.encode("utf8")
        response = requests.post(Controller.search_url,headers=headers, data=data)

        logging.info(f"[Controller][search_chunks] Search Response len : {len(response.text)}")
        logging.debug(f"[Controller][search_chunks] Search Response chunks : {response.text}")
        logging.info(f"[Controller][search_chunks] Search End! : {question}")

        # Start to parse the searched chunks
        dict_results = json.loads(response.text)

        search_results = {}

        if dict_results.get('results'):

            for result in dict_results['results']:

                item = {}

                chunk = result['chunk']

                item['title'] = chunk['documentMetadata']['title']
                item['uri'] = chunk['documentMetadata']['uri']
                item['pageSpan'] = f"{chunk['pageSpan']['pageStart']} ~ {chunk['pageSpan']['pageEnd']}"
                item['content'] = chunk['content']
                item['question'] = question

                if 'chunkMetadata' in chunk:
                    
                    add_chunks = chunk['chunkMetadata']
                    if 'previousChunks' in add_chunks:
                        # chunk 는 현재 Contents에 가까운것 부터 나타남.
                        p_chunks = chunk['chunkMetadata']['previousChunks']
                        if p_chunks:
                            for p_chunk in p_chunks:
                                item['content'] = p_chunk['content'] +"\n"+ item['content']

                    if 'nextChunks' in add_chunks:
                        n_chunks = chunk['chunkMetadata']['nextChunks']
                        if n_chunks:
                            for n_chunk in n_chunks:
                                item['content'] = item['content'] +"\n"+ n_chunk['content']

                search_results['result'] = item

        return search_results

    def context_verifier(self, context : str, question : str)->str:

        """
        The purpose of this function is to decrease the context size for the better latency. 
        Small context size helps to decrease the latency. 
        """

        prompt = PromptTemplate.from_template("""
            당신은 <Question>의 내용을 바탕으로 <Context>의 내용이 관련이 있는 여부를 판단하는 AI Agent 입니다. 
            아래 <Context>의 내용이 아래 <Question>과 관련이 있으면 "Yes" 라고 답하세요.
            만일, 아래 <Context>의 내용이 아래 <Question>과 관련이 없으면 "No"라고 답하세요.

            <Context>
                {context}
            </Context>

            <Question>
                {question}        
            </Question>
                                              
        """)

        prompt = prompt.format(context=context['result']['content'],
                            question=question)

        result = self.call_gemini(prompt, env.gemini_1_5_pro)

        logging.info(f"[Controller][context_verifier] Question : {question}, Verification Result :{result}")

        # if the context is relevant to the question, return the context. 
        
        if result.strip() == "Yes":
            return context

    def call_gemini(self, prompt, gemini_model):
        
        gemini_model = GenerativeModel(gemini_model)

        generation_config = {
            "candidate_count": 1,
            "max_output_tokens": 8092,
            "temperature": 0.5,
            "top_p": 1,
            "top_k": 40
        }
        responses = gemini_model.generate_content(
            [prompt],
            generation_config = generation_config
        ) 

        logging.debug(f"[Controller][call_gemini] Final response Len {len(responses.text)}")

        return responses.text            

