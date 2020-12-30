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

## Supported storage functions
