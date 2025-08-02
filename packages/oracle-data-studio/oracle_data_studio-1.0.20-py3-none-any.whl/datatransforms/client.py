'''
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

REST Client for all the data transforms operation.
NOT FOR EXTERNAL DEVELOPERS.

APIs available are subjected to change , hence all the operations must be reouted 
through Workbench APIs exposed for developers. 

'''
import json
import base64
import os
import logging
import copy
import re
import time
import uuid
from string import Template

import requests

from datatransforms.connection import Connection
from datatransforms.project import Project
#pylint: disable=too-many-lines,all
class DataTransformsException(Exception):
    """
    Exception class for all the client opertion failures
    """
    pass


class Singleton(type):
    """
    Internal class to make a singleton instance 
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DataTransformsClient(metaclass=Singleton):

    """
    Houses APIs for all the REST operations that can be performed on data transforms.
    """
    #url = "http://"+instance_ip_port+"/odi-rest"
    CONTENT_TYPE_APPLICATION_JSON = "application/json"
    #url = ""
    payload = {}
    headers = {}
    projects = {}
    connections = {}
    data_entities = {}
    datastores = {}
    schemas = {}

    connection_schemas = {}
    connection_schemas_stores = {}
    # we dont have REST API to get data entity by connection and schema. 
    # Hence we are building this internally.
    connection_schemas_stores_detail = {}

    adp_ignore_ssl=False
    logging.basicConfig(level=logging.WARNING)
    connected = False
    _instance = None
    client = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            DataTransformsClient.client=self
            self._instance = self

    @staticmethod
    def getClient():
        """
        Returns the instane of the DataTransformsClient 
        Used only for test purposes
        """
        if DataTransformsClient.client is None:
            DataTransformsClient.client=DataTransformsClient()
        return DataTransformsClient.client

    def isConnectionActive(self):
        """
        Returns true if the connection is alive to the deployment
        """
        return self.connected
    
    def re_connect(self):
        if not self.isConnectionActive():
            self.connect()

    def get_url(self):
        """
        Resolves the client URL based on configuration params.
        """
        if (not DataTransformsClient.headers and "AUTH_HEADERS_XFORMS_AUTH" in os.environ):
            DataTransformsClient.headers = {
                'Content-Type': DataTransformsClient.CONTENT_TYPE_APPLICATION_JSON,
                'Authorization':  os.environ["AUTH_HEADERS_XFORMS_AUTH"]
            }
            logging.info("Updated auth headers............")

        DataTransformsClient.url=os.environ['xforms_url']   
        logging.debug(DataTransformsClient.url)
        return DataTransformsClient.url

        raise DataTransformsException("Invalid data transforms environment to connect")

    def get_headers(self):
        """
        Returns REST client headers
        """
        return DataTransformsClient.headers

    def connect_adbs_with_token(self,base_url,token):
        if ('ADP_ENV' not in os.environ):
            raise DataTransformsException("Environment property ADP_ENV must be true to connect to ADBS")
        temp_base_url=base_url
        self.base_url=base_url+"/odi-rest"
        DataTransformsClient.url=base_url+"/odi-rest"
        logging.debug(base_url)
        self.token=token
        request_id="99"+str(time.time_ns())
        DataTransformsClient.headers = {
            'Content-Type': DataTransformsClient.CONTENT_TYPE_APPLICATION_JSON,
            'Authorization': "Bearer " + token,
            'Request-Id':request_id
        }
        os.environ["AUTH_HEADERS_XFORMS_AUTH"]="Bearer " + token

    def wait_for_adbs_container_up(self,base_url,access_token):
        """Waits for the container to come up if it was evicted due to inactivity"""
        logging.debug("Performing status check on container")
        logging.debug("Waiting for Container Up with wait time %d attempt %d",self.wait_seconds , self.connect_attempts)
        isUP=self.__get_container_status(base_url,access_token)
        if isUP is False:
            if self.connect_attempts == 0:
                logging.fatal("Unable to get container status, Max attempts exceeded")
                raise DataTransformsException("Max connect atempts exceeded %d",self.connect_attempts)
            
            logging.info("Container not up, waiting for %ds attempt=%d",self.wait_seconds,self.connect_attempts)
            time.sleep(self.wait_seconds)
            self.connect_attempts=self.connect_attempts-1
            #print("Recursive check for Up" + str(self.connect_attempts))
            self.wait_for_adbs_container_up(base_url,access_token)
            logging.info("Container not available, performing status check \
                         Attempts %d",self.connect_attempts)
            

        return 

    def __get_container_status(self,base_url,access_token):
    
        container_status_url = base_url + "/odimetrics/container/provisioning/status"
        logging.info("Checking container status for ADBS deployment " + container_status_url)
        
        headers={}
        cookie_string = "Authorization=" + access_token +"; ORA_FPC=id="+str(uuid.uuid1())+"; WTPERSIST="
        headers['Cookie']=cookie_string
        headers['Accept']="*/*"
        headers['Accept-Encoding']="gzip, deflate, br"
        headers['Connection']="keep-alive"
        headers['User-Agent']="DataTransforms Python Client"
        response = self.__get(container_status_url, headers, None)
        #print(response.json())
        #print(response.status_code)
        #print(response.content)

        if response.status_code == 200:
            logging.debug("Container is alive and running")
            return True
        else:
            logging.info("Container is NOT UP " + str(response.json()))
            return False


    def connect(self, instance_ip, user, pwd):
        os.environ['MP_ENV']="True"
        auth_string = user+":"+pwd
        auth_string_base64 = base64.b64encode(auth_string.encode("ascii")).decode("ascii")
        os.environ['DATA_TRANSFORMS_IP'] = instance_ip
        os.environ['DATA_TRANSFORMS_AUTH'] = auth_string_base64
        os.environ['DATA_TRANSFORMS_PORT'] = "9999"
        url = "http://"+os.environ['DATA_TRANSFORMS_IP']+":"+os.environ['DATA_TRANSFORMS_PORT']
        self.connect_withurl(url,user,pwd)

    def connect_withurl(self,instance_url,user,pwd):
        os.environ['xforms_url']=instance_url
        auth_string = user+":"+pwd
        auth_string_base64 = base64.b64encode(auth_string.encode("ascii")).decode("ascii")
        os.environ['DATA_TRANSFORMS_AUTH'] = auth_string_base64
        token = self.__connect()
        request_id="99"+str(time.time_ns())
        DataTransformsClient.headers = {
            'Content-Type': DataTransformsClient.CONTENT_TYPE_APPLICATION_JSON,
            'Authorization': token,
            'Request-Id':request_id
        }
        os.environ['xforms_url']=instance_url+"/odi-rest"
        os.environ["AUTH_HEADERS_XFORMS_AUTH"]=token
       

    def __connect(self):
        auth_url = self.get_url() + "/odi-rest/v1/token/"
        logging.debug("Authentication URL ==>" + auth_url)
        logging.debug("Data Transforms URL " + self.url)
        logging.debug(os.environ['DATA_TRANSFORMS_AUTH'])

        payload = {}
        DataTransformsClient.headers = {
            'Content-Type': DataTransformsClient.CONTENT_TYPE_APPLICATION_JSON,
            'Authorization': 'Basic '+os.environ['DATA_TRANSFORMS_AUTH']
        }
        os.environ["AUTH_HEADERS_XFORMS_CONTENT_TYPE"] = DataTransformsClient.CONTENT_TYPE_APPLICATION_JSON
        os.environ["AUTH_HEADERS_XFORMS_AUTH"] = 'Basic '+os.environ['DATA_TRANSFORMS_AUTH']

        response = self.__post( auth_url, headers=DataTransformsClient.headers, payload_data=payload)
        logging.debug(response.headers)
        logging.debug(response.text)

        if (response.status_code != 200):
            raise DataTransformsException(
                "Failed to connect to " + auth_url + "\nCode" + str(response.status_code) + " Reason " + response.text)
        
        return response.json()["message"]
    
    def create_project(self, name, code=None , folder="DefaultFolder"):
        self.get_all_projects()

        logging.info("Creating project " + name + " " + "in folder" + folder)
        logging.info("Checking if project available in cache ")
        if name in self.projects.keys():
            logging.info("Project " + name + " already exists")
        else:
            if code == None or code == "":
                code = name.replace(" ","").upper()  
                project_template_string="""{
    "name": "$project_name",
    "code": "$project_code",
    "globalId": null,
    "folders": [
        {
            "folderName": "$project_folder",
            "globalId": null,
            "parentProject": "$project_name",
            "parentFolder": null,
            "mappings": {},
            "packages": {},
            "folders": []
        }
    ]
    }"""
                s = Template(project_template_string)
                payload = s.safe_substitute(
                    project_name=name, project_code=code, project_folder=folder)
                logging.debug(payload)
                projectsEndpoint = self.get_url() + "/v1/projects"
                response = requests.request(
                    "POST", projectsEndpoint, headers=self.get_headers(), data=payload)
                if response.status_code == 200:
                    logging.info("Project create " + name + " [OK]")
                    self.get_all_projects()
                    return True
                else:
                    logging.error("Project Sync [KO]")
                    logging.error(response.text)
                    return False

    def get_all_projects(self):
        get_projects_ep = self.get_url() + "/v1/projects/list"
        #print("Getting all the projects from " + get_projects_ep)

        response = self.__get(get_projects_ep, self.get_headers(), self.payload)
        response_json = response.json()
        # print(response.text)
        if response.status_code != 200:
            logging.error("Endpoint " + get_projects_ep + " Failed with Status=" + 
                          str(response.status_code) + " Reason " + response.text) 
            raise DataTransformsException("Failed loading projects "
                                          + str(response.status_code) + " Reason " + response.text )
        
        self.projects = self.__get_name_globalid_from_json(response_json)
        return self.projects

    def get_all_dataflows_from_project(self, project_id):
        get_dataflows_ep = self.get_url()+"/v1/projects/id/"+project_id+"/mappings/list"
        response = self.__get(get_dataflows_ep, headers=self.get_headers(), data=self.payload)
        response_json = response.json()
        return self.__get_name_globalid_from_json(response_json)

    def get_all_workflows_from_project(self, project_id):
       
        get_worklows_ep = self.get_url()+"/v1/projects/id/"+project_id+"/packages/list"
        response = self.__get(get_worklows_ep, headers=self.get_headers(), data=self.payload)
        response_json = response.json()
        return self.__get_name_globalid_from_json(response_json)

    def get_all_dataloads_from_project(self, project_id):
        get_dataflows_ep = self.get_url()+"/v1/projects/id/" + \
            project_id+"/bulkloads/list"
        response = self.__get( get_dataflows_ep, headers=self.get_headers(), data=self.payload)
        response_json = response.json()

        return self.__get_name_globalid_from_json(response_json, "bulkLoadName")

    def __get_name_globalid_from_json(self, response_json, name_field=None):
        name_global_id = {}

        if name_field is not None:
            name_key = name_field
        else:
            name_key = "name"

        for item in response_json:
            name_global_id[item[name_key]] = item['globalId']
        return name_global_id

    def get_dataflow_by_id(self, dataflow_id):
        # http://123.123.123.123:9999/odi-rest/v1/mappings/id/9a9a9a9a-8d8d-4343-9898-444444444444
        get_dataflow_by_id_ep = self.get_url()+"/v1/mappings/id/"+dataflow_id
        response = self.__get( get_dataflow_by_id_ep, headers=self.get_headers(), data=self.payload)
        if response.status_code != 200:
            raise DataTransformsException("Dataflow with id=" +dataflow_id + " not found")
        return response.text

    def get_workflow_by_id(self, workflow_id):
        get_dataflow_by_id_ep = self.get_url()+"/v1/packages/id/"+workflow_id
        response = self.__get( get_dataflow_by_id_ep, headers=self.get_headers(), data=self.payload)
        return response.text
    
    def get_dataload_by_id(self, dataload_id):
        get_dataflow_by_id_ep = self.get_url()+"/v1/bulkload/id/"+dataload_id
        response = self.__get( get_dataflow_by_id_ep, headers=self.get_headers(), data=self.payload)
        return response.text

    def get_all_connections(self):
        get_projects_ep = self.get_url() + "/v1/dataservers/list"
        logging.debug("Connecting to " + get_projects_ep)

        response = self.__get( get_projects_ep, headers=self.get_headers(), data=self.payload)
        
        if response.status_code != 200:
            message = "Response code " + str(response.status_code) + " Message=" + response.text
            raise DataTransformsException("Failed loading connections {message}".format(message=message))
        else:            
            response_json = response.json()
            for connection in response_json:
                self.connections[connection['name']] = connection['globalId']
            #logging.debug(self.connections)
            return self.connections

    def get_dataentity_by_id(self, entity_global_id):
        get_dataentity_ep = self.get_url()+"/v1/datastores/id/"+entity_global_id
        response = self.__get( get_dataentity_ep, headers=self.get_headers(), data=self.payload)
        # print(response.status_code)
        response_json = response.json()
        # print(json.dumps(response_json,indent=3))
        return response_json

    def get_dataentity_by_name(self, data_entity_name):
        #print("Fetch data entity by Name")
        #print(self.connection_schemas_stores)
        if (not bool(self.connection_schemas_stores)):
            print("Loading cache")
            self.load_cache()

        if(data_entity_name not in self.connection_schemas_stores.keys()):
            raise DataTransformsException(
                "Data entity " + data_entity_name + " doesn't exist")
        data_entity_global_id = self.connection_schemas_stores[data_entity_name]
        return self.get_dataentity_by_id(data_entity_global_id)

    def get_all_datastores(self):
        get_datastores_ep = self.get_url() + "/v1/datastores/list"
        response = self.__get( get_datastores_ep, headers=self.get_headers(), data=self.payload)
        #logging.debug(response.text)

        response_json = response.json()
        for datastore in response_json:

            datastore_name = datastore['name']
            datastore_global_id = datastore['globalId']
            schema_name = datastore['schemaName']
            schema_global_id = datastore['schemaGlobalId']
            connection_name = datastore['dataServerName']

            self.datastores[datastore_name] = datastore_global_id

            resolved_connection_schema = connection_name+"."+schema_name
            self.schemas[resolved_connection_schema] = schema_global_id
            resolved_store_name = resolved_connection_schema+"."+datastore_name
            self.connection_schemas[resolved_connection_schema] = schema_global_id
            self.connection_schemas_stores[resolved_store_name] = datastore_global_id
            self.connection_schemas_stores_detail[resolved_store_name] = datastore

            #print(connection_name+"."+schema_name+"."+datastore_name  + " " + datastore_global_id)
        #logging.debug(self.datastores)
        return self.datastores

    def resolve_connection_schema_ref_from_cache(self, schema_names):
        references = {}
        for schema_name in schema_names:
            references[schema_name] = self.connection_schemas[schema_name]
        return references

    def load_cache(self):
        self.get_all_connections()
        logging.info("Loaded connections")
        self.get_all_projects()
        logging.info("Loaded projects")
        self.get_all_datastores()
        logging.info("Loaded data stores")

    def getect(self, name, folder):
        logging.info("Creating project " + name + " " + "in folder" + folder)
        logging.info("Checking if project available in cache ")
        if (name in self.projects.keys()):
            logging.info("Project " + name + " already exists")
        else:
            project_template_string="""{
  "name": "$project_name",
  "code": "$project_code",
  "globalId": null,
  "folders": [
      {
          "folderName": "$project_folder",
          "globalId": null,
          "parentProject": "$project_name",
          "parentFolder": null,
          "mappings": {},
          "packages": {},
          "folders": []
      }
  ]
}"""
            s = Template(project_template_string)
            payload = s.safe_substitute(
                project_name=name, project_code=name.upper(), project_folder=folder)
            logging.debug(payload)
            projectsEndpoint = self.get_url() + "/v1/projects"
            response = requests.request(
                "POST", projectsEndpoint, headers=self.get_headers(), data=payload)
            if response.status_code == 200:
                logging.info("Project create " + name + " [OK]")
            else:
                logging.error("Project Sync [KO]")
                logging.error(response.text)

    def check_if_df_exists(self,project_id,df_name):
        project_mappings_list_ep=self.get_url()+"/v1/projects/id/{project_id}/mappings/list".format_map(locals())
        response = self.__get(project_mappings_list_ep,headers=self.get_headers(),data=None)
        if response.status_code == 200:
            logging.debug("Dataflow check listings [OK]")
            json_doc= response.json()
            for dataflow_entry in json_doc:
                if df_name == dataflow_entry["name"]:
                    return True,dataflow_entry["globalId"]
            
            return False,None
        else:
            logging.error("Dataflow KM Options fetch [KO]")
            logging.error(response.text)
            logging.error(response.status_code)
            raise DataTransformsException("Fetch all dataflows failed")
    
    def check_if_dataload_exists(self,project_id,dataload_name):
        project_mappings_list_ep=self.get_url()+"/v1/projects/id/{project_id}/bulkloads/list".format_map(locals())
        response = self.__get(project_mappings_list_ep,headers=self.get_headers(),data=None)
        if response.status_code == 200:
            logging.debug("Dataflow check listings [OK]")
            json_doc= response.json()
            for dataload_entry in json_doc:
                if dataload_name == dataload_entry["bulkLoadName"]:
                    return True,dataload_entry["globalId"]
            return False,None
        else:
            logging.error("Dataflow KM Options fetch [KO]")
            logging.error(response.text)
            logging.error(response.status_code)
            raise DataTransformsException("Fetch all dataflows failed")
    
    def check_if_workflow_exists(self,project_id,workflow_name):
        workflow_mappings_list_ep=self.get_url()+"/v1/projects/id/{project_id}/packages/list".format_map(locals())
        response = self.__get(workflow_mappings_list_ep,headers=self.get_headers(),data=None)
        if response.status_code == 200:
            logging.debug("Dataflow check listings [OK]")
            json_doc= response.json()
            for dataload_entry in json_doc:
                if workflow_name == dataload_entry["name"]:
                    return True,dataload_entry["globalId"]
            return False,None
        else:
            logging.error("Dataflow KM Options fetch [KO]")
            logging.error(response.text)
            logging.error(response.status_code)
            raise DataTransformsException("Fetch all dataflows failed")


    def fetch_km_options(self,target_node_name,dataflow_payload):
        km_options_ep=self.get_url()+"/v1/mappings/km/node/{target_node_name}".format_map(locals())
        #print(dataflow_payload)
        response = self.__post(km_options_ep,headers=self.get_headers(),payload_data=dataflow_payload)
        if response.status_code == 200:
            logging.debug("Dataflow KM Options fetched [OK]")
            return True,response.json()
        else:
            logging.error("Dataflow KM Options fetch [KO]")
            logging.error(response.text)
            logging.error(response.status_code)
            return False,None

    def update_dataflow_from_json_payload(self, data_flow_payload):
        data_flow_endpoint = self.get_url() + "/v1/mappings"
        response = self.__put( data_flow_endpoint, headers=self.get_headers(), payload_data=data_flow_payload)
        if response.status_code == 200:
            logging.debug("Dataflow Update Sync [OK]")
            return True
        else:
            logging.error("Dataflow Update Sync [KO]")
            logging.error(response.text)
            logging.error(response.status_code)
            return False


    def create_dataflow_from_json_payload(self, data_flow_payload):
        data_flow_endpoint = self.get_url() + "/v1/mappings"
        response = self.__post( data_flow_endpoint, headers=self.get_headers(), payload_data=data_flow_payload)
        if response.status_code == 200:
            logging.debug("Dataflow Sync [OK]")
            #print(response.json()["globalId"])
            return True,response.json()["globalId"]
        else:
            logging.error("Dataflow Sync [KO]")
            logging.error(response.text)
            logging.error(response.status_code)
            return False,None

    def create_workflow_from_json_payload(self, workflow_json_payload):
        workflow_endpoint = self.get_url() + "/v1/packages"
        response = self.__post( workflow_endpoint, headers=self.get_headers(), payload_data=workflow_json_payload)
        if response.status_code == 200:
            logging.info("Workflow Sync [OK]")
            return True
        else:
            logging.error(response.text)
            logging.error("Workflow Sync [KO]")
            return False
        
    def update_workflow_from_json_payload(self, workflow_json_payload):
        workflow_endpoint = self.get_url() + "/v1/packages"
        response = self.__put( workflow_endpoint, headers=self.get_headers(), payload_data=workflow_json_payload)
        if response.status_code == 200:
            logging.info("Workflow Update Sync [OK]")
            return True
        else:
            logging.error(response.text)
            logging.error("Workflow Update Sync [KO]")
            return False
        

    def create_dataload(self, dataload_json_payload):
        dataload_endpoint = self.get_url() + "/v1/bulkload"
        #print(dataload_json_payload)
        response = self.__post( dataload_endpoint, headers=self.get_headers(), payload_data=dataload_json_payload)
        if response.status_code == 200:
            logging.info("DataLoad Sync [OK]")
        else:
            logging.error("DataLoad Sync [KO]")
            logging.error(response.text)

    def update_dataload(self, dataload_json_payload):
        dataload_endpoint = self.get_url() + "/v1/bulkload"
        #print(dataload_json_payload)
        response = self.__put( dataload_endpoint, headers=self.get_headers(), payload_data=dataload_json_payload)
        if response.status_code == 200:
            logging.info("DataLoad Update Sync [OK]")
        else:
            logging.error("DataLoad Update Sync [KO]")
            logging.error(response.text)

    def import_entities(self,import_payload):
        """Initiates the import data entities job"""
        import_endpoint = self.get_url() + "/v1/datastores/import/auto"
        headers_import = self.get_headers()
        extended_headers={"Accept":"*/*","Accept-Encoding":"gzip, deflate",
                          "Content-Type":DataTransformsClient.CONTENT_TYPE_APPLICATION_JSON}
        headers_import.update(extended_headers)
        #print("Headers for import " + str(headers_import))
        #print(import_payload)
        response = self.__post( import_endpoint, headers=headers_import, payload_data=import_payload)

        if response.status_code == 200:
            logging.info("Import DataEntities started [OK]")
            #print(response.text)
            session_name=response.json()["sessionName"]
            return session_name
        else:
            logging.info("Import DataEntities started [KO]")
            print(response.text)
            return None

    def __get(self,endpoint,headers, data):
       
        if (self.adp_ignore_ssl):
            print("Bypass SSL Verification enabled")
            session = requests.Session()
            session.verify = False
            session.trust_env = False
            os.environ['CURL_CA_BUNDLE']="" 
            return requests.request("GET", url=endpoint, headers=headers, data=data,verify=False)

        return requests.request("GET", url=endpoint, headers=headers, data=data)
    
    def __post(self,endpoint,headers, payload_data):

        if (self.adp_ignore_ssl):
            session = requests.Session()
            session.verify = False
            session.trust_env = False
            os.environ['CURL_CA_BUNDLE']=""
            return requests.request("POST", endpoint,headers, payload_data)

        return requests.request("POST", url=endpoint,headers=headers, data=payload_data)
#DataTransformsClient().connect_adbs()

    def __put(self,endpoint,headers, payload_data):

        if (self.adp_ignore_ssl):
            session = requests.Session()
            session.verify = False
            session.trust_env = False
            os.environ['CURL_CA_BUNDLE']="" 
            return requests.request("POST", endpoint,headers, payload_data)

        return requests.request("PUT", url=endpoint,headers=headers, data=payload_data)


    def __delete(self,endpoint,headers, data):
       
        if (self.adp_ignore_ssl):
            print("Bypass SSL Verification enabled")
            session = requests.Session()
            session.verify = False
            session.trust_env = False
            os.environ['CURL_CA_BUNDLE']="" 
            return requests.request("GET", url=endpoint, headers=headers, data=data,verify=False)

        return requests.request("DELETE", url=endpoint, headers=headers, data=data)
    
    def __delete_project(self,project_name):
        project_endpoint = self.get_url()+"/v1/projects/id/"
        projects = self.get_all_projects()
        if project_name in projects:
            project_id = projects[project_name]
            project_endpoint += project_id
            delete_response = self.__delete(project_endpoint,DataTransformsClient.headers,data=None)
            if delete_response.status_code == 200:
                logging.info("Project deleted " + project_name)
                return True, delete_response
            else:
                logging.error("Project delete failed " + project_name + " Received status " + delete_response.status_code)
                return False, delete_response
            
        else: 
            logging.error("Given project " + project_name + " doesn't exist")
            return False,None

    def __delete_connection(self,connection_name):
        connection_endpoint=self.get_url()+"/v1/dataservers/id/"
        connections = self.get_all_connections()
        if connection_name in connections:
            connection_id=connections[connection_name]
            connection_endpoint+= connection_id + "?cascade=true"
            #print(connection_endpoint)
            delete_response = self.__delete(connection_endpoint,DataTransformsClient.headers,data=None)
            if delete_response.status_code == 200:
                logging.info("Connection deleted " + connection_name)
                return True, delete_response
            else:
                logging.error("Connection delete failed " + connection_name + " Received status " + str(delete_response.status_code))
                return False, delete_response
            
        else: 
            logging.error("Given connection " + connection_name + " doesn't exist")
            return False,None
        
    def delete(self,model_object):
        
        if isinstance(model_object,Connection):
            logging.info("Deleting connection  " + model_object.name)
            self.__delete_connection(model_object.name)
        
        if isinstance(model_object,Project):
            print("Deleting Project " + model_object.name)
            self.__delete_project(model_object.name)

    def fetch_token(self,connection_options):
        url = connection_options["auth_token_url"]
        user=connection_options["xforms_user"]
        pwd=connection_options["pswd"]
        tenant_name = connection_options["tenancy_ocid"]
        database_name = connection_options["adw_name"]
        cloud_database_name = connection_options["adw_ocid"]
        
        payload_dict = {
            'grant_type' : "password",
            "username" : user,
            "password" : pwd,
            "tenant_name" : tenant_name,
            "database_name" : database_name,
            "cloud_database_name" : cloud_database_name
        }
        #payload = '''{"grant_type": "password","username": \"+user+"\","password": \""+pwd+"\","tenant_name": "SYSTEST2","database_name": "ADPODIT1","cloud_database_name": "ADPODIT1"}'''
        payload = json.dumps(payload_dict)
        request_id=str(time.time_ns())
        headers={
            'Content-Type':'application/json',
            'Request-Id':request_id
        }
        response = requests.request("POST", url=url,headers=headers, data=payload)
        #print(response_token.text)
        #logging.debug("Token fetch status " + str(response.status_code))
        #logging.debug("Token fetch status " + str(response.text))
        if response.status_code == 200:
            response_json = response.json()
            return response_json["access_token"]
        else:
            err_text = response.text
            logging.fatal(err_text)
            raise DataTransformsException(err_text)
            

    def get_connection_types(self):
        """
        Returns the list of available Connection type (code) in an deployment
        """
        connection_type_ep = self.get_url()+"/v1/technos/supported/detail"
        response = self.__get(connection_type_ep,self.headers,None)

        if response.status_code != 200:
            raise  DataTransformsException("Failed to get connction types")

        response_json = response.json()
        connection_type_codes=[]
        connection_type_jdbc_drivers={}

        for connection_types in response_json:
            con_type_code = connection_types["code"]
            connection_type_codes.append(con_type_code)
            
            connection_type_jdbc_drivers[con_type_code]=self.get_jdbc_defaults(con_type_code)

        return connection_type_jdbc_drivers
    
    def get_jdbc_defaults(self,connection_type_code):
        jdbc_defaults_ep = self.get_url()+"/v1/technos/jdbc_defaults/"+connection_type_code
        response = self.__get(jdbc_defaults_ep,self.headers,None)

        if response.status_code != 200:
            raise  DataTransformsException("Failed to get connction JDBC Defaults")
    
        response_json = response.json()
        return (list(response_json.keys()))[0]


    def process_wallet(self,wallet_path):

        if not os.path.isfile(wallet_path):
            raise DataTransformsException ("Invalid wallet path " + wallet_path)

        dir,file_name = os.path.split(wallet_path)

        multipart_form_data = {
            'name': file_name,
            'file' : (file_name, open(wallet_path, 'rb'), 'application/zip')
        }
        process_wallet_ep = self.get_url()+"/v1/wallet/processWallet"


        spl_headers = copy.deepcopy(DataTransformsClient.headers)
        spl_headers["Accept"]="*/*"
        spl_headers.pop('Content-Type')
        response = requests.post(process_wallet_ep, headers=spl_headers,files=multipart_form_data)

        if response.status_code != 200:
            raise DataTransformsException("Failed to process wallet " + wallet_path)

        response_json = response.json()
        self.__dump_payload(response)
        #print("\n\n\n")
        #print(response_json)
        return response_json["walletLocation"],response_json["services"]

    def __dump_payload(self,response):
        __dump_payload=False
        if __dump_payload:
            print("\n\n\n")
            print(response.request.body)
            print(response.request.headers)
            print(response)
            print(response.text)
            print(response.status_code)

    def create_connection_from_json(self,connection_json_payload):

        connection_endpoint = self.get_url() + "/v1/dataservers"
        response = self.__post(
             connection_endpoint, headers=self.get_headers(),
             payload_data=connection_json_payload)
        if response.status_code == 200:
            logging.info("Connection Sync [OK]")
        else:
            logging.error("Connection Sync [KO]")
            logging.error(response.text)


    def update_connection_from_json(self,connection_json_payload):

        connection_endpoint = self.get_url() + "/v1/dataservers"
        response = self.__put(
            connection_endpoint, headers=self.get_headers(),
            payload_data=connection_json_payload)
        if response.status_code == 200:
            logging.info("Connection Sync [OK]")
        else:
            logging.error("Connection Sync [KO]")
            logging.error(response.text)
            raise DataTransformsException("Update connection %s failed",connection_json_payload["name"])


    def create_de_from_json(self,connection_json_payload):

        connection_endpoint = self.get_url() + "/v1/datastores/create/auto"
        response = self.__post( connection_endpoint, headers=self.get_headers(), payload_data=connection_json_payload)
        if response.status_code == 200:
            logging.info("DataEntity Sync [OK]")
        else:
            logging.info("DataEntity Sync [KO]")
            print(response.text)
    
    def update_de_from_json(self,connection_json_payload):

        connection_endpoint = self.get_url() + "/v1/datastores"
        response = self.__put( connection_endpoint, headers=self.get_headers(), payload_data=connection_json_payload)
        if response.status_code == 200:
            logging.info("update_de_from_json Sync [OK]")
        else:
            logging.info("update_de_from_json Sync [KO]")
            print(response.text)
    
    def export_datastores(self,file_name):
        get_datastores_ep = self.get_url() + "/v1/datastores/list"
        response = self.__get( get_datastores_ep, headers=self.get_headers(), data=self.payload)
        #logging.debug(response.text)

        response_json = response.json()

        header =["data_entity_name","connection_name","schema_name"]
        
        csv_data=""
        header_row = ",".join(header) + "\n"
        csv_data += header_row
        for datastore in response_json:
            row=[]
            datastore_name = datastore['name']
            datastore_global_id = datastore['globalId']
            schema_name = datastore['schemaName']
            schema_global_id = datastore['schemaGlobalId']
            connection_name = datastore['dataServerName']

            row.append(datastore_name)
            row.append(connection_name)
            row.append(schema_name)

            row_str = ",".join(row) + "\n"
            csv_data+=row_str

            de_json = self.get_dataentity_by_id(datastore_global_id)

            de_cols = de_json["columns"]

            de_file=open(file_name+"/"+datastore_name+".csv","w")
            de_data=""
            for col in de_cols:
                name = col["name"]
                position = str(col["position"])
                dataType = col["dataType"]
                length=str(col["length"])
                scale = str(col["scale"])
                de_row=[name,position,dataType,length,scale]
                #print(de_row)
                de_data+=",".join(de_row)+"\n"

            de_file.write(de_data)
            de_file.close()
            
            
        f = open(file_name+"/schema.csv","w")
        f.write(csv_data)
        f.close()

    def is_connection_available(self, connection_name):
        """Method to check fi the given connection is available. 
        This method does REST API call to get all connections and validates if the given connection name is available in 
        the data transforms deployment. 

        If connection is found with given name, connection reference (connection_global_id) is returned. Exception is thrown otherwise
        Note - This API is available only for validation purpose. Developer shall not use the returned reference (ID) anywhere
        as it is not gauranteed to maintain the same ID across deployments. 
        """
        logging.info("Fetching data entities using live connection")
        logging.debug("Fetching connections ...")
        connections = self.get_all_connections()
        if connection_name not in connections.keys():
            raise DataTransformsException("Invalid connection {connection_name} , not found".format(connection_name=connection_name))
        connection_global_id = connections[connection_name]
        return connection_global_id
    
    def fetch_live_tables(self, schema_global_id):
        live_tables_ep = self.get_url() + "/v1/dataservers/schemas/liveTables"
        live_tables_paylaod_dict = {"physicalSchemaGlobalId": schema_global_id ,"agentName":"OracleDIAgent1"}
        logging.debug("Fetching live tables {live_tables_ep} with payload {live_tables_paylaod_dict}".format_map(locals()))
        response = self.__post(live_tables_ep,headers=self.get_headers(),payload_data=json.dumps(live_tables_paylaod_dict))
        if response.status_code != 200:
            failure_msg = "Live tables fetch failure for {connection_name}.{schema_name} ".format_map(locals())
            logging.error(failure_msg)
            raise DataTransformsException(failure_msg)
        else:
            logging.debug(str(response.json()))
            return response


    def is_alive_connection(self, connection_name, connection_global_id):
        """
        Verifies the connectivity of the given connection 

        """
        connection_ok = self.test_connection(connection_global_id)
        if not connection_ok:
            logging.error("Failed test connection for %s",connection_name)
            raise DataTransformsException(
                f"Test connection to {connection_name} failed, check the connection details or the server")


    def test_connection(self,connection_globalid):
        """
        Method to check if the connectivity is valid for the given connection. 
        returns False, if the connection could not be established.

        """
        test_connection_ep = self.get_url() + "/v1/jobs/test_connection"
        payload_dict={"objectId":connection_globalid,"agentName":"OracleDIAgent1"}

        response = self.__post(test_connection_ep,headers=self.get_headers(),payload_data=json.dumps(payload_dict))
        if response.status_code != 200:
            return False
        else:
            return True

    def __get_live_schemas(self, connection_global_id):
        live_schemas_ep = self.get_url() + "/v1/dataservers/liveSchemas"
        live_schemas_payload_dict = {"dataServerGlobalId": connection_global_id,"agentName":"OracleDIAgent1"}
        response = self.__post(live_schemas_ep,headers=self.get_headers(),payload_data=json.dumps(live_schemas_payload_dict))
        if response.status_code != 200:
            raise DataTransformsException("Failed to fetch live schemas for {connection_name}".format(locals()))
        else:
            #logging.debug("Live schema list " + str(response.json()))
            schema_list = response.json()
            return schema_list

    def auto_create_schema(self, schema_name, connection_global_id):
        attach_schema_ep = self.get_url() + "/v1/dataservers/id/{connection_global_id}/schemas".format(connection_global_id=connection_global_id)
        attach_schema_payload_dict = {"schemaShortName": schema_name}
        response = self.__post(attach_schema_ep,headers=self.get_headers(),payload_data=json.dumps(attach_schema_payload_dict))
        if response.status_code != 200:
            logging.debug(str(response.status_code) + " " + str(response.text))
            raise DataTransformsException("Failed to attach schema {schema_name} to connection {connection_global_id}".format_map(locals()))
        else:
            attach_schema_json = response.json()
        return attach_schema_json
    
    def attach_schema_with_connection(self, connection_name,schema_name):
        connection_global_id= self.is_connection_available(connection_name)
        result = self.auto_create_schema(schema_name,connection_global_id)
        return result["globalId"]


    def get_all_data_entities(self,connection_name,schema_name,live=False,matching=None):
        """
        Utility method to get all the data entities available for the connection & schema
        This method performs get all data entity call on the system - then filters them by 
        connection and schema. Hence this operation is time consuming one, based on the available
        entities in the system. 

        Returns JSON array - where each element represent data entity.
                Note - the JSON returned is specific to the environment where it is extracted from. 
                It can't be used as is for loading to other systems as is without cleansing &
                resolving global ID for target system(s)
        """

        if not live:
            get_datastores_ep = self.get_url() + "/v1/datastores/list"
            response = self.__get( get_datastores_ep, headers=self.get_headers(), data=self.payload)
            #logging.debug(response.text)

            response_json = response.json()

            data_stores=[]
            for datastore in response_json:
                datastore_name = datastore['name']
                datastore_global_id = datastore['globalId']
                de_schema_name = datastore['schemaName']
                de_con_name = datastore['dataServerName']

                if connection_name == de_con_name and de_schema_name == schema_name:
                    de_json = self.get_dataentity_by_id(datastore_global_id)
                    data_stores.append(de_json)
            
            return data_stores
        else:
            connection_global_id = self.is_connection_available(connection_name)
            logging.debug("Found connection {connection_name} with {connection_global_id}, validating connectivity ....".format_map(locals()))
            self.is_alive_connection(connection_name,connection_global_id,)
            logging.debug("Connectivity OK, fetching connection details")
            response = self.get_connection_details(connection_global_id)
            resposne_payload = response.json()
            schemas =resposne_payload["schemas"]
            logging.debug("Verifying if the schema {schema_name} is already available ".format(schema_name=schema_name))
            schema_available = next((schema for schema in schemas if schema["schemaShortName"] == schema_name),False)
            schema_global_id = None
            schema_tech = None 
            if schema_available:
                schema_global_id = schema_available["globalId"]
                schema_tech = schema_available["technology"]

            else:
                logging.debug("Schema {schema_name} not attached with connection {connection_name} ".format_map(locals()))
                logging.debug("Validating given schema is available in \
                              the connection. Fetching live schemas for {connection_name}".format_map(locals()))
                
                schema_list = self.__get_live_schemas(connection_global_id)
                if schema_name not in schema_list:
                    err_msg ="Schema with {schema_name} not available under {connection_name}".format_map(locals())
                    logging.error(err_msg)
                    raise DataTransformsException(err_msg)
                    
                logging.debug("Attaching schema {schema_name} with connection {connection_name} ".format_map(locals()))
                attach_schema_json = self.auto_create_schema(schema_name, connection_global_id)
                schema_global_id=attach_schema_json["globalId"]
                schema_tech=attach_schema_json["technology"]

            logging.debug("Fetching live tables from schema {schema_name}".format_map(locals()) )
            response = self.fetch_live_tables(schema_global_id)
            #logging.debug("Live tables data " + str(response.json()))
            logging.debug("Live tables fetched OK")

            tables_available = response.json()
            data_entities=[]
            logging.debug("Collecting data entities list")
            before_size = len(tables_available)

            if matching is not None:
                p = re.compile(matching)
                logging.debug("Matching filter found, extracting only matching tables {matching}".format(matching=matching))
                before_size = len(tables_available)
                tables_available = [ tbl for tbl in tables_available if p.match(tbl) ]
                after_size = len(tables_available)
                logging.info("After applying matching flter, before={before_size} after={after_size}".format_map(locals()))
            else:
                logging.info("***No matching filter applied, {before_size} tables will be used to generate data entities***"\
                             .format(before_size=before_size))

            for table_name in tables_available:
                logging.debug("Preparing column metadata from live query ")
                query_text = "select * from {schema_name}.\"{table_name}\"".format_map(locals())
                table_metadata_json = self.__fetch_table_metadata(connection_global_id, query_text)
                logging.debug("Preparing column metadata from live query {query_text}".format(query_text=query_text) + " [OK]")

                data_entity={}
                data_entity["name"]=table_name
                data_entity["technologyCode"]=schema_tech
                data_entity["schemaName"]=schema_name
                data_entity["dataServerName"]=connection_name
                
                de_cols=[]
                position=0
                for column_def in table_metadata_json:
                    de_col={}
                    position+=1
                    #TODO Better copy , then manipulate the values or remove unwanted keys
                    de_col["name"] = column_def["name"]
                    de_col["length"] = column_def["length"]
                    de_col["position"] = str(position)
                    de_col["dataType"] = column_def["type"]
                    de_col["dataTypeCode"] = column_def["type"]
                    de_col["scale"]=str(column_def["scale"])
                    de_cols.append(de_col)
        
                data_entity["columns"]=de_cols
                data_entities.append(data_entity)
            return data_entities
            

    def __fetch_table_metadata(self, connection_global_id, query_text):
        logging.debug("Fetching table metadata for {connection_global_id} with query {query_text}".format_map(locals()))
        table_metadata_ep=self.get_url()+"/v1/dataservers/previewQueryMetaData"
        table_metadata_payload_dict = {"dataServerGlobalId":connection_global_id,"queryText":query_text,"agentName":"OracleDIAgent1"}
        response = self.__post(table_metadata_ep,headers=self.get_headers(),payload_data=json.dumps(table_metadata_payload_dict))
        if response.status_code != 200:
            logging.debug("__fetch_table_metadata Response failure " + str(response.status_code) + " " + str(response.text))
            raise DataTransformsException("Failed to fetch table metadata for payload {query_text}".format(locals()))
        else:
            table_metadata_json = response.json()
            return table_metadata_json

    def validate_sql_text(self, connection_global_id, query_text):
        logging.debug("validate_sql_text {connection_global_id} with query {query_text}".format_map(locals()))
        table_metadata_ep=self.get_url()+"/v1/variables/validateSqlText"

        table_metadata_payload_dict = {"dataServerGlobalId":connection_global_id,"queryText":query_text,"agentName":"OracleDIAgent1"}
        response = self.__post(table_metadata_ep,headers=self.get_headers(),payload_data=json.dumps(table_metadata_payload_dict))
        if response.status_code != 200:
            logging.debug("__fetch_table_metadata Response failure " + str(response.status_code) + " " + str(response.text))
            return False,response.text
        else:
            table_metadata_json = response.json()
            return True,table_metadata_json

    def get_connection_details(self, connection_global_id):
        """Method that returns connection details for the given connection global id
        """
        get_connection_details_ep = self.get_url()+"/v1/dataservers/id/{connection_global_id}".format_map(locals())
        response = self.__get( get_connection_details_ep, headers=self.get_headers(), data=self.payload)
        if response.status_code != 200:
            logging.error("Failed to load the connection " + connection_global_id + " Received status " + str(response.status_code))
            print(str(response.status_code) + "\n" + response.text)
            raise DataTransformsException("Failed to load the connection " + 
                                          connection_global_id + " Received status " + str(response.status_code))
        return response


    def get_all_connection_with_props(self,collection_type):
        """
        Utility method to get the metadata collection in json format. Supported collections are 
        Connection, Data Entitities. Note - This operation may be time consuming based on the number of 
        entities available in the environment. 

        collection_type - one of the supported collection 'connection' or 'dataentity'
        Data Transforms Exception is thrown if the status received is NOT 200. 
        """
        collection_types = {'connection':  "/v1/dataservers/list"}
        get_all_ep = self.get_url() + collection_types.get(collection_type)
        response = self.__get( get_all_ep, headers=self.get_headers(), data=self.payload)
        if response.status_code != 200:
            logging.error("Failed to load all the connections " + str(response.status_code))
            logging.error("Connections load failure" + str(response.text))
            raise DataTransformsException("Failed to load all the connections ")
        
        collection = response.json()
        connections=[]
        for object in collection:
            connection_global_id= object["globalId"]
            response = self.get_connection_details(connection_global_id)
            connections.append(response.json())
        return connections

    def get_about_string(self):
        about_ep=self.get_url()+"/v1/about"
        #print(about_ep)
        #print("Headers \n\n\n\n" + str(self.get_headers()))

        response = self.__get(about_ep,self.get_headers(),self.payload)
        if response.status_code != 200:
            print("Failed to get information from " +about_ep + "Status code=" + str(response.status_code))
            print(response.text)
        else:
            about_dict = response.json()
            return about_dict

    def list_all_schema_in_connection(self,connection_name):
        connection_global_id=self.is_connection_available(connection_name)
        schema_ep=self.get_url()+"/v1/dataservers/id/{connection_global_id}/schemas".format_map(locals())

        response = self.__get(schema_ep,self.get_headers(),self.payload)
        if response.status_code != 200:
            logging.ERROR("Failed to get schema in connection " + str(response.status_code))
            logging.ERROR(response.text)
            raise DataTransformsException("Failed to get schema in connection")
        else:
            json_doc = response.json()
            #print(json_doc)
            schema_dict={}
            for entry in json_doc:
                schema_dict[entry["schemaShortName"]]=entry["globalId"]
            return schema_dict

    def create_schedule(self,schedule_payload,existing=False):
        schedules_ep=self.get_url()+"/v1/jobs/schedule"
        #print(schedule_payload)
        if not existing:
            logging.debug("Creating new schedule...")
            response = self.__post(schedules_ep,headers=self.get_headers(),payload_data=schedule_payload)
        else:
            logging.debug("Updating schedule...")
            response = self.__put(schedules_ep,headers=self.get_headers(),payload_data=schedule_payload)

        if response.status_code == 200:
            logging.info("Schedule sync [OK]")
            return True,response.json()["globalId"]
        else:
            logging.info("Schedule sync [KO]")
            logging.error("Schedule Sync Failed, Staus=" + str(response.status_code) + " Error Message" + response.text)
            return False,None

    def get_all_schedules(self):
        schedules_list_ep=self.get_url()+"/v1/jobs/schedules"
        response = self.__get(schedules_list_ep,self.get_headers(),self.payload)
        if response.status_code != 200:
            logging.ERROR("Failed to get schedules " + str(response.status_code))
            logging.ERROR(response.text)
            raise DataTransformsException("Failed to get schedules " + str(response.status_code) +  " " + response.text)
        else:
            json_doc = response.json()
            #print(json_doc)
            schedules_dict={}
            for entry in json_doc:
                schedules_dict[entry["name"]]=entry["globalId"]
            return schedules_dict
        
    def check_if_schedule_exists(self,schedule_name):
        logging.debug("CHecking for schedule " + schedule_name)
        schedules=self.get_all_schedules()
        if schedule_name in schedules.keys():
            #raise DataTransformsException("Schedule {schedule_name} already exists ".format_map(locals()))
            logging.debug("Schedule " + schedule_name + " available")
            return True,schedules[schedule_name]
        else:
            logging.debug("Schedule " + schedule_name + " not available")
            return False,None

    def __delete_schedule_by_global_id(self,schedule_global_id):
        delete_schedule_ep = self.get_url()+"/v1/jobs/schedule/id/{schedule_global_id}".format_map(locals())
        delete_response = self.__delete(delete_schedule_ep,DataTransformsClient.headers,data=None)
        if delete_response.status_code == 200:
            logging.info("Schedule deleted " + schedule_global_id)
            return True, delete_response
        else:
            logging.error("Delete schedule failed " + schedule_global_id + " Status code=" 
                          + str(delete_response.status_code)
                          + "Message=" + delete_response.text)
            
            return False, delete_response
            

    def delete_schedule_by_name(self,schedule_name):
        is_found,schedule_global_id = self.check_if_schedule_exists(schedule_name)
        if is_found:
            return self.__delete_schedule_by_global_id(schedule_global_id)
        else:
            #raise DataTransformsException("Failed to delete schedule, {schedule_name} not found".format_map(locals()))
            return False,None
    
    def get_current_time_from_deployment(self):
        logging.debug("Fetching current time in deployment")
        current_time_ep = self.get_url()+"/v1/jobs/scheduler/currentTime"
        response = self.__get(current_time_ep,self.get_headers(),self.payload)
        if response.status_code != 200:
            logging.error("Failed to get current time " + str(response.status_code))
            logging.error(response.text)
            raise DataTransformsException("Failed to get schedules " + str(response.status_code) +  " " + response.text)
        else:
            json_doc = response.json()
            current_time = json_doc["message"]
            current_time_adjusted = current_time[:-5]
            logging.debug("Current time in depolyment instance " + current_time + " " + current_time_adjusted)
            return current_time_adjusted 

    def create_variable(self,variable_payload,is_existing=False):
        logging.debug("Creating variable")
        logging.debug(variable_payload)
        variable_create_ep=self.get_url()+"/v1/variables"
        if not is_existing:
            response = self.__post(variable_create_ep,headers=self.get_headers(),payload_data=variable_payload)
        else:
            response = self.__put(variable_create_ep,headers=self.get_headers(),payload_data=variable_payload)

        if (response.status_code == 200):
            variable_global_id=response.json()["variableGlobalId"]
            logging.debug("Variable {variable_global_id} sync [OK]".format_map(locals()) )
            return True,variable_global_id
        else:
            logging.error("Variable sync [KO]")
            logging.error(str(response.status_code) + " " + response.text)
    
    def get_all_variables(self,project_id):
        all_variables_ep=self.get_url()+"/v1/variables/project/id/{project_id}".format_map(locals())
        response = self.__get(all_variables_ep,self.get_headers(),self.payload)
        if response.status_code != 200:
            logging.error("Failed to get all variables from project " + str(response.status_code))
            logging.error(response.text)
            raise DataTransformsException("Failed to get all variables " + str(response.status_code) +  " " + response.text)
        else:
            json_doc = response.json()
            variable_dict={}
            
            for variable_entry in json_doc:
                variable_dict[variable_entry["variableName"]]=variable_entry["variableGlobalId"]
            return variable_dict,json_doc
    
    def get_all_schemas_created_under_connection(self,data_server_global_id):
        """Returns only the schemas created under the connection already in data transforms."""
        existing_schemas_ep=self.get_url()+"/v1/dataservers/schemas/names?dataServerId={data_server_global_id}".format_map(locals())
        response = self.__get(existing_schemas_ep,self.get_headers(),self.payload)
        if response.status_code != 200:
            logging.error("Failed to get all schemas from connection {data_server_global_id}".format_map(locals()))
            logging.error(response.text)
            raise DataTransformsException("Failed to get all existing schemas " + str(response.status_code) +  " " + response.text)
        else:
            json_doc = response.json()
            variable_dict={}

            for variable_entry in json_doc:
                variable_dict[variable_entry["name"]]=variable_entry["globalId"]
            return variable_dict

    def get_live_schemas_from_connection(self,data_server_global_id):
        """Returns list of available schema by connecting to respective data system

        Arguments:
            data_server_global_id -- unique ID of the data server

        Returns:
            list of available schema in the data server
        """
        schema_list = self.__get_live_schemas(data_server_global_id)
        return schema_list

    def check_if_project_exists(self,project_name):
        """Check if the project is present in data transfroms, 
        Returns Project_ID if the given project_name is found.
        Raises DataTransformsException if the given project_name is not found
        """
        projects=self.get_all_projects()
        if project_name not in projects:
            raise DataTransformsException("Invalid Project " + project_name)
        return projects[project_name]

    def do_post(self,endpoint,headers, payload_data):
        """Method to initiate POST on given endpoint and paylaod"""
        return self.__post(endpoint,headers,payload_data)
    
