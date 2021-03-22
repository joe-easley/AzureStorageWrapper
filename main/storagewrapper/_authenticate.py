from azure.storage.blob import ContainerSasPermissions
from azure.storage.fileshare import AccountSasPermissions
from azure.identity import ClientSecretCredential, UsernamePasswordCredential
from azure.keyvault.secrets import SecretClient
from datetime import timedelta
from storagewrapper._exceptions import AuthenticationError


class AuthenticateFunctions:
    """
    Sets up authentication for azure storage operations

    Can either authenticate as a user, or using an app registration.

    In both instances a credential dictionary will need to passed at instantiation

    If authenticating as a user it will look something like:
    
    params = {"authentication_method": "user",
              "client_id": "XXXX",
              "username": "username@website.com",
              "password": "Wouldn'tYouLikeToKnow"}

    If authenticating as a user this will look like:

    params = {"authentication_method":"client_secret",
              "client_id": "XXXX"
              "storage_account_app_id": "aadappreg123",
              "storage_account_app_key": "XXXXXX"}

    args:
        params (dict): dictionary of params used to authenticate

    """

    def __init__(self, params):
        self.params = params
        self.token = self.__generate_credential()
        
        if "sas_permissions" in self.params:

            self.container_sas_permissions = self.__define_container_sas_permissions()
            self.fileshare_sas_permissions = self.__define_fileshare_sas_permissions()
        
        elif "sas_permissions" not in self.params:
            self.container_sas_permissions = self.__default_container_sas_permissions()
            self.fileshare_sas_permissions = self.__default_fileshare_sas_permissions()
        
        self.sas_duration = self.__define_sas_duration()

    def __generate_client_secret_credential(self, tenant_id, app_id, app_key):
        """
        Generates a token using a app id
        param tenant_id: str
        param storage_account_id: str
        param storage_account_key: str

        return client_secret: ClientSecretObj
        """

        try:

            token_credential = ClientSecretCredential(tenant_id=tenant_id, client_id=app_id, client_secret=app_key)

        except Exception as e:

            raise Exception(e)

        return token_credential

    def __generate_user_credential(self, client_id, username, password):

        """
        Generates a token using user credential (usually email and password)
        param client_id: str
        param username: str
        param password: str

        return token_credential: UsernamePasswordCredential obj
        """

        try:

            token_credential = UsernamePasswordCredential(client_id=client_id, username=username, password=password)

        except Exception as e:

            raise Exception(e)

        return token_credential

    def __define_container_sas_permissions(self):
        
        permissions = self.params["sas_permissions"]

        if "container_permissions" in permissions:
            
            try:

                container_permissions = permissions["container_permissions"]

                read = container_permissions["read"]
                add = container_permissions["add"]
                create = container_permissions["create"]
                write = container_permissions["write"]
                delete = container_permissions["delete"]
                delete_previous_version = container_permissions["delete_previous_version"]
                tag = container_permissions["tag"]

                return ContainerSasPermissions(read=read, add=add, create=create, write=write, delete=delete, 
                                               delete_previous_version=delete_previous_version, tag=tag)
            except KeyError:

                raise AuthenticationError("If specifying container SAS permissions all permissions status must be provided")
        
        elif "container_permission" not in permissions:

            return ContainerSasPermissions(read=True, add=True, create=True, write=True, 
                                           delete=True, delete_previous_version=True, tag=True)
    
    def __default_container_sas_permissions(self):
        return ContainerSasPermissions(read=True, add=True, create=True, write=True, 
                                       delete=True, delete_previous_version=True, tag=True)

    def __define_fileshare_sas_permissions(self):
        
        permissions = self.params["sas_permissions"]

        if "file_permisisons" in permissions:
            
            try:

                fileshare_permissions = permissions["file_permissions"]

                read = fileshare_permissions["read"]
                write = fileshare_permissions["write"]
                delete = fileshare_permissions["delete"]
                delete_previous_version = fileshare_permissions["delete_previous_version"]
                list_files = fileshare_permissions["list"]
                add = fileshare_permissions["add"]
                create = fileshare_permissions["create"]
                update = fileshare_permissions["update"]
                process = fileshare_permissions["process"]
                tag = fileshare_permissions["tag"]
                filter_by_tags = fileshare_permissions["filter_by_tags"]

                return AccountSasPermissions(read=read, write=write, delete=delete, list=list_files, 
                                             add=add, create=create, update=update, process=process, 
                                             delete_previous_version=delete_previous_version, tag=tag, 
                                             filter_by_tags=filter_by_tags)
            except KeyError:

                raise AuthenticationError("If specifying container SAS permissions all permissions status must be provided")
        
        elif "file_permissions" not in permissions:

            return AccountSasPermissions(read=True, write=True, delete=True, list=True, 
                                         add=True, create=True, update=True, process=True, 
                                         delete_previous_version=True, tag=True, 
                                         filter_by_tags=True)

    def __default_fileshare_sas_permissions(self):
        return AccountSasPermissions(read=True, write=True, delete=True, list=True, 
                                     add=True, create=True, update=True, process=True, 
                                     delete_previous_version=True, tag=True, filter_by_tags=True)

    def __define_sas_duration(self):
        if ["sas_duration"] in self.params:
            sas_duration = timedelta(hours=self.params["sas_duration"])
            return sas_duration
        
        else:
            sas_duration = timedelta(hours=1)
            return sas_duration

    def __generate_credential(self):
        """
        Will generate credential based on authentication_method selected

        return token_crential: Azure credential obj
        """
        
        try:

            authentication_method = self.params["authentication_method"]

            if authentication_method == "client_secret":

                tenant_id = self.params["client_id"]

                app_id = self.params["app_id"]
                app_key = self.params["app_key"]

                token_credential = self.__generate_client_secret_credential(tenant_id, app_id, app_key)

                return token_credential

            elif authentication_method == "user":

                client_id = self.params["client_id"]
                username = self.params["username"]
                password = self.params["password"]

                token_credential = self.__generate_user_credential(client_id, username, password)

                return token_credential

            else:
                raise AuthenticationError(f"Authentication method given invalid: {authentication_method}. Must be 'user' or 'client_secret'.")
        
        except KeyError:

            print("KeyError: Check Authentication Params")
            
            raise KeyError