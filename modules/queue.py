from azure.storage.queue import generate_queue_sas, QueueClient, QueueServiceClient, AccountSasPermissions, ResourceTypes generate_account_sas, QueueSasPermissions
from datetime import datetime, timedelta

class QueueFunctions:

    def __init__(self, token, storage_account, queue_name, sas_duration, sas_permissions=None, vault_url=None, secret_name=None):
        self.token = token
        self.sas_permissions = sas_permissions
        self.vault_url = vault_url
        self.secret_name = secret_name
        self.queue_client = self._gen_queue_client(storage_account, queue_name)

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

    def _gen_queue_client(self, storage_account, queue_name):

        url = f"https://{storage_account}.queue.core.windows.net/{queue_name}"

        queue_client = QueueClient().from_queue_url(queue_url=url, credential=self.token)

        return queue_client

    def clear_messages(self, timeout=10):
        """
        Deletes all messages from a queue. Timeout value auto-set to 10seconds.

        param timeout: int
        """

        self.queue_client.clear_messages(timeout=timeout)

    def create_queue(self, metadata, timeout=10):
        """
        Creates a new queue in storage acct. Timeout value auto-set to 10seconds.

        param metadata: dict
        param timeout: int
        """

        self.queue_client.create_queue(metadata=metadata, timeout=timeout)

    def receive_message(self, timeout=10, visibility_timeout=300):
        """
        Removes a message from the front of the queue. 
        Returns QueueMessage Class.
        Server timeout defaults to 10 seconds
        Visibility timeout defaults to 300 seconds

        param timeout: int
        param visibility_timeout: int

        return message: QueueMessage class
        """

        message = self.queue_client.receive_message(visibility_timeout=visibility_timeout, timeout=timeout)

        return message

    def delete_message(self, message, pop_receipt, timeout=10):
        """
        Deletes a message from the queue.
        Timeout defaults to 10 seconds
        Message can either be a message object or id as a str

        param message: str or QueueMessage
        param pop_receipt: str
        param timeout: int
        """

        self.queue_client.delete_message(message=message, pop_receipt=pop_receipt, timeout=timeout)

    def send_message(self, content, visibility_timeout=604800, time_to_live=604800, timeout=10):
        """
        Sends a message to queue.
        Default time to live is 7 days, however this can be specified in seconds. Set to infinity with -1.
        visibility timeout specifies the time that the message will be invisible. After the timeout expires, the message will become visible. Defaults to 7 days

        param content: str
        param visibility_timeout: int

        return sent_message: QueueMessage object
        """

        sent_message = self.queue_client.send_message(content=content, visibility_timeout=visibility_timeout, time_to_live=time_to_live, timeout=timeout)

        return sent_message

    def update_message(self, message, pop_receipt, content, visibility_timeout=604800, timeout=10):
        """
        Updates the visibility timeout of a message, or updates the content of a message
        Server timeout defaults to 10 seconds

        param message: str or QueueMessage
        param pop_receipt: str
        param content: str
        param visibility_timeout: int
        param timeout: int
        """
        updated_message = self.queue_client.update_message(message, pop_receipt=pop_receipt, content=content)