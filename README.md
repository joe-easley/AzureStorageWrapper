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

This can be accessed using something like:

    authentication = AuthenticationFunctions(params).token

The dictionary must include;
- authentication_method (e.g "client_secret" or "user"). See Authentication sections for more information
- sas_duration (in hours)

## Authentication

To use the azure storage functions you must first authenticate.

There are currently two ways of authorising access.

1. As a user

If you have access as user to an azure storage resource then you can authenticate as that user by assigning the value "user" to the authentication key in the params dictionary. If using this method you must also add client_id, username and password as key value pairs to the param dictionary.

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
                        "secret_name": "account_key"}

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

- create_fileshare_directory(storage_account_name, file_share_name, directory_path)

Creates a directory in chosen file share. Returns status