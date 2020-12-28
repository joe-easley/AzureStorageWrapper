from azure.identity import ClientSecretCredential, UsernamePasswordCredential

class Authenticate:
    """
    Sets up authentication for azure storage operations
    """

    def __generate_client_secret_credential(self, tenant_id, storage_account_id, storage_account_key):
        """
        Generates a token using a app id
        param tenant_id: str
        param storage_account_id: str
        param storage_account_key: str

        return client_secret: ClientSecretObj
        """

        token_credential = ClientSecretCredential(tenant_id, storage_account_id, storage_account_key)

        return token_credential

    def __generate_user_credential(self, client_id, username, password):

        """
        Generates a token using user credential (usually email and password)
        param client_id: str
        param username: str
        param password: str

        return token_credential: UsernamePasswordCredential obj
        """

        token_credential = UsernamePasswordCredential(client_id=client_id, username=username, password=password)

        return token_credential

    def generate_credential(self, params):
        """
        Will generate credential based on authentication_method selected
        
        param authentication_method: str
        param: kwargs

        return token_crential: Azure credential obj
        """
        if authentication_method == "client_secret":

            tenant_id = params["tenant_id"]
            storage_account_id = params["storage_account_id"]
            storage_account_key = params["storage_account_key"]

            token_credential  = self.__generate_client_secret_credential(tenant_id, storage_account_id, storage_account_key)
            
            return token_credential
        
        elif authentication_method == "User":

            client_id = params["client_id"]
            username = params["username"]
            password = params["password"]

            token_credential = self.__generate_user_credential(client_id, username, password)