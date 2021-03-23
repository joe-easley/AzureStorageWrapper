from azure.storage.queue import QueueServiceClient
from storagewrapper._exceptions import QueueFunctionsError
import sys


class QueueFunctions:
    """
    Using a token generated in AuthenticateFunctions gives access to the following queue functions.

    clear messages
    receive message
    delete message
    send message
    update message
    create queue
    delete queue

    Required params:

    param token: Authentication.token

    Optional params:

    handle_exceptions (bool): If True will handle exceptions. Defaults to False

    If a queue client exists (eg after using create queue) then this can be client can be used rather than a fresh client being generated
    """

    def __init__(self, authenticator, storage_account_name, handle_exceptions=False):
        self.authenticator = authenticator
        self.token = self.authenticator.token
        self.storage_account_name = storage_account_name
        self.handle_exceptions = handle_exceptions

    def __str__(self):
        return f"Functions for operating queue storage within storage account:'{self.storage_account_name}'"

    def __handle_errors(self, func_name, error, exception_type=None):

        error_message = f"{error} in {func_name}"

        if self.handle_exceptions:

            return False
        
        elif not self.handle_exceptions:

            self.__raise_exceptions(message=error_message, exception_type=exception_type)

    def __raise_exceptions(self, message, exception_type):

        if exception_type is None:

            raise QueueFunctionsError(message)

        else:
            raise exception_type(message)

    def _generate_queue_service_client(self):
        """
        Creates a queue service client using a token created by authentication module

        param storage_account_name: str
        param token: Authentication obj

        return QueueServiceClient obj
        """

        url = f"https://{self.storage_account_name}.blob.core.windows.net/"

        queue_service_client = QueueServiceClient(account_url=url, credential=self.token)

        return queue_service_client

    def _gen_queue_client(self, queue_name):
        """
        Generates a queue client using a queue service client
        param storage_account: str
        param queue_name: str

        return QueueClient obj
        """
        queue_service_client = self._generate_queue_service_client()
        queue_client = queue_service_client.get_queue_client(queue_name)

        return queue_client

    def create_queue(self, name, metadata=None, timeout=10):
        """
        Creates a new queue in storage acct. Timeout value auto-set to 10seconds.
        Returns a queue client object for created queue

        param name: name
        param metadata: dict
        param timeout: int

        return QueueClient obj

        """

        try:

            queue_service_client = self._generate_queue_service_client()
            queue_service_client.create_queue(name=name, metadata=metadata, timeout=timeout)

            return True

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def clear_messages(self, queue_name, timeout=10):
        """
        Deletes all messages from a queue. Timeout value auto-set to 10seconds.

        param timeout: int
        """
        try:
            queue_client = self._gen_queue_client(queue_name=queue_name)
            queue_client.clear_messages(timeout=timeout)

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

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
        try:
            message = self.queue_client.receive_message(visibility_timeout=visibility_timeout, timeout=timeout)

            return message

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def delete_message(self, message, pop_receipt, timeout=10):
        """
        Deletes a message from the queue.
        Timeout defaults to 10 seconds
        Message can either be a message object or id as a str

        param message: str or QueueMessage
        param pop_receipt: str
        param timeout: int

        return None
        """
        try:

            self.queue_client.delete_message(message=message, pop_receipt=pop_receipt, timeout=timeout)

            return None

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def send_message(self, content, visibility_timeout=604800, time_to_live=604800, timeout=10):
        """
        Sends a message to queue.
        Default time to live is 7 days, however this can be specified in seconds. Set to infinity with -1.
        visibility timeout specifies the time that the message will be invisible. After the timeout expires, the message will become visible. Defaults to 7 days

        param content: str
        param visibility_timeout: int

        return sent_message: QueueMessage object
        """
        try:

            sent_message = self.queue_client.send_message(content=content, visibility_timeout=visibility_timeout, time_to_live=time_to_live, timeout=timeout)

            return sent_message

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def update_message(self, message, pop_receipt, content, visibility_timeout=604800, timeout=10):
        """
        Updates the visibility timeout of a message, or updates the content of a message
        Server timeout defaults to 10 seconds

        param message: str or QueueMessage
        param pop_receipt: str
        param content: str
        param visibility_timeout: int
        param timeout: int

        return updated_message: QueueMessage object
        """

        try:
            updated_message = self.queue_client.update_message(message, pop_receipt=pop_receipt, content=content)

            return updated_message

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def delete_queue(self, queue_name, timeout=120):
        """
        Deletes the queue and all contained messages
        Operation likely to take at least 40 seconds. Configure timeout accordingly. Default 120 seconds

        param queue_name: str
        param timeout: int (secs)

        return None
        """

        try:
            queue_service_client = self._generate_queue_service_client()
            queue_service_client.delete_queue(queue=queue_name, timeout=timeout)

            return None

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def list_queues(self, name_starts_with="", include_metadata=True, results_per_page=100, timeout=60):
        """
        Returns a generator to list the queues under the specified account.
        The generator will lazily follow the continuation tokens returned by the service and stop when all queues have been returned.
        All params are optional, default behaviour is to list all queues in specified account.

        param name_starts_with: str
        param include_metadata: bool default=True,
        results_per_page: int
        param timeout: int

        return iterable (auto-paging) of QueueProperties

        """
        try:
            queue_service_client = self._generate_queue_service_client()
            list_queues = queue_service_client.list_queues(
                name_starts_with=name_starts_with,
                include_metadata=include_metadata,
                results_per_page=results_per_page,
                timeout=timeout
            )

            return list_queues

        except Exception as e:
                
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def create_queue_service_client(self):
        queue_service_client = self._generate_queue_service_client()
        return queue_service_client
