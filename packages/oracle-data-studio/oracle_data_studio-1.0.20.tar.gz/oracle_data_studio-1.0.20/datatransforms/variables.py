'''
Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

Represents variable definitions in datatransforms
'''

from enum import Enum
class VariableTypes(Enum):
    """Variable data types supported by datatransforms"""
    DATE="DATE"
    SHORT_TEXT="SHORT_TEXT"
    LONG_TEXT="LONG_TEXT"
    NUMERIC="NUMERIC"

class KeepHistory(Enum):
    """Enum for variable history options"""
    LATEST_VALUE='LATEST_VALUE'

class Variable:
    """Represents Variable object defined in datatransforms.
    Typically variable has name, datatype, default value and project where it belongs"""
    # pylint: disable=invalid-name,too-many-arguments,too-many-instance-attributes
    def __init__(self,name,variable_type,default_value,project_name):
        """
        Create a variable with name,type,default_value(optional) 
        and project where it should be created.

        Exception will be raised if project_name is not found in 
        the deployment while create/save operation is performed
        """
        self.variableName=name
        self.variableGlobalId=None
        if isinstance(variable_type,VariableTypes):
            self.variableType=variable_type.value
        else:
            self.variableType=type

        #self.global_variable=False
        self.defaultValue=default_value
        self.project_name=project_name
        self.projectGlobalId=None
        self.dataServerGlobalId=None
        self.physicalSchemaGlobalId=None
        self.physicalSchema=None

        self.valuePersistence=KeepHistory.LATEST_VALUE.value

        self.physicalSchemaShort=None
        self.connection_name=None
        self.refreshQuery=None
        self.is_refresh_set=True
        self.project = None

    def keep_history(self,history):
        """Update the keep history option, the input can be a string or enum
        if history is passed as enum, its value is obtained and considered for the option"""
        if isinstance(type,KeepHistory):
            self.valuePersistence=history.value
        else:
            self.valuePersistence=history

    def refresh(self,connection_name,schema_name,sql_query):
        """Refresh the variable value from database query. 
        exception is thrown when sql_query is not a valid one. 
        """
        self.physicalSchemaShort=schema_name
        self.connection_name=connection_name
        self.refreshQuery=sql_query
        self.is_refresh_set=True

    def add_to_project(self,project_name=None,project_code=None):
        """Project name and code associated with the variable
        """
        if project_name is not None:
            self.project_name = project_name
        elif project_code is not None:
            self.project = project_code
