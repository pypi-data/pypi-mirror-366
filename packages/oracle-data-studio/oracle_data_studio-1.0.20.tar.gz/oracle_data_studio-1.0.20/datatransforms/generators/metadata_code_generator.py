"""
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

Contains classes that generate metadata python script by connecting to existing 
deployment
"""
import logging
import getpass

from datatransforms.workbench import DataTransformsWorkbench,WorkbenchConfig

class ConnectionCodeGenerator:

    """
    Houses utility method(s) to extract connection definition from an existing 
    datatransforms deployment and generate an executable python script that 
    re-creates connections. Useful for re-creating the connections in other environments 
    with customizations like (change of credentials or wallet)
    """
    def __init__(self):
        logging.info("Loading active workbench")
        connect_params = WorkbenchConfig.get_workbench_config(
            getpass.getpass("Enter deployment password:"))
        self.workbench = DataTransformsWorkbench()
        self.workbench.connect_workbench(connect_params)

    def export_connections_as_script(self,python_file):
        """
        Utility method to export all the connection objects defined in datatransforms
        as executable python script
        """
        connections = self.workbench.get_client().get_all_connection_with_props('connection')
        self.__generate_py_code(connections,python_file)

    def __generate_py_code(self,connections,python_file):
        header_code_comment = """##Utlity script that loads connection in the system"""
        header_code = \
        """
from datatransforms.workbench import DataTransformsWorkbench,DataTransformsException,WorkbenchConfig
from datatransforms.models import Connection
from datatransforms.connection_types import ConnectionTypes
import logging
        """

        workbench_load_code = """
##Load active workbench from configuration
connect_params = WorkbenchConfig.get_workbench_config(getpass.getpass("Enter deployment password:"))
workbench = DataTransformsWorkbench()
workbench.connect(connect_params['xforms_ip'],connect_params['xforms_user'],connect_params['pswd'])


"""
        full_code = header_code_comment +"\n" + header_code + "\n" + "\n" + workbench_load_code
        # pylint: disable=possibly-unused-variable
        #optimise later, false +
        for connection in connections:
            con_name = connection["name"]
            con_var_name=con_name.replace(" ", "").lower()+"_connection"
            con_tech = connection["technology"]

             # pylint: disable=line-too-long
             #optimise later, wrapping the generated code next line causing error on syntax
            con_code_fragment = """{con_var_name} = Connection().connection_name("{con_name}").of_type(ConnectionTypes.{con_tech})"""
            con_code_fragment=con_code_fragment.format_map(locals())+"\n"

            con_props = connection["connectionProperties"]
            con_props_fragment = ""

            for con_prop,con_prop_value in con_props.items():
                if con_prop == "dataServerProperties" or con_prop == "walletURL":
                    continue

                if isinstance(con_prop_value,str):
                    con_prop_value="\""+con_prop_value+"\""
                con_prop_fragment = """{con_var_name}.property("{con_prop}",{con_prop_value})\n"""
                con_prop_fragment=con_prop_fragment.format_map(locals())
                con_code_fragment += con_prop_fragment

            workbench_save_fragment = "workbench.save_connection({con_var_name})\n\n"
            con_code_fragment+=workbench_save_fragment.format_map(locals())
            full_code += con_code_fragment

            with open(python_file,"w",encoding="utf-8") as f:
                f.write(full_code)

class DataEntityCodeGenerator:

    """Utility class that generates the Python code from existing data entities or live tables. 

    
    Generation of data entities is done in two modes. 
    a) Live b) Existing - disovered or already reverse engineered in data transforms 
    deployment. 

    Live - in this mode , the generation of python script will query metadata using 
    the connection and schema. 

    Existing - in this mode ONLY reverse engineered objects are generated as code. 

    In Live mode - the connectivity must be successful with the given connection as 
    it is being done realtime. exception is raised otherwise. 

    In Existing - the discovered/reverse engineered objects are generated as is to 
    python code, connection will not be established. Hence even if the connection is 
    offline, generation will happen from existing entities.

    Where this can be used ? 
    The implementation enables the developer to capture all the reverse engineered 
    objects from a connection and load to other environment(s) without needing to 
    re-run reverse engineering. 

    The generated code does not get executed by default, developer can review the 
    data entities and load only required entities from the generated code and 
    version-control them as part of their project.
    """

    def __init__(self):
        logging.info("Loading active work bench")
        connect_params = WorkbenchConfig.get_workbench_config(getpass.getpass("Enter deployment password:"))
        self.workbench = DataTransformsWorkbench()
        self.workbench.connect_workbench(connect_params=connect_params)

    #pylint ignore=too-many-arguments,possibly-unused-variable
    #optimise later
    def generate_data_entities_script(self,connection_name,
                                      schema_name,python_file=None,live=False,matching=None):

        """
        Generates python script to create/re-create data entities. 
        live = Fale indicates - to generate the script from existing 
        entities (reverse engineered already)

        live = True , generates data entities through live schema, 
        live tables and live column operations . Does not impact the repo

        matching - filter based on regular expression (AB*|DE* indicates 
        generate tables start with AB* or DE* - ignore the rest)
        """
        if python_file is None:
            #pylint: disable=possibly-unused-variable
            con_file_name=connection_name.replace(" ","").lower()
            schema_file_name=schema_name.replace(" ","").lower()

            python_file="{con_file_name}_{schema_file_name}_entities.py".format_map(locals())
            logging.info("Data Entities will be generated in script file %s",python_file)

        data_entities = self.workbench.get_client().\
            get_all_data_entities(
                connection_name=connection_name,
                schema_name=schema_name,
                live=live,
                matching=matching)
        self.__generate_py_code(data_entities,python_file)

    def __generate_py_code(self,data_entities,python_file):
        logging.debug("Preparing to generate py script")
        full_code = self.__generate_initial_code()

        if data_entities:
            for data_entity in data_entities:
                de_name = data_entity["name"]
                de_var_name=de_name.lower()+"_entity"
                de_var_name=de_var_name.replace(" ","")
                de_var_name=de_var_name.replace("$","_")
                de_var_name=de_var_name.replace(".","_")
                # pylint: disable=possibly-unused-variable,invalid-name
                de_tech= data_entity["technologyCode"]
                de_schema = data_entity["schemaName"]
                de_connection  = data_entity["dataServerName"]
                # pylint: disable=line-too-long
                #optimise later, wrapping the generated code next line causing error on syntax

                de_code_fragment = """{de_var_name} = DataEntity().from_connection("{de_connection}","{de_schema}").entity_name("{de_name}")"""
                de_code_fragment=de_code_fragment.format_map(locals())+"\n"

                de_cols = data_entity["columns"]
                de_col_fragment = ""

                for col in de_cols:
                    col_name = col["name"]
                    position = str(col["position"])
                    dataType = col["dataType"]
                    dataTypeCode = col["dataTypeCode"]
                    length=str(col["length"])
                    scale = str(col["scale"])
                    de_col_fragment = """{de_var_name}.add_column(name="{col_name}",position={position},dataType="{dataType}",dataTypeCode="{dataTypeCode}",length={length},scale={scale})"""
                    de_col_fragment=de_col_fragment.format_map(locals()) + "\n"
                    de_code_fragment += de_col_fragment

                workbench_save_fragment = "workbench.save_data_entity({de_var_name})\n\n"
                de_code_fragment+=workbench_save_fragment.format_map(locals())
                full_code += de_code_fragment
        else:
            full_code+= "\n\n ## NO Data entities available to generate the code"

        with open(python_file,"w",encoding="utf-8") as file:
            file.write(full_code)

        logging.debug("Data entity preparation successfully completed %s" , python_file)

    def __generate_initial_code(self):
        """
        Utility method to generate the initial code block.
        """
        header_code_comment = """##Utlity script that loads the data entities in the system"""
        header_code = \
        """
from datatransforms.workbench import DataTransformsWorkbench,DataTransformsException,WorkbenchConfig
from datatransforms.dataentity import DataEntity
import logging
        """

        workbench_load_code = """
##Load active workbench from configuration
connect_params = WorkbenchConfig.get_workbench_config("")
workbench = DataTransformsWorkbench()
workbench.connect_workbench(connect_params)
"""
        full_code = header_code_comment +"\n" + header_code + "\n" + "\n" + workbench_load_code
        return full_code
