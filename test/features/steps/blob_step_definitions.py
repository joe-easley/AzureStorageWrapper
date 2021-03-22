from storagewrapper import AuthenticateFunctions, BlobFunctions
from behave import given, when, then
import os
from unittest import TestCase as tc


@given("parameters are set up for blob")
def set_up_params(context):
    context.client_id = context.config.userdata.get("tenant_id")
    context.vault_url = context.config.userdata.get("vault_url")
    context.app_id = context.config.userdata.get("app_id")
    context.app_key = context.config.userdata.get("app_key")
    context.storage_account_name = context.config.userdata.get("storage_account_name")
    context.blob_name = "blob.txt"
    context.params = {"client_id": context.client_id,
                      "app_id": context.app_id,
                      "app_key": context.app_key,
                      "vault_backed": False}


@given("credential is generated with {authentication_method} for blob")
def generate_credential(context, authentication_method):

    context.params["authentication_method"] = authentication_method
    context.authenticator = AuthenticateFunctions(context.params)


    assert context.token is not None


@given("BlobFunctions has been instantiated with all permissions")
def instantiate_blob_functions(context):
    context.blob_functions = BlobFunctions(authenticator=context.authenticator, storage_account_name=context.storage_account_name)


@when("a {container} is created")
def create_test_container(context, container):
    creation_status = context.blob_functions.create_container(container_name=container)
    print(creation_status)
    assert creation_status is True


@when("a upload to blob function is called to {container}")
def upload_file_to_blob(context, container):
    path_to_file = f"{os.getcwd()}/data/{context.blob_name}"
    blob_client = context.blob_functions.upload_blob(blob_name=context.blob_name, data=path_to_file, container_name=container)
    assert blob_client is not None


@then("all {container} in storage account are listed")
def list_all_containers(context, container):
    list_of_containers = context.blob_functions.list_containers()
    containers_retrieved = []
    for blob_container in list_of_containers:
        containers_retrieved.append(blob_container.name)

    assert container in containers_retrieved


@then("list blobs function is used in {container}")
def use_list_blobs_function(context, container):
    list_blobs = context.blob_functions.list_blobs(container_name=container)
    assert context.blob_name in list_blobs


@then("blob is deleted from {container}")
def delete_newly_uploaded_blob(context, container):
    blob_deleted = context.blob_functions.delete_blob(context.blob_name, container_name=container)
    assert blob_deleted is True


@then("blob {container} is deleted")
def delete_new_container(context, container):
    container_deleted = context.blob_functions.delete_container(container_name=container)
    assert container_deleted is True
