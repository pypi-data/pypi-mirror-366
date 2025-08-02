'''
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

Provides Client access and operations for runtime artifacts in Data Transforms'''

import logging
import json 
from enum import Enum

from datatransforms.client import DataTransformsClient,DataTransformsException


class RuntimeEnpoints(Enum):
    """List of runtime endpoints (without base URL) for REST API calls
    """
    GET_JOBS_STATUS="/v1/jobs/light"
    RUN_DATA_FLOW="/v1/jobs/mapping/run"
    RUN_DATA_LOAD="/v1/jobs/bulkload/run"
    RUN_WORKFLOW="/v1/jobs/package/run"

class RuntimeClient(DataTransformsClient):
    """REST Client for runtime operations on Data Transforms instance.
    This include - starting execution of dataflow, workflow , getting the jobs 
    and their status. 
    """
    def get_all_jobs_by_status(self,status=None):
        """Returns all the jobs by Status.
        """
        logging.debug("Fetch jobs by status %s", status)
        url = self.get_url()
        resolved_ep = url + RuntimeEnpoints.GET_JOBS_STATUS.value
        job_status_payload = {
                                "fromDate": "",
                                "toDate": "",
                                "timeZone": "UTC",
                                "showQueuedJobs": False
                            }
        response = self.do_post(resolved_ep,
            headers=self.get_headers(),
            payload_data=json.dumps(job_status_payload))

        if response.status_code != 200:
            logging.error("Failed to get all jobs %s ", str(response.status_code))
            logging.error(response.text)
            raise DataTransformsException("Failed to get all jobs "
                                          + str(response.status_code) +  " " + response.text)
        else:
            json_doc = response.json()
            job_dict={}
            for entry in json_doc:
                job_session=entry["sessionName"]
                job_id=entry["globalId"]
                job_status=entry["status"]
                job_dict[job_session+":"+job_id]=job_status
            return job_dict

    def run_dataflow(self,project_name,datafow_name):
        """Starts execution of the data flow. Returns session ID and status
        if the run operation is accepted. Exception is thrown otherwise. 

        Returns - dictionary with jobsession as key and status of the job as value.
        Jobsession can be used query the status of the session to monitor the job 
        """

        projects = self.get_all_projects()
        if project_name not in projects:
            raise DataTransformsException("Invalid project " + project_name)

        dataflows = self.get_all_dataflows_from_project(projects[project_name])
        if datafow_name not in dataflows:
            raise DataTransformsException("Invalid Dataflow to run " + str(locals()))

        url = self.get_url()
        resolved_ep = url + RuntimeEnpoints.RUN_DATA_FLOW.value
        execute_dataflow_payload = {
                            "objectId": dataflows[datafow_name],
                            "agentName": "OracleDIAgent1"
                        }
        response = self.do_post(resolved_ep,headers=self.get_headers(),
            payload_data=json.dumps(execute_dataflow_payload))

        if response.status_code != 200:
            logging.error("Failed to start dataflow %s", str(response.status_code))
            logging.error(response.text)
            raise DataTransformsException("Failed to get all jobs "
                                          + str(response.status_code) +  " " + response.text)
        else:
            json_doc = response.json()
            job_dict={}
            job_session=json_doc["sessionName"]
            job_id=json_doc["globalId"]
            job_status=json_doc["status"]
            job_dict[job_session+":"+job_id]=job_status
            return job_dict

    def run_dataload(self,project_name,dataload_name):
        """Starts execution of the data flow. Returns session ID and status
        if the run operation is accepted. Exception is thrown otherwise. 

        Returns - dictionary with jobsession as key and status of the job as value.
        Jobsession can be used query the status of the session to monitor the job 
        """

        projects = self.get_all_projects()
        if project_name not in projects:
            raise DataTransformsException("Invalid project " + project_name)

        dataloads = self.get_all_dataloads_from_project(projects[project_name])
        if dataload_name not in dataloads:
            raise DataTransformsException("Invalid DataLoad to run " + str(locals()))

        url = self.get_url()
        resolved_ep = url + RuntimeEnpoints.RUN_DATA_LOAD.value
        execute_dataflow_payload = {
                "objectId":  dataloads[dataload_name],
                "synchronous": False,
                "agentName": "OracleDIAgent1"
            }
        response = self.do_post(resolved_ep,headers=self.get_headers(),
            payload_data=json.dumps(execute_dataflow_payload))

        if response.status_code != 200:
            logging.error("Failed to start dataflow %s", str(response.status_code))
            logging.error(response.text)
            raise DataTransformsException("Failed to get all jobs "
                                          + str(response.status_code) +  " " + response.text)
        else:
            json_doc = response.json()
            logging.debug("Job started ...%s ",  str(json_doc))
            job_dict={}
            job_session=json_doc["enhancedExecutionName"]
            job_id=json_doc["enhancedExecutionId"]
            job_status=json_doc["status"]
            job_dict[job_session+":"+job_id]=job_status
            return job_dict


    def run_workflow(self,project_name,workflow_name):
        """Starts execution of the workflow. Returns session ID and status
        if the run operation is accepted. Exception is thrown otherwise. 

        Returns - dictionary with jobsession as key and status of the job as value.
        Jobsession can be used query the status of the session to monitor the job 
        """

        projects = self.get_all_projects()
        if project_name not in projects:
            raise DataTransformsException("Invalid project " + project_name)

        workflows = self.get_all_workflows_from_project(projects[project_name])
        if workflow_name not in workflows:
            raise DataTransformsException("Invalid workflow to run " + str(locals()))

        url = self.get_url()
        resolved_ep = url + RuntimeEnpoints.RUN_WORKFLOW.value
        execute_dataflow_payload = {
                "objectId":  workflows[workflow_name],
                "agentName": "OracleDIAgent1"
            }
        response = self.do_post(resolved_ep,headers=self.get_headers(),
            payload_data=json.dumps(execute_dataflow_payload))

        if response.status_code != 200:
            logging.error("Failed to start workflow %s", str(response.status_code))
            logging.error(response.text)
            raise DataTransformsException("Failed to start workflow "
                                          + str(response.status_code) +  " " + response.text)
        else:
            json_doc = response.json()
            logging.debug("Job started ...%s ",  str(json_doc))
            job_dict={}
            job_session=json_doc["sessionName"]
            job_id=json_doc["globalId"]
            job_status=json_doc["status"]
            job_dict[job_session+":"+job_id]=job_status
            return job_dict
