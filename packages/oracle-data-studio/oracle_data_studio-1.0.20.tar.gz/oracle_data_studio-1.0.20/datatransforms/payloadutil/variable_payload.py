'''
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

Class that generates payload JSON for the respective operators for variables. 

All the APIs provided here might change, hence it is not exposed for external developers
Variables operations must be used through Variable and Workbech APIs
'''
import json
import logging

from datatransforms.variables import Variable
from datatransforms.client import DataTransformsClient,DataTransformsException
#pylint: disable=all

class VariablePayLoadResolver:

    def __init__(self):
        self.client = DataTransformsClient()
        pass


    def resolve_variable_payload(self,variable):
       
        if not isinstance(variable,Variable):
            raise DataTransformsException("Invalid variable object")

        logging.debug("Resolving project for variable " + variable.variableName)
        projects =self.client.get_all_projects()
        if variable.project_name not in projects.keys():
            raise DataTransformsException("Invalid variable object, Project {project_name} not available".format(project_name=variable.project_name))

        variable.projectGlobalId=projects[variable.project_name]

        logging.debug(
            "Checking if variable %s exists under project %s", 
            variable.variableName, variable.project_name)

        is_existing=False
        variable_dict = self.client.get_all_variables(variable.projectGlobalId)
        if variable.variableName in variable_dict.keys():
            variable.variableGlobalId=variable_dict[variable.variableName]
            is_existing=True


        if 'is_refresh_set' in variable.__dict__ and variable.is_refresh_set:
            if variable.connection_name is None \
                or variable.physicalSchemaShort is None \
                or variable.refreshQuery is None:

                raise DataTransformsException(
                    "Invalid variable object, refresh must have connection name, \
                        schema and sql query to refresh")

            connections = self.client.get_all_connections()
            if variable.connection_name not in connections.keys():
                raise DataTransformsException("Invalid variable object, provided connection {connection_name} not found"
                                              .format(connection_name=variable.connection_name) )
            logging.debug("Resolved connection for variable " + variable.variableName)
            variable.dataServerGlobalId=connections[variable.connection_name]
            

            logging.debug("Resolving schema used in variable " + variable.variableName)
            schema_dict = self.client.get_all_schemas_created_under_connection(variable.dataServerGlobalId)
            if variable.physicalSchemaShort not in schema_dict.keys():
                logging.debug("Referenced schema " + variable.physicalSchemaShort + " not found in existing schema, checking live")
                live_schemas = self.client.get_live_schemas_from_connection(variable.dataServerGlobalId)
                if variable.physicalSchemaShort not in live_schemas:
                    raise DataTransformsException("Invalid variable, Referenced schema {schema} not found under {connection}"
                                                  .format(schema=variable.physicalSchemaShort,connection=variable.connection_name))
                
                logging.debug("Schema is not available under connection, attaching")
                schema_global_id = self.client.attach_schema_with_connection(variable.connection_name,variable.physicalSchemaShort)
                variable.physicalSchemaGlobalId=schema_global_id
                variable.physicalSchema=variable.connection_name + "." + variable.physicalSchemaShort
            else:
                variable.physicalSchemaGlobalId=schema_dict[variable.physicalSchemaShort]
                variable.physicalSchema=variable.connection_name + "." + variable.physicalSchemaShort

            logging.debug("Validating variable refresh query %s" , variable.variableName)
            is_query_ok,query_validation_message = self.client.validate_sql_text(
                variable.dataServerGlobalId,variable.refreshQuery)

            if not is_query_ok:
                raise DataTransformsException(
                    "invalid variable, Refresh query validation failed with message " 
                    + query_validation_message)

        del variable.project_name 
        to_be_removed_from_json_payload = ['project_name','connection_name','is_refresh_set']

        var_dict = variable.__dict__

        for entry in to_be_removed_from_json_payload:
            if entry in var_dict.keys():
                del var_dict[entry] 

        if 'variableGlobalId' in var_dict and var_dict["variableGlobalId"] is None:
            del var_dict["variableGlobalId"]
        var_dict["global"]=False
        variable_payload=json.dumps(var_dict)
        return is_existing,variable_payload

    def create_variable(self,variable):
        """
        Creates new variable. JSON document is generated from variable object,
        and performs REST API call to create variable in datatransforms 
        """
        is_existing,payload = self.resolve_variable_payload(variable)
        return self.client.create_variable(payload,is_existing)
    