from storagewrapper import FileShareFunctions, AuthenticateFunctions
from behave import given, when, then
import os


@given("parameters are set up for fileshare")
def set_up_params(context):
    context.tenant_id = context.config.userdata.get("tenant_id")
    print(context.tenant_id)
    context.vault_url = context.config.userdata.get("vault_url")
    context.app_id = context.config.userdata.get("app_id")
    context.app_key = context.config.userdata.get("app_key")
    context.storage_account_name = context.config.userdata.get("storage_account_name")
    context.file_name = "blob.txt"
    context.params = {"client_id": context.tenant_id,
                      "app_id": context.app_id,
                      "app_key": context.app_key}


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
    status = context.fileshare_functions.create_fileshare_directory(share_name=share, directory_path=directory)

    assert status is True

@when("a {recursive_path} directory is created recursively in FS {share}")
def create_directory_recursively(context, recursive_path, share):
    status = context.fileshare_functions.create_fileshare_directory(share_name=share, directory_path=recursive_path, recursive=True)

    assert status is True

@when("a {file} is uploaded to {share} in {directory}")
def upload_file_to_new_share(context, file, share, directory):
    path_to_file = f"{os.getcwd()}/data/{context.file_name}"

    with open(path_to_file, "rb") as data:
        file_client = context.fileshare_functions.upload_file(share_name=share, directory_path=directory, file_name=file, data=data)
        data.close()
    
    assert file_client is not None

def check_dirs(context, share, directory):
    dirs = context.fileshare_functions.list_directories_and_files(share)
    for folder in dirs:
        if folder['name'] == directory:
            return True
    return False

def check_files(context, share, directory, file_name):
    files = context.fileshare_functions.list_directories_and_files(share_name=share, directory_name=directory)
    for file in files:
        if file['name'] == file_name:
            return True
    return False

@then('{file} and {directory} are found in {share}')
def check_files_and_dirs_exist(context, file, directory, share):
    dir_status = check_dirs(context, share, directory)
    print(f"Directory exists: {dir_status}")

    file_status = check_files(context, share, directory, file_name=file)
    print(f"File exists: {file_status}")

    assert dir_status and file_status

@then("{file} is deleted from {directory} in {share}")
def delete_file_from_share(context, file, directory, share):
    file_path = f"{directory}/{file}"

    delete_status = context.fileshare_functions.delete_file(share_name=share, file_path=file_path)
    print(f"{file} has been deleted from {directory}: {delete_status}")

    assert delete_status

@then("{directory} is deleted from {share}")
def delete_directory_from_share(context, directory, share):
    delete_dir_status = context.fileshare_functions.delete_directory(share_name=share, directory_name=directory)
    print(f"{directory} has been deleted from {share}")

    assert delete_dir_status

@then("{recursive_path} is deleted recursively from {share}")
def delete_path_recursively(context, recursive_path, share):
    delete_dir_status = context.fileshare_functions.delete_directory(share_name=share, directory_name=recursive_path, recursive=True)

    assert delete_dir_status

@then("FS {share} is deleted")
def delete_file_share(context, share):
    delete_share_status = context.fileshare_functions.delete_share(share_name=share)
    assert delete_share_status