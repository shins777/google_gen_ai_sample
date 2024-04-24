
import time
import vertexai
import google.oauth2.credentials
import google.auth.transport.requests
from google.oauth2 import service_account

from vertexai.preview.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models

import rag.constant as env

class RAG():
    
    final_contexts = None

    def __init__(self):

        credentials = service_account.Credentials.from_service_account_file(
            env.svc_acct_file, 
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )

        with open('/Users/hangsik/projects24/audio_translation/src/rag/product.txt','r') as file:
            self.final_contexts = file.read()
            #print(self.final_contexts)

        vertexai.init(project=env.project_id, location=env.region, credentials = credentials )

        print(f"[RAG][__init__] credentials  : {credentials}")
        print(f"[RAG][__init__] gemini_model  : {env.gemini_1_0_pro}")
        print(f"[RAG][__init__] Initialize Controller done!")

    def process(self, question:str)->str:
        
        t1 = time.time()

        final_prompt = f"""
        
        당신은 금융상품에 대해 검색해서 상담해주는 AI 상담원입니다. 
        아래 <Question> 에 대한 답변을 할 때 반드시 <Context> 내에 있는 내용만을 참고해서 요약해서 간략하게 단답형으로 답변해주세요.

        <Context> 
            {self.final_contexts} 
        
        </Context>
        
        <Question> 
            {question} 
        </Question>

        """

        # gemini is more concise to answer as of Mar 12, 2024.
        final_outcome = self.call_gemini(final_prompt, env.gemini_1_0_pro)

        print(f"[RAG][response] question : {question}")
        print(f"[RAG][response] final_outcome : {final_outcome}")

        t2 = time.time()

        llm_request= round(t2-t1,3)

        print(f"[RAG][process] Final_outcome : {llm_request}")
    
        return final_outcome
    

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

        print(f"[RAG][call_gemini] Final response Len {len(responses.text)}")

        return responses.text     