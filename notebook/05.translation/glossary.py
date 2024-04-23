# Copyright 2024 shins777@gmail.com

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.cloud import translate_v3 as translate

class GlossaryTest():

    client = None

    def __init__(self,svc_acct_file):
        from google.oauth2 import service_account

        credentials = service_account.Credentials.from_service_account_file(
            svc_acct_file, 
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        self.client = translate.TranslationServiceClient(credentials=credentials)
        # self.client = translate.TranslationServiceClient()

        print(self.client)  

    def create_glossary(self, 
                    project_id: str, 
                    location:str,
                    glossary_file: str, 
                    glossary_id: str,
                    source_lang_code:str,
                    target_lang_code:str,                        
                    timeout: int = 180,
                ) -> translate.Glossary:
        """
        https://cloud.google.com/translate/docs/advanced/glossary#format-glossary
        """

        print(f"project id {project_id}")
        print(f"region id {location}")
        print(f"client id {self.client}")

        name = self.client.glossary_path(project_id, location, glossary_id)

        language_codes_set = translate.types.Glossary.LanguageCodesSet(
            language_codes=[source_lang_code, target_lang_code]
        )

        gcs_source = translate.types.GcsSource(input_uri=glossary_file)

        input_config = translate.types.GlossaryInputConfig(gcs_source=gcs_source)

        glossary = translate.types.Glossary(
            name=name, language_codes_set=language_codes_set, input_config=input_config
        )

        parent = f"projects/{project_id}/locations/{location}"
        operation = self.client.create_glossary(parent=parent, glossary=glossary)

        result = operation.result(timeout)
        print(f"Glossary Created: {result.name}")
        print(f"Input Uri: {result.input_config.gcs_source.input_uri}")

        return result

    def delete_glossary(self,
                project_id: str,
                location: str,
                glossary_id: str,
                timeout: int = 180,
            ) -> translate.Glossary:
        """Delete a specific glossary based on the glossary ID.
        """

        name = self.client.glossary_path(project_id, location, glossary_id)

        operation = self.client.delete_glossary(name=name)
        result = operation.result(timeout)
        print(f"Deleted: {result.name}")

        return result

    def get_glossary(self,
            project_id: str, 
            location:str,
            glossary_id: str,
        ) -> translate.Glossary:
        """Get a particular glossary based on the glossary ID.
        """

        name = self.client.glossary_path(project_id, location, glossary_id)

        response = client.get_glossary(name=name)
        print(f"Glossary name: {response.name}")
        print(f"Entry count: {response.entry_count}")
        print(f"Input URI: {response.input_config.gcs_source.input_uri}")

        return response

    def list_glossaries(self,
            project_id: str,
            location:str
        ) -> translate.Glossary:

        """List Glossaries.
        """

        parent = f"projects/{project_id}/locations/{location}"

        # Iterate over all results
        for glossary in self.client.list_glossaries(parent=parent):
            # print(glossary)
            print(f"glossary id: {glossary.display_name}")

        return glossary

    def translate_with_glossary(self,
            text: str,
            project_id: str,
            location:str,
            glossary_id: str,
            source_lang_code,
            target_lang_code,

        ) -> translate.TranslateTextResponse:
        """Translates a given text using a glossary.
        """
        
        parent = f"projects/{project_id}/locations/{location}"

        glossary = self.client.glossary_path(
            project_id, "us-central1", glossary_id  # The location of the glossary
        )

        glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary)

        response = self.client.translate_text(
            request={
                "contents": [text],
                "parent": parent,
                "glossary_config": glossary_config,
                "source_language_code": source_lang_code,
                "target_language_code": target_lang_code,                
            }
        )

        return response