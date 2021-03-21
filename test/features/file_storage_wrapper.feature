@file_wrapper_functions

Feature: File storage functionality

    Tests file functionality developed for the azure storage wrapper library

    Scenario Outline: FileShareFunctions are used
        Given parameters are set up for fileshare
        Given credential is generated with <authentication_method> for fileshare
        And FileShareFunctions has been instantiated with all permissions
        When file<share> is called for creation
        When a <directory> is created in <share>
        When a <file> is uploaded to <share> in <directory>
        Then <file> and <directory> are found in <share>
        Examples:
            | authentication_method | share       | directory | file    |
            | client_secret         | test-share  | toplevel  | test.txt|