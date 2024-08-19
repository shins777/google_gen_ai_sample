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

# 이 파일은 Vertex AI Search 기반의 RAG 구성을 위한 환경 설정입니다.
# 실행전에 해당 환경 정보를 구성하세요.

# Logging level( INFO | DEBUG )
logging = "INFO"

# 프로젝트 정보. 
project_id = "ai-hangsik"
region="asia-northeast3"

# 모델 정보.
# 모델은 여러개 등록해서 코드상에서 해당 목적에 맞게 구성하시면됩니다. 
gemini_1_0_pro = "gemini-1.0-pro"
gemini_1_5_pro = "gemini-1.5-pro"

# GCP내 Cloud shell 환경
# Stand alone 어플리케이션 환경에서 접근하기 위해서 service account 파일을 등록해 놓습니다.
# 이 설정은 해당 인증이 완료된 GCP 내라든지 ADC 가 되어 있는 환경에서는 다른 형태로 인증형태를 구성할 수 있습니다. 
svc_acct_file = "/home/admin_/keys/ai-hangsik-71898c80c9a5.json"

# 로컬 PC 환경.
# PC 환경에서의 서비스 어카운드 위치를 지정해 놓습니다. 
#svc_acct_file = "/Users/hangsik/projects24/_service_account_key/ai-hangsik-71898c80c9a5.json"

# Vertex AI Search를 Grounding service로 활용하기 위한 목적으로 
# Vertex AI Search에서의 Configuration > Integration 내의 REST API 의 endpoint를 넣습니다.
search_url = "https://discoveryengine.googleapis.com/v1alpha/projects/721521243942/locations/global/collections/default_collection/dataStores/it-laws-ds_1713063479348/servingConfigs/default_search:search"

# 검색 결과 개수
num_search = 2
