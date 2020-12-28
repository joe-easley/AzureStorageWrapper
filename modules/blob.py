from azure.storage.blob import BlobServiceClient, generate_container_sas, ContainerSasPermissions, BlobClient
from authenticate import Authenticate

class Blob:
    """
    Contains wrapper functions to authenticate and interact with blob storage
    """

    def create_blob_sas_token(self, storage_account_key, storage_account_id, storage_account_name, container_name):
        """
        Generates blob sas token

        param storage_account_key: str 
        param storage_account_id: str 
        param storage_account_name: str 
        param container_name: str

        return sas_key: str
        """
        
        blob_service_client = self.create_blob_service_client(storage_account_key, storage_account_id, storage_account_name)
        sas_key = self._create_sas_key(blob_service_client, storage_account_name, container_name)

        return sas_key

    def create_blob_client_from_url(self, blob_name, storage_account_key, storage_account_id, storage_account_name, container_name):
        """
        Generates a blob sas url, requires blob_name
        
        param blob_name: str
        param storage_account_key: str 
        param storage_account_id: str 
        param storage_account_name: str 
        param container_name: str
        
        return blob_client: BlobClientObj
        """

        blob_sas_token = self.create_blob_sas_token(storage_account_key, storage_account_id, storage_account_name, container_name)
        
        blob_sas_url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/{blob_name}?{blob_sas_token}"

        blob_client = BlobClient.from_blob_url(blob_sas_url)

        return blob_client

    def create_blob_service_client(self, tenant_id, storage_account_key, storage_account_id, storage_account_name):
        """
        """

        token = Authenticate.generate_credential(authentication_method=)

        url = f"https://{storage_account_name}.blob.core.windows.net/"

        blob_service_client = BlobServiceClient(account_url=url, credential=token)

        return blob_service_client

    