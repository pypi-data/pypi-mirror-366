'''
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

APIs to create data load in data transforms.
'''

import json
import logging

from datatransforms.workbench import DataTransformsWorkbench

#pylint: disable=invalid-name
class SourceSchema:
    """JSON Model representation of SourceSchema in data load
    """
    def __init__(self,schemaShortName,globalId,schemaName,parentServer):
        self.schemaShortName=schemaShortName
        self.globalId=globalId
        self.schemaName=schemaName
        self.parentServer=parentServer

class SourceModel:
    """JSON Model representation of SourceModel in data load
    """
    def __init__(self,sourceSchema):
        self.schema=sourceSchema

class TargetSchema:
    """JSON Model representation of Target Schema in data load"""
    def __init__(self,schemaShortName,globalId,parentServer):
        self.schemaShortName=schemaShortName
        self.globalId=globalId
        self.parentServer=parentServer

class TargetModel:
    """JSON Model representaion of Target Model in data load
    """
    def __init__(self,sourceSchema):
        self.schema=sourceSchema

class DataLoadTable:
    """Represents the table participating in data load
    """
    class EntityColumn:
        """JSON Model representation of EntityColumn in data load"""
        def __init__(self,columnName,incrementalInd,mergeInd,columnType):
            self.columnName=columnName
            self.incrementalInd=incrementalInd
            self.mergeInd=mergeInd
            self.columnType=columnType

    def __init__(
            self,sourceTableName,targetPreloadAction,incremental_column=None,merge_columns=None):
        self.sourceTableName=sourceTableName
        self.targetPreloadAction=targetPreloadAction
        self.entityCols=[]

        if incremental_column is not None:
            merge_index=False

            if merge_columns is not None and incremental_column in merge_columns:
                merge_index=True

            column_type=""
            incremental_colum_obj = DataLoadTable.EntityColumn(
                incremental_column,True,merge_index,column_type)
            self.entityCols.append(incremental_colum_obj)

        if merge_columns is not None:
            for merge_column in merge_columns:
                self.entityCols.append(
                    DataLoadTable.EntityColumn(merge_column,False,merge_index,column_type))

class DataLoadPayloadResolver:
    """Resolves the JSON Payload from Data Load object"""
    def __init__(self):
        client = DataTransformsWorkbench.client
        client.load_cache()
        #self.data_stores=client.get_all_datastores()
        self.connection_schemas_stores_detail=client.connection_schemas_stores_detail
        self.schema_map=client.schemas
        self.client=client

    def resolve_models(self,dataLoad):
        """Resolves the dependant objects with globalIDs from the name
        Internal method. """
        #pylint: disable=attribute-defined-outside-init
        self.dataLoad = dataLoad

        if isinstance(self.dataLoad,DataLoad):
            if self.dataLoad.parentProjectName not in self.client.projects:
                logging.debug("Project {self.dataLoad.parentProjectName} not found, creating one ")
                project_code=self.dataLoad.parentProjectName.replace(" ","").upper()
                self.client.create_project(name=self.dataLoad.parentProjectName,code=project_code)
                self.client.get_all_projects()

            print(self.client.projects)
            self.dataLoad.parentProjectID=self.client.projects[self.dataLoad.parentProjectName]

            src_schema_short_name=self.dataLoad.sourceModel.schema.schemaShortName
            src_con_name= self.dataLoad.sourceModel.schema.parentServer

            self.dataLoad.sourceModel.schema.globalId=self.resolve_schema_global_id(
                src_con_name,src_schema_short_name)

            tgt_schema_short_name=self.dataLoad.targetModel.schema.schemaShortName
            tgt_con_name= self.dataLoad.targetModel.schema.parentServer
            #tgt_schema_global_id=self.schema_map[tgt_con_name+"."+tgt_schema_short_name]
            self.dataLoad.targetModel.schema.globalId=self.resolve_schema_global_id(
                tgt_con_name,tgt_schema_short_name)

            src_tables = self.dataLoad.sourceTables
            filtered_stores={}

            print("[INFO] filtering data stores")
            for key,value in self.connection_schemas_stores_detail.items():
                #pylint: disable=line-too-long
                #to be optimised 
                if value["dataServerName"] == src_con_name and value["schemaName"] == src_schema_short_name:
                    filtered_stores[value["name"]]=value["globalId"]

            print("[INFO] filtered data stores")
            column_type_dict={}
            for key,value in filtered_stores.items():
                entity_def= self.client.get_dataentity_by_id(value)
                columns=entity_def["columns"]
                for column in columns:
                    column_type_dict[key+"."+column["name"]]=column["dataTypeCode"]
            print("[INFO] Resolved table column types")
            for src_table in src_tables:
                if isinstance(src_table,DataLoadTable):
                    entitycols = src_table.entityCols
                    for entity_column in entitycols:
                        key=src_table.sourceTableName+"."+entity_column.columnName
                        if key not in column_type_dict:
                            raise Exception("Invalid column " + key)
                        data_type_code = column_type_dict[key]
                        entity_column.columnType=data_type_code

        return self.dataLoad

    def resolve_schema_global_id(self,conn_name,schema_name):
        """Returns global ID if the schema already available in data transforms,
        otherwise creates and attaches schema to the connection and resolves the globalID"""

        #ideally this call is not required, since get data stores API doesn't return empty schema
        #another call is required 
        logging.debug("Fetching all schema under connection {conn_name}".format_map(locals()))
        schema_dict = self.client.list_all_schema_in_connection(conn_name)
        logging.debug("Available schema")
        logging.debug(schema_dict)
        if schema_name in schema_dict.keys():
            logging.debug("Schema found, resolving...")
            schema_global_id=schema_dict[schema_name]
            return schema_global_id  
        else:
            logging.debug(
                "Schema{schema_name} NOT found under {conn_name}, attaching...".
                format_map(locals()))
            attached_schema_global_id=self.client.attach_schema_with_connection(
                conn_name,schema_name)
            return attached_schema_global_id

    def check_if_dataload_exists(self,project_id,dataload_name):
        """Verifies if the given data laod exists in the project 

        Arguments:
            project_id -- project global ID 
            dataload_name -- to be verified 

        Returns:
            True if the dataload already exists, False otherwise
        """
        return self.client.check_if_dataload_exists(project_id,dataload_name)

    def create_dataload(self,payload_json):
        """Triggers the REST client to create the dataload based on the given JSON document

        Arguments:
            payload_json -- resolved payload for creating data load
        """
        self.client.create_dataload(payload_json)

    def update_dataload(self,payload_json):
        """Performs update/overwrite operation on the given data load

        Arguments:
            payload_json -- resolved payload for creating data load
        """
        self.client.update_dataload(payload_json)

class DataLoad:
    """Data Load enables loading of data from source schema to target. 
    Typical data load will have a unique name , project name, source connection 
    and tables to be loadedalong with target connection. 
    """
    resolver = None
    #pylint: disable=attribute-defined-outside-init
    def __init__(self,name,project_name):
        self.globalId=None
        self.bulkLoadName=name

        self.parentProjectName=project_name
        self.parentProjectID=""
        self.sourceTables=[]
        self.bulkLoadMode="INCREMENTAL"
        self.dataLoadOptions={}
        DataLoad.resolver = DataLoadPayloadResolver()

    def __create_payload(self):
        resolver=DataLoadPayloadResolver()
        resolved_obj = resolver.resolve_models(self)
        exists,global_id=resolver.check_if_dataload_exists(
            resolved_obj.parentProjectID,resolved_obj.bulkLoadName)
        if not exists:
            del resolved_obj.globalId
            payload_json= json.dumps(resolved_obj,default=lambda o: o.__dict__)
            #print(payload_json)
            resolver.create_dataload(payload_json)
        else:
            resolved_obj.globalId=global_id
            payload_json= json.dumps(resolved_obj,default=lambda o: o.__dict__)
            resolver.update_dataload(payload_json)

    def source(self,source_schema):
        """Adds source schema for data load 

        Arguments:
            source_schema -- source schema name

        Returns:
            current object
        """
        source_info = source_schema.split(".")
        self.sourceModel=SourceModel(
            SourceSchema(source_info[1],"unresolved",source_schema,source_info[0]))
        return self

    def target(self,target_schema):
        """Adds the target schema for data load

        Arguments:
            target_schema -- schema name for target

        Returns:
            current object
        """
        source_info = target_schema.split(".")
        self.targetModel = TargetModel(TargetSchema(source_info[1],"unresolved",source_info[0]))
        return self

    def incremental_merge(self,table_name,incremental_column,merge_keys):
        """Adds the table to be loaded with incremental merge mode in data load

        Arguments:
            table_name -- to be loaded in target 
            incremental_column -- column name used for incremental mode
            merge_keys -- list of column(s) to be used as merge keys 

        Returns:
            current object
        """
        self.sourceTables.append(
            DataLoadTable(table_name,"INCREMENTAL_MERGE",incremental_column,merge_keys))
        return self

    def incremental_append(self,table_name,incremental_column):
        """Adds the given table for incrmental append in data load 

        Arguments:
            table_name -- to be loaded in incremental append mode.
            incremental_column -- column name to be used for incremental append

        Returns:
            current object
        """
        self.sourceTables.append(DataLoadTable(table_name,"INCREMENTAL_APPEND",incremental_column))
        return self

    def recreate(self,table_name):
        """Adds the table to be created in data load 

        Arguments:
            table_name -- to be recreted in target 

        Returns:
            current object
        """
        self.sourceTables.append(DataLoadTable(table_name,"RECREATE"))
        return self

    def append(self,table_name):
        """Adds the table for append operation in data load

        Arguments:
            table_name -- to be loaded in append mode 

        Returns:
            current object
        """
        self.sourceTables.append(DataLoadTable(table_name,"APPEND"))
        return self

    def truncate(self,table_name):
        """Adds the table for truncate operation

        Arguments:
            table_name -- to be truncated before load in the target

        Returns:
            current object
        """
        self.sourceTables.append(DataLoadTable(table_name,"TRUNCATE"))
        return self

    def create_dataload(self):
        """Create data load in data transforms"""
        self.__create_payload()
