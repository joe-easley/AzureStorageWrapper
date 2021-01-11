@storage_wrapper_functions

Feature: Blob storage functionality

    Feature Description

    Background:
        Given parameters are set up

    Scenario Outline: BlobFunctions are used
        # Given a token has been created
        Given credential is generated with <authentication_method>
        Examples: 
        | authentication_method | 
        | client_secret         | 
        And BlobFunctions has been instantiated with all permissions
        When a upload to blob function is called
        Then list blobs function is used
