from azurestoragewrapper import AuthenticateFunctions, BlobFunctions, FileShareFunctions, QueueFunctions

params = {"tenant_id": "7988742d-c543-4b9a-87a9-10a7b354d289",
          "authentication_method": "client_secret",
          "vault_backed": False,
          "app_id_name": "dbStorageReaderAppRegistrationAppId",
          "app_key_name": "dbStorageReaderAppRegistrationKey",
          "vault_url": "https://acdcdev1-kv-databricks.vault.azure.net/",
          "storage_account_app_id": "72948d1f-543f-41d7-b656-a14cb995f97e",
          "storage_account_app_key": "d5249a68-ecfc-4f13-8d49-a346057d67fa",
          "share_access_key_secret_name": "ecognitionStorageAccountAccessKey",
          "storage_acct_name": "acdcdev1databricks"}


token = AuthenticateFunctions(params).token
sas_permissions = {"read": True,
                   "write": True,
                   "delete": False,
                   "list": False}
# print(token)

blob_functions = BlobFunctions(token=token, storage_account_name="acdcdev1databricks", container_name="acdcdev1-databricks", sas_permissions=sas_permissions)

# with open(r"C:\Users\jeasley\FurtherLearning_azure.PNG", "rb") as f:
#     file_contents = f.read()
# blob_functions.upload_blob(blob_name="terry.PNG", data=file_contents)

# list_of_blobs = blob_functions.list_blobs()
# print(type(list_of_blobs))
# for item in list_of_blobs:
#     print(item)

# blob_functions.delete_blob("terry.PNG")

# list_of_blobs = blob_functions.list_blobs()
# print(type(list_of_blobs))
# for item in list_of_blobs:
#     print(item)
print("something")
containers = blob_functions.list_containers()
print(type(containers))
for item in containers:
    print(item)

print("something else")
client = blob_functions.blob_service_client
containers = client.list_containers()
print(containers)
for item in containers:
    print(item.name)