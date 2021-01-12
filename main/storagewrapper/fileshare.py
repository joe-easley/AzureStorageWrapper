from azure.keyvault.secrets import SecretClient
from azure.storage.file import FileService
from azure.storage.fileshare import generate_account_sas, ResourceTypes, AccountSasPermissions, ShareServiceClient
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

    def _create_share_service_client(self, share_name):
        account_url = f"https://{self.storage_account_name}.file.core.windows.net/{share_name}"
        sas_token = self._create_sas_for_fileshare()
        share_service_client = ShareServiceClient(account_url=account_url, credential=sas_token)
        return share_service_client

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

    def create_fileshare_directory(self, file_share_name, directory_path, metadata=None, fail_on_exist=False,
                                   file_permission=None, smb_properties=None, timeout=20):
        """Creates a directory in a specified share. If creating low level dir high level must exist.

        Args:
            file_share_name (str): Name of existing share.
            directory_path (str): Name of directory to create, including the path to the parent directory
            metadata (dict(str, str), optional): A dict with name_value pairs to associate with the share as metadata. Defaults to None.
            fail_on_exist (bool, optional): specify whether to throw an exception when the directory exists. False by default. Defaults to False.
            file_permission (str): File permission, a portable SDDL. Defaults to None
            smb_properties (SMBProperties Class, optional): Sets the SMB related file properties. Defaults to None.
            timeout (int, optional): The timeout parameter is expressed in seconds.. Defaults to 20.

        Returns:
            True if directory is created, False if directory already exists
        """

        status = self.file_service.create_directory(share_name=file_share_name, directory_name=directory_path)

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

            self.share_service_client = self._create_share_service_client(share_name=share_name)
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

        status = self.file_service.delete_directory(share_name, directory_name, fail_not_exist, timeout)

        return status

    def delete_file(self, share_name, directory_name, file_name, timeout=20):
        """Marks the specified file for deletion. The file is later deleted during garbage collection.

        Args:
            share_name (str): Name of existing share
            directory_name (str): The path to the directory.
            file_name (str): Name of existing file.
            timeout (int, optional): expressed in seconds. Defaults to 20.
        """

        self.file_service.delete_file(share_name, directory_name, file_name, timeout)

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

            share_service_client = self._create_share_service_client(share_name=share_name)
            self.share_service_client.delete_share(share_name, timeout=timeout, delete_snapshots=delete_snapshots)

            return True

        else:

            self.share_service_client.delete_share(share_name, timeout=timeout, delete_snapshots=delete_snapshots)

            return True

    def exists(self, share_name, directory_name=None, file_name=None, timeout=20, snapshot=None):
        """Returns a boolean indicating whether the share exists if only share name is given
        If directory_name is specificed a boolean will be returned indicating if the directory exists.
        If file_name is specified as well, a boolean will be returned indicating if the file exists.

        Args:
            share_name (str): Name of a share.
            directory_name (str, optional): The path to a directory. Defaults to None.
            file_name (str, optional): Name of a file. Defaults to None.
            timeout (str, optional): Expressed in seconds. Defaults to None.
            snapshot (str, optional): A string that represents the snapshot version, if applicable. Defaults to None.

        Returns:
            bool: A boolean indicating whether the resource exists
        """

        exists = self.file_service.exists(share_name, directory_name, file_name, timeout, snapshot)

        return exists

    def list_directories_and_files(self, share_name, directory_name=None, num_results=5000,
                                   marker=None, timeout=10, prefix=None, snapshot=None):
        """Returns a generator to list the directories and files under the specified share.
        The generator will lazily follow the continuation tokens returned by the service and stop when all directories
        and files have been returned or num_results is reached.

        If num_results is specified and the share has more than that number of files and directories,
        the generator will have a populated next_marker field once it finishes.
        This marker can be used to create a new generator if more results are desired.

        Args:
            share_name (str): Name of existing share.
            directory_name (str, optional): The path to the directory. Defaults to None.
            num_results (int, optional): Specifies the maximum number of files to return, including all directory elements. Defaults to 5000.
            marker (str, optional): An opaque continuation token. This value can be retrieved from the next_marker field of a previous generator objec. Defaults to None.
            timeout (int, optional): expressed in seconds. Defaults to 10.
            prefix (str, optional): list only the files and/or directories with the given prefix. Defaults to None.
            snapshot (str, optional): A string that represents the snapshot version, if applicable. Defaults to None.

        Returns:
            Generator
        """

        list_of_directories_and_files = self.file_service.list_directories_and_files(share_name, directory_name, num_results, marker, timeout, prefix, snapshot)

        return list_of_directories_and_files

    def list_shares(self, prefix=None, marker=None, num_results=None, include_metadata=False, timeout=20, include_snapshots=False):
        """Returns a generator to list the shares under the specified account. The generator will lazily follow the continuation tokens returned by the service
        and stop when all shares have been returned or num_results is reached.

        Args:
            prefix (str, optional): Filters the results to return only shares whose names begin with the specified prefix. Defaults to None.
            marker (str, optional): An opaque continuation token. This value can be retrieved from the next_marker field of a previous generator object. Defaults to None.
            num_results (int, optional): Specifies the maximum number of shares to return. Defaults to None.
            include_metadata (bool, optional): Specifies that share metadata be returned in the response. Defaults to False.
            timeout (int, optional): expressed in seconds. Defaults to 20.
            include_snapshots (bool, optional): Specifies that share snapshots be returned in the response. Defaults to False.

        Returns:
            [type]: [description]
        """

        share_list = self.file_service.list_shares(prefix, marker, num_results, include_metadata, timeout, include_snapshots)

        return share_list
