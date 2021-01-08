@storage_wrapper_functions

Feature: Blob storage functionality

    Feature Description

    Background:
        Given parameters are set up
        And credential is generated with <authentication_method>
        | authentication_method |
        | client_secret         |

    Scenario: BlobFunctions are used
        Given a token has been created
        And BlobFunctions has been instantiated with all permissions
