# Google Grounding Services
## 1. Vertex AI Search
Vertex AI Search 는 Google의 Managed Out of box Vector search tool 입니다. 
사용자는 정형, 비정형, Web site 데이터를 특별한 전처리 없이 그대로 시멘틱서치를 위해서 Vectorization을 자동화된 방법으로 처리해주는 구글의 서비스입니다.  
* https://cloud.google.com/generative-ai-app-builder/docs/enterprise-search-introduction

### References  

#### Vertex AI Search 메뉴얼
* https://cloud.google.com/generative-ai-app-builder/docs/try-enterprise-search
* https://cloud.google.com/generative-ai-app-builder/docs/create-datastore-ingest

#### 기타 참고 사항
* quotas : https://cloud.google.com/generative-ai-app-builder/quotas#allocation-quotas

---

## 2. BigQuery as a Vector store.
BigQuery의 새로운 기능으로 Vector 데이터를 저장하고 검색할 수 있는 기능을 제공합니다.
* https://cloud.google.com/bigquery/docs/vector-search-intro?hl=ko

### References  

#### BigQuery Vector Search Langchain 메뉴얼
*   https://python.langchain.com/docs/integrations/vectorstores/bigquery_vector_search
*   https://api.python.langchain.com/en/stable/vectorstores/langchain_community.vectorstores.bigquery_vector_search.BigQueryVectorSearch.html#langchain_community.vectorstores.bigquery_vector_search.BigQueryVectorSearch
