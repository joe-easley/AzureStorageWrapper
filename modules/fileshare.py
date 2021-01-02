from authenticate import AuthenticateFunctions
from azure.keyvault.secrets import SecretClient
from azure.storage.file import FileService
from azure.storage.fileshare import generate_account_sas, ResourceTypes, AccountSasPermissions
from datetime import datetime, timedelta

class FileShareFunctions:

    def __init__(self, token, vault_url=None, secret_name=None):
        self.token = token
        self.vault_url = vault_url
        self.secret_name = secret_name

    def _create_sas_for_fileshare(self, storage_account_name):
        """
        Generates sas key for fileshare, requires key to account being stored in key vault
        param
        """
        
        sas_duration = self.params["sas_duration"]
        secret = self.__get_secret()

        fs_sas_token = generate_account_sas(
            account_name=storage_account_name,
            account_key=secret,
            resource_types=ResourceTypes(service=True, container=True, object=True),
            permission=AccountSasPermissions(read=True, write=True),
            expiry=datetime.utcnow() + timedelta(hours=sas_duration)
        )

        return fs_sas_token

    def _create_file_service(self, storage_account_name):
        """
        creates file service object
        """

        fs_sas_token = self._create_sas_for_fileshare(storage_account_name)

        file_service = FileService(account_name=storage_account_name, sas_token=fs_sas_token)

        return file_service

    def __get_secret(self):
        """
        Retrieves storage acct access key from key vault
        
        param vault_url: str
        param secret_name: str

        return secret
        """
        vault_url = self.vault_url
        secret_name = self.secret_name

        secret_client = SecretClient(vault_url=vault_url, credential=self.token)
        secret = secret_client.get_secret(secret_name)

        return secret.value

    def create_fileshare_directory(self, storage_account_name, file_share_name, directory_path):
        """
        Creates a directory in a preexisting file share

        param file_share_name: str
        param directory_path: str
        param storage_account_name: str
        """
        file_service = self._create_file_service(storage_account_name)
        status = file_service.create_directory(share_name=file_share_name, directory_name=directory_path)

        return status
