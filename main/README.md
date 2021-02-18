![Behave Tests](https://github.com/joe-easley/AzureStorageWrapper/workflows/Behave%20Tests/badge.svg?branch=main)

# AzureStorageWrapper
A wrapper for azure storage tools

## Setup

The azure storage wrapper requires a configuration dictionary to be setup in order to successfully authenticate and run commands. The module is currently setup to receive a dictionary similar to below.

Example:

    params = {"authentication_method": "user", 
              "client_id": "XXXX",
              "username": "username@username.com",
              "password": "Wouldn'tYouLikeToKnow,
              "sas_duration": "5"}

This can be used using something like:

    authentication_token = AuthenticationFunctions(params).token

The dictionary must include;
- authentication_method (e.g "client_secret" or "user"). See Authentication sections for more information
- sas_duration (in hours)

## Authentication

To use the azure storage functions you must first authenticate.

There are currently two ways of authorising access.

1. As a user

If you have access as user to an azure storage resource then you can authenticate as that user by assigning the value "user" to the authentication key in the params dictionary. If using this method you must also add client_id(aka "tenant id"), username and password as key value pairs to the param dictionary.

[For further information see here](https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.usernamepasswordcredential?view=azure-python)

2. As a service principal

You can use a service principal to authenticate access. You can do this by assigning the value "client_secret" to the authentication key in the params dictionary. If using this method you must also add tenant_id, storage_account_id and storage_account_key as key value pairs to the param dictionary.

[For further information see here](https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.clientsecretcredential?view=azure-python)

The token is stored as an instance variable so could be stored as: 
    token = AuthenticateFunctions(params).token

Further authentication is required for using the FileShareFunctions. FileShareFunctions uses an account key to generate an account sas token. This library requires this account key to be stored as a secret in key vault. 

Therefore to retrieve this secret the FileShareFunctions class must be initiated with a token from the AuthenticateFunctions class as above, but also with a dictionary containing vault_url and secret_name.

Example:

    fileshare_params = {"vault_url": "vault.url.com",
                        "secret_name": "sshh top secret"}

    FileShareFunctions(token, fileshare_params)   


# Supported storage functions

## Blob

The currently supported operations on blob storage use the BlobFunctions class.

The BlobFunctions class must be initiated by passing an authentication credential and a sas duration.

    BlobFunctions(token, sas_duration)

 They have the following methods:

- upload_blob(blob_name, data, container_name, storage_account_name, blob_type)

Uploads a blob to a specified container. No directories exist in blob, but can be inferred in blob name for a virtual directory e.g level1/level2/file. All arguments passed as strings

- delete_blob(storage_account_name, container_name, blob_name)

Deletes a specified blob. Arguments must be passed as a string

- list_blobs(container_name, storage_account_name)

Lists all blobs in a specified container. Returns a list

## FileShare

The FileShareFunctions class must be initiated as above (see authentication section). After that the following methods may be called:

- create_fileshare_directory(share_name, directory_path)

Creates a directory in chosen file share. Returns Directory-updated property dict (Etag and last modified).

- copy_file(share_name, file_path, source_url)

Copies a file from blob or other file share to a specified share machine. On completion returns a [FileProperties](https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.fileproperties?view=azure-python) object

    create_share(share_name, metadata=None, quota=1, timeout=10, share_service_client=None)

Creates a new share in storage_account

    delete_directory(share_name, directory_name)

Deletes the specified empty directory. Note that the directory must be empty before it can be deleted. Attempting to delete directories that are not empty will fail.

    delete_file(share_name, file_name)

Marks the specified file for deletion. The file is later deleted during garbage collection.

    list_directories_and_files(self, share_name, directory_name, name_starts_with, timeout)

Returns a generator to list the directories and files under the specified share.

    list_shares(name_starts_with, include_metadata, include_snapshots, timeout)

Returns list of shares in storage account

    upload_file(share_name, directory_path, file_name, data, metadata, length, max_concurrency)

Uploads a file to a file share

## Currently unsupported FileShare operations
If there are other fileshare operations that are unsupported by this wrapper then you can generate the following clients to interact with them:

- [create_share_service_client()](https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.shareserviceclient?view=azure-python)

This method will allow access to any of the the ShareServiceClient class methods

- [create_share_directory_client(share_name, directory)](https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.sharedirectoryclient?view=azure-python)

This method will allow access to any of the the ShareDirectoryClient class methods

- [create_share_client(share_name)](https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.shareclient?view=azure-python)

This method will allow access to any of the the ShareClient class methods

- [create_share_file_client(share_name, file_path)](https://docs.microsoft.com/en-us/python/api/azure-storage-file-share/azure.storage.fileshare.sharefileclient?view=azure-python)

## Queue

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