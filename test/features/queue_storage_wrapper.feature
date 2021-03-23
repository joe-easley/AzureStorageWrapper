@queue_wrapper_functions

Feature: Queue storage functionality

    Tests queue functionality developed for the azure storage wrapper library

    Scenario Outline: QueueFunctions are used
        Given parameters are set up for queues
        And credential is generated with <authentication_method> for queue
        And a <queue_name> is created
        Then a <message> is sent to <queue_name>
        Then the <queue_name> is deleted
        Examples: 
        | queue_name    | authentication_method | message      |
        | test-queue    | client_secret         | test message |
        
