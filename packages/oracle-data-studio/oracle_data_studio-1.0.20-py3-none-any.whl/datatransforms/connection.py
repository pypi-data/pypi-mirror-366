'''
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
Copyright (c) 2023-2025, Oracle and/or its affiliates.

Provides APIs to create and manage connections in Data Transforms
'''
import json
import base64

#DONOT REMOVE THIS IMPORT , The classes are used in eval, loaded dynamically from string
# pylint: disable=unused-import
from datatransforms.connection_types import ConnectionTypes, ConnectionTypeDrivers

# pylint: disable=invalid-name
class Connection:

    """Captures the connection attributes to be created in Data Transforms
    Every connection has unique name, connection type, connectivity attributes 
    (eg credentials, wallets) and custom property (specific to a connection type, 
    as key/value pair)
    """
    def __init__(self):
        """Initialises the connection"""
        self.name=""
        self.technology=""
        self.connectionProperties={}
        self.connectionProperties["isWalletConnection"]=False
        self.schemas=[]

    @staticmethod
    def encode_pwd(pwd):
        """
        Returns base64 encoded string
        """
        return str(base64.b64encode(pwd.encode()),encoding='UTF-8')

    def connection_name(self,connection_name):
        """Name of the connection"""
        self.name=connection_name
        return self

    def of_type(self,connection_type):
        """Connection Type, Refer ConnectionTypeDrivers for the supported enums
        connection_type should be one of the supported connection types """
        self.technology=connection_type.value
        #pylint: disable=eval-used
        #literaleval need to be evaluated
        self.using_driver(eval("ConnectionTypeDrivers."+connection_type.value))
        return self

    def usingWallet(self,wallet_file_path):
        """Attach wallet while creating a connection in the Data transforms. 
        wallet_file_path - fully qualified path where the wallet file is available. 
        While creating the connection, wallet file is loaded and encoded to base64 form 
        and uploaded.
        """
        self.connectionProperties["isWalletConnection"]=True
        self.connectionProperties["walletURL"]=wallet_file_path
        return self

    def with_credentials(self,username,password):
        """
        User and password details. password must be base64encoded 
        """
        self.connectionProperties["username"]=username
        self.connectionProperties["password"]=password
        return self

    def using_driver(self,jdbcDriver):
        """JDBC Driver class for connection. All the JDBC Drivers supported by Data Transforms
        are captured and provided as developer friendly enum"""
        self.connectionProperties["jdbcDriverName"]=jdbcDriver
        return self

    def property(self,property_name,property_value):
        """
        Data transforms connections require custom properties 
        """
        self.connectionProperties[property_name]=property_value
        return self

    def globalID(self,global_id):
        """Unique ID assigned by Data Transforms for the connection. 
        Mostly un-used. Developers should not set or use global ID. Meant for troubleshooting ONLY.

        Arguments:
            global_id -- unique ID of the connection
        """
        #pylint: disable=attribute-defined-outside-init
        self.globalId=global_id

    def prepare_payload(self):
        """Prepares JSON payload for the connection object. This method is exposed for debugging 
        or logging at the client side for troubleshooting ONLY. 

        Returns:
            JSON document representation of the connection object
        """
        connection_json = json.dumps(self,default=lambda o: o.__dict__)
        return connection_json

    def get_connection_name(self):
        """
        Returns the connection name
        """
        return self.name
