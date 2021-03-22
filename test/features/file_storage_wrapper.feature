@file_wrapper_functions

Feature: File storage functionality

    Tests file functionality developed for the azure storage wrapper library

    Scenario Outline: FileShareFunctions are used
        Given parameters are set up for fileshare
        Given credential is generated with <authentication_method> for fileshare
        And FileShareFunctions has been instantiated with all permissions
        When file<share> is called for creation
        When a <directory> is created in <share>
        When a <recursive_path> directory is created recursively in FS <share>
        When a <file> is uploaded to <share> in <directory>
        Then <file> and <directory> are found in <share>
        Then <file> is deleted from <directory> in <share>
        Then <directory> is deleted from <share>
        Then <recursive_path> is deleted recursively from <share>
        Then <share> is deleted
        Examples:
            | authentication_method | share       | directory | file    | recursive_path          |
            | client_secret         | test-share  | toplevel  | test.txt| topdir/middir/bottomdir |