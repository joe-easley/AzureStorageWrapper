from azure.storage.blob import BlobServiceClient, generate_container_sas, ContainerSasPermissions, BlobClient, BlobType
from datetime import datetime, timedelta


class BlobFunctions:
    """
    A wrapper on blob storage functions

    Args:
        token(TokenCredentialsClass obj): A token from the authentication module
        storage_account_name(str): Name of the storage account
        container_name(str, Optional): Name of container, required for operations within a container eg blob deletion, blob list etc. Defaults to None.
        sas_duration(int, Optional): Controls how long a container sas is valid for. Defaults to 1 hour
        sas_permissions(dict, Optional): Controls what permissions a SAS has. Defaults to read, write, list and delete permissions.

    Attributes:
        token(TokenCredentialsClass obj): A token from the authentication module
        blob_service_client(BlobServiceClient obj): A blob service client that could be used for operations unsupported by this library
        container_client(ContainerClient obj): A container client that could be used for operations unsupported by this library

    """

    def __init__(self, token, storage_account_name, container_name=None, sas_duration=1, sas_permissions=None):
        self.token = token
        self.storage_account_name = storage_account_name
        self.container_name = container_name
        self.sas_duration = sas_duration
        self.sas_permissions = sas_permissions
        self.blob_service_client = self._create_blob_service_client()
        self.container_client = self._create_container_client()

    def _create_blob_sas_token(self):
        """
        Generates blob sas token

        param storage_account_key: str
        param storage_account_id: str
        param container_name: str

        return sas_key: str
        """

        sas_key = self._create_sas_key()

        return sas_key

    def _create_sas_key(self):

        sas_duration = self.sas_duration

        udk = self.blob_service_client.get_user_delegation_key(key_start_time=datetime.utcnow(), key_expiry_time=datetime.utcnow() + timedelta(hours=sas_duration))

        csp = self.__define_sas_permissions()

        sas_token = generate_container_sas(
            account_name=self.storage_account_name,
            container_name=self.container_name,
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
            read_permissions = self.sas_permissions["read"]
            write_permissions = self.sas_permissions["write"]
            delete_permissions = self.sas_permissions["delete"]
            list_permissions = self.sas_permissions["list"]

            permissions = ContainerSasPermissions(read=read_permissions, write=write_permissions,
                                                  delete=delete_permissions, list=list_permissions)

            return permissions

    def _create_blob_client_from_url(self, blob_name):
        """
        Generates a blob sas url, requires blob_name

        param blob_name: str
        param storage_account_key: str
        param storage_account_id: str

        return blob_client: BlobClientObj
        """

        blob_sas_token = self._create_blob_sas_token()

        blob_sas_url = f"https://{self.storage_account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{blob_sas_token}"

        blob_client = BlobClient.from_blob_url(blob_sas_url)

        return blob_client

    def _create_blob_service_client(self):
        """
        """

        url = f"https://{self.storage_account_name}.blob.core.windows.net/"

        blob_service_client = BlobServiceClient(account_url=url, credential=self.token)

        return blob_service_client

    def _create_container_client(self):
        """
        Generates a container client using blob service client

        param container name: str
        return container_client: ContainerClientObj
        """

        if self.container_name is not None:

            container_client = self.blob_service_client.get_container_client(self.container_name)

            return container_client

        else:
            return None

    def list_blobs(self, name_starts_with="", timeout=10):
        """Returns a generator to list the blobs under the specified container

        Args:
            name_starts_with (str, optional): Filters the results to return only blobs whose names begin with the specified prefix.
            timeout (int, optional): expressed in seconds. Defaults to 10.

        Returns:
            list: list of all blobs in container
        """

        blobs_in_container = self.container_client.list_blobs()

        blobs_list = []

        for blob in blobs_in_container:

            blobs_list.append(blob.name)

        return blobs_list

    def delete_blob(self, blob_name):
        """Deletes a specified blob

        Args:
            blob_name (str): name of blob to delete

        Returns:
            None: None is returned if blob successfully deleted
        """

        self.container_client.delete_blob(blob_name, delete_snapshots=None)

        return None

    def upload_blob(self, blob_name, data, blob_type="BlockBlob"):
        """Creates a new blob from a data source with automatic chunking

        Args:
            blob_name (str or BlobProperties): The blob with which to interact. If specified, this value will override a blob value specified in the blob URL
            data (str): The blob data to upload.
            blob_type (str, optional): The type of the blob. This can be either BlockBlob, PageBlob or AppendBlob. Defaults to "BlockBlob".

        Returns:
            BlobClient: a client with which to interact with the uploaded blob
        """

        blob_client = self._create_blob_client_from_url(blob_name)
        blob_client.upload_blob(data=data, blob_type=blob_type)

        return blob_client

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
            None if deletion is successful

        Raises:
            Exception: If container given does not match instantiated version exception is raised
        """
        if container_name == self.container_name:

            self.container_client.delete_container()

        else:
            raise Exception("Container specified for deletion does not match that instantiated in BlobFunctions class call")

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
        if container_name == self.container_name:

            self.container_client.create_container(container_name, metadata, public_access, kwargs)
            return True

        else:
            raise Exception("Container specified for creation does not match that instantiated in BlobFunctions class call")

    def list_containers(self, **kwargs):
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

        retrieved_containers = self.blob_service_client.list_containers(kwargs)

        return retrieved_containers
