'''
Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/.

Copyright (c) 2023-2025, Oracle and/or its affiliates.

'''

import json
from typing import Union
from .rest import Rest

class AdpMisc():
    '''
    classdocs
    '''
    def __init__(self) -> None:
        '''
        Constructor
        '''
        self.rest=None
        self.response_format = {
            'resultSetMetadata': False,
            'statementInformation': False,
            'statementText': False,
            'binds': False,
            'result': True,
            'response': False
            }

    def set_rest(self, rest : Rest) -> None:
        '''
            Set Rest instance
            
            @param rest (Rest): rest instance
        '''
        self.rest = rest

    #pylint: disable=too-many-arguments

    def global_search(self, search_string : str, rowstart : int, numrow : int, sort_by : list =None, hide_system_tables : bool = False, hide_private_tables: bool = False, resultapp : str = None, resultannotation : str = None) -> str:
        '''
            Search objects in the DB
            
            @param searchString (String): string to search
            @param rowstart (Integer): first index of searching
            @param numrow (Integer): number of returned rows
            @param sortBy (*): list of sort, e.g. [{column: "entity_name", direction: "asc"}]
            @param hideSystemTables  (boolean):
            @param hidePrivateTables (boolean):
            @param resultapp (String):
            @param resultannotation (*):
        '''

        data = "search={}".format(search_string)
        if sort_by is not None:
            data = data + "&sortjson={}".format(self.rest.encode(self.rest.stringify(sort_by)))
        else:
            data = data + "&sortjson="
        if hide_system_tables:
            data = data + "&hidesys=true"
        else:
            data = data + "&hidesys=false"
        if hide_private_tables:
            data = data + "&hideprivate=true"
        else:
            data = data + "&hideprivate=false"
        if resultapp is not None:
            data = data + "&resultapp={}".format(resultapp)
        if resultannotation is not None:
            data = data + "&resultannotation={}".format(resultannotation)
        data = data +"&rowstart={0}&numrows={1}".format(rowstart, numrow)

        url = "{0}/_adplmd/_services/objects/search2/?{1}".format(self.rest.get_prefix(), data)

        return self.rest.get(url)

    def lineage_search(self, search_string : str, rowstart : int, numrow : int, sort_by  : list = None, hide_system_tables : bool = False, hide_private_tables : bool = False, resultapp : str = None, resultannotation : str = None) -> str:
        '''
            Search objects in the DB
            
            @param searchString (String): string to search
            @param rowstart (Integer): first index of searching
            @param numrow (Integer): number of returned rows
            @param sortBy (*): list of sort, e.g. [{column: "entity_name", direction: "asc"}]
            @param hideSystemTables  (boolean):
            @param hidePrivateTables (boolean):
            @param resultapp (String):
            @param resultannotation (*):
        '''

        data = "search={}".format(search_string)
        if sort_by is not None:
            data = data + "&sortjson={}".format(self.rest.encode(self.rest.stringify(sort_by)))
        else:
            data = data + "&sortjson="
        if hide_system_tables:
            data = data + "&hidesys=true"
        else:
            data = data + "&hidesys=false"
        if hide_private_tables:
            data = data + "&hideprivate=true"
        else:
            data = data + "&hideprivate=false"
        if resultapp is not None:
            data = data + "&resultapp={}".format(resultapp)
        if resultannotation is not None:
            data = data + "&resultannotation={}".format(resultannotation)
        data = data +"&rowstart={0}&numrows={1}".format(rowstart, numrow)

        url = "{0}/_adplmd/_services/objects/search/?{1}".format(self.rest.get_prefix(), data)

        return self.rest.get(url)

    #pylint: enable=too-many-arguments


    def run_query(self, statement : str, offset : int = None, limit : int = None, asof=None) -> Union[str, list]:
        '''
            Execute statement
            
            @param statement (String): Statement to execute
            @param offset (Integer):
            @param limit (Integer):
            @param asof:
        '''

        payload={"statementText": statement}
        if offset is not None:
            payload["offset"] = offset
        if limit is not None:
            payload["limit"] = limit
        if asof is not None:
            payload["asof"] = asof
        return self.execute(payload)

    def execute(self, payload : dict, parse : bool = True) -> Union[str, list]:
        '''
            Execute statement
            
            @param payload (*): payload to execute statements
            @param parse (boolean): True is requires to parse the output
        '''

        url = "{0}/_/sql".format(self.rest.get_prefix())
        text = self.rest.post(url, payload)
        #print(text)
        #print(json_object)
        if parse:
            json_object = json.loads(text)
            json_object2 =json_object['items'][0]
            if json_object2.get('resultSet') is None:
                return text
            json_object3 =json_object2['resultSet']
            if json_object3.get('items') is None:
                return text
            json_object4 =json_object3['items']
            return json_object4
        return text

    def list_tables(self, owner: str  = None) -> str:
        '''
            Get list of tables
            @param owner (String): schema name of the tables (None means that the current schema is used)            
        '''
        if owner is None:
            owner = self.rest.username

        search_string = '( owner: {0} ) ( type: TABLE ) ( application: DATABASE )'.format(owner)
        return self.global_search(search_string=search_string, rowstart=1, numrow=20001,hide_system_tables=True, hide_private_tables=True, resultapp="ADPINS")

    def list_views(self, owner : str = None) -> str:
        '''
            Get list of views
            @param owner (String): schema name of the views (None means that the current schema is used)            
        '''

        if owner is None:
            owner = self.rest.username

        search_string = '( owner: {0} ) ( type: VIEW ) ( application: DATABASE )'.format(owner)
        return self.global_search(search_string=search_string, rowstart=1, numrow=20001,hide_system_tables=True, hide_private_tables=True, resultapp="ADPINS")

    def drop_table(self, table_name : str)-> Union[str, list]:
        '''
            Drop the table
            
            @param tableName (String): Name of table to be dropped
        '''
        tables = [table_name]
        return self.drop_tables(tables)

    def drop_view(self, view_name : str)-> Union[str, list]:
        '''
            Drop the view
            
            @param ViewName (String): Name of view to be dropped

        '''
        views = [view_name]
        return self.drop_views(views)

    def drop_tables(self, table_names : list) -> Union[str, list]:
        '''
            Drop the tables
            
            @param tableNames (*): Array of table names to be dropped
        '''
        statements = ['SET DEFINE OFF;']
        for table_name in table_names:
            statements.append("DROP TABLE {0}.\"{1}\" CASCADE CONSTRAINTS;".format(self.rest.username, table_name.upper()))

        statement = '\n'.join(statements)
        payload = {'statementText': statement }
        return self.execute(payload, False)

    def drop_views(self, view_names : list)-> Union[str, list]:
        '''
            Drop the views
            
            @param viewNames (*): Array of view names to be dropped
        '''
        statements = ['SET DEFINE OFF;']
        for view_name in view_names:
            statements.append("DROP VIEW {0}.\"{1}\";".format(self.rest.username, view_name.upper()))
        statement = '\n'.join(statements)
        payload = {'statementText': statement }
        return self.execute(payload, False)

    def get_entity_ddl(self, entity_name, entity_type, owner = None) -> str:
        '''
            Get entity DDL
            
            @param entityName (String): name of the entity
            @param entityType (String): type of the entity
            @param owner (String): schema name of the entity (None means that the current schema is used)
        '''
        if owner is None:
            owner = self.rest.username
        url="{0}/_adpavd/_services/objects/getentityddl/?name={1}&type={2}&owner={3}".format(self.rest.get_prefix(), entity_name.upper(), entity_type.upper(), owner)
        return self.rest.get(url)

    def get_table_columns(self, table_name : str, owner : str = None, limit : int = 256, offset : int = 0) -> list:
        '''
            Get columns of the table
 
            @param tableName (String): name of the table              
            @param limit (Integer): maximum number of columns              
            @param offset (Integer): first index of columns              
            @param owner (String): the scheme of the table (None means that the current schema is used)               
        '''

        return self._table_metadata("columns", table_name.upper(), owner, limit, offset)

    def get_table_constraints(self, table_name : str, owner : str = None, limit : int = 256, offset : int = 0) -> list:
        '''
            Get constraints of the table
 
            @param tableName (String): name of the table              
            @param limit (Integer): maximum number of constraints              
            @param offset (Integer): first index of constraints              
            @param owner (String): the scheme of the table (None means that the current schema is used)               
        '''

        return self._table_metadata("constraints", table_name.upper(), owner, limit, offset)

    def insert_row(self, table_name: str, data, mapping=None, owner : str = None) -> Union[str, list]:
        '''
            Insert row table from data
 
            @param tableName (String): name of the table              
            @param data (Json): data to insert int he form  {"column_name":"value",...}
            @param mapping (Json): mapping in the form {"column":"table_column",...}, None means that data has table columns names
            @param owner (String): the scheme of the table (None means that the current schema is used)               
        '''

        if owner is None:
            owner = self.rest.username

        columns_dict = self._convert_columns_to_json(table_name.upper(), owner)

        new_data = self._collect_data(data, columns_dict, mapping)

        correct = True
        for key, table_value in columns_dict.items():
            if table_value['nullable'] == 'No':
                if columns_dict.get(key) is None:
                    correct = False
                    break

        if not correct:
            return "Not all nullable columns have values"

        cols = []
        values=[]
        binds = []

        index = 1
        for key, table_value in new_data.items():
            cols.append(' ' + key)
            value = self._format_value(table_value['data_format'])
            values.append(value)
            bind = {'index': index, 'data_type':'VARCHAR2','batch':True,'value': str(table_value['value'])}
            binds.append(bind)
            index = index + 1

        statement = 'SET DEFINE OFF;\nINSERT INTO {0}.\"{1}\" ({2} ) VALUES ({3} );'.format(owner, table_name.upper(), ','.join(cols), ','.join(values))

        #print(statement)
        #print(binds)

        return self._execute(statement, binds)

    def update_row(self, table_name : str, data : dict, where_column : str, mapping: dict = None, owner : str = None) -> Union[str, list]:
        '''
            Update data in the specified row table
 
            @param tableName (String): name of the table              
            @param data (Json): data to insert int he form  {"column_name":"value",...}
            @param mapping (Json): mapping in the form {"column":"table_column",...}, None means that data has table columns names
            @param whereColumn (String): column name of the data that specifies the constraint on append               
            @param owner (String): the scheme of the table (None means that the current schema is used)               
        '''

        if owner is None:
            owner = self.rest.username

        columns_dict = self._convert_columns_to_json(table_name, owner)

        new_data = self._collect_data(data, columns_dict, mapping, where_column)

        where_col = where_column
        if mapping is not None:
            where_col = mapping.get(where_column)
        if where_col is None:
            return "Where column is not match"
        where_format = self._format_column(columns_dict, where_col, data.get(where_column))

        cols = []
        binds = []

        index = 1
        for key, table_value in new_data.items():
            value = self._format_value(table_value['data_format'])
            cols.append(f' {key}={value}')
            bind = {'index': index, 'data_type':'VARCHAR2','batch':True,'value': str(table_value['value'])}
            binds.append(bind)
            index = index + 1

        value = self._format_value(where_format, str(data.get(where_column)))
        bind = {'index': index, 'data_type':'VARCHAR2','batch':True,'value': value}
        binds.append(bind)

        statement = 'SET DEFINE OFF;\nUPDATE {0}.\"{1}\" SET {2} WHERE {3}=?;'.format(owner, table_name, ','.join(cols), where_col)

        #print(statement)
        #print(json.dumps(binds, indent=2))

        return self._execute(statement, binds)

    def _convert_columns_to_json(self, table_name : str, owner : str = None) -> dict:
        '''
             Convert table metadata to json for easy access
 
            @param tableName (String): name of the table              
            @param owner (String): the scheme of the table (None means that the current schema is used)               
       '''

        if owner is None:
            owner = self.rest.username

        columns_dict = {}
        columns = self._table_metadata('columns', table_name.upper(), owner)
        for column in columns:
            column_name = column['column_name']
            columns_dict[column_name]=column

        return columns_dict

    def _format_column(self, columns : dict, column_name : str, value : str) -> str:

        column = columns[column_name]
        if column is None:
            return None
        data_format = None
        if column['data_type'] == 'DATE' or  column['data_type'] == 'TIMESTAMP':
            data_format = self._get_format_mask(value)
            json_format = json.loads(data_format)
            format_mask = json_format['formatMask']
            if format_mask.startswith('FXFM'):
                data_format = format_mask.replace('FXFM','')
        return data_format

    def _format_value(self, data_format : str, value : str = None) -> str:

        if value is None:
            ret_val = ' ?'
        else:
            ret_val = value
        if data_format is not None:
            if value is None:
                ret_val = ' to_date(?, \'{0}\')'.format(data_format)
            else:
                ret_val = ' to_date({0}, \'{1}\')'.format(value, data_format)

        return ret_val

    def _get_format_mask(self, value : str) -> str:
        '''
            Get date format
            @param value (String): date value
        '''
        payload = { 'dates': value }

        url = "{0}/_adpdi/_services/objects/format-mask/".format(self.rest.get_prefix())
        return self.rest.post(url, payload)

    def _table_metadata(self, obj_type : str, table_name : str, owner : str = None, limit : int = 256, offset : int = 0) -> list:
        '''
            Get part of table metadata
        '''

        if owner is None:
            owner = self.rest.username

        url = "{0}/_sdw/_services/browsers/table/{1}/?OBJECT_NAME={2}&OBJECT_OWNER={3}&limit={4}&offset={5}&q=%7B%7D".format(self.rest.get_prefix(), obj_type, table_name.upper(), owner, limit, offset)
        text = self.rest.get(url)
        json_text = json.loads(text)
        return json_text['items']


    def _execute(self, statement : str, binds : list)-> Union[str, list]:
        '''
            Call runQuery
            @param statement (String) - statement to execute
            @param binds - json with values
        '''
        payload = {'responseFormat': self.response_format,
                'statementText': statement,
                'binds':binds
                }
        return self.execute(payload, False)

    def _collect_data(self, data : dict, columns : dict, mapping : dict, where_column : str = None) -> dict:
        new_data = {}
        for key, value in data.items():
            if where_column is not None:
                if key == where_column:
                    continue
            column_name = key
            if mapping is not None:
                column_name = mapping.get(key)
            if column_name is None:
                return  "Mapping is not match"
            column = columns[column_name]
            if column is None:
                continue
            data_format = self._format_column(columns, column_name, value)
            new_data[column_name] = {'value':value, 'data_type': column['data_type'], 'data_format':data_format}
        return new_data
