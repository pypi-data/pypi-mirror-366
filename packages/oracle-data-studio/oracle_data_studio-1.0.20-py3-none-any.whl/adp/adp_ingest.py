'''
    Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

    Copyright (c) 2023-2025, Oracle and/or its affiliates.

'''

import os
import json
import urllib.parse
import time
from datetime import datetime
from typing import Tuple
from .adp_misc import AdpMisc
from .rest import Rest

class AdpIngest():
    '''
    classdocs
    '''
    def __init__(self) -> None:
        '''
        Constructor
        '''
        self.response_format = {
            'resultSetMetadata': False,
            'statementInformation': False,
            'statementText': False,
            'binds': False,
            'result': True,
            'response': False
            }
        self.utils = AdpMisc()
        self.rest=None

    def set_rest(self, rest : Rest) -> None:
        '''
            Set Rest instance
            
            @param rest (Rest): rest instance
        '''
        self.rest = rest
        self.utils.set_rest(rest)

    def get_database_links(self, owner: str = None) -> str:
        '''
            Get Database Links        
            @param owner (String): schema name of the database links (None means that the current schema is used)            
        '''
        if owner is None:
            owner = self.rest.username

        query= "owner: {0} application: DATABASE type: DB_LINK".format(owner)
        sort_json = [{'column': 'entity_name', 'direction':'asc'}]
        return self.utils.global_search(self.rest.encode(query), 0, 20001, sort_json, True, False)

    def get_db_link_owner_tables(self, db_link : str) -> str:
        '''
            Get all object related with Database link
            
            @param dbLink (String): name of the Database link
        '''

        payload = {'db_link': db_link, 'filter':'%'}
        url = "{0}/_adpdi/_services/objects/dblinkownertables/".format(self.rest.get_prefix())
        text = self.rest.post(url, payload)

        json_text = json.loads(text)

        records = {}
        i = 1
        while i < len(json_text):
            json_record = json_text[i]
            table_name = json_record[1]
            records[table_name] = {'dbLink': db_link, 'owner':json_record[0], 'tableName': table_name, 'numRows':json_record[2], 'avgRowLen':json_record[3]}
            i = i + 1

        return json.dumps(records)

    def get_credential_list(self) -> str:
        '''
            List of avaiable credentials
        '''
        url = '{0}/_adpdi/_services/objects/credentials/'.format(self.rest.get_prefix())
        return self.rest.get(url)

    def create_ocid_credential( self, credential_name_ocid : str, user_ocid : str, tenancy_ocid : str, private_key: str, fingerprint: str) -> str:
        '''
            Create OCI credentials
            @param credential_name_ocid (String): name of the credential
            @param user_ocid (String): the user's OCID
            @param tenancy_ocid (String): the tenancy's OCID
            @param private_key (String):  the generated private key without a passphrase
            @param fingerprint (String):he fingerprint       
        '''
        credentials = []
        text = self.get_credential_list()
        json_text = json.loads(text)
        t1 = json_text['items']
        for t2 in t1:
            credentials.append(t2['credential_name'].upper())
        if credential_name_ocid in credentials:
            return '{"error":"Credential already exists"}'
        payload = {
            "credentialNameOcid": credential_name_ocid,
            "userOcid": user_ocid,
            "tenancyOcid": tenancy_ocid,
            "privKey": private_key,
            "fingerprint": fingerprint
	    }

        url = '{0}/_adpdi/_services/objects/credential/create-oci-credential/'.format(self.rest.get_prefix())
        return self.rest.post(url, payload)

    def create_credential(self, credential_name: str, username: str, password: str) ->str:
        '''
            Create credential

            @param credential_name (String): name of the credential
            @param username (String): cloud username
            @param password (String): cloud pasword

        '''
        credentials = []
        text = self.get_credential_list()
        json_text = json.loads(text)
        t1 = json_text['items']
        for t2 in t1:
            credentials.append(t2['credential_name'].upper())
        if credential_name in credentials:
            return '{"error":"Credential already exists"}'

        payload = {"credential_name": credential_name, "username": username, "password": password}
        url = '{0}/_adpdi/_services/objects/createcredential/'.format(self.rest.get_prefix())
        return self.rest.post(url, payload)

    def drop_credential(self, credential_name : str) -> str:
        '''
            Drop the Credential
            
            @param credential_name (String): name of the credential
        '''
        payload = {'credentialName': credential_name}
        url = '{0}/_adpdi/_services/objects/dropcredential/'.format(self.rest.get_prefix())
        return self.rest.post(url, payload)

    def create_cloud_storage_link(self, storage_link_name : str, uri : str, credential_name :str, description : str = None) -> str:
        '''
            Create the Cloud Storage Link
            
            @param storageLinkName (String): name for the cloud storage link
            @param uri (String): URI of Object Store compartment including trailing slash
            @param credentialName (String): Credential Name
            @param description (String): Description for the link. If None, use storageLinkName
        '''
        storages = []
        text = self.get_cloud_storage_link_list()
        json_text = json.loads(text)
        t1 = json_text['nodes']
        for t2 in t1:
            storages.append(t2['data']['name'].upper())
        if storage_link_name in storages:
            return '{"error":"Cloud storage link already exists"}'
        if description is None:
            description = storage_link_name
        metadata = {'description': description, 'storageType': 'object_store', 'files': None}
        cred_type = 'create_cred'
        if credential_name is None:
            cred_type = 'no-cred'
            credential_name = ''
        url = '{0}/_adpdi/_services/objects/create_cloud_storage_link/'.format(self.rest.get_prefix())
        payload = {'storage_link_name': storage_link_name,
                   'uri': uri,
                   'metadata': self.rest.stringify(metadata),
                   'credential_name': credential_name,
                   'edit': False,
                   'credType': cred_type}
        return self.rest.post(url, payload)

    def drop_cloud_storage_link(self, storage_link_name : str) -> str:
        '''
            Drop the Cloud Storage Link
            
            @param storageLinkName (String): name for the Cloud Storage Link
        '''

        payload = {'storage_link_name': storage_link_name}
        url = '{0}/_adpdi/_services/objects/drop_cloud_storage_link/'.format(self.rest.get_prefix())
        return self.rest.delete(url, payload)

    def get_cloud_storage_link_list(self, owner : str = None) -> str:
        '''
            Get cloud storage links
            @param owner (String): schema name of the Cloud Storage Link (None means that the current schema is used)            
        '''
        if owner is None:
            owner = self.rest.username

        return self.utils.global_search("owner: "+owner +" application: CLOUD type:CLOUD_STORAGE_LINK",0,20001)

    def get_cloud_objects(self, storage_link : str, owner : str = None) -> str:
        '''
            Get Cloud Objects
            
            @param storageLink (String): name of the Cloud Storage Link
            @param owner (String): schema name of the Cloud STorage Link (None means that the current schema is used)            
        '''
        if owner is None:
            owner = self.rest.username

        search_string = "owner: "+owner +"  type: CLOUD_OBJECT  application: CLOUD  parent~= '^\"STORAGE_LINK\".\""+storage_link +"\"' rootName:\"" + storage_link +"\" rootNameSpace:STORAGE_LINK "
        return self.utils.global_search(self.rest.encode(search_string), 0,20001, [{"column":"entity_name","direction":"asc"}], True)

    def _get_available_table_name(self, table_name : str, list_tables : list = None) ->str:
        '''
            Get unique name of the table
            
            @param tableName (String): target table name
            @param listTables (String): already assigned table names
        '''

        cart_table = {'cartTables':[]}
        if list_tables is not None:
            cart_table = {'cartTables':[','.join(list_tables)]}
        url = "{0}/_adpdi/_services/objects/generate_table_name/?targetTableName={1}&cartTableList={2}".format(self.rest.get_prefix(), table_name, self.rest.encode(self.rest.stringify(cart_table)))
        text = self.rest.get(url)
        json_text = json.loads(text)
        if json_text['status_code'] != 0:
            return "No available table name"

        return json_text['returnedTableName']


    def get_consumer_groups(self) -> list:
        '''
            Get list of available consumer groups
        '''

        consumer_groups = []
        url = "{0}/_adpdi/_services/objects/consumer-group-classes/".format(self.rest.get_prefix())
        text = self.rest.get(url)
        job_classes = json.loads(text)
        for job_class in job_classes['jobClasses']:
            consumer_groups.append(job_class['jobClassName'])

        return consumer_groups

    def copy_tables_from_db_link(self, tables : list, consumer_group:str='LOW') -> list:
        '''
            Copy tables from the Database link to the current schema
            
            @param tables: list of dictionary with the following fields:
                - owner (String): owner of the table
                - tableName (String): table name in the Database link
                - dbLink (String): name of the Database link
                - targetTableName (String): optiona, target table name in the current database. If is None, use tableName field 
        '''
        return self._copy_or_link_database_tables(tables, consumer_group, False)

    def link_tables_from_db_link(self, tables : list, consumer_group:str='LOW') -> list:
        '''
            link tables (create view) from the Database link to the current schema
            
            @param tables: list of dictionary with the following fields:
                - owner (String): owner of the table
                - tableName (String): table name in the Database link
                - dbLink (String): name of the Database link
                - targetTableName (String): optiona, target table name in the current database. If is None, use tableName field 
        '''

        return self._copy_or_link_database_tables(tables, consumer_group, True)

    def _copy_or_link_database_tables(self, tables : list, consumer_group : str, is_link : bool) -> list:
        '''
            Copy tables from the Database link to the current schema
            
            @param tables: list of dictionary with the following fields:
                - owner (String): owner of the table
                - tableName (String): table name in the Database link
                - dbLink (String): name of the Database link
                - targetTableName (String): optiona, target table name in the current database. If is None, use tableName field 
        '''
        consumer_groups = self.get_consumer_groups()
        if consumer_group not in consumer_groups:
            consumer_group = consumer_groups[0]

        objects_list = []
        table_dict = {}

        for table in tables:
            if table.get('targetTableName') is None:
                table['targetTableName'] = table['tableName']

        tables = self._get_table_names(tables)

        for table in tables:
            db_link_params = {"schema": table["owner"], "object" : table["tableName"], "name": table["dbLink"]}

            target_table_name = table["targetTableName"]
            text = self.object_analyze({"dbLink":db_link_params})

            json_metadata = json.loads(text)

            metadata = self._generate_metadata_source(json_metadata)

            parameters = {"tableName": table['targetTableName'], "overwriteOption": "AUTO",
					"loadMethod": "APPEND", "dbLink": db_link_params, "jobClass":consumer_group}

            object_list = self.get_object_list(parameters, metadata, is_link)
            objects_list.append({'objectList':object_list})
            table_data = { "schema": table["owner"],
                    "tableName" : table["tableName"],
                    "targetTableName": table["targetTableName"],
                    "name": table["dbLink"] }
            table_dict[target_table_name] = table_data

        ingest_manifest_json = {'tables': objects_list}

        payload = { 'bucket_name': None, 'credential_name': None,  'ingest_manifest_json': self.rest.stringify(ingest_manifest_json)}
        url = "{0}/_adpdi/_services/objects/ingest_cloud_object/".format(self.rest.get_prefix())
        ret = self.rest.post(url, payload)
        json_object = json.loads(ret)
        col = json_object[0]
        request_id = col['requestId']
        return self.progress_status(request_id, table_dict)

    def get_object_list(self, parameters:dict, table_desc: dict, is_link:bool) ->list:
        '''
        get object list
        '''
        object_list = {"headerStartRow": 1,
			"useSimpleColumnNames": True,
			"objectDesc": {
                "metadataSourceType": "INLINE",
                "metadataSourceOwner": None,
                "metadataSource":table_desc},
            "runAsBackgroundJob": "Y",
			"noCollectionSource": True,
			"checkPII": True }
        if is_link:
            object_list["overwriteOption"] ="SKIP"
            object_list["loadMethod"] = "AUTO"
            object_list["ingestOption"] = "EXTERNALVIEW"
        else:
            object_list["overwriteOption"] ="AUTO"
            object_list["loadMethod"] = "APPEND"

        for key in parameters.keys():
            value = parameters[key]
            object_list[key] = value

        ret_object = [object_list]

        return ret_object


    def object_analyze(self, parameters:dict) -> str:
        '''
            Get the metadata for ingest object
            
            @param parameters (dict): additinal parametersf for dblink table or sloud storage file

        '''

        manifest = {'ingestOption':'DIGESTMETADATA','allWarnings': True, 'useSimpleColumnNames':True, 'flattenJson':'DISABLE','tableName':'TEST', 'checkPII': True}

        for key in parameters.keys():
            value = parameters[key]
            manifest[key] = value

        options = {'postJobTransforms':[{'type':'trimcolumns'}]}
        payload = {'ingest_manifest_json': self.rest.stringify(manifest),
                   'options_json': self.rest.stringify(options) }

        url = '{0}/_adpdi/_services/objects/ingest_cloud_object_analyze/'.format(self.rest.get_prefix())
        return self.rest.post(url, payload)

    def copy_cloud_objects(self, objects : list, consumer_group: str = 'LOW') -> list:
        '''
            Copy of cloud objects to the current schema
            
            @param objects (*): List of object to copy:
                - storageLink (String): name of the Cloud Storage link
                - objectName (String): object name in the Coud Storage link
                - targetTableName (String): optiona, target table name in the current database. If is None, use tableName field 

            @param consumerGroup (String): job class for ingest job
        '''

        return self._ingest_cloud_objects(objects, consumer_group, False)

    def link_cloud_objects(self,objects : list, consumer_group:str='LOW') -> list:
        '''
            Create external tables on cloud objects
            
            @param objects (*): List of object to copy:
                - storageLink (String): name of the Cloud Storage link
                - objectName (String): object name in the Coud Storage link
                - targetTableName (String): optiona, target table name in the current database. If is None, use tableName field 

            @param consumerGroup (String): job class for ingest job
        '''
        return self._ingest_cloud_objects(objects, consumer_group, True)


    def _ingest_cloud_objects(self, objects : list, consumer_group : str, is_link : bool) -> list:
        '''
            Perform ingest cloud object
            
            @param objects (*): List of object to copy:
                - storageLink (String): name of the Cloud Storage link
                - objectName (String): object name in the Coud Storage link
                - targetTableName (String): optiona, target table name in the current database. If is None, use tableName field 
            
            @param consumerGroup (String): job class for ingest job
            @param isLink (boolean): true if the external table is created
        '''

        consumer_groups = self.get_consumer_groups()
        if consumer_group not in consumer_groups:
            consumer_group = consumer_groups[0]

        for target_object in objects:
            if target_object.get('targetTableName') is None:
                target_object['targetTableName'] = self._convert_table_name(os.path.splitext(os.path.basename(target_object['objectName']))[0])
            target_table_name = target_object['targetTableName']

        objects = self._get_table_names(objects)

        ingest_manifest_json = {'tables':[]}

        init_format_string = {"ignoremissingcolumns":True,"ignoreblanklines":True,"blankasnull":True,"rejectlimit":10000,"trimspaces":"lrtrim","skipheaders":1}
        objects_list = []
        table_dict ={}

        for target_object in objects:
            storage_link = target_object['storageLink']
            object_name = target_object['objectName']
            target_table_name = target_object['targetTableName']

            parameters = {'adpBucket':storage_link,'objectName':object_name, "formatString":init_format_string}

            text = self.object_analyze(parameters)
            json_metadata = json.loads(text)

            format_string = json_metadata[0]["formatString"]
            metadata = self._generate_metadata_source(json_metadata)

            parameters = {'adpBucket':storage_link,"tableName": target_table_name, "overwriteOption": "AUTO",'objectNames':[{'objectName':object_name}],
					"loadMethod": "APPEND", "jobClass":consumer_group, "formatString":format_string}

            object_list = self.get_object_list(parameters, metadata, is_link)
            objects_list.append({'objectList':object_list})
            table_data = { "storageLink": storage_link,
                    "targetTableName": target_table_name,
                    'objectName':object_name}
            table_dict[target_table_name] = table_data

        ingest_manifest_json = {'tables': objects_list}

        payload = { 'bucket_name': None, 'credential_name': None,  'ingest_manifest_json': self.rest.stringify(ingest_manifest_json)}
        url = "{0}/_adpdi/_services/objects/ingest_cloud_object/".format(self.rest.get_prefix())
        ret = self.rest.post(url, payload)
        json_object = json.loads(ret)
        col = json_object[0]
        request_id = col['requestId']
        return self.progress_status(request_id, table_dict)

    def cloud_progress_status(self, request_id: int, schema: str = None) -> str:
        '''
        Get job progress status
        '''
        if schema is None:
            schema = self.rest.username

        request_desc = [{"schema": schema,"request_id":request_id}]
        request_text = urllib.parse.quote(self.rest.stringify(request_desc))
        t = round(time.time())

        url = f"{self.rest.get_prefix()}/_adpdi/_services/objects/cloud_ingest_progress_status/?request_desc={request_text}&_={t}"

        return self.rest.get(url)

    def _generate_metadata_source(self, manifest : dict) -> list:
        '''
            Generate metadata after metadata analyzing
            
            @param manifest (*): output of metadata analyzing
        '''
        metadata = []
        for column in manifest[0]['metadataSource']:
            column_metadata = {'columnName':column['columnName'], 'dataType': column['dataType'], 'columnId':column['columnId'], 'fieldName': column['fieldName'], 'skipColumn': False, 'dataFormat': column["dataFormat"] }
            if column['dataType'] == 'VARCHAR2':
                column_metadata['dataLength'] = column['dataLength']
            if column.get('sourcePath') is not None:
                column_metadata['sourcePath'] = column['sourcePath']

            metadata.append(column_metadata)

        return metadata

    def progress_status(self, request_id:int, table_dict:dict) -> list:
        '''
            Waiting for ingest completion
        '''
        result_data = []

        while True:
            is_continue = False
            time.sleep(3)
            text = self.cloud_progress_status(request_id)
            responses = json.loads(text)
            for response in responses:
                status = response["status"]
                if status !="complete":
                    is_continue = True
                    break
            if is_continue:
                continue
            for response in responses:
                table_data = table_dict[response['table_name']]
                if response['rows_total'] is not None:
                    table_data["rowsCopied"] = response['rows_total']
                result_data.append(table_data)
            return result_data

    def _get_date_time(self) -> str:
        '''
            Get current date
        '''
        now = datetime.now()
        return now.strftime("%m%d%Y_%H%M%S")


    def _convert_table_name(self, name : str) -> str:
        '''
            Convert table name
            
            @param name (String): name of the table or column

        '''
        name = name.replace('.', '_').replace('-', '_').upper()
        return name


    def _get_table_names(self, files: list ) -> list:
        '''
            Check table names
                
            @param files (*): list of files to load
        '''

        list_tables = []
        for file in files:
            table_name = file['targetTableName']
            table_name = self._get_available_table_name(table_name, list_tables)
            list_tables.append(table_name)
            file['targetTableName'] = table_name

        return files

    def load_data(self, content_list : list) -> list:
        '''
            Load content to tables

            @param content_list (*): list of contents to load with the following fields:
                - content (*): list of columns with its content Each column contains of column name and list of its values. All column shuold have the same length of values.
                - targetTableName (String): target table name in the current database. If is None, use fileName field
        '''


        content_list = self.update_table_names(content_list)

        table_name = content_list[0]['targetTableName']

        output_record = []

        table_names = []
        for table in content_list:

            table_name = table['targetTableName']
            table_names.append(table_name)

            #  Check length of the content

            content = table['content']
            length = -1
            for data in content:
                if length == -1:
                    length = len(content[data])
                    continue
                if length != len(content[data]):
                    message = "Content of the table has different column length"
                    json_message = {'message': message}
                    return json_message

            #print(file)
            columns = self.add_metadata(table)
            #print(json.dumps(columns, indent=2))

            statement = self.create_table(columns, table_name)
            payload = {'responseFormat': self.response_format, 'statementText': statement }

            #print(payload)
            self.utils.execute(payload, False)
            #print(text)

            error_table = 'ADP$ERR$' + table_name

            self.drop_error_log(error_table)
            self.create_error_log(table_name, error_table)


            timestamp=str(round(datetime.now().timestamp()))

            statement, binds = self.insert_rows(columns, table, error_table, timestamp)
            for bind in binds:
                payload = {'responseFormat': self.response_format,
                'statementText': statement,
                'binds':bind
                }
                #print(payload)

                self.utils.execute(payload, False)

            items = list(table['content'].values())
            rows_copied = len(items[0])

            record = {'fileName': table_name, 'targetTableName': table_name, 'rowsCopied': rows_copied}
            output_record.append(record)

        return output_record

    def update_table_names(self, content_list : list) -> list:
        '''
            Update table names for files
                
            @param files (*): list of files to load       
        '''

        for table in content_list:
            table_name = self._convert_table_name(table.get('targetTableName'))

            table['targetTableName'] = table_name

        return content_list

    def drop_error_log(self, error_table: str, owner : str = None) -> str:
        '''
            Drop error log table
            @param errorTable (String): name of the error log table        
            @param owner (String): schema name of the error log table (None means that the current schema is used)            
        '''

        if owner is None:
            owner = self.rest.username

        payload = { 'owner': owner, 'err_objectname': '\"' + error_table + '\"'}

        url = "{0}/_adpdi/_services/objects/drop-error-log/".format(self.rest.get_prefix())
        return self.rest.post(url, payload)


    def create_error_log(self, table_name : str, error_table : str, owner : str = None) -> str:
        '''
            Create error log table
            
            @param tableName (String): target table name in the current database
            @param errorTable (String): name of the error log table        
            @param owner (String): schema name of the error log table (None means that the current schema is used)            
        '''
        if owner is None:
            owner = self.rest.username

        payload = { 'owner': owner, 'objectname': '\"' + table_name + '\"',
                   'err_objectname': '\"' + error_table + '\"', 'skip_unsupported_columns': True}

        url = "{0}/_adpdi/_services/objects/error-log/".format(self.rest.get_prefix())
        return self.rest.post(url, payload)

    def add_metadata(self, columns : dict) -> list:
        '''
            Add datatype to all columns
            
            @param columns (*): columns of the data
        '''
        text = self.get_content(columns)
        metadata = self.get_inline_source(text)
        json_metadata = json.loads(metadata)
        return self.add_column_types(columns['content'], json_metadata)

    def add_column_types(self, data : dict, metadata : dict) -> list:
        '''
            Read datatype from metadata
            
            @param data (*): columns of the data
            @param metadata (String): metadata

        '''
        columns = []

                #json_text = json.loads(metadata)

        items = metadata['items']

        for item in items:
            if item.get('dbmsOutput') is not None:
                dbms = item.get('dbmsOutput')
                dbms = dbms.strip()
                dbms = dbms.replace('\\r', '')
                dbms = dbms.replace('\\n', '')
                dbms = dbms.replace('\n', '')
                json_dbms = json.loads(dbms)
                source_metadata = json_dbms[0]['sourceMetadata']

                for metadata_part in source_metadata:
                    column = {}
                    field_name = metadata_part['fieldName']
                    column['column'] = metadata_part['columnName']
                    data_type = metadata_part['dataType']
                    if data_type == 'TIMESTAMP':
                        data_type = 'DATE'
                    column['datatype'] = data_type
                    if column['datatype'] == 'DATE':
                        data_format = self.get_format_mask(data[column['column']][0])
                        json_format = json.loads(data_format)
                        format_mask = json_format['formatMask']
                        if format_mask.startswith('FXFM'):
                            column['data_format'] = format_mask.replace('FXFM','')
                    elif column['datatype'] == 'VARCHAR2':
                        column['datatype'] = 'VARCHAR2(4000)'

                    payload = {field_name: column}
                    columns.append(payload)
        return columns

    def get_inline_source(self, content) -> list:
        '''
            Get metadata of the CSV file
            
            @param content (String): the content of the CSV file
        '''

        metadata_source = {'tableName': 'mytable', 'formatString': {'delimiter': ','} }
        ingest_parameters = {'ingestOption': 'DIGESTMETADATA', 'stagingOption':'EXTERNAL_TABLE'}
        statement_array = ['SET SERVEROUTPUT ON', 'SET DEFINE &;', 'SET ESCAPE OFF;', 'SET TIMING ON;', 'ALTER SESSION SET NLS_LANGUAGE = \'AMERICAN\';',
            'DECLARE', '    result CLOB;', '    i   INTEGER;', 'BEGIN',  
            'result := DBMS_INGEST.ingest_inline_source(:1, \n\'{0}\', \'{1}\');'.format(self.rest.stringify(metadata_source),self.rest.stringify(ingest_parameters)),
            'FOR i in 1..CEIL(LENGTH(result) / 4000)LOOP',
            '    dbms_output.put(DBMS_LOB.SUBSTR(result, 4000, (i - 1) * 4000 + 1));', 'END LOOP;', 'dbms_output.put_line(\'\');', 'END;']

        statement = ""
        for text in statement_array:
            statement = statement + text + '\n'
        #print(self.rest.stringify(statement))
        binds = [{'index': 1, 'data_type':'CLOB', 'value': content}]
        payload={'statementText': statement, 'offset': 0, 'limit': 100, 'binds': binds}

        #print(self.rest.stringify(payload))

        return self.utils.execute(payload, False)

    def get_format_mask(self, value : str) -> str:
        '''
            Get date format
            @param value (String): date value
        '''
        payload = { 'dates': value }

        url = "{0}/_adpdi/_services/objects/format-mask/".format(self.rest.get_prefix())
        return self.rest.post(url, payload)

    def create_table(self, columns: list, table_name : str):
        '''
            Produce Create table statement
            @param tableName (String): name of the table        
        '''
        cols = []

        for column in columns:
            description = list(column.values())
            col = '{0} {1}'.format(description[0]['column'] ,description[0]['datatype'])
            cols.append(col)


        statement = 'SET DEFINE OFF;\nCREATE TABLE {0}.\"{1}\" ( {2} );\n'.format(self.rest.username, table_name, ','.join(cols))

        return statement


    def insert_rows(self, columns : list, table_data : dict, error_table : str, timestamp : str) ->Tuple[str, list]:
        '''
            Produce insert into table statement
            
            @param tableName (String): name of the table        
            @param errorTable (String): name of the error log table        
            @param timestamp (String): current timestamp for error log table 
        '''
        cols = []
        values=[]
        binds = []

        table_name  = table_data['targetTableName']

        index = 1
        for column in columns:
            #print(column)
            description = list(column.values())
            cols.append(' ' + description[0]['column'])

            value = ' ?'
            if description[0].get('data_format') is not None:
                value = ' to_date(?, \'{0}\')'.format(description[0]['data_format'])
            values.append(value)
            index = index + 1

        statement = 'SET DEFINE OFF;\nINSERT INTO {0}.\"{1}\" ({2} ) VALUES ({3} ) LOG ERRORS INTO \"{4}\" (\'{5}\') REJECT LIMIT UNLIMITED;'.format(self.rest.username, table_name, ','.join(cols), ','.join(values), error_table, timestamp)

        binds = self.create_bind(columns, table_data)
        return statement, binds

    def create_bind(self, columns : list, content : dict) -> list:
        '''
            Create bind payload
        '''
        all_binds = []

        chunk_size = 1000

        content_list = content['content']

        #print(content_list)

        items = list(content_list.values())
        length = len(items[0])


        for i in range(0, length, chunk_size):
            binds = []
            index = 1
            for column in columns:
                col = tuple(column)
                content_column = content_list[col[0]]

                bind = {'index': index, 'data_type':'VARCHAR2','batch':True,'value': content_column[i:i+chunk_size]}
                binds.append(bind)
                index = index + 1
            all_binds.append(binds)

        return all_binds

    def get_content(self, table : dict, limit=100) -> str:
        '''
            Convert columns to CSV format
            
            @param columns (*): list of columns
            @param limit (Integer): maximum number of rows
        '''
        header = table['content'].keys()
        rows = []

        add_rows = True

        for column in header:
            content = table['content'][column]
            i = 0
            for value in content:
                if add_rows:
                    rows.append([])
                rows[i].append(json.dumps(value))
                i = i+1
                if i >= limit:
                    break
            add_rows = False

        ret_val = ','.join(header) + '\n'
        for row in rows:
            ret_val = ret_val + ','.join(row) + '\n'

        return ret_val

