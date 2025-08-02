'''
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

Provides Client access and operations for Dataflow API in Data Transforms
'''

import logging

from enum import Enum

from datatransforms.client import DataTransformsClient,DataTransformsException

#pylint: disable=invalid-name
class DataFlowEnpoints(Enum):
    """List of runtime endpoints (without base URL) for REST API calls
    """
    GET_JOBS_STATUS="/v1/jobs/light"
    RUN_DATA_FLOW="/v1/jobs/mapping/run"

class DataFlowClient(DataTransformsClient):
    """REST Client for dataflow endpoint(s) in  Data Transforms instance.
    This include - validating the dataflow, simulate the code generation etc.,
    """

    def validate(self,project_name,dataflow_name):
        """Validates the given dataflow
        Raises DataTransformException - if project_name or dataflow_name doesn't exist
        """
        project_id=self.check_if_project_exists(project_name)
        df_exists,df_id=self.client.check_if_df_exists(project_id,dataflow_name)
        if df_exists:
            result = self.validate_dataflow_by_id(df_id)
            #print(result.text)
            return result

        raise DataTransformsException("Invalid dataflow " +dataflow_name)

    # my code
    def simulate(self,project_name,dataflow_name):
        """Simulate the generated SQL code on an existing dataflow.
        Returns SQL/Generated code based on the dataflow defintion
        Raises DataTransformsException if either project or dataflow is invalid
        """
        project_id=self.check_if_project_exists(project_name)
        df_exists,df_id=self.client.check_if_df_exists(project_id,dataflow_name)
        if df_exists:
            result = self.client.simulate_show_sql_dataflow_by_id(df_id)
            return result
        raise DataTransformsException("Invalid dataflow " +dataflow_name)

    def validate_dataflow_by_id(self, dataflow_id):
        """Internal method that performs validate operation on given dataflow id. 
        Returns the validation result if the validation is successful. 
        Raises DataTransformsException otherwise
        """
        validate_dataflow_by_id_url = self.get_url()+"/v1/mappings/validate/id/"+dataflow_id
        response = self.do_post(
            validate_dataflow_by_id_url,
            headers=self.get_headers(),
            payload_data={})

        if response.status_code == 200:
            logging.info("Validate DataFlow SQL [OK]")
            return response
        else:
            logging.info("Validate DataFlow SQL [KO]")
            raise DataTransformsException(response.status_code + " " + response.text)

    def simulate_show_sql_dataflow_by_id(self, dataflow_id):
        """Internal method Simlates the generated SQL code on given dataflow ID
        Returns the result if the simulate operation is successful, 
        Raises DataTransformsException otherwise
        """
        simulate_ep = self.get_url() + "/v1/mappings/id/"+dataflow_id+"/simulate"
        response = self.do_post(
            simulate_ep,
            headers=self.get_headers(),
            payload_data={})
        simulate_dict={}

        if response.status_code == 200:
            logging.info("Simulate DataFlow SQL [OK]")
            json_doc = response.json()
            tasks=json_doc["steps"][0]["tasks"]
            for task in tasks:
                taskName = task["taskName"]
                targetDataServer = task["target"]["targetDataServer"]
                targetSchema = task["target"]["targetSchema"]
                targetTechnology = task["target"]["targetTechnology"]
                targetCommand = task["target"]["targetCommand"]
                key="/*" + taskName + "[" + targetDataServer +" -> " + targetSchema + " ] " + \
                "[ " + targetTechnology + " ] */"
                simulate_dict[key]=targetCommand
            return simulate_dict
        else:
            logging.info("Simulate DataFlow SQL [KO]")
            raise DataTransformsException(response.status_code + " " + response.text)
