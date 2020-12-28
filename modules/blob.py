from azure.storage.blob import BlobServiceClient, generate_container_sas, ContainerSasPermissions, BlobClient
from authenticate import Authenticate
from datetime import datetime

class Blob:
    """
    Contains wrapper functions to authenticate and interact with blob storage

    param params: dict
    """

    def __init__(self, params):
        self.params = params

    def _create_blob_sas_token(self, storage_account_name, container_name):
        """
        Generates blob sas token

        param storage_account_key: str 
        param storage_account_id: str 
        param storage_account_name: str 
        param container_name: str

        return sas_key: str
        """
        
        blob_service_client = self._create_blob_service_client(storage_account_name)
        sas_key = self._create_sas_key(blob_service_client, storage_account_name, container_name)

        return sas_key

    def _create_sas_key(self, blob_service_client, storage_account_name, container_name):
        
        sas_duration = self.params["sas_duration"]

        udk = blob_service_client.get_user_delegation_key(key_start_time=datetime.utcnow(), key_expiry_time=datetime.utcnow() + timedelta(hours=sas_duration))

        csp = ContainerSasPermissions(read=True, write=True, delete=True, list=True)

        sas_token = generate_container_sas(
            account_name=storage_account_name
            container_name=container_name,
            user_delegation_key=udk,
            permission=csp,
            expiry=datetime.utcnow() + timedelta(hours=sas_duration)
        )

        return sas_token

    def _create_blob_client_from_url(self, blob_name, storage_account_name, container_name):
        """
        Generates a blob sas url, requires blob_name
        
        param blob_name: str
        param storage_account_key: str 
        param storage_account_id: str 
        param storage_account_name: str 
        param container_name: str
        
        return blob_client: BlobClientObj
        """
        
        blob_sas_token = self._create_blob_sas_token(storage_account_name, container_name)
        
        blob_sas_url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/{blob_name}?{blob_sas_token}"

        blob_client = BlobClient.from_blob_url(blob_sas_url)

        return blob_client

    def _create_blob_service_client(self, storage_account_name):
        """
        """

        token = Authenticate.generate_credential(self.params)

        url = f"https://{storage_account_name}.blob.core.windows.net/"

        blob_service_client = BlobServiceClient(account_url=url, credential=token)

        return blob_service_client

    def _create_container_client(self, container_name):
        """
        Generates a container client using blob service client

        param container name: str
        return container_client: ContainerClientObj
        """
        storage_account_name = self.params["storage_account_name"]

        blob_service_client = self._create_blob_service_client(storage_account_name)
        container_client = blob_service_client.get_container_client(container_name)

        return container_client

    def list_blobs(self, container_name):
        
        """
        generates list of blobs
        """

        container_client = self._create_container_client(container_name)
        blobs_in_container = container_client.list_blobs()

        blobs_list = []

        for blob in blobs_in_container:

            blobs_list.append(blob.name)
        
        return blobs_list

    def delete_blob(self, container_name, blob_name):
        """
        deletes a specified blob
        param container_name: str
        param blob_name: str

        return True if successful
        """

        container_client = self._create_container_client(container_name)
        container_client.delete_blob(blob_name, delete_snapshots=None)

        return True

    def upload_blob(self, blob_name, data, container_name, blob_type):
        """
        Uploads a blob to specified container
        param blob_name: str
        param path_to_data: str
        param container_name: str
        param blob_type: str

        return True if successful
        """

        blob_client = self._create_blob_client_from_url(blob_name, storage_account_name, container_name)
        blob_client.upload_blob(data, blob_type=blob_type)

        return True
