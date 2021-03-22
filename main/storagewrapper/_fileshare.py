from azure.keyvault.secrets import SecretClient
from azure.storage.fileshare import generate_account_sas, ResourceTypes, AccountSasPermissions, ShareServiceClient, ShareClient, ShareDirectoryClient, ShareAccessTier
from datetime import datetime
from storagewrapper._exceptions import FileShareFunctionsError, InitialisationError
import sys


class FileShareFunctions:
    """
        Initialiser for FileShareFunctions class obj

        For authentication requirements to be met one of the following two configurations must be provided

        1. A Storage Account Access Key is provided during initialisation
        2. A token credential from AuthenticateFunctions, along with a key vault url and secret name. The storage account access key must be stored as a secret in this key vault

        Args:
            storage_account_name (str): Name of the storage account
            storage_account_access_key (str, optional): Access key that will authenticate operations of this library
            vault_url (str, optional): URL of key vault in which account access key is stored
            secret_name (str, optional): Name of the access key secret which is stored in key vault
            token(token obj, optional): Credential created in AuthenticateFunctions
    """

    def __init__(self, storage_account_name, authenticator, storage_account_access_key=None, vault_url=None, secret_name=None, handle_exceptions=False):
        self.storage_account_name = storage_account_name
        self.authenticator = authenticator
        self.sas_duration = self.authenticator.sas_duration
        self.token = self.authenticator.token
        self.sas_permissions = self.authenticator.fileshare_sas_permissions
        self.storage_account_access_key = storage_account_access_key
        self.vault_url = vault_url
        self.secret_name = secret_name
        
        self.handle_exceptions = handle_exceptions
        
    def __str__(self):
        return f"Functions for operating fileshare storage within storage account:'{self.storage_account_name}'"

    def __handle_errors(self, func_name, error, exception_type=None):

        error_message = f"{error} in {func_name}"

        if self.handle_exceptions:

            return False
        
        elif not self.handle_exceptions:

            self.__raise_exceptions(message=error_message, exception_type=exception_type)

    def __raise_exceptions(self, message, exception_type):

        if exception_type is None:

            raise FileShareFunctionsError(message)

        else:
            raise exception_type(message)

    def _create_sas_for_fileshare(self):
        """
        Generates sas key for fileshare
        Requires key to account being stored in key vault
        param
        """
        if self.storage_account_access_key is None:
            secret = self.__get_secret()

            fs_sas_token = generate_account_sas(
                account_name=self.storage_account_name,
                account_key=secret,
                resource_types=ResourceTypes(service=True, container=True, object=True),
                permission=self.sas_permissions,
                expiry=datetime.utcnow() + self.sas_duration
            )

            return fs_sas_token
        
        else:

            fs_sas_token = generate_account_sas(
                account_name=self.storage_account_name,
                account_key=self.storage_account_access_key,
                resource_types=ResourceTypes(service=True, container=True, object=True),
                permission=self.sas_permissions,
                expiry=datetime.utcnow() + self.sas_duration
            )

            return fs_sas_token

    def _create_share_service_client(self):
        
        sas_token = self._create_sas_for_fileshare()
        account_url = f"https://{self.storage_account_name}.file.core.windows.net/"
        share_service_client = ShareServiceClient(account_url=account_url, credential=sas_token)

        return share_service_client

    def _get_share_client(self, share_name):
        fs_sas = self._create_sas_for_fileshare()
        account_url = f"https://{self.storage_account_name}.file.core.windows.net"
        share_client = ShareClient(account_url=account_url, share_name=share_name, credential=fs_sas)

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
        if self.vault_url is None:

            self.__handle_errors("init", error="vault_url not initialised", exception_type=InitialisationError)

        if self.secret_name is None:

            self.__handle_errors("init", error="secret_name not initialised", exception_type=InitialisationError)

        if self.token is None:
            
            self.__handle_errors("Retrieving secret", error="token not provided", exception_type=InitialisationError)

        secret_client = SecretClient(vault_url=self.vault_url, credential=self.token)
        secret = secret_client.get_secret(self.secret_name)

        return secret.value

    def copy_file(self, share_name, file_path, source_url):
        """
        Copies a file from a url to file share destination
        
        Args:
            share_name (str): share must exist
            file_path (str): full file path
            source_url (str): source url of file to be copied. May need to authenticate url with sas if in azure storage

        Returns:
            FileProperties Class Obj
            https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.fileproperties?view=azure-python
        """
        try:
            share_file_client = self._get_share_file_client(share_name, file_path)

            share_file_client.start_copy_from_url(source_url)

            file_properties = share_file_client.get_file_properties(timeout=10)

            return file_properties
        
        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def create_fileshare_directory(self, share_name, directory_path, recursive=False):
        """Creates a new directory under the directory referenced by the client..

        Args:
            share_name (str): Name of existing share.
            directory_path (str): Name of directory to create, including the path to the parent directory

        Returns:
            True if successful.
        """
        try:
            if not recursive:

                share_directory_client = self._get_directory_client(share_name, directory_path)

                share_directory_client.create_directory()

                return True

            elif recursive:

                path = ""
                directories = directory_path.split("/")
                path = directories[0]

                share_directory_client = self._get_directory_client(share_name, path)
                share_directory_client.create_directory()

                for directory in directories[1:]:
                    path = f"{path}/{directory}"
                    
                    print(path)
                    
                    share_directory_client = self._get_directory_client(share_name, path)
                    share_directory_client.create_directory()
                
                return True

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def create_share(self, share_name, quota=1, access_tier="Hot", metadata=None, timeout=10):
        """
        Creates a file share within the initiated storage account

        Args:
            share_name (str): Name of share to be created
            quota (int, optional): Volume of file share being created in bytes. Defaults to 1073741824 (1Gb)
            access_tier (str, optional): Either "Hot", "TransactionOptimized" or "Cool". Defaults to Hot.
            metadata (dict, optional): Name-value pairs associated with the share as metadata. Defaults to None
            timeout (int, optional): server timeout expressed in seconds. Defaults to 10
        """

        try:
            share_client = self._get_share_client(share_name=share_name)

            share_client = share_client.create_share(quota=quota, access_tier=ShareAccessTier(access_tier), timeout=timeout, metadata=metadata)

            return share_client
        
        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def create_share_client(self, share_name):
        """
        For operations not supported by the storage wrapper this method will create a share client.
        
            Args:
                share_name (str): name of share


            Returns:
                ShareDirectoryClient class obj
                https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.shareclient?view=azure-python
        """
        try:
            share_client = self._get_share_client(share_name)

            return share_client

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def create_share_directory_client(self, share_name, directory):
        """
        For operations not supported by the storage wrapper this method will create a share directory client.
        
            Args:
                share_name (str): name of share in which directory resides
                directory (str): directory name within share

            Returns:
                ShareDirectoryClient class obj
                https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.sharedirectoryclient?view=azure-python
        """
        try:
            share_directory_client = self._get_directory_client(share_name, directory)

            return share_directory_client

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def create_share_file_client(self, share_name, file_path):
        """
        For operations not supported by the storage wrapper this method will create a share file client.
        
            Args:
                share_name (str): name of share in which directory resides
                directory (str): directory name within share

            Returns:
                ShareFileClient class obj
                https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.sharefileclient?view=azure-python
        """
        try:

            share_file_client = self._get_share_file_client(share_name, file_path)

            return share_file_client

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def create_share_service_client(self):
        """
        For operations not supported by the storage wrapper this method will create a share service client.
        
            Returns:
                ShareServiceClient class obj
                https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.shareserviceclient?view=azure-python
        """

        try:

            share_service_client = self._create_share_service_client()
            return share_service_client

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status
    
    def delete_directory(self, share_name, directory_name, recursive=False, delete_files=False, timeout=10):
        """Deletes the specified empty directory. Note that the directory must be empty before it can be deleted.
        Attempting to delete directories that are not empty will fail.
        Can delete all folders below specified directory recursively

        Args:
            share_name (str): Name of existing share.
            directory_name (str): Name of directory to delete, including the path to the parent directory.
            timeout (int, optional): expressed in seconds. Defaults to 20.

        Returns:
            bool: True if directory is deleted, False otherwise
        """

        try:
            if recursive:

                self.files = []
                self.directories = []

                self.__recursively_generate_list_of_files_and_dirs(self, share_name, directory_name)
                
                if delete_files:

                    for file in self.files:

                        self.delete_file(share_name=share_name, file_path=file)

                
                for directory in self.directories:

                    directory_client = self._get_directory_client(share_name, directory)
                    directory_client.delete_directory(timeout=timeout)
                
                return True
            
            elif not recursive:

                directory_client = self._get_directory_client(share_name, directory_name)
                directory_client.delete_directory(timeout=timeout)

                return True

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def delete_file(self, share_name, file_path):
        """Marks the specified file for deletion. The file is later deleted during garbage collection.

        Args:
            share_name (str): Name of existing share
            file_path (str): Name of existing file and path.
            timeout (int, optional): expressed in seconds. Defaults to 20.
        """

        try:

            share_file_client = self._get_share_file_client(share_name, file_path)
            share_file_client.delete_file()

            return True

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def delete_files(self, share_name, directory_name, file_names, recursive=False, delete_directory=True):
        """Deletes multiple files. If recursive is selected then all files within the specified directory and below will be deleted,
        default behaviour for recursive deletion is for directories to also be removed, can be controlled with delete_directories.

        Args:
            share_name ([str]): Name of the share
            file_names (list)
            recursive (bool, optional): True will recursively delete all files and folders below parent directory. Defaults to False.
            delete_directory(bool, optional): True will delete folders during a recursive deletion. Defaults to False
        """

        try:

            if recursive:

                self.files = []
                self.directories = []

                self.__recursively_generate_list_of_files_and_dirs(share_name, directory_name)

                for file in self.files:
                    self.delete_file(share_name=share_name, file_path=file)
                
                if delete_directory:

                    for directory in self.directories:

                        self.delete_directory(share_name=share_name, directory_name=directory)
                
                return True

            elif not recursive:
                
                for file in file_names:

                    file_path = f"{directory_name}/{file}"

                    self.delete_file(share_name=share_name, file_path=file_path)

                return True

            else:

                raise FileShareFunctionsError("Recursive argument not recognised")

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def __recursively_generate_list_of_files_and_dirs(self, share_name, directory_name):

        files_and_dirs = self.list_directories_and_files(share_name, directory_name)

        for file in files_and_dirs:
            
            if file['is_directory']:
                
                sub_dir = f"{directory_name}/{file['name']}"

                self.directories.append(sub_dir)

                self.__recursively_generate_list_of_files_and_dirs(share_name, directory_name=sub_dir)

            elif not file['is_directory']:

                file_path = f"{directory_name}/{file['name']}"

                self.files.append(file_path)

    def delete_share(self, share_name, timeout=10, delete_snapshots=None):
        """Marks the specified share for deletion. If the share does not exist, the operation fails on the service

        Args:

            share_name (str): [description]

            timeout (int, optional): expressed in seconds. Defaults to 10.

            delete_snapshots (DeleteSnapshot, optional): To delete a share that has snapshots, this must be specified as DeleteSnapshot.Include. Defaults to None.

        Returns:
            bool: True if share is deleted, False share doesn't exist.
        """
        try:

            share_service_client = self._create_share_service_client()
            share_service_client.delete_share(share_name, timeout=timeout, delete_snapshots=delete_snapshots)

            return True
        
        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

    def list_directories_and_files(self, share_name, directory_name="", name_starts_with="", marker="", timeout=10):
        """Returns a generator to list the directories and files under the specified share.
        The generator will lazily follow the continuation tokens returned by the service and stop when all directories
        and files have been returned or num_results is reached.

        Args:
            share_name (str): Name of existing share.
            directory_name (str): The path to the directory.
            name_starts_with (str, optional): list only the files and/or directories with the given prefix. Defaults to None.
            marker (str, optional): An opaque continuation token. This value can be retrieved from the next_marker field of a previous generator object. If specified, this generator will begin returning results from this point.
            timeout (int, optional): expressed in seconds. Defaults to 10.
            

        Returns:
            Generator
        """
        try:

            directory_client = self._get_directory_client(share_name=share_name, directory_path=directory_name)

            list_of_directories_and_files = directory_client.list_directories_and_files()

            return list_of_directories_and_files

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

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
        try:

            share_service_client = self._create_share_service_client()
            shares = share_service_client.list_shares()
            share_list = list(shares)

            return share_list

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status

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

        try:

            share_directory_client = self._get_directory_client(share_name, directory_path)
            share_file_client = share_directory_client.upload_file(file_name=file_name, data=data, metadata=metadata, length=length)

            return share_file_client

        except Exception as e:
            
            status = self.__handle_errors(sys._getframe().f_code.co_name, e)

            return status
