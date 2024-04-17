from google.cloud import translate_v3 as translate

class AdaptiveTest():

    client = None

    def __init__(self,svc_acct_file):
        from google.oauth2 import service_account

        credentials = service_account.Credentials.from_service_account_file(
            svc_acct_file, 
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        self.client = translate.TranslationServiceClient(credentials=credentials)

        print(self.client)  

    def create_adaptive_mt_dataset(self,
            project_id:str,
            location:str,
            dataset_id:str,
            display_name:str,
            source_language_code:str,
            target_language_code:str

        ):

        adaptive_mt_dataset = translate.AdaptiveMtDataset()
        adaptive_mt_dataset.name = f"projects/{project_id}/locations/{location}/adaptiveMtDatasets/{dataset_id}"
        adaptive_mt_dataset.display_name = display_name
        adaptive_mt_dataset.source_language_code = source_language_code
        adaptive_mt_dataset.target_language_code = target_language_code
        
        request = translate.CreateAdaptiveMtDatasetRequest(
            parent=f"projects/{project_id}/locations/{location}",
            adaptive_mt_dataset=adaptive_mt_dataset,
        )
        response = self.client.create_adaptive_mt_dataset(request=request)
        
        print(f"[AdaptiveTest][create_adaptive_mt_dataset] : {response}")

        return response


    def import_adaptive_mt_file( self,
            project_id:str,
            location:str,
            dataset_id:str,
            input_file_uri:str
        ):

        print(project_id)
        print(location)
        print(dataset_id)
        print(input_file_uri)

        gcs_input_source = translate.GcsInputSource()
        gcs_input_source.input_uri = input_file_uri

        request = translate.ImportAdaptiveMtFileRequest(
            parent=f"projects/{project_id}/locations/{location}/adaptiveMtDatasets/{dataset_id}",
            gcs_input_source=gcs_input_source
        )
        response = self.client.import_adaptive_mt_file(request)
        
        print(f"[AdaptiveTest][import_adaptive_mt_file] : {response}")
        
        return response


    def adaptive_mt_translate(self,
            project_id:str,
            location:str,
            dataset_id:str,
            input_text:str
        ):

        # Initialize the request
        request = translate.AdaptiveMtTranslateRequest(
            parent=f"projects/{project_id}/locations/{location}",
            dataset=f"projects/{project_id}/locations/{location}/adaptiveMtDatasets/{dataset_id}",
            content=[input_text]
        )

        response = self.client.adaptive_mt_translate(request)

        #print(f"[AdaptiveTest][adaptive_mt_translate] : {response}")
        
        return response

    def list_adaptive_mt_datasets(self,
            project_id:str,
            location:str):

        request = translate.ListAdaptiveMtDatasetsRequest(
            parent=f"projects/{project_id}/locations/{location}",
        )
        response = self.client.list_adaptive_mt_datasets(request)
        print(response)

    def delete_adaptive_mt_dataset(self,
            project_id:str,
            location:str,
            dataset_id:str):

        request = translate.DeleteAdaptiveMtDatasetRequest(
            name=f"projects/{project_id}/locations/{location}/adaptiveMtDatasets/{dataset_id}"
        )
        response = self.client.delete_adaptive_mt_dataset(request)
        print(response)

    def list_adaptive_mt_files(self,
            project_id:str,
            location:str,
            dataset_id:str):

        request = translate.ListAdaptiveMtFilesRequest(
            parent=f"projects/{project_id}/locations/{location}/adaptiveMtDatasets/{dataset_id}"
        )
        response = self.client.list_adaptive_mt_files(request)
        print(response)

    def delete_adaptive_mt_file(self,
            project_id:str,
            location:str,
            dataset_id:str,
            file_id:str):

        request = translate.DeleteAdaptiveMtFileRequest(
            name=f"projects/{project_id}/locations/{location}/adaptiveMtDatasets/{dataset_id}/adaptiveMtFiles/{file_id}"
        )
        response = self.client.delete_adaptive_mt_file(request)
        print(response)
        



  

