# AzureStorageWrapper

![Behave Tests](https://github.com/joe-easley/AzureStorageWrapper/workflows/Behave%20Tests/badge.svg?branch=main)

A wrapper for azure storage tools.

Tests currently failing due to azure test account being temporarily unavailable. Blob functions and most file functions have been recently tested and are working as expected.

## Setup

To run functions you must authenticate. The Authentication module (below) can do this, though if you have a [token credential object](https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity?view=azure-python) then you can pass this directly to the storage functions classes and bypass the Authentication module.

## Authentication

To use the azure storage functions you must first authenticate.

An instantiated AuthenticateFunctions class object will provide the authorisation necessary to run BlobFunctions and FileShareFunctions. When one of the methods belonging to BlobFunctions or FileShareFunctions is run, it will generate a SAS token to create, update or delete resources. If left unspecified, the SAS that is generated resorts to *most permissive*. This is order for this library to be as user friendly to use as possible, however it is *strongly* recommended that you specify what permissions the SAS will allow. For more information on [Blob](https://docs.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.containersaspermissions?view=azure-python) and [FileShare](https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.accountsaspermissions?view=azure-python) SAS permissions.

By specifying a permission as False (as below) the SAS will default to generating no credentials for that storage type.

The SAS duration will default to 1 hour unless otherwise specified, this can be overridden as below.

    sas_permissions = {
                        "container_permissions":
                            {
                                "read": True,
                                "write": True,
                                "delete": True,
                                "delete_previous_version": True,
                                "list":True,
                                "tag": True
                            },
                        "file_permissions":
                            {
                                "read": True,
                                "write": True,
                                "delete": True,
                                "delete_previous_version": True,
                                "list": True,
                                "add": True,
                                "create": True,
                                "update": True,
                                "process": True,
                                "tag": True,
                                "filter_by_tags": True}
                             },
                        "queue_permissions": False
                      }
    sas_duration = 1

There are currently two ways of authorising access.

1. As a user

If you have access as user to an azure storage resource then you can authenticate as that user by assigning the value "user" to the authentication key in the params dictionary. If using this method you must also add client_id(aka "tenant id"), username and password as key value pairs to the param dictionary.

[For further information see here](https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.usernamepasswordcredential?view=azure-python)

    params = {"authentication_method": "user",
              "client_id": "XXXX",
              "username": "joebloggs@microsoft.com",
              "password": "password123",
              "sas_permissions": sas_permissions,
              "sas_duration": sas_duration}
    
    authenticator = AuthenticateFunctions(params)

1. As a service principal

You can use a service principal to authenticate access. You can do this by assigning the value "client_secret" to the authentication key in the params dictionary. If using this method you must also add tenant_id, app_id and app_key as key-value pairs to the param dictionary.

[For further information see here](https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.clientsecretcredential?view=azure-python)

    params = {"authentication_method": "user",
              "client_id": "XXXX",
              "app_id": "applicationId",
              "app_key": "applicationKey",
              "sas_permissions": sas_permissions,
              "sas_duration": sas_duration}
    
    authenticator = AuthenticateFunctions(params)

Further authentication is required for using the FileShareFunctions. FileShareFunctions uses an account key to generate an account sas token. This library requires this account key to either be given as an argument during instantiation, or vault url and secret name given so that this secret can be retrieved. More information below.

BlobFunctions and FileShareFunctions are

## Supported storage functions

### Blob

The currently supported operations on blob storage use the BlobFunctions class.

The BlobFunctions class must be initiated by passing an authentication credential and a sas duration.

Asterisk denotes optional parameter

    BlobFunctions(storage_account_name, authenticator, sas_method*, vault_url*, access_key_secret_name*, handle_exceptions*)

 They have the following methods:

- upload_blob(blob_name:str, data:str, container_name:str, overwrite*:bool, blob_type*:str)

Uploads a blob to a specified container. No directories exist in blob, but can be inferred in blob name for a virtual directory e.g level1/level2/file. All arguments passed as strings

- delete_container(container_name:str, lease*:str, if_modified_since*:str, if_unmodified_since*:str, etag*:str, match_condition*:str, timeout*:int)

Deletes a container

- create_container(container_name:str, metadata:dict, public_access:str/[PublicAccess](https://docs.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.publicaccess?view=azure-python))
  
- delete_blob(storage_account_name, container_name, blob_name)

Deletes a specified blob. Arguments must be passed as a string

- list_blobs(container_name, storage_account_name)

Lists all blobs in a specified container. Returns a list

### FileShare

The FileShareFunctions class must be initiated as above (see authentication section). After that the following methods may be called:

- Copy File

    copy_file(share_name, file_path, source_url)

Copies a file from blob or other file share to a specified share machine. On completion returns a [FileProperties](https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.fileproperties?view=azure-python) object

- Create Directory

    create_fileshare_directory(share_name, directory_path, recursive*)

Creates a directory in chosen file share. Returns True if successful. If recursive=True then will allow for recursive directory creation eg topdir/middledir/bottomdir would be created.

- Create new File Share

    create_share(share_name, quota*=1*, access_tier*, metadata*, timeout*)

Creates a new share in storage_account

- Delete directory

    delete_directory(share_name, directory_name, recursive, delete_files)

If recursive=False then deletes the specified empty directory. Note that the directory must be empty before it can be deleted. Attempting to delete directories that are not empty will fail.

If recursive=True will recursively delete all directories below target directory, if delete_files=True then will delete all files encountered.

- Delete File

    delete_file(share_name, file_name)

Marks the specified file for deletion. The file is later deleted during garbage collection.

- Delete Share
  
    delete_share

- List directories and files on share

    list_directories_and_files(self, share_name, directory_name, name_starts_with, timeout)

Returns a generator to list the directories and files under the specified share.

- List all File Shares

    list_shares(name_starts_with, include_metadata, include_snapshots, timeout)

Returns list of shares in storage account

- Upload file to File Share

    upload_file(share_name, directory_path, file_name, data, metadata, length, max_concurrency)

Uploads a file to a file share

### Currently unsupported FileShare operations

If there are other fileshare operations that are unsupported by this wrapper then you can generate the following clients to interact with them:

- [create_share_service_client()](https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.shareserviceclient?view=azure-python)

This method will allow access to any of the the ShareServiceClient class methods

- [create_share_directory_client(share_name, directory)](https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.sharedirectoryclient?view=azure-python)

This method will allow access to any of the the ShareDirectoryClient class methods

- [create_share_client(share_name)](https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.shareclient?view=azure-python)

This method will allow access to any of the the ShareClient class methods

- [create_share_file_client(share_name, file_path)](https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.sharefileclient?view=azure-python)

This method will allow access to any of the the ShareFileClient class methods

### Queue

Queue operations use the QueueFunctions class. This can be instantiated by at a minimum passing an authentication token and storage account name.

    QueueFunctions(token, storage_account_name)

To use the functions a queue client or service client will be required. If you have an existing queue client then this can be used:

    QueueFunctions(token, storage_account_name, queue_client)

If not then one can be generated by passing in the storage account and queue names

    QueueFunctions(token, storage_account=storage_account_name, queue_name=queue_name)

Once the class has been successfully set up then the following functions can be used;

- clear_messages(timeout)

Deletes all messages in a queue. Optional param to control server timeout, default is 10 seconds

- receive_message(timeout, visibility_timeout)

Removes a message from front of queue. Returns a [QueueMessageClass obj](https://docs.microsoft.com/en-us/python/api/azure-storage-queue/azure.storage.queue.queuemessage?view=azure-python). Optional paramaters to control server timeout (default is 10 seconds) and visibility_timeout (default 300 secs)

- delete_message(message, pop_receipt, timeout)

Deletes a message from the queue
Requires either a [QueueMessageClass obj](https://docs.microsoft.com/en-us/python/api/azure-storage-queue/azure.storage.queue.queuemessage?view=azure-python) or a Message id as a str.

- send_message(content, visibility_timeout, time_to_live)

Sends a message to queue.
Default time to live is 7 days, however this can be specified in seconds. Set to infinity with -1.
visibility timeout specifies the time that the message will be invisible. After the timeout expires, the message will become visible. Defaults to 7 days

- update_message(message, pop_receipt, content, visibility_timeout)
Updates the visibility timeout of a message, or updates the content of a message. Server timeout defaults to 10 seconds

- create_queue(name, metadata)
Creates a queue in a storage account. Metadata can be passed in as key:value pairs. Optional timeout param (default 10 secs)

- delete_queue(queue_name)

Deletes a queue and all contained messages. Operation takes 40 secs or more so amend timeout value accordingly (default is 2 mins)

- list_queues()
Returns a generator to list queues under specified storage account.
Optional params:
    name_starts_with(str)
    include_metadate(Bool)
    results_per_page(int)
    timeout(int)
