# AzureStorageWrapper
A wrapper for azure storage tools

## Authentication

To use the azure storage functions you must first authenticate.

There are currently two ways of authorising

1. As a user
If you have access as user to an azure storage resource then you can authenticate as that user by assigning the value "user" to the authentication key in the params dictionary. If using this method you must also add client_id, username and password as key value pairs to the param dictionary.

[For further information see here](https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.usernamepasswordcredential?view=azure-python)

2. As a service principal

to run MUST have param dict that include
- authentication_method (e.g "client_secret" or "user")
- sas_duration (in hours)