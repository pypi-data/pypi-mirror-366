'''
Licensed under the Universal Permissive License v 1.0 as shown at
 https://oss.oracle.com/licenses/upl/.

 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

Exposes all the APIs available for consumption.

'''
import configparser
import logging
import os
from importlib.resources import files
from string import Template

from datatransforms.client import DataTransformsClient,DataTransformsException
from datatransforms.restclients.runtime_api import RuntimeClient
from datatransforms.restclients.dataflow_api import DataFlowClient

from datatransforms.connection import Connection
from datatransforms.dataentity import DataEntity
from datatransforms.project import Project
from datatransforms.schedule import Schedule
from datatransforms.variables import Variable
from datatransforms.secrets_util import SecretsStore
from datatransforms.payloadutil.variable_payload import VariablePayLoadResolver

#pylint: disable=C0103:invalid-name
#some of the member variables are aligned with JSON payload definitions of datatransforms

class WorkbenchConfig:

    """
    APIs to load configuration params for connecting workbench. 
    Typical workbench configuration consists of one or more deployment 
    configuration which developer can connect to. 

    This implementation uses Python's ConfigParser , which loads 
    configurations and sections as per 'ini' file format. THe config 
    file 'deployment.config' is searched based on OS path environment or current working directory.
    """
    config = configparser.ConfigParser()
    mp_config_set = ('xforms_ip','xforms_user','pswd')

    @staticmethod
    def get_workbench_config(pswd):
        """
        Loads the deployment.config from the current directory and returns the parsed configuration

        pswd - credential to be used for accessing the environment.
        """
        ACTIVE_PROFILE_NAME = "ACTIVE"
        DEPLOYMENT_NAME ='deployment'
        config = WorkbenchConfig.config
        found = config.read('deployment.config')
        logging.debug("Loaded config")
        logging.debug(config.sections())

        if found is None or len(config.sections()) < 1:
            raise DataTransformsException(
                "Failed to read deployment configuration. File deployment.config is not found")
        logging.debug("Checking if ACTIVE deployment is configured")
        deployment_config_params={}
        if config.has_section(ACTIVE_PROFILE_NAME):
            logging.info("Loading active deployment configuration")

            if DEPLOYMENT_NAME not in config.options(ACTIVE_PROFILE_NAME):
                raise DataTransformsException(
                    "Active deployment missing in configuration. Available options" 
                    + str(config.options(ACTIVE_PROFILE_NAME)))

            active_profile_reference=config.get(ACTIVE_PROFILE_NAME,DEPLOYMENT_NAME)
            logging.debug(
                "Loading default deployment  %s " , active_profile_reference)
            if active_profile_reference not in config.sections():
                err_msg = f"Missing config section {active_profile_reference}"
                logging.error(err_msg)
                raise DataTransformsException(err_msg)
            logging.debug("Loading configuration for %s ", active_profile_reference)
            deployment_config_params = dict(config.items(active_profile_reference))
            WorkbenchConfig.validate_config_params(deployment_config_params)

            deployment_config_params=WorkbenchConfig.__resolve_secure_fields(
                deployment_config_params)
            if pswd is None or pswd == "":
                raise DataTransformsException("Invalid credential, " \
                "credential can't be empty or null")
            deployment_config_params["pswd"]=pswd

            if 'xforms_url' in deployment_config_params:
                url = deployment_config_params['xforms_url']
                if url.endswith("/"):
                    url=url[:-1]
                    print("URL Modified to remove /. Modified URL " + url)
                    deployment_config_params['xforms_url']=url

            return deployment_config_params
        else:
            logging.fatal("active deployment configuration missing")
            raise DataTransformsException("No active configuration available to connect")

    @staticmethod
    def validate_config_params(config_params):
        """
        Validates configuration parameters as per the defintion.
        Used only as an iternal method, It doesn't throw any error in current version. 
        """
        #Validate market place parameters - instance-ip, user, password must be available
        #validate ADBS parameters - token URL, tenancy, db ocid, dbname, user, password
        #params_from_config = list(config_params.keys())
        if set(WorkbenchConfig.mp_config_set).issubset(config_params):
            #if market place configuration is available ignore the rest from defaults
            if 'xforms_url' in config_params:
                del config_params['xforms_url']
            logging.debug("profile found for Market place deployment")

    @staticmethod
    def __resolve_secure_fields(deployment_config_params):
        #eheck if the developer has secured the password using keyring
        if ('pswd' in deployment_config_params.keys() and
            deployment_config_params['pswd'].startswith('keyring:')):
            logging.debug("Credentials are secured")
            key_ring_store_str=deployment_config_params['pswd']
            key_ids = key_ring_store_str.split(":")

            if len(key_ids) <2:
                #this should not occur here...
                raise DataTransformsException(
                    "Secured entry must have keyring:<service> or keyring:<service>|<user>")

            if key_ids[0] != "keyring":
                raise DataTransformsException("Unsupported secret store. Only keyring is supported")

            #check if there is service & user option provided
            if "|" in key_ids[1]:
                keyring_entry = key_ids[1].split("|")
                pswd = SecretsStore().get_pswd(keyring_entry[0],keyring_entry[1])
                deployment_config_params['pswd']=pswd
                return deployment_config_params
            else:
                user,pswd = SecretsStore().get_credentials(service=key_ids[1])
                deployment_config_params['xforms_user']=user
                deployment_config_params['pswd']=pswd
                return deployment_config_params
        else:
            #password is not secured. return as is
            return deployment_config_params

class DataTransformsWorkbench:

    """
    Workbench connects to the configured deployment and acts as entry point for all the operations. 
    """
    active_workbench=None
    client = None
    runtime_client=None
    dataflow_client=None
    _instance = None

    def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.client=DataTransformsClient()
            self.runtime_client=RuntimeClient()
            self.dataflow_client=DataFlowClient()
            self._instance = self
            logging.debug("Runtime ready")

    def get_client(self):
        """
        Returns the REST Client for operations. This function is rarely required for consumption
        Developers shall use the respective operations exposed for managing 
        Dataflows, DataLoads and Workflows
        """
        if DataTransformsWorkbench.client is None:
            DataTransformsWorkbench.client=DataTransformsClient()
            DataTransformsClient.client=DataTransformsClient()
        return DataTransformsWorkbench.client

    def connect(self,ip,user,pwd):
        """
        Connects workbench to customer managed Data Transforms (marketplace instance).
        Recommended only for unit test purposes.
        For production usage use connect_workbench(connect_params)
        """
        self.get_client().connect(ip,user,pwd)

    def connect_workbench(self,connect_params):
        """
        Connects the workbench with active deployment for performing operations.       
        Raises DataTransformsException if the connection could not be established or 
        connection operation encounters authentication failure 

        if the deploymnet configured is of type ADBS, container status is queried first.
        If the container is not available, 4 attempts are made with 15 seconds interval 
        (with max wait time of 1 minute). If the container is not available after the max 
        attempts, exception is raised.

        """
        if 'xforms_url' in connect_params and 'xforms_user' \
            in connect_params and len(connect_params)==3:
            #check if the params are only URL and User,
            # in such case detect as simple URL based auth.
            self.get_client().connect_withurl(
                connect_params['xforms_url'],connect_params['xforms_user'],connect_params['pswd'])
            self.get_runtime_client().connect_withurl(
                connect_params['xforms_url'],connect_params['xforms_user'],connect_params['pswd'])
            self.get_dataflow_client().connect_withurl(
                connect_params['xforms_url'],connect_params['xforms_user'],connect_params['pswd'])

        elif 'xforms_url' in connect_params:
            os.environ['ADP_ENV']="True"
            xforms_url = connect_params['xforms_url']
            connect_params['auth_token_url'] = xforms_url+"/broker/pdbcs/public/v1/token"
            logging.info("Connecting to ADBS %s ",connect_params['auth_token_url'])
            access_token = self.get_client().fetch_token(connect_params)

            os.environ['auth_token_url']=connect_params['auth_token_url']
            os.environ['xforms_url'] = xforms_url+"/odi-rest"
            os.environ['DATA_TRANSFORMS_AUTH'] = "Bearer " + access_token

            self.get_client().connect_attempts=6
            self.get_client().wait_seconds=20
            self.get_client().wait_for_adbs_container_up(xforms_url,access_token)

            self.get_client().connect_adbs_with_token(xforms_url,access_token)
            self.get_runtime_client().connect_adbs_with_token(xforms_url,access_token)
            self.get_dataflow_client().connect_adbs_with_token(xforms_url,access_token)

        elif 'xforms_ip' in connect_params:
            self.get_client().connect(
                connect_params['xforms_ip'],connect_params['xforms_user'],connect_params['pswd'])
            self.get_runtime_client().connect(
                connect_params['xforms_ip'],connect_params['xforms_user'],connect_params['pswd'])
            self.get_dataflow_client().connect(
                connect_params['xforms_ip'],connect_params['xforms_user'],connect_params['pswd'])
        else:
            raise DataTransformsException(
                "Invalid deployment configuration. No Market place, or ADP deployments found ")

    def get_all_connections(self):
        """
        Returns all the available connections in data transforms instance.
        """
        return self.get_client().get_all_connections()

    def get_all_datastores(self):
        """
        Returns all the data entities available in datatransforms instance
        """
        return self.get_client().get_all_datastores()

    def get_all_data_entities(self):
        """
        Returns all the data entities available in datatransforms instance
        """
        return self.get_client().get_all_datastores()

    def save_connection(self,connection_obj):
        """
        Saves the connection object to the repository. If the connection with
        given name is already found , Update operation is performed. 

        """
        if not isinstance(connection_obj,Connection):
            raise DataTransformsException("Invalid connection object")

        connection_name = connection_obj.get_connection_name()
        if "walletURL" in connection_obj.connectionProperties:
            logging.info("Found wallet based connection, uploading wallet")
            wallet_location,services = self.get_client().process_wallet(
                connection_obj.connectionProperties["walletURL"])
            connection_obj.connectionProperties["walletURL"]=wallet_location
            print("wallet_location %s %s", wallet_location, services)

        all_connections = self.get_all_connections()

        if connection_name in all_connections.keys():
            logging.debug("Connection  already exists, updating connection %s" , connection_name)
            global_id= all_connections[connection_name]
            connection_obj.globalID(global_id)

            connection_json_payload=connection_obj.prepare_payload()
            #print("\n\n\n")
            #print(connection_json_payload)
            return self.get_client().update_connection_from_json(connection_json_payload)
        else:
            connection_json_payload=connection_obj.prepare_payload()
            return self.get_client().create_connection_from_json(connection_json_payload)

    def test_connection(self,connection_obj):
        """
        Tests the given connection Object.

        Parameters
        connection_object - valid connection object with connection name, 

        Resolves the connection id from name and perform test to check the connectivity.
        Raise Data transforms exception if the test on the connection fails
        """

        if not isinstance(connection_obj,Connection):
            raise DataTransformsException("Invalid connection object")
        connection_map = self.get_client().get_all_connections()
        if connection_obj.get_connection_name() not in connection_map:
            raise DataTransformsException("Invalid connection to test, given connection not found")
        connection_id = connection_map[connection_obj.get_connection_name()]

        return self.get_client().test_connection(connection_id)

    def save_data_entity(self,entity_obj):
        """
        API to store the data entity in DataTransforms
        """
        if not isinstance(entity_obj,DataEntity):
            raise DataTransformsException("Invalid data entity")

        #self.getClient().load_cache()
        self.get_all_datastores()

        con_name = entity_obj.dataServerName
        schema_name = entity_obj.model["schema"].schemaShortName
        store_name = entity_obj.dataStore.name


        fq_store_name = ".".join([con_name,schema_name,store_name])
        fq_schema = ".".join([con_name,schema_name])

        #print(fq_store_name + "\n\n")
        if fq_store_name in self.client.connection_schemas_stores_detail:
            logging.info("Data entity %s already exists, Ignoring",fq_store_name)
        else:
            logging.info("Data Entity doesn't exist, creating one")

            connections = self.get_all_connections()
            if con_name not in connections:
                raise DataTransformsException("Connection " + con_name + " not available")

            logging.debug("Fetching connection details to get registered schemas ")
            con_id=connections[con_name]
            con_details = self.get_client().get_connection_details(con_id)
            con_details_json = con_details.json()
            connection_registered_schemas = con_details_json["schemas"]

            for connection_registered_schema in connection_registered_schemas:
                schemaName = connection_registered_schema["schemaName"]
                schema_global_id = connection_registered_schema["globalId"]

                if schemaName == fq_schema:
                    logging.debug(
                        "{fq_schema} is already available {schema_global_id}".format_map(locals()) )
                    entity_obj.model["schema"].schema_globalID(schema_global_id)

            conneciton_global_id= connections[con_name]
            entity_obj.dataServerGlobalId(conneciton_global_id)

            logging.info("Creating data entity from connection= {con_name} schema {schema_name}")
            json_payload = entity_obj.prepare_payload()

            self.get_client().create_de_from_json(json_payload)

    def __prepare_data_entity_import_job(self, connection_name,schema_name):
        """Provides the default options for the given connection name"""

        connection_id = self.__resolve_connection(connection_name)
        schema_id = self.__resolve_schema(connection_id,schema_name)

        print("Initiating import entity for " + connection_name,schema_name)
        my_resources = files("generators")
        data = my_resources.joinpath("reverse_template.json").read_text()
        inputs = {"connection_name":connection_name,
                  "connection_id":connection_id,
                  "schema_name":schema_name,
                  "schema_global_id":schema_id}
        contents = Template(data).substitute(inputs).encode("utf-8")

        return contents

    def __resolve_connection(self,connection_name):
        """
        Resolves internal ID of the connection, raises Datatransforms Exception
        if failed.
        """
        connections = self.get_all_connections()
        if connection_name not in connections.keys():
            raise DataTransformsException(f"{connection_name} not found ")
        return connections[connection_name]

    def __resolve_schema(self,connection_id,schema_name):
        """
        Resolves the schema global id for the given connection and schema. 
        If the schema is not found, creates new one in data transforms. 
        """
        schemas = self.get_client().get_all_schemas_created_under_connection(connection_id)
        if schema_name not in schemas.keys():
            schema_obj = self.get_client().auto_create_schema(
                schema_name=schema_name,connection_global_id=connection_id)
            logging.debug("Resolved schema %s to %s by creating new",
                          schema_name,schema_obj["globalId"])
            return schema_obj["globalId"]
        schema_id = schemas[schema_name]
        logging.debug("Resolved schema %s to %s from existing schemas", schema_name,schema_id)
        return schema_id

    def import_data_entities(self,connection_name,schema_name,import_options=None):
        """
        Initiates the job for importing data entities for a given connection. 
        This is async operation which returns immediately after the job is started. 
        Caller of this API need to track the status of the job either through 
        polling or monitoring the state change with some callback methods. 
        """
        if import_options is not None:
            raise DataTransformsException("Customizing import options not available")
        import_payload = self.__prepare_data_entity_import_job(connection_name,schema_name)

        return self.get_client().import_entities(import_payload)

    def save_project(self,project):
        """Saves project in data transforms"""
        if isinstance(project,Project):
            self.get_client().create_project(
                name=project.name,code=project.code,folder=project.folder)
        else:
            raise DataTransformsException("Invalid Project object for save.")

    def delete_connection(self,connection):
        """Deletes the connection in DataTransforms.
        Caution !! Deleting connection will result in all the dependant
        objects also to be deleted"""
        if not isinstance(connection,Connection):
            raise DataTransformsException("Invalid connection object")

        return self.get_client().delete(connection)

    def delete_project(self,project):
        """
        Deletes the project and its contents from data transforms instance. 
        This action deletes all the project bound objects, can't be undone.
        """
        if not isinstance(project,Project):
            raise DataTransformsException("Invalid Project object")

        return self.get_client().delete(project)

    def print_about_string(self):
        """Displays details about the environment"""
        about_dict = self.get_client().get_about_string()
        current_time = self.get_client().get_current_time_from_deployment()
        is_mp= os.environ['MP_ENV'] if 'MP_ENV' in os.environ else "False"

        deployment_type = "Marketplace " if is_mp == "True" else "Autonomous DB"

        about_dict["Current Time in Deployment Instance"]=current_time
        about_dict["Deployment Type"]=deployment_type
        about_dict["Deployment Instance"] = self.client.get_url()

        print("\nOracle Data Transforms - Deployment details")
        print("-"*70)
        for key,value in about_dict.items():
            print(key  + " : " + str(value))
        print("-"*70)

    def save_schedule(self,schedule):
        """
        Saves the schedule & details of schedule
        """
        if not isinstance(schedule,Schedule):
            raise DataTransformsException("Invalid schedule object")
        schedule.create()

    def delete_schedule(self,schedule):
        """
        Removes the schedule from DataTransforms
        """
        if not isinstance(schedule,Schedule):
            raise DataTransformsException("Invalid schedule object")

        return self.get_client().delete_schedule_by_name(schedule.name)

    def get_all_schedules(self):
        """
        Returns all the available scheduled jobs
        """
        schedules= self.get_client().get_all_schedules()
        schedule_obj_list=[]
        for schedule_name in schedules:
            schedule_obj_list.append(Schedule(schedule_name))
        return schedule_obj_list

    def save_variable(self,variable):
        """
        Saves variable & details in DataTransforms
        """
        if not isinstance(variable,Variable):
            raise DataTransformsException("Invalid variable object")
        VariablePayLoadResolver().create_variable(variable)

    def get_runtime_client(self):
        """Returns runtime client instance initialised at the time of 
        creating workbech
        """
        return self.runtime_client

    def get_dataflow_client(self):
        """Returns client instance for performing dataflow operations"""
        return self.dataflow_client

    def run(self,exec_obj):
        """Initiates the run/execution on the given object. The object could be 
        a DataFlow, DataLoad or Workflow
        """
        self.get_runtime_client().run(exec_obj)


class WorkbenchCache:
    """
    Cache class for housing frequently used entities, 
    to avoid multiple network calls for read operations
    Future purpose
    """
    connections={}
    datastores={}

    @staticmethod
    def get_connections():
        """Returns all the available connections from cache"""
        return WorkbenchCache.connections
    @staticmethod
    def get_data_entities():
        """Returns all the available data entities from cache"""
        return WorkbenchCache.datastores
    