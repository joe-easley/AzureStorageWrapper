from azure.keyvault.secrets import SecretClient
from azure.storage.file import FileService
from azure.storage.fileshare import generate_account_sas, ResourceTypes, AccountSasPermissions, ShareServiceClient, ShareClient, ShareDirectoryClient
from datetime import datetime, timedelta


class FileShareFunctions:

    def __init__(self, token, storage_account_name, sas_duration=1, vault_url=None, secret_name=None, file_service_client=None):
        self.token = token
        self.vault_url = vault_url
        self.secret_name = secret_name
        self.sas_duration = sas_duration
        self.storage_account_name = storage_account_name
        self.file_service = self._create_file_service()

    def _create_sas_for_fileshare(self):
        """
        Generates sas key for fileshare
        Requires key to account being stored in key vault
        param
        """
        secret = self.__get_secret()

        fs_sas_token = generate_account_sas(
            account_name=self.storage_account_name,
            account_key=secret,
            resource_types=ResourceTypes(service=True, container=True, object=True),
            permission=AccountSasPermissions(read=True, write=True),
            expiry=datetime.utcnow() + timedelta(hours=self.sas_duration)
        )

        return fs_sas_token

    def _create_file_service(self):
        """
        creates file service object
        """

        fs_sas_token = self._create_sas_for_fileshare()

        file_service = FileService(account_name=self.storage_account_name, sas_token=fs_sas_token)

        return file_service

    def _create_share_service_client(self):

        sas_token = self._create_sas_for_fileshare()
        account_url = f"https://{self.storage_account_name}.file.core.windows.net/"
        share_service_client = ShareServiceClient(account_url=account_url, credential=sas_token)

        return share_service_client

    def _get_share_client(self, share_name):
        share_service_client = self._create_share_service_client()
        share_client = share_service_client.get_share_client(share=share_name)

        return share_client

    def _get_directory_client(self, share_name, directory_path):
        share_client = self._get_share_client(share_name)
        share_directory_client = share_client.get_directory_client(directory_path=directory_path)

        return share_directory_client

    def _get_share_file_client(self, share_name, file_path):
        share_client = self._get_share_client(share_name)
        share_file_client = share_client.get_file_client(file_path)

        return share_file_client

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

    def create_fileshare_directory(self, share_name, directory_path):
        """Creates a new directory under the directory referenced by the client..

        Args:
            share_name (str): Name of existing share.
            directory_path (str): Name of directory to create, including the path to the parent directory

        Returns:
            Directory-updated property dict (Etag and last modified).
        """

        share_directory_client = self._get_directory_client(share_name, directory_path)

        status = share_directory_client.create_directory()

        return status

    def copy_file(self, dest_share, directory_name, file_name, copy_source, metadata=None, timeout=20):
        """

        Args:
            dest_share (str): share must exist
            directory_name (str): directory must exis
            file_name (str): If the destination file exists, it will be overwritten. Otherwise, it will be created
            copy_source (str): A URL of up to 2 KB in length that specifies an Azure file or blob
            metadata (dict, optional): Name-value pairs associated with the file as metadata
            timeout (int, optional): expressed in seconds. Defaults to 20.

        Returns:
            CopyProperties: Copy operation properties such as status, source, and ID
        """

        copy_properties = self.file_service.copy_file(share_name=dest_share, directory_name=directory_name,
                                                      file_name=file_name, copy_source=copy_source, metadata=metadata, timeout=timeout)

        return copy_properties

    def create_file_from_bytes(self, share_name, directory_name, file_name, file,
                               index=0, count=None, content_settings=None, metadata=None,
                               validate_content=False, progress_callback=None, max_connections=2,
                               file_permission=None, smb_properties=None, timeout=30):
        """Creates a new file from an array of bytes, or updates the content of an existing file, with automatic chunking and progress notifications.

        Args:

            share_name (str): Name of existing share

            directory_name (str): The path to the directory.

            file_name (str): Name of file to create or update.

            file (str): Content of file as an array of bytes.

            index (int, optional): Start index in the array of bytes. Defaults to 0.

            count (int, optional): Number of bytes to upload. Set to None or negative value to upload all bytes starting from index. Defaults to None.

            content_settings (ContentSettings obj, optional): ContentSettings object used to set file properties. Defaults to None.

            metadata (dict, optional): Name-value pairs associated with the file as metadata. Defaults to None.

            validate_content (bool, optional): If true, calculates an MD5 hash for each range of the file. Defaults to False.

            progress_callback ([type], optional): Callback for progress with signature function(current, total). Defaults to None.

            max_connections (int, optional): Maximum number of parallel connections to use. Defaults to 2.

            file_permission (str, optional): File permission, a portable SDDL. Defaults to None.

            smb_properties (SMbProperties obj, optional): Sets the SMB related file properties. Defaults to None.

            timeout (int, optional):  expressed in seconds. Defaults to 30.
        """

        self.file_service.create_file_from_bytes(share_name, directory_name, file_name, file,
                                                 index, count, content_settings, metadata, validate_content, progress_callback,
                                                 max_connections, file_permission, smb_properties, timeout)

    def __filter_vars(self, **kwargs):
        arguments = {}

        for key, value in kwargs.items():
            if value is not None:
                arguments[key] = value

        return arguments

    def create_share(self, share_name, metadata=None, quota=1, timeout=10, share_service_client=None):
        """Creates a new share in storage_account. If the share with the same name already exists,
        the operation fails on the service. By default, the exception is swallowed by the client unless exposed with fail_on_exist

        Args:

            share_name (str): Name of share to create

            metadata (dict, optional): A dict with name_value pairs to associate with the share as metadata. Defaults to None.

            quota (int, optional): Specifies the maximum size of the share, in gigabytes. Must be greater than 0, and less than or equal to 5TB (5120). Defaults to 1.

            timeout (int, optional): expressed in seconds. Defaults to 10.

            share_service_client (ShareServiceClient obj, optional): If share service client exists can be used here, otherwise a new one is generated. Defaults to None.

        Returns:
            True if share is created, False if already exists
        """

        arguments = self.__filter_vars(share_name=share_name, metadata=metadata, quota=quota, timeout=timeout, share_service_client=share_service_client)
        if share_service_client is None:

            self.share_service_client = self._create_share_service_client()
            status = self.share_service_client.create_share(**arguments)

            return status

        else:

            status = self.share_service_client.create_share(**arguments)

            return status

    # def create_file(self):
    #     ShareFileClient(account_url=, share_name=)

    def delete_directory(self, share_name, directory_name, fail_not_exist=False, timeout=20):
        """Deletes the specified empty directory. Note that the directory must be empty before it can be deleted.
        Attempting to delete directories that are not empty will fail.

        Args:
            share_name (str): Name of existing share.
            directory_name ([str): Name of directory to delete, including the path to the parent directory.
            fail_not_exist (bool, optional): Specify whether to throw an exception when the directory doesn't exist. Defaults to False.
            timeout (int, optional): expressed in seconds. Defaults to 20.

        Returns:
            bool: True if directory is deleted, False otherwise
        """
        directory_client = self._get_directory_client(share_name, directory_name)
        directory_client.delete_directory()

        return True

    def delete_file(self, share_name, file_name):
        """Marks the specified file for deletion. The file is later deleted during garbage collection.

        Args:
            share_name (str): Name of existing share
            directory_name (str): The path to the directory.
            file_name (str): Name of existing file and path.
            timeout (int, optional): expressed in seconds. Defaults to 20.
        """
        share_file_client = self._get_share_file_client(share_name, file_name)
        share_file_client.delete_file()

        return True

    def delete_share(self, share_name, timeout=10, delete_snapshots=None, share_service_client=None):
        """Marks the specified share for deletion. If the share does not exist, the operation fails on the service

        Args:

            share_name (str): [description]

            timeout (int, optional): expressed in seconds. Defaults to 10.

            delete_snapshots (DeleteSnapshot, optional): To delete a share that has snapshots, this must be specified as DeleteSnapshot.Include. Defaults to None.

            share_service_client (ShareServiceClient obj, optional): If share service client exists can be used here, otherwise a new one is generated. Defaults to None.

        Returns:
            bool: True if share is deleted, False share doesn't exist.
        """
        if share_service_client is None:

            share_service_client = self._create_share_service_client()
            self.share_service_client.delete_share(share_name, timeout=timeout, delete_snapshots=delete_snapshots)

            return True

        else:

            self.share_service_client.delete_share(share_name, timeout=timeout, delete_snapshots=delete_snapshots)

            return True

    def list_directories_and_files(self, share_name, directory_name="", name_starts_with="", timeout=10):
        """Returns a generator to list the directories and files under the specified share.
        The generator will lazily follow the continuation tokens returned by the service and stop when all directories
        and files have been returned or num_results is reached.

        Args:
            share_name (str): Name of existing share.
            directory_name (str, optional): The path to the directory. Defaults to "".
            timeout (int, optional): expressed in seconds. Defaults to 10.
            name_starts_with (str, optional): list only the files and/or directories with the given prefix. Defaults to None.

        Returns:
            Generator
        """

        share_client = self._get_share_client(share_name)

        list_of_directories_and_files = share_client.list_directories_and_files(directory_name=directory_name, name_starts_with=name_starts_with)

        return list_of_directories_and_files

    def list_shares(self, name_starts_with="", include_metadata=False, include_snapshots=False, timeout=10):
        """
        Returns list of shares in storage account

        Args:
            name_starts_with (str, optional): Filters the results to return only shares whose names begin with the specified name_starts_with.
            include_metadata (bool, optional): Specifies that share metadata be returned in the response. Defaults to ""
            include_snapshots (bool, optional): Specifies that share snapshot be returned in the response. Defaults to False
            include_deleted (bool, optional): Specifies that deleted shares be returned in the response. This is only for share soft delete enabled account. Defaults to False
            timeout (int, optional): Timeout in seconds, defaults to 10

        Returns:
            List
        """

        share_service_client = self._create_share_service_client()
        shares = share_service_client.list_shares()
        share_list = list(shares)

        return share_list

    def upload_file(self, share_name, directory_path, file_name, data, metadata=None, length=None, max_concurrency=None):
        """
        Uploads a file to a file share
        https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.sharedirectoryclient?view=azure-python#upload-file-file-name--data--length-none----kwargs-

        Args:
            share_name (str): Name of the share to upload data to
            directory_path (str): Path on file share to store data
            file_name (str): Target file name
            data (str): Source of data
            metadata (dict, optional): Name-value pairs associated with the file as metadata.
            length (int, optional): Length of file in bytes (up to 1Tb)

        Returns:
            ShareFileClient class obj 

        """
        share_directory_client = self._get_directory_client(share_name, directory_path)
        share_file_client = share_directory_client.upload_file(file_name=file_name, data=data, metadata=metadata, length=length)

        return share_file_client