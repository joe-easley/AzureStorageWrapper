from azure.storage.queue import generate_queue_sas, QueueClient, QueueServiceClient, AccountSasPermissions, ResourceTypes generate_account_sas, QueueSasPermissions

class QueueFunctions:

    def __init__(self, token, sas_duration, sas_permissions=None):
        self.token = token
        self.sas_permissions = sas_permissions

    def _create_sas_key(self):
        
        queue_service_client = self._generate_queue_service_client(storage_account_name)
        sas_key = 
        ****************
        pass
        
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