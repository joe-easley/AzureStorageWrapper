from azurestoragewrapper.blob import BlobFunctions
from azurestoragewrapper.authenticate import AuthenticateFunctions
from behave import given, when, then


@given("parameters are set up")
def set_up_params(context):
    context.tenant_id = context.config.userdata.get("tenant_id")
    context.vault_url = context.config.userdata.get("vault_url")
    context.storage_account_app_id = context.config.userdata.get("storage_account_app_id")
    context.storage_account_app_key = context.config.userdata.get("storage_account_app_key")
    context.storage_account_name = context.storage_account_app_id = context.config.userdata.get("storage_account_name")
    context.container_name = context.config.userdata.get("container_name")
    context.blob_name = "sampleblob.txt"
    context.params = {"tenant_id": context.tenant_id,
                      "storage_account_app_id": context.storage_account_app_id,
                      "storage_account_app_key": context.storage_account_app_key,
                      }
    context.BlobFunctions = BlobFunctions()
    context.AuthenticateFunctions = AuthenticateFunctions()


@given("credential is given")
def generate_credential(context):
    context.token = context.AuthenticateFunctions(context.params).token


@given("a token has been created")
def assert_credential_exists(context):
    assert context.token is not None


@given("BlobFunctions has been instantiated with all permissions")
def instantiate_blob_functions(context):
    context.blob_functions = context.BlobFunctions(token=context.token, storage_account_name=context.storage_account_name,
                                                   container_name=context.container_name)


@when("list blobs function is used")
def use_list_blobs_function(context):
    context.list_blobs = context.blob_functions.list_blobs()


@then("list of blobs is generated")
def check_list_of_blobs(context):
    assert type(context.list_blobs) is list


@when("a upload to blob function is called")
def upload_file_to_blob(context):
    file_location = r"test\data\blob.txt"
    with open(file_location, "rb") as f:
        blob_to_upload = f.read()
    context.blob_functions(blob_name=context.blob_name, data=blob_to_upload)
