@queue_wrapper_functions

Feature: Queue storage functionality

    Tests queue functionality developed for the azure storage wrapper library

    Scenario Outline: QueueFunctions are used
        Given parameters are set up for queues
        And credential is generated with <authentication_method> for queue
        And a <queue_name> is created
        Examples: 
        | queue_name    | authentication_method |
        | test-queue    | client_secret         |
        
