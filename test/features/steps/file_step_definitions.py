from storagewrapper.fileshare import FileShareFunctions
from storagewrapper.authenticate import AuthenticateFunctions
from behave import given, when
# import os


@given("parameters are set up for fileshare")
def set_up_params(context):
    context.tenant_id = context.config.userdata.get("tenant_id")
    context.vault_url = context.config.userdata.get("vault_url")
    context.storage_account_app_id = context.config.userdata.get("storage_account_app_id")
    context.storage_account_app_key = context.config.userdata.get("storage_account_app_key")
    context.storage_account_name = context.config.userdata.get("storage_account_name")
    context.blob_name = "blob.txt"
    context.params = {"tenant_id": context.tenant_id,
                      "storage_account_app_id": context.storage_account_app_id,
                      "storage_account_app_key": context.storage_account_app_key,
                      "vault_backed": False}


@given("credential is generated with {authentication_method} for fileshare")
def generate_credential(context, authentication_method):

    context.params["authentication_method"] = authentication_method
    context.token = AuthenticateFunctions(context.params).token

    assert context.token is not None


@given("FileShareFunctions has been instantiated with all permissions")
def instantiate_blob_functions(context):
    context.fileshare_functions = FileShareFunctions(token=context.token, storage_account_name=context.storage_account_name,
                                                     sas_duration=2, vault_url=context.vault_url,
                                                     secret_name="fileshareaccesskey")
    assert context.fileshare_functions is not None


@when("file{share} is called for creation")
def create_new_file_share(context, share):
    share_client = context.fileshare_functions.create_share(share_name=share)

    assert share_client is not None


@when("a {directory} is created in {share}")
def create_directory_in_share(context, directory, share):
    status = context.fileshare_functions.create_fileshare_directory(file_share_name=share, directory_path=directory)

    assert status is True

# @when("a {file} is uploaded to {share}")
# def upload_file_to_new_share(context, file, share):
