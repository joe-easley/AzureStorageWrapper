@storage_wrapper_functions

Feature: Blob storage functionality

    Feature Description

    Background:
        Given parameters are set up

    Scenario Outline: BlobFunctions are used
        # Given a token has been created
        Given credential is generated with <authentication_method>
        And BlobFunctions has been instantiated with all permissions and <container> name
        When a <container> is created
        When a upload to blob function is called
        Then all <container> in storage account are listed
        Then list blobs function is used
        Then blob is deleted
        Then <container> is deleted
        Examples: 
        | authentication_method | container         |
        | client_secret         | testing-container |
