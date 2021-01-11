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


@given("BlobFunctions has been instantiated with all permissions")
def instantiate_blob_functions(context):
    path_to_file = f"{os.getcwd()}/data/{context.blob_name}"
    context.blob_functions = BlobFunctions(token=context.token, storage_account_name=context.storage_account_name,
                                           container_name=context.container_name, sas_duration=2, sas_method="AccessKey", vault_url=context.vault_url, access_key_secret_name="storagewrapperaccountaccesskey"
                                           )
    context.blob_functions.upload_blob(blob_name=context.blob_name, data=path_to_file)


@then("list blobs function is used")
def use_list_blobs_function(context):
    context.list_blobs = context.blob_functions.list_blobs()
    assert context.list_blobs[0] == context.blob_name


@when("a upload to blob function is called")
def upload_file_to_blob(context):
    path_to_file = f"{os.getcwd()}/data/{context.blob_name}"
    context.blob_functions.upload_blob(blob_name=context.blob_name, data=path_to_file)
