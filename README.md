# google_gen_ai_sample
Feedback to shins777@gmail.com

## 참고사항.
이 repository 에 있는 예제는 Generativa AI 개발자들이 Google Generative AI를 쉽게 사용하도록 돕기 위해 만든 Python 코드입니다.  
각 폴더의 주제별로 구분되어서 Python 소스 코드가 제공이 되며, 시간이 지남에 따라서 제품 기능상의 업그레이드로 동작하지 않는 코드가 있을 수 있습니다.

## API 참고
상세한 Python API 정보는 아래 URL 참고하세요.
* Langchain Vertex AI API : https://api.python.langchain.com/en/stable/google_vertexai_api_reference.html
* Langchain library : https://github.com/langchain-ai/langchain

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

