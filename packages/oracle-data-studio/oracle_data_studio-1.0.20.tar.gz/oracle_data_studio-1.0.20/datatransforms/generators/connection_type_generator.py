""" 
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

Utility script that generages enumerations for Connection Types and 
Drivers required for the connection. This script is not intended to 
be run by developers. It generates the connection types by connecting to a 
deployment instance. This is usually done at the distribution time.

Ensure python path is set appropriately for running this code
"""
import os
import getpass

from datatransforms import client
from datatransforms.workbench import WorkbenchConfig,DataTransformsWorkbench


def treat_special_type(conn_code):
    """
    Converts the connection types with special characters to standard 
    python variable name conversion. Also maintains a dictionary of mapped
    connection types
    """
    sepcial_types={"AHA!":"AHA"}

    if conn_code in sepcial_types:
        return sepcial_types[code]
    else:
        return conn_code

connect_params = WorkbenchConfig.get_workbench_config(getpass.getpass("Enter deployment password:"))
workbench = DataTransformsWorkbench()
workbench.connect_workbench(connect_params)
connection_type_codes = workbench.client.get_connection_types()
path_to_generate_code = os.path.dirname(client.__file__)

CON_TYPE_FILE_NAME = "connection_types.py"
CLASS_FRAGMENT_ENUM = """

from enum import Enum

#Enum type of all the supported connection types 
#This is generated code (Oracle Data Transforms) 
class ConnectionTypes(Enum):

"""

CLASS_JDBC_DRIVERS = """

class ConnectionTypeDrivers:

"""

CONNECTION_ENUM_FRAGMENT=""
CONNECTION_JDBC_DRIVER_FRAGMENT=""

for connection_type_code,jdbcdriver in connection_type_codes.items():
    CONNECTION_ENUM_FRAGMENT+= "    " \
        + treat_special_type(connection_type_code) + \
            " = " + "\"" + connection_type_code + "\"" + "\r\n"

    CONNECTION_JDBC_DRIVER_FRAGMENT += "    " + \
        treat_special_type(connection_type_code) \
            + " = " + "\"" + jdbcdriver + "\"" + "\r\n"

code = CLASS_FRAGMENT_ENUM + CONNECTION_ENUM_FRAGMENT

code += "\n\n"

code += CLASS_JDBC_DRIVERS + "\n" + CONNECTION_JDBC_DRIVER_FRAGMENT

print ("Creating connection types Python code @ " + path_to_generate_code)

code_path = os.path.join(path_to_generate_code,CON_TYPE_FILE_NAME)
conn_type_code_file = open(code_path,"w",encoding="utf-8")
conn_type_code_file.write(code)
conn_type_code_file.close()

print ("Connection types ready " + code_path)
