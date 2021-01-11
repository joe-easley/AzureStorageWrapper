from storagewrapper.blob import BlobFunctions
from storagewrapper.authenticate import AuthenticateFunctions
from behave import given, when, then
import os


@given("parameters are set up")
def set_up_params(context):
    context.tenant_id = str(context.config.userdata.get("tenant_id"))
    context.vault_url = str(context.config.userdata.get("vault_url"))
    context.storage_account_app_id = str(context.config.userdata.get("storage_account_app_id"))
    context.storage_account_app_key = str(context.config.userdata.get("storage_account_app_key"))
    context.storage_account_name = context.config.userdata.get("storage_account_name")
    context.container_name = context.config.userdata.get("container_name")
    context.blob_name = "blob.txt"
    context.params = {"tenant_id": context.tenant_id,
                      "storage_account_app_id": context.storage_account_app_id,
                      "storage_account_app_key": context.storage_account_app_key,
                      "vault_backed": False}


@given("credential is generated with {authentication_method}")
def generate_credential(context, authentication_method):

    context.params["authentication_method"] = authentication_method
    context.token = AuthenticateFunctions(context.params).token
    assert context.token is not None


@given("BlobFunctions has been instantiated with all permissions and {container} name")
def instantiate_blob_functions(context, container):
    context.blob_functions = BlobFunctions(token=context.token, storage_account_name=context.storage_account_name,
                                           container_name=container, sas_duration=2, sas_method="AccessKey", vault_url=context.vault_url, access_key_secret_name="storagewrapperaccountaccesskey"
                                           )


@when("a {container} is created")
def create_test_container(context, container):
    creation_status = context.blob_functions.create_container(container_name=container)
    assert creation_status is True


@when("a upload to blob function is called")
def upload_file_to_blob(context):
    path_to_file = f"{os.getcwd()}/data/{context.blob_name}"
    blob_client = context.blob_functions.upload_blob(blob_name=context.blob_name, data=path_to_file)
    assert blob_client is not None


@then("all {container} in storage account are listed")
def list_all_containers(context, container):
    list_of_containers = context.blob_functions.list_containers()
    for container in list_of_containers:
        print(container.name)


@then("list blobs function is used")
def use_list_blobs_function(context):
    context.list_blobs = context.blob_functions.list_blobs()
    assert context.list_blobs[0] == context.blob_name


@then("blob is deleted")
def delete_newly_uploaded_blob(context):
    blob_deleted = context.blob_functions.delete_blob(context.blob_name)
    assert blob_deleted is True

@then("{container} is deleted")
def delete_new_container(context, container):
    container_deleted = context.blob_functions.delete_container(container_name=container)
    assert container_deleted is True
