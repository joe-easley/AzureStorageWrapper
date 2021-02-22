from azure.identity import ClientSecretCredential, UsernamePasswordCredential
from azure.keyvault.secrets import SecretClient
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

    def __generate_client_secret_credential(self, tenant_id, storage_account_id, storage_account_key):
        """
        Generates a token using a app id
        param tenant_id: str
        param storage_account_id: str
        param storage_account_key: str

        return client_secret: ClientSecretObj
        """

        try:

            token_credential = ClientSecretCredential(tenant_id, storage_account_id, storage_account_key)

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

    def __generate_credential(self):
        """
        Will generate credential based on authentication_method selected

        return token_crential: Azure credential obj
        """
        authentication_method = self.params["authentication_method"]

        if authentication_method == "client_secret":

            tenant_id = self.params["client_id"]

            storage_account_app_id = self.params["storage_account_app_id"]
            storage_account_app_key = self.params["storage_account_app_key"]

            token_credential = self.__generate_client_secret_credential(tenant_id, storage_account_app_id, storage_account_app_key)

            return token_credential

        elif authentication_method == "user":

            client_id = self.params["client_id"]
            username = self.params["username"]
            password = self.params["password"]

            token_credential = self.__generate_user_credential(client_id, username, password)

            return token_credential

        else:
            raise AuthenticationError(f"Authentication method given invalid: {authentication_method}. Must be 'user' or 'client_secret'.")
