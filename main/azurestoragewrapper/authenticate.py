from azure.identity import ClientSecretCredential, UsernamePasswordCredential
from azure.keyvault.secrets import SecretClient


class AuthenticateFunctions:
    """
    Sets up authentication for azure storage operations
    """

    def __init__(self, params):
        self.params = params
        self.token = self.generate_credential()

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

    def __get_secret(self, secret_name):

        vault_url = self.params["vault_url"]

        secret_client = SecretClient(vault_url=vault_url, credential=self.token)
        secret = secret_client.get_secret(secret_name)

        return secret.value

    def _check_if_vault_backed(self):

        if self.params['vault_backed'] is True:

            storage_account_app_key = self.__get_secret(self.params["app_key_name"])
            storage_account_app_id = self.__get_secret(self.params["app_id_name"])

            return storage_account_app_key, storage_account_app_id

        else:
            try:
                storage_account_app_id = self.params["storage_account_app_id"]
                storage_account_app_key = self.params["storage_account_app_key"]

                return storage_account_app_key, storage_account_app_id

            except Exception as e:
                raise Exception("Failed to identify app id and key: \n{}".format(e))

    def generate_credential(self):
        """
        Will generate credential based on authentication_method selected

        param authentication_method: str
        param: kwargs

        return token_crential: Azure credential obj
        """
        authentication_method = self.params["authentication_method"]

        if authentication_method == "client_secret":

            tenant_id = self.params["tenant_id"]

            storage_account_app_key, storage_account_app_id = self._check_if_vault_backed()

            token_credential = self.__generate_client_secret_credential(tenant_id, storage_account_app_id, storage_account_app_key)

            return token_credential

        elif authentication_method == "User":

            client_id = self.params["client_id"]
            username = self.params["username"]
            password = self.params["password"]

            token_credential = self.__generate_user_credential(client_id, username, password)

            return token_credential
