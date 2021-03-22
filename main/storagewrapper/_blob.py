from azure.storage.blob import BlobServiceClient, generate_container_sas, ContainerSasPermissions, BlobClient
from azure.keyvault.secrets import SecretClient
from datetime import datetime
from storagewrapper._exceptions import BlobFunctionsError

import sys


class BlobFunctions:
    """
    A wrapper on blob storage functions

    Args:
        authenticator(AuthenticateFunctions class): provides authentication to service blob functions
        storage_account_name(str): Name of the storage account
        sas_method (str, optional): Controls whether a user delegation key is used to generate SAS or whether an access key stored in key vault is used. If access key then vault_url, access_key_secret_name must be provided. Defaults to UserDelegationKey.
        handle_exceptions (bool, optional): If True exceptions raised are handled silently and passed back as a message in the return, if False raises an exception. Default is False
    
    Attributes:
        token(TokenCredentialsClass obj): A token from the authentication module
        blob_service_client(BlobServiceClient obj): A blob service client that could be used for operations unsupported by this library
        container_client(ContainerClient obj): A container client that could be used for operations unsupported by this library

    """

    def __init__(self, storage_account_name, authenticator, sas_method="UserDelegationKey", vault_url=None, access_key_secret_name=None, handle_exceptions=False):
        self.authenticator = authenticator
        self.token = self.authenticator.token
        self.storage_account_name = storage_account_name
        self.sas_duration = self.authenticator.sas_duration
        self.sas_permissions = self.authenticator.container_sas_permissions
        self.sas_method = sas_method
        self.vault_url = vault_url
        self.access_key_secret_name = access_key_secret_name
        self.handle_exceptions = handle_exceptions
    
    def __str__(self):
        return f"Functions for operating blob storage within storage account:'{self.storage_account_name}'"

    def __handle_errors(self, func_name, error):
        if self.handle_exceptions:

            return False
        
        elif not self.handle_exceptions:

            raise BlobFunctionsError(f"Failed to execute {func_name} with error {error}")

    def __create_blob_sas_token(self, container_name):
        """
        Generates blob sas token

        param storage_account_key: str
        param storage_account_id: str
        param container_name: str

        return sas_key: str
        """

        sas_key = self.__create_sas_key(container_name)

        return sas_key

    def __create_sas_key(self, container_name):

        sas_token = self.__access_key_or_udk(container_name)

        return sas_token

    def __access_key_or_udk(self, container_name):
        """Checks if access key is required or if User Delegation Key method is

        Returns:
            str: SAS token
        """

        if self.sas_method == "UserDelegationKey":

            blob_service_client = self.__create_blob_service_client()

            udk = blob_service_client.get_user_delegation_key(key_start_time=datetime.utcnow(),
                                                              key_expiry_time=datetime.utcnow() + timedelta(hours=self.sas_duration))

            sas_token = generate_container_sas(
                account_name=self.storage_account_name,
                container_name=container_name,
                user_delegation_key=udk,
                permission=self.sas_permissions,
                expiry=datetime.utcnow() + self.sas_duration
            )

            return sas_token

        elif self.sas_method == "AccessKey":

            access_key = self.__get_secret()

            sas_token = generate_container_sas(
                account_name=self.storage_account_name,
                container_name=self.container_name,
                account_key=access_key,
                permission=self.sas_permissions,
                expiry=datetime.utcnow() + self.sas_duration
            )

            return sas_token

        else:
            raise Exception("sas_method not UserDelegationKey or AccessKey")

    def __get_secret(self):
        """
        Retrieves storage acct access key from key vault

        return secret
        """

        secret_client = SecretClient(vault_url=self.vault_url, credential=self.token)
        secret = secret_client.get_secret(self.access_key_secret_name)

        return secret.value

    def __create_blob_client_from_url(self, blob_name, container_name):
        """
        Generates a blob sas url, requires blob_name

        param blob_name: str
        param storage_account_key: str
        param storage_account_id: str

        return blob_client: BlobClientObj
        """

        blob_sas_token = self.__create_blob_sas_token(container_name=container_name)

        blob_sas_url = f"https://{self.storage_account_name}.blob.core.windows.net/{container_name}/{blob_name}?{blob_sas_token}"

        blob_client = BlobClient.from_blob_url(blob_sas_url)

        return blob_client

    def __create_blob_service_client(self):
        """
        """

        url = f"https://{self.storage_account_name}.blob.core.windows.net/"

        blob_service_client = BlobServiceClient(account_url=url, credential=self.token)

        return blob_service_client

    def __create_container_client(self, container_name):
        """
        Generates a container client using blob service client

        param container name: str
        return container_client: ContainerClientObj
        """

        blob_service_client = self.__create_blob_service_client()

        container_client = blob_service_client.get_container_client(container_name)

        return container_client

    def list_blobs(self, container_name, name_starts_with="", timeout=10):
        """Returns a generator to list the blobs under the specified container

        Args:
            name_starts_with (str, optional): Filters the results to return only blobs whose names begin with the specified prefix.
            timeout (int, optional): expressed in seconds. Defaults to 10.

        Returns:
            list: list of all blobs in container
        """
        try:
            container_client = self.__create_container_client(container_name=container_name)

            blobs_in_container = container_client.list_blobs()

            blobs_list = []

            for blob in blobs_in_container:

                blobs_list.append(blob.name)

            return blobs_list
        
        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def delete_blob(self, blob_name, container_name):
        """Deletes a specified blob

        Args:
            blob_name (str): name of blob to delete

        Returns:
            True: True is returned if blob successfully deleted
        """
        try:
            
            container_client = self.__create_container_client(container_name=container_name)

            container_client.delete_blob(blob_name, delete_snapshots=None)

            return True
        
        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def upload_blob(self, blob_name, data, container_name, overwrite=True, blob_type="BlockBlob"):
        """Creates a new blob from a data source with automatic chunking

        Args:
            blob_name (str or BlobProperties): The blob with which to interact. If specified, this value will override a blob value specified in the blob URL
            data (str): The blob data to upload.
            container_name (str): Name of container to upload blob to
            overwrite (bool, opt): Whether an existing blob should be overwritten. Defualts to True
            blob_type (str, optional): The type of the blob. This can be either BlockBlob, PageBlob or AppendBlob. Defaults to "BlockBlob".

        Returns:
            BlobClient: a client with which to interact with the uploaded blob
        """
        try:

            blob_client = self.__create_blob_client_from_url(blob_name, container_name)
            blob_client = blob_client.upload_blob(data=data, blob_type=blob_type, overwrite=overwrite)

            return blob_client
        
        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def delete_container(self, container_name, lease=None, if_modified_since=None, if_unmodified_since=None, etag=None, match_condition=None, timeout=20):
        """Deletes a specified container

        Args:
            container_name (str): Name of container
            lease (optional): only deletes if container has active lease and matches this ID
            if_modified_since (datetime, optional): A datetime value. Azure expects this to be utc
            if_unmodified_since (datetime, optional): A datetime value. Azure expects this to be utc
            etag (str, optional): An ETag value, or the wildcard character (*)
            match_condition (MatchConditions obj, optional): The match condition to use upon the etag.
            timeout (int, optional): Expressed in seconds. Defaults to 20

        Returns:
            True if deletion is successful

        Raises:
            Exception: If container given does not match instantiated version exception is raised
        """
        try:

            container_client = self.__create_container_client(container_name)

            container_client.delete_container()

            return True

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def create_container(self, container_name, metadata=None, public_access=None, **kwargs):
        """Creates a new container under the specified account. If the container with the same name already exists, the operation fails.

        Args:
            container_name (str): Name of container
            metadata ([type], optional): [description]. Defaults to None.
            public_access ([type], optional): [description]. Defaults to None.

        Returns:
            Bool: True if container is created

        Raises:
            Exception: If container given does not match instantiated version exception is raised
        """
        try:

            blob_service_client = self.__create_blob_service_client()

            if metadata is None:
                blob_service_client.create_container(container_name)

            elif metadata is not None:

                blob_service_client.create_container(container_name, metadata)

            return True

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def list_containers(self, name_starts_with=None, include_metadata=False, include_deleted=False, results_per_page=5000, timeout=10):
        """
        Returns a generator to list the containers under the specified account.

        The generator will lazily follow the continuation tokens returned by the service and stop when all containers have been returned.

        Args:
            name_starts_with (str, optional): Filters the results to return only containers whose names begin with the specified prefix. Defaults to None.
            include_metadata (bool, optional): Specifies that container metadata to be returned in the response. Defaults to False.
            include_deleted (bool, optional): Specifies that deleted containers to be returned in the response. Defaults to False.
            results_per_page (int, optional): The maximum number of container names to retrieve per API call. Defaults to 5000.
            timeout (int, optional): expressed in seconds. Defaults to 10.

        Returns:
            ListGenerator: a generator to list containers under specified account
        """
        try:

            blob_service_client = self.__create_blob_service_client()

            retrieved_containers = blob_service_client.list_containers(name_starts_with=name_starts_with, include_metadata=include_metadata,
                                                                       include_deleted=include_deleted, results_per_page=results_per_page, timeout=timeout)
            return retrieved_containers

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status
