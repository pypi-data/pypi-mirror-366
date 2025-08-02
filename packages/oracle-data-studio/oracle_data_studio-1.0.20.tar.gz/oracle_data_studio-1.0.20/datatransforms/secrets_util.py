'''
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

Defines contracts for updating and retrieving the credentials via underlying secure store
'''

class SecretsStore:
    """
    Houses the APIs contracts for credential or sensitive data store.
    Developers can extend to provide an implementation abstracting the
    password store or directly use respective stores for handling 
    sensitive fields like connection passwords or access keys
    """
    __registered_keystore=None

    @staticmethod
    def register_keystore(key_store_implementation):
        """
        Register a custom key store implementation. The custom implemntation shall 
        extend SecretStore class and provide APIs for credential management operations.
        """
        SecretsStore.__registered_keystore=key_store_implementation

    @staticmethod
    def get_secret_store():
        """
        Returns an instance of secret store
        """
        if SecretsStore.__registered_keystore is None:
            raise ValueError("No secretstores registered")
        else:
            return SecretsStore.__registered_keystore

    #All the keyring usage should move to a new class with Keyringkeystore
    def store_pswd(self,serviceid,user,pswd):
        """Delegates the method call to keyring library to store the password,
        User of this API requires service and user to get the password.
        """
        raise ValueError("Not implemented")

    def get_pswd(self,service,user):
        """Fetches password from the keyring store, uses keyring library"""
        raise ValueError("Not implemented")

    def store_credentials(self,service,user,pswd):
        """Store credential stores both user and password as separate entries under the service.
        To fetch credentials service name is sufficient"""
        raise ValueError("Not implemented")

    def get_credentials(self,service):
        """Returns user,passwrod from the secret store based on service"""
        raise ValueError("Not implemented")
        