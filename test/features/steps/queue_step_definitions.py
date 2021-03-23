from storagewrapper import QueueFunctions, AuthenticateFunctions
from behave import given, when, then
import os


@given("parameters are set up for queues")
def set_up_params(context):
    context.tenant_id = context.config.userdata.get("tenant_id")
    context.vault_url = context.config.userdata.get("vault_url")
    context.app_id = context.config.userdata.get("app_id")
    context.app_key = context.config.userdata.get("app_key")
    context.storage_account_name = context.config.userdata.get("storage_account_name")
    context.file_name = "blob.txt"
    context.params = {"client_id": context.tenant_id,
                      "app_id": context.app_id,
                      "app_key": context.app_key}

@given("credential is generated with {authentication_method} for queue")
def generate_credential(context, authentication_method):

    context.params["authentication_method"] = authentication_method
    context.authenticator = AuthenticateFunctions(context.params)

    assert context.authenticator is not None

@given("a {queue_name} is created")
def create_queue(context, queue_name):
    context.queue_functions = QueueFunctions(authenticator=context.authenticator, storage_account_name=context.storage_account_name)

    creation_status = context.queue_functions.create_queue(queue_name=queue_name)

    assert creation_status

@then("a {message} is sent to {queue_name}")
def send_message_to_queue(context, message, queue_name):

    message_status = context.queue_functions.send_message(content=message, queue_name=queue_name)

    assert message_status

@then("the {queue_name} is deleted")
def delete_the_queue(context, queue_name):
    delete_status = context.queue_functions.delete_queue(queue_name=queue_name)

    assert delete_status