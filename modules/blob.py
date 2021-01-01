from azure.storage.blob import BlobServiceClient, generate_container_sas, ContainerSasPermissions, BlobClient
from authenticate import AuthenticateFunctions
from datetime import datetime, timedelta

class BlobFunctions:
    """
    Contains wrapper functions to authenticate and interact with blob storage

    param params: dict
    """

    def __init__(self, token, sas_duration, sas_permissions=None):
        self.token = token
        self.sas_duration = sas_duration
        self.sas_permissions = sas_permissions

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
        
        sas_duration = self.sas_duration

        udk = blob_service_client.get_user_delegation_key(key_start_time=datetime.utcnow(), key_expiry_time=datetime.utcnow() + timedelta(hours=sas_duration))

        csp = self.__define_sas_permissions()

        sas_token = generate_container_sas(
            account_name=storage_account_name,
            container_name=container_name,
            user_delegation_key=udk,
            permission=csp,
            expiry=datetime.utcnow() + timedelta(hours=sas_duration)
        )

        return sas_token

    def __define_sas_permissions(self):
        
        if self.sas_permissions is None:

            permissions = ContainerSasPermissions(read=True, write=True, delete=True, list=True)
            
            return permissions
        
        else:
            read_permissions = self.__str_to_bool(self.sas_permissions["read"])
            write_permissions = self.__str_to_bool(self.sas_permissions["write"])
            delete_permissions = self.__str_to_bool(self.sas_permissions["delete"])
            list_permissions = self.__str_to_bool(self.sas_permissions["list"])

            permissions = ContainerSasPermissions(read=read_permissions, write=write_permissions, 
                                                delete=delete_permissions, list=list_permissions)

            return permissions

    def __str_to_bool(self, string):
        """
        Converts string input to Boolean
        """
        if string == "True":
            return True

        elif string == "False":
            return False

        else:
            raise ValueError(f"{string} not appropriate sas permission value. Must be True or False.")
    
    
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

        url = f"https://{storage_account_name}.blob.core.windows.net/"

        blob_service_client = BlobServiceClient(account_url=url, credential=self.token)

        return blob_service_client

    def _create_container_client(self, container_name, storage_account_name):
        """
        Generates a container client using blob service client

        param container name: str
        return container_client: ContainerClientObj
        """

        blob_service_client = self._create_blob_service_client(storage_account_name)
        container_client = blob_service_client.get_container_client(container_name)

        return container_client

    def list_blobs(self, container_name, storage_account_name):
        
        """
        generates list of blobs
        """

        container_client = self._create_container_client(container_name, storage_account_name)
        blobs_in_container = container_client.list_blobs()

        blobs_list = []

        for blob in blobs_in_container:

            blobs_list.append(blob.name)
        
        return blobs_list

    def delete_blob(self, storage_account_name, container_name, blob_name):
        """
        deletes a specified blob
        param container_name: str
        param blob_name: str

        return status from delete_blob()
        """

        container_client = self._create_container_client(container_name, storage_account_name)
        status = container_client.delete_blob(blob_name, delete_snapshots=None)

        return status

    def upload_blob(self, blob_name, data, container_name, storage_account_name, blob_type):
        """
        Uploads a blob to specified container
        param blob_name: str
        param path_to_data: str
        param container_name: str
        param blob_type: str

        return status from upload_blob()
        """

        blob_client = self._create_blob_client_from_url(blob_name, storage_account_name, container_name)
        status = blob_client.upload_blob(data, blob_type=blob_type)

        return status
