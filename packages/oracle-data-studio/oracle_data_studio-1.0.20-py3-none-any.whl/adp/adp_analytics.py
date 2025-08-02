'''
Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/.

Copyright (c) 2023-2025, Oracle and/or its affiliates.

'''
import json
import time
from typing import Tuple
from requests.exceptions import HTTPError
from .rest import Rest
from .rest import ThreadWithResult
from .adp_misc import AdpMisc

#pylint: disable=R0904
class AdpAnalytics():
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.utils = AdpMisc()
        self.rest=None
        self.error = False

    def set_rest(self, rest: Rest):
        '''
            Set Rest instance
            
            @param rest (Rest): rest instance
        '''
        self.rest = rest
        self.utils.set_rest(rest)

    def get_list(self, owner : str = None) -> str:
        '''
            Gel list of Analytic Views
            @param owner (String): schema name of the analytic views (None means that the current schema is used)
        '''
        if owner is None:
            owner = self.rest.username
        search_string = "( owner: {0}  )  ( type: ANALYTIC_VIEW  )  ( application: DATABASE )".format(owner)
        return self.utils.global_search(search_string=search_string, rowstart=1, numrow=50,hide_system_tables=True, hide_private_tables=True, resultapp="ADPINS")

    def drop(self, model_name : str, delete_objects : bool = True) -> str:
        '''
            Drop the Analytic view
            
            @param model_name (String): name of the Analytic view
            @param delete_objects (boolean): Delete object
        '''
        if self.is_exist(model_name):
            delete="FALSE"
            if delete_objects:
                delete = "TRUE"
            url = "{0}/_adpavd/_services/objects/dropavmodel/".format(self.rest.get_prefix())
            data={"name": model_name, "deleteObjects": delete}
            self.rest.post(url, data)
            return 'success'
        return "{\"message\": \"Analytic view does not exist\"}"

    def get_measures_list(self, av_name : str, owner : str = None) -> str:
        '''
            Get list of measures for Analytic view 
            @param av_name (String): name of the Analytic view
            @param owner (String): schema name of the analytic view (None means that the current schema is used)
       '''
        if owner is None:
            owner = self.rest.username
        if self.is_exist(av_name, owner):
            url = "{0}/_adpins/_services/objects/entityhierarchy/?entityschema={1}&entitytype=MEASURE&parentpath=\"DB\".\"{2}\"".format(self.rest.get_prefix(), self.rest.encode(owner), self.rest.encode(av_name))
            return self.rest.get(url)
        return "{\"message\": \"Analytic view does not exist\"}"


    def get_data_preview(self, entity_name : str, owner : str = None) ->str:
        '''
            Get data preview for the analytic view
            @param entity_name (String): name of the Analytic view
            @param owner (String): schema name of the analytic view (None means that the current schema is used)
        '''
        if owner is None:
            owner = self.rest.username
        if self.is_exist(entity_name, owner):
            data = {"object":{ "owner": owner,"name": entity_name, "type": "ANALYTIC_VIEW"}, "metadata": {}, "results": { "metadata": True, "data": True }}
            data_text = self.rest.stringify(data)
            url = "{0}/_adpavd/_services/objects/avdata/?av_query_json={1}".format(self.rest.get_prefix(), self.rest.encode(data_text))
            return self.rest.get(url)
        return "{\"message\": \"Analytic view does not exist\"}"

    def get_metadata(self, av_name : str, owner : str = None) -> str:
        '''
            Get Analytic view metadata
            @param av_name (String): name of the analytic view
            @param owner (String): schema name of the analytic view (None means that the current schema is used)
        '''
        if owner is None:
            owner = self.rest.username
        if self.is_exist(av_name, owner):
            url = "{0}/_adpanalytics/_services/objects/getAVMetadata/?av_name={1}&owner={2}".format(self.rest.get_prefix(), av_name, owner)
            return self.rest.get(url)
        return "{\"message\": \"Analytic view does not exist\"}"


    def get_dimension_names(self,av_name : str) -> str:
        '''
            Get dimension names for the Analytic view
            @param av_name (String): name of the analytic view
        '''

        if self.is_exist(av_name):
            url =  "{0}/_adpanalytics/_services/objects/getDimensionNames/?av_name={1}".format(self.rest.get_prefix(), av_name)
            return self.rest.get(url)
        return "{\"message\": \"Analytic view does not exist\"}"

    def get_fact_table_name(self, av_name : str) -> str:
        '''
            Get name of fact table for the Analytic view
            @param av_name (String): name of the Analytic view
        '''

        if self.is_exist(av_name):
            url = "{0}/_adpanalytics/_services/objects/getFactTableNames/?av_name={1}".format(self.rest.get_prefix(), av_name)
            return self.rest.get(url)
        return "{\"message\": \"Analytic view does not exist\"}"

    def get_error_classes_from_dim(self, av_name : str, dimension : str) -> str:
        '''
            Get error class for the dimension name for the Analytic view
            @param av_name (String): name of the Analytic view
            @param dimension (String): name of the dimension
        '''

        if self.is_exist(av_name):
            get_details = {
                "av_name": av_name,
                "dimension": dimension
            }
            url = "{0}/_adpanalytics/_services/objects/getErrorClassesFromDim/?get_dim_details={1}".format(self.rest.get_prefix(), self.rest.encode(self.rest.stringify(get_details)) )
            return self.rest.get(url)
        return "{\"message\": \"Analytic view does not exist\"}"

    def get_error_classes_from_fact_tab(self, av_name : str, fact_tab : str) -> str:
        '''
            Get error class for the fact table for the Analytic view
            @param av_name (String): name of the Analytic view
            @param factTab (String): name of the fact table
        '''

        if self.is_exist(av_name):
            get_details = {
                "av_name": av_name,
                "fact_tab": fact_tab
            }
            url = "{0}/_adpanalytics/_services/objects/getErrorClassesFromFactTab/?get_tab_details={1}".format(self.rest.get_prefix(), self.rest.encode(self.rest.stringify(get_details)) )
            return self.rest.get(url)
        return "{\"message\": \"Analytic view does not exist\"}"

    def quality_report(self, av_name: str) ->str:
        '''
            Get quality report
        '''
        if self.is_exist(av_name):

            error_list = []

            text = self.get_fact_table_name(av_name)
            j = json.loads(text)
            fact_table = j["FACT_TABLE_NAME"]

            text = self.get_dimension_names(av_name)
            j = json.loads(text)

            dims = []
            for dim in j:
                dims.append(dim['DIMENSION_NAME'])

            text = self.get_error_classes_from_fact_tab(av_name, fact_table)
            j = json.loads(text)
            count = j[0]['ERROR_COUNT']
            if count == 0:
                error_text = f'Fact table {fact_table} has no errors'
                error_list.append(error_text)
            else:
                error_messages = []
                error_data = j[0]['errorData']
                for err_data in error_data:
                    error_messages.append(err_data['ERROR_MESSAGE'])
                messages = ";".join(error_messages)
                error_text = f'Fact table {fact_table} has {count} errors: {messages}'
                error_list.append(error_text)

            for dim in dims:
                text = self.get_error_classes_from_dim(av_name, dim)
                j = json.loads(text)
                count = j[0]['ERROR_COUNT']
                if count == 0:
                    error_text = f'Dimension {dim} has no errors'
                    error_list.append(error_text)
                else:
                    error_messages = []
                    error_data = j[0]['errorData']
                    for err_data in error_data:
                        error_messages.append(err_data['ERROR_MESSAGE'])
                    messages = ";".join(error_messages)
                    error_text = f'Dimension {dim} has {count} errors: {messages}'
                    error_list.append(error_text)

            return json.dumps(error_list)
        return "{\"message\": \"Analytic view does not exist\"}"

    def _get_payload(self, levels : bool, column_names : list, entity_name : str, hierarchies : list, measures : list, where_condition : list, owner = None) -> dict:
        '''
            Get payload for getting data
            
            @param levels:
            @param columnNames:
            @param entityName:
            @param hierarchies:
            @param measures:
            @param whereCondition:
            @param owner (String): schema name of the entity (None means that the current schema is used)
       '''
        if owner is None:
            owner = self.rest.username
        return {
            "visualspec": {"hierOrder": False,"addAllHiers": False, "addAllMeas": False, "hierAttributes": True,
                "levels": levels, "columns": column_names},
            "object": { "owner": owner, "name": entity_name, "type": "ANALYTIC_VIEW"},
            "queryspec": {   "hierarchies": hierarchies, "measures": measures,
                "where": where_condition, "fromDepth": 1, "toDepth": 100},
            "results": { "metadata": True, "data": True}
        }

    def get_data(self, levels : bool, column_names : list, entity_name : str, hierarchies : list, measures : list, where_condition : list, owner = None) -> str:
        '''
            Get data of the Analytic view
            
            @param levels:
            @param columnNames:
            @param entityName:
            @param hierarchies:
            @param measures:
            @param whereCondition:
            @param owner (String): schema name of the enrtity (None means that the current schema is used)
        '''
        if self.is_exist(entity_name):
            payload = self._get_payload(levels, column_names, entity_name, hierarchies, measures, where_condition, owner)
            url = "{0}/_adpanalytics/_services/objects/getAVData/".format(self.rest.get_prefix())
            #print(url)
            return self.rest.post(url, payload)
        return "{\"message\": \"Analytic view does not exist\"}"


    def get_sql(self, levels : bool, column_names : list, entity_name : str, hierarchies : list, measures : list, where_condition : list, owner = None) -> str:
        '''
            Get SQL query for data of the Analytic view
            
            @param levels:
            @param columnNames:
            @param entityName:
            @param hierarchies:
            @param measures:
            @param whereCondition:
            @param owner (String): schema name of the entity (None means that the current schema is used)
       '''

        if self.is_exist(entity_name):
            payload = self._get_payload(levels, column_names, entity_name, hierarchies, measures, where_condition, owner)
            url = "{0}/_adpanalytics/_services/objects/getSQL/".format(self.rest.get_prefix())
            return self.rest.post(url, payload)
        return "{\"message\": \"Analytic view does not exist\"}"


    def compile(self, av_name : str, owner : str = None) -> str:
        '''
            Compile the Analytic view
            
            @param avName (String): name of the Analytic view
            @param owner (String): schema name of the fact table (None means that the current schema is used)
        '''
        if owner is None:
            owner = self.rest.username
        if self.is_exist(av_name, owner):
            url = "{0}/_adpavd/_services/objects/compile_av/".format(self.rest.get_prefix())
            data = { "name": av_name, "schema": owner }
            return self.rest.post(url, data)
        return "{\"message\": \"Analytic view does not exist\"}"

    def generate_data(self, table : str, data_field : str, skip  : str = None, prefix : str = "Data") -> Tuple[list, list]:
        '''
            Extract data from getAVData
            
            @param table (String): payload of getAVData
            @param dataField (String): name of the columns to extract
            @param skip (String): true if skip null values
            @param prefix (String): prefix for labels or column name in the query
        '''
        categories = []
        data = []
        i = 1
        json_data = json.loads(table)
        for json_line in json_data:
            #print(json_line)
            is_skip = True
            if skip is None:
                is_skip = False
            elif json_line[skip] is not None:
                is_skip = False
            if not is_skip:
                data.append(json_line[data_field])
                if json_line.get(prefix) is None:
                    categories.append(prefix+str(i))
                else:
                    categories.append(json_line[prefix])
                i = i + 1

        return categories, data

    def create_auto(self, fact_table : str, skip_dimensions : bool = False, owner : str = None) -> str:
        '''
            Create the Analytic view  based on fact table  without specifing name or mesures
            
            @param factTable (String): fact table of the Analytic view
            @param owner (String): schema name of the fact table (None means that the current schema is used)
        '''
        if not owner:
            owner = self.rest.username.upper()
        parameters = {"factTable": fact_table, "owner": owner,  "model": fact_table+"_MODEL",
            "avModelName": "AV_" + fact_table, "avName": fact_table + "_AV",
            "caption": fact_table.replace("_", " ") +" Analytic View", 
            "sources": None, "progressKey": None}

        is_exists = self.is_exist(parameters["avName"], parameters["owner"])
        if is_exists > 0:
            av_name = parameters['avName']
            message = f"Analytic View {av_name} already exists"
            json_message = {'message': message}
            return json_message

        payload = self._generate_payload_for_lineage(parameters)
        text = self._av_model_source_lineage(payload)
        parameters["progressKey"] = self._get_progress_key()
        if skip_dimensions:
            parameters["sources"] = None
        else:
            parameters["sources"] = self._find_candidate_dims_for_fact(fact_table, owner)

        self.error = False
        thread = ThreadWithResult(target=self._auto_analytic_view, args=(parameters,))
        thread.run()
        while True:
            text = self.get_model("SYS$PROGRESS_INDICATOR", parameters["progressKey"], owner)
            json_text = json.loads(text)
            
            if "state" in json_text:
                if json_text.get("state") == "COMPLETE":
                    break
            if self.error:
                return thread.get()
            time.sleep(5)

        json_text = json.loads(thread.get())

        json_object = json_text["analyticViews"]
        json_object["analyticViewName"] = parameters["avName"]
        del json_text["avjson"]
        avjson={"useAVName":True}
        json_text["avjson"] = avjson

        text = self._create_model(self.rest.stringify(json_text), parameters)


        return text

    def create(self, fact_table : str, dimensions: list, measures: list, av_name: str = None, owner : str = None) -> str:
        '''
            Create the Analytic view based on dimension tables and measures, arguments have to be provided, you can use create_auto to create Analytic view only based on fact table
            
            @param factTable (String): fact table of the Analytic view
            @param dimensions (String): dimension tables of the Analytic view
            @param measures (String): measure columns of the fact table
            @param av_name (String): Analytic View name
            @param owner (String): schema name of the fact table (None means that the current schema is used)
        '''
        if owner is None:
            owner = self.rest.username
        if av_name is None:
            av_name = fact_table + '_AV'

        if self.is_exist(av_name):
            message = {"status": "error", "messsage": "Analytic View already exists"}
            return json.dumps(message)

        payload = self.generate_payload(fact_table, av_name)


        try:
            payload['analyticViews']["measures"] = self.check_measures(fact_table, measures, owner)
        except ImportError as e:
            return e.msg

        tables = []
        for dimension in dimensions:
            tables.append({"owner": owner, "source":dimension})
        payload["sources"] = tables

        try:
            payload['analyticViews']["joins"] = self.check_hierarchy(fact_table, owner, tables)
        except ImportError as e:
            return e.msg

        url = "{0}/_adpavd/_services/objects/get_hierarchies_from_tables/?tables={1}".format(self.rest.get_prefix(), self.rest.stringify(tables))
        text = self.rest.get(url)
        hierarchies = json.loads(text)
        payload['analyticViews']["hierarchies"] = hierarchies


        data = {"json": self.rest.stringify(payload), "owner": owner, "name": av_name, "genav": "Y"}
        #print(json.dumps(data, indent=2))

        url = "{0}/_adpavd/_services/objects/createmodel/".format(self.rest.get_prefix())
        return self.rest.post(url, data)

    def check_measures(self, fact_table : str, measures: list, owner : str) -> list:
        '''
            Check fact table contains measures
        '''
        text = self.table_columns(fact_table, owner)
        json_text = json.loads(text)
        items = json_text['items']
        names = []
        for item in items:
            name_meas = item['column_name']
            if name_meas in measures:
                names.append(item)
        if len(names) != len(measures):
            message = {"status": "error", "messsage": "Analytic View has no measure"}
            raise ImportError(message)

        return self.generate_measures(fact_table, owner, names)

    def check_hierarchy(self, fact_table : str, owner : str, tables: list):
        '''
            Check hierarchy
        '''
        url = "{0}/_adpavd/_services/objects/find_joins/?fact_owner={1}&fact_table={2}&dim_tables={3}".format(self.rest.get_prefix(), owner, fact_table, self.rest.stringify(tables))

        text = self.rest.get(url)
        json_text = json.loads(text)

        if len(tables) != len(json_text):
            status = False
            for table in tables:
                table_name = table['owner'] + '.' + table['source']
                for item in json_text:
                    if item['hierarchySource'] == table_name:
                        status = True
                        break
                if not status:
                    message = {"status": "error", "messsage": 'Table ' + table['source'] + ' has no hierarchy'}
                    raise ImportError(message)
                status = False
        return json_text

    def table_columns(self, table_name: str, owner: str) -> str:
        '''
            List table columns
        '''
        url = "{0}/_adpavd/_services/objects/table-column-profile/?tableOwner={1}&tableName={2}".format(self.rest.get_prefix(), owner, table_name)

        return self.rest.get(url)

    def generate_payload(self, fact_table: str, av_name: str) ->dict:
        '''
            Generate payload for creation
        '''
        caption = fact_table.replace("_", " ") +" Analytic View"

        data = { "analyticViews": {
        "name":fact_table+"_MODEL","analyticViewName":av_name,
        "caption":caption,"description":caption,
        "project_code":av_name,"project_id":None,
        "hierarchies":[],"joins":[],"measures":[],
        "classifications": [{"name": "CAPTION", "value": caption}, {"name": "DESCRIPTION", "value": caption}] },
        "sources":[], 
        "avExtensions":[{"name":"AV_AUTONOMOUS_AGGREGATE_CACHE","value":"ENABLED"},
            {"name":"AV_BASETABLE_QUERY_TRANSFORM","value":"DISABLED"},
            {"name":"AV_TRANSPARENCY_VIEWS","value":"ENABLED"}],
        "name":av_name,"project_code":av_name, "avjson":{"useAVName": True}
         }

        return data

    def generate_measures(self, fact_table: str, owner: str, names: list) -> list:
        '''
            Generate measures
        '''
        measures = []
        for name in names:
            measure = {
				"classifications": [
					{
						"name": "AVX_DATA_TYPE",
						"value": name['data_type']
					},
					{
						"name": "CAPTION",
						"value": name['column_name']
					},
					{
						"name": "DESCRIPTION",
						"value": name['column_name']
					},
					{
						"name": "FORMAT_STRING",
						"value": ""
					}
				],
				"measureName": name['column_name'],
				"owner": owner,
				"source": fact_table,
				"sourceColumn": name['column_name'],
				"aggregateBy": "SUM"
			}
            measures.append(measure)
        return measures

    def create(self, fact_table : str, dimensions: list, measures: list, av_name: str = None, owner : str = None) -> str:
        '''
            Create the Analytic view based on dimension tables and measures
            
            @param factTable (String): fact table of the Analytic view
            @param dimensions (String): dimension tables of the Analytic view
            @param measures (String): measure columns of the fact table
            @param av_name (String): Analytic View name
            @param owner (String): schema name of the fact table (None means that the current schema is used)
        '''
        if owner is None:
            owner = self.rest.username
        if av_name is None:
            av_name = fact_table + '_AV'

        if self.is_exist(av_name):
            message = {"status": "error", "messsage": "Analytic View already exists"}
            return json.dumps(message)

        payload = self.generate_payload(fact_table, av_name)


        try:
            payload['analyticViews']["measures"] = self.check_measures(fact_table, measures, owner)
        except ImportError as e:
            return e.msg

        tables = []
        for dimension in dimensions:
            tables.append({"owner": owner, "source":dimension})
        payload["sources"] = tables

        try:
            payload['analyticViews']["joins"] = self.check_hierarchy(fact_table, owner, tables)
        except ImportError as e:
            return e.msg

        url = "{0}/_adpavd/_services/objects/get_hierarchies_from_tables/?tables={1}".format(self.rest.get_prefix(), self.rest.stringify(tables))
        text = self.rest.get(url)
        hierarchies = json.loads(text)
        payload['analyticViews']["hierarchies"] = hierarchies


        data = {"json": self.rest.stringify(payload), "owner": owner, "name": av_name, "genav": "Y"}
        #print(json.dumps(data, indent=2))

        url = "{0}/_adpavd/_services/objects/createmodel/".format(self.rest.get_prefix())
        return self.rest.post(url, data)

    def check_measures(self, fact_table : str, measures: list, owner : str) -> list:
        '''
            Check fact table contains measures
        '''
        text = self.table_columns(fact_table, owner)
        json_text = json.loads(text)
        items = json_text['items']
        names = []
        for item in items:
            name_meas = item['column_name']
            if name_meas in measures:
                names.append(item)
        if len(names) != len(measures):
            message = {"status": "error", "messsage": "Analytic View has no measure"}
            raise ImportError(message)

        return self.generate_measures(fact_table, owner, names)

    def check_hierarchy(self, fact_table : str, owner : str, tables: list):
        '''
            Check hierarchy
        '''
        url = "{0}/_adpavd/_services/objects/find_joins/?fact_owner={1}&fact_table={2}&dim_tables={3}".format(self.rest.get_prefix(), owner, fact_table, self.rest.stringify(tables))

        text = self.rest.get(url)
        json_text = json.loads(text)

        if len(tables) != len(json_text):
            status = False
            for table in tables:
                table_name = table['owner'] + '.' + table['source']
                for item in json_text:
                    if item['hierarchySource'] == table_name:
                        status = True
                        break
                if not status:
                    message = {"status": "error", "messsage": 'Table ' + table['source'] + ' has no hierarchy'}
                    raise ImportError(message)
                status = False
        return json_text

    def table_columns(self, table_name: str, owner: str) -> str:
        '''
            List table columns
        '''
        url = "{0}/_adpavd/_services/objects/table-column-profile/?tableOwner={1}&tableName={2}".format(self.rest.get_prefix(), owner, table_name)

        return self.rest.get(url)

    def generate_payload(self, fact_table: str, av_name: str) ->dict:
        '''
            Generate payload for creation
        '''
        caption = fact_table.replace("_", " ") +" Analytic View"

        data = { "analyticViews": {
        "name":fact_table+"_MODEL","analyticViewName":av_name,
        "caption":caption,"description":caption,
        "project_code":av_name,"project_id":None,
        "hierarchies":[],"joins":[],"measures":[],
        "classifications": [{"name": "CAPTION", "value": caption}, {"name": "DESCRIPTION", "value": caption}] },
        "sources":[], 
        "avExtensions":[{"name":"AV_AUTONOMOUS_AGGREGATE_CACHE","value":"ENABLED"},
            {"name":"AV_BASETABLE_QUERY_TRANSFORM","value":"DISABLED"},
            {"name":"AV_TRANSPARENCY_VIEWS","value":"ENABLED"}],
        "name":av_name,"project_code":av_name, "avjson":{"useAVName": True}
         }

        return data

    def generate_measures(self, fact_table: str, owner: str, names: list) -> list:
        '''
            Generate measures
        '''
        measures = []
        for name in names:
            measure = {
				"classifications": [
					{
						"name": "AVX_DATA_TYPE",
						"value": name['data_type']
					},
					{
						"name": "CAPTION",
						"value": name['column_name']
					},
					{
						"name": "DESCRIPTION",
						"value": name['column_name']
					},
					{
						"name": "FORMAT_STRING",
						"value": ""
					}
				],
				"measureName": name['column_name'],
				"owner": owner,
				"source": fact_table,
				"sourceColumn": name['column_name'],
				"aggregateBy": "SUM"
			}
            measures.append(measure)
        return measures

    def _generate_payload_for_lineage(self, parameters : dict) -> dict:
        '''
            Generate payload for Lineage
            
            @param parameters (*): parameters for payload generation 
        '''
        data = {"analyticViews":
            {"name":parameters["model"],"analyticViewName":parameters["avModelName"],
            "caption":parameters["avModelName"],"description":parameters["avModelName"],
            "project_code":parameters["model"],"project_id":None,
            "hierarchies":[],"joins":[],"measures":[]},
            "sources":[{"owner":parameters["owner"],"source":parameters["factTable"]}],
            "avExtensions":[{"name":"AV_AUTONOMOUS_AGGREGATE_CACHE","value":"ENABLED"},
                {"name":"AV_BASETABLE_QUERY_TRANSFORM","value":"DISABLED"},
                {"name":"AV_TRANSPARENCY_VIEWS","value":"ENABLED"}],
            "name":parameters["avName"],"project_code":parameters["avName"]}
        return data

    def _av_model_source_lineage(self, payload : dict) -> str:
        '''
            Start Lineage model source
            
            @param payload (*): payload for lineage 
        '''
        url = "{0}/_adpavd/_services/objects/avmodelsourcelineage/".format(self.rest.get_prefix())
        data = {"model_json": self.rest.stringify(payload)}
        return self.rest.post(url, data)

    def _get_progress_key(self) -> str:
        '''
            Get progress key for crating the Analytic view 
        '''
        url = "{0}/_adpavd/_services/progress_indicator/get_progress_key/".format(self.rest.get_prefix())
        return self.rest.get(url)


    def _find_candidate_dims_for_fact(self, fact_table: str, owner : str) -> list:
        '''
            Find dimensions for the fact table
            
            @param pfactTable (String): fact table of the Analytic view 
            @param owner (String): schema name of the fact table (None means that the current schema is used)
        '''
        url = "{0}/_adpavd/_services/objects/findcandidatedimsforfact/?schema={1}&facttable={2}".format(self.rest.get_prefix(), owner.upper(), fact_table)
        text = self.rest.get(url)
        tables = []
        json_object = json.loads(text)
        recommended = json_object.get('Recommended')
        if recommended:
          for item in recommended:
              tables.append(item.get('DimTable'))

        return tables

    def _auto_analytic_view(self, parameters : dict) -> str:
        '''
            Start Lineage model source
            
            @param  parameters (*): additional parameters 
        '''

        sources = None
        if parameters["sources"] is not None:
            sources = ",".join(parameters["sources"])

        data = {"owner":parameters["owner"],"fact":parameters["factTable"], "sources":sources,
                "accuracy":80,"name":parameters["avName"], "caption": parameters["caption"], "description":parameters["caption"],
                "code":parameters["avName"], "progresskey":parameters["progressKey"], "crossschema":None}

        url = "{0}/_adpavd/_services/autoav/".format(self.rest.get_prefix())


        try:
            text = self.rest.post(url, data, timeout=None)
        except HTTPError:
            self.error = True
            text = "Automated AV generation has failed. No Hierarchies or Measures could be created"

        return text

    def is_exist(self, av_name : str, owner : str = None)-> bool:
        '''
            Check that the Analytic View exists
            
            @param parameters (*): additional parameters
        '''
        if owner is None:
            owner = self.rest.username

        url = "{0}/_adpavd/_services/objects/av_exists/?owner={1}&name={2}".format(self.rest.get_prefix(), owner, av_name)
        text = self.rest.get(url)
        json_text = json.loads(text)
        json_item = json_text["items"][0]
        count = json_item.get("count")
        return count > 0

    def _create_model(self, payload, parameters : dict) -> str:
        '''
            Create Lineage model
            
            @param payload (*): payload for lineage
            @param parameters (*): additional parameters 
    
        '''
        data = {"json": payload, "owner": parameters["owner"], "name": parameters["avName"], "genav": "Y"}
        url = "{0}/_adpavd/_services/objects/createmodel/".format(self.rest.get_prefix())
        return self.rest.post(url, data)

    def get_model(self, entity_type : str, entity_name : str, owner : str) -> str:
        '''
            Get Lineage Model
            @param entityName (String): name of the entity
            @param entityType (String): type of the entity
            @param owner (String): schema name of the fact table (None means that the current schema is used)
        '''
        url = "{0}/_adpavd/_services/objects/getmodel/?type={1}&name={2}&owner={3}".format(self.rest.get_prefix(), self.rest.encode(entity_type), self.rest.encode(entity_name), owner.upper())
        return self.rest.get(url)

