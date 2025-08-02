"""
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

Workbench is where developers implement data transformation pipelines, data loads, workflows ,
organise them in projects etc., 

Workbench is identified by its name and the working directory (file system where the code 
is maintained) under the workbench, deployment configurations, projects are maintained. 

Provides utilities for preparing workbench in a given directory. 
"""

import logging
import os

class LocalWorkbench:
    """
    Contains utility methods to create a workbench - dedicated work area
    for the python scripts organised in respective folders. 
    """

    __CONNECTIONS_DIR_NAME="Connections"
    __DATA_ENTITIES_DIR_NAME="DataEntities"
    __PROJECTS_DIR_NAME="Projects"
    __SCHEDULES_DIR_NAME="Schedules"

    def __init__(self,base_directory):
        self.workbench_name=""
        self.pwd(base_directory)

    def pwd(self,base_directory):
        """
        Updates the present working directory
        """
        self.pwd_root=base_directory

    def prepare_workbench(self,workbench_name):
        """
        Creates necessary directories and config files required for workbench.
        """
        logging.info("Preparing workbench")
        wb_dir = os.path.join(self.pwd_root,workbench_name)
        if not os.path.isdir(wb_dir):
            raise EnvironmentError("DataTransformsWorkbench invalid workbench name. \
                Must be a valid directory" + wb_dir)

        workbench_dir = os.path.join(self.pwd_root, workbench_name)
        self.workbench_name=workbench_name

        connections = os.path.join(workbench_dir,LocalWorkbench.__CONNECTIONS_DIR_NAME)
        data_entities=os.path.join(workbench_dir,LocalWorkbench.__DATA_ENTITIES_DIR_NAME)
        projects_dir_name=os.path.join(workbench_dir,LocalWorkbench.__PROJECTS_DIR_NAME)

        os.makedirs(workbench_dir)
        os.makedirs(connections)
        os.makedirs(data_entities)
        os.makedirs(projects_dir_name)

        logging.info("Workbech ready")

    # def __prepare_workbench_config(self,workbench_name,workbench_dir):

    #     config_file_name=workbench_name+".config"
    #     workbench_config = {
    #         "XFORMS_ENV":"DEFAULT",
    #         "XFORMS_IP":"<ip-address>",
    #         "XFORMS_USER":"<user>",
    #         "XFORMS_PWD" : "<pwd>"}


    def prepare_project(self,project_name):
        """
        Utlity method to initialise the project directory.
        This will create and organise set of directories for the scripts
        """
        workbench_dir = os.path.join(self.pwd_root, self.workbench_name)

        projects_dir_name=os.path.join(workbench_dir,LocalWorkbench.__PROJECTS_DIR_NAME)

        project_base_dir = os.path.join(projects_dir_name,project_name)
        data_load_dir =os.path.join(project_base_dir,"DataLoads")
        data_flow_dir =os.path.join(project_base_dir,"DataFlows")
        data_workflow_dir =os.path.join(project_base_dir,"Workflows")
        data_scheduel_dir =os.path.join(project_base_dir,"Schedules")

        os.makedirs(project_base_dir)
        os.makedirs(data_load_dir)
        os.makedirs(data_flow_dir)
        os.makedirs(data_workflow_dir)
        os.makedirs(data_scheduel_dir)

        logging.info("Project ready")
