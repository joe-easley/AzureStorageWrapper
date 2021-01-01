from azure.storage.queue import QueueClient, AccountSasPermissions, generate_account_sas, QueueSasPermissions

class QueueFunctions:

    def __init__(self, token, sas_duration):
        self.token = token

    def _create_sas_key(self):

        permissions = QueueSasPermissions(read=True)
        
        