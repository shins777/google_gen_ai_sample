# Gemini Pro  
Gemini 는 Multi Modality 기반에서 학습된 모델입니다. 
Gemini Pro 내에는 아래와 같이 두가지 모델이 있으며, 각각 Text, Image, Video를 처리하는 목적으로 사용됩니다.    
* Gemini Pro Text : 주로 Text 기반의 처리를 하는 Model.  
* Gemini Pro Vision : Image, Video 를 분석하는데 사용되는 모델.  

---

# References  

## API 참고
상세한 Python API 정보는 아래 URL 참고하세요.
* Langchain library : https://github.com/langchain-ai/langchain
* Langchain Vertex AI API : https://api.python.langchain.com/en/stable/google_vertexai_api_reference.html

만일 Gemini Native code를 사용하시려면 아래 URL 참고하세요.  
Gemini Native code를 사용하면 상대적으로 약간의 Latency 이점을 얻을 수 있습니다.
* Getting start : https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal?hl=ko
* API 참고(Python SDK) : https://cloud.google.com/vertex-ai/generative-ai/docs/sdk-for-llm/llm-sdk-overview
* API 참고(REST API) : https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/overview?hl=ko
* 기타 유용한 정보들 : https://cloud.google.com/vertex-ai/generative-ai/docs/release-notes?hl=ko

## 인증방법
코드를 Colab 환경에서 실행하기 위해서는 아래와 같은 인증이 필요합니다.  
만일 다른 환경에서 실행한다면, 아래와 URL 정보를 참고하여 GCP에 접근 하는 환경을 구성해야 합니다. 
* https://cloud.google.com/docs/authentication?hl=ko

만일 어플리케이션이 로컬환경에서 처리되어서 Service account file 이 있다면, 아래 가이드가 하나의 인증 방법이 될수 있습니다.
* https://cloud.google.com/docs/authentication/provide-credentials-adc?hl=ko

## 기타 참고 사항
* Latest Update : Feb 2024: 
    - Gemini 1.5 Pro :   
        - 최근에는 Gemini 1.5 Pro가 출시되어 Private Preview 단계에서 좀더 진화된 모델을 제공하고 있습니다.  
        - https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/#performance. 


