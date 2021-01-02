from azure.storage.queue import generate_queue_sas, QueueClient, QueueServiceClient, AccountSasPermissions, ResourceTypes generate_account_sas, QueueSasPermissions
from datetime import datetime, timedelta

class QueueFunctions:

    def __init__(self, token, sas_duration, sas_permissions=None, vault_url=None, secret_name=None):
        self.token = token
        self.sas_permissions = sas_permissions
        self.vault_url = vault_url
        self.secret_name = secret_name

    def _create_sas_key(self, storage_account_name, queue_name):
        
        queue_service_client = self._generate_queue_service_client(storage_account_name)
        
        sas_permissions = self.__define_sas_permissions()

        secret = self.__get_secret()

        sas_key = generate_queue_sas(
            account_name=storage_account_name,
            queue_name=queue_name, 
            account_key=secret, 
            permission=sas_permissions, 
            expiry=datetime.utcnow() + timedelta(hours=sas_duration)
            )

        return sas_key
        
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

    def __define_sas_permissions(self):
        """
        Defines SAS permissions for queue storage
        If SAS permissions is not defined in class instantiation then all permissions will be granted,
        if not then sas_permissions dict shall be used
        """
        if self.sas_permissions is None:
            permissions = QueueSasPermissions(read=True, add=True, 
                                              update=True, process=True)
            return permissions
        
        else:
            read_permissions = self.__str_to_bool(self.sas_permissions["read"])
            add_permissions = self.__str_to_bool(self.sas_permissions["add"])
            update_permissions = self.__str_to_bool(self.sas_permissions["update"])
            process_permissions = self.__str_to_bool(self.sas_permissions["process"])

            permissions = QueueSasPermissions(read=read_permissions, add=add_permissions, 
                                              update=update_permissions, process=process_permissions)

    def _generate_queue_service_client(self):

        url = f"https://{storage_account_name}.blob.core.windows.net/"

        queue_service_client = QueueServiceClient(account_url=url, credential=self.token)

        return queue_service_client

    def __str_to_bool(self, string):
        if string == "True":
            return True

        elif string == "False":
            return False

        else:
            raise ValueError(f"{string} not appropriate sas permission value. Must be True or False.")