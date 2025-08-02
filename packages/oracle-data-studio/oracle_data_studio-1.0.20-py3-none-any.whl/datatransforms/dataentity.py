"""
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
Copyright (c) 2023-2025, Oracle and/or its affiliates.

Houses APIs to create data entity in Data Transforms
"""
import json

# pylint: disable=invalid-name
class DataEntity:
    #pylint: disable=attribute-defined-outside-init
    """Enables creation of data entity in data transforms.
    """
    def from_connection(self,dataServerName,schema_name):
        """Prepares data entity from connection and schema"""
        self.dataServerName=dataServerName
        self.model={}
        self.model["schema"]=DataStoreSchema(schema_name)
        return self

    #pylint: disable=method-hidden
    def dataServerGlobalId(self,dataServerGlobalId):
        """Updates the data entity with unique Global ID.
        Internal method used when data store is resolved. d"""
        self.dataServerGlobalId=dataServerGlobalId
        return self

    def entity_name(self,name):
        """Updates the data entity name

        Arguments:
            name -- data entity name

        Returns:
            current object
        """
        self.dataStore=DataStoreDetails(
            name,resourceName=name,defaultAlias=name,dataStoreType="TABLE",technologyCode="")
        return self

    def globalID(self,globalId):
        """Updates the globalID of the data store. Internal method"""
        self.globalId=globalId
        return self

    def resource_name(self,resourceName):
        """Updates resource name of the data entity"""
        self.resourceName=resourceName
        return self

    def data_store_type(self,dataStoreType):
        """Updates the data store type"""
        self.dataStoreType=dataStoreType
        return self

    def add_column(self,name,position,dataType,dataTypeCode,length,scale):
        """Adds the column to data entity

        Arguments:
            name -- column name
            position -- position of the column
            dataType -- column data type
            dataTypeCode -- column data type code 
            length -- column length
            scale -- column scale if applicable

        Returns:
            _description_
        """
        column = DataStoreColumn(name,position,dataType,dataTypeCode,length,scale)
        self.dataStore.columns.append(column)
        return self

    def prepare_payload(self):
        """Called by workbench while performing save operation. 
        This method just give READ access of JSON being sent to Data Transforms. 

        Returns:
            JSON document of the data entity
        """
        connection_json = json.dumps(self,default=lambda o: o.__dict__)
        return connection_json

class DataStoreDetails:
    """Initialises data entity with its details"""
    def __init__(self,name,resourceName,defaultAlias,dataStoreType="TABLE",technologyCode=None):
        self.name=name
        self.resourceName=resourceName
        self.defaultAlias=defaultAlias
        self.dataStoreType=dataStoreType
        self.technologyCode=technologyCode
        self.columns=[]

class DataStoreSchema:
    """Model representation of data store schema
    """
    def __init__(self,schemaShortName):
        self.schemaShortName=schemaShortName

    def schema_globalID(self,globalId):
        """Updates the global ID of the schema"""
        #pylint: disable=attribute-defined-outside-init
        self.globalId=globalId

class DataStoreColumn:
    """Represents the column in the data entity
    """
    def __init__(self,name,position,dataType,dataTypeCode,length,scale):
        self.name=name
        self.position=position
        self.dataType=dataType
        self.dataTypeCode=dataTypeCode
        self.length=length
        self.scale=scale
        self.isMandatory=False

    def store_globalId(self,globalId):
        """Update the column globale ID"""
        #pylint: disable=attribute-defined-outside-init
        self.globalId=globalId
