'''
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

Houses APIs for creating, managing schedules in data transforms.
'''


from datetime import datetime,timedelta
import json
import logging

from datatransforms.client import DataTransformsClient


TIME_FORMAT_STR ='%Y-%m-%dT%H:%M:%S'

SCHEDULE_RESOURCE_TYPE_WORKFLOW="oracle.odi.domain.project.OdiPackage"
SCHEDULE_RESOURCE_TYPE_DATAFLOW="oracle.odi.domain.mapping.Mapping"
SCHEDULE_STATUS_ACTIVE = "ACTIVE"
SCHEDULE_STATUS_INACTIVE = "INACTIVE"

class WeeklySchedule:
    # pylint: disable=invalid-name,too-few-public-methods
    """Constants that create developer friendly version of string values used in schedule"""

    DAYS_ALL="MONDAY,TUESDAY,WEDNESDAY,THURSDAY,FRIDAY,SATURDAY,SUNDAY"
    DAYS_WEEKDAY="MONDAY,TUESDAY,WEDNESDAY,THURSDAY,FRIDAY"
    DAYS_WEEKENDS="SATURDAY,SUNDAY"
    MONDAY="MONDAY"
    TUESDAY="TUESDAY"
    WEDNESDAY="WEDNESDAY"
    THURSDAY="THURSDAY"
    FRIDAY="FRIDAY"
    SATURDAY="SATURDAY"
    SUNDAY="SUNDAY"

class MonthlyDayOfMonthSchedule:
    # pylint: disable=invalid-name,too-few-public-methods
    """Constants that create developer friendly version of string values used in schedule"""

    LAST_DAY_OF_MONTH="LAST_DAY_OF_MONTH"
    THE_DAY_BEFORE_THE_END_OF_MONTH="THE_DAY_BEFORE_THE_END_OF_MONTH"

    FIRST = "FIRST"
    SECOND = "SECOND"
    THIRD = "THIRD"
    FOURTH = "FOURTH"
    LAST = "LAST"
    SECOND_LAST="SECOND_LAST"
    THIRD_LAST="THIRD_LAST"

class ScheduleException(Exception):
    """Exception for schedule API"""
    def __init__(self, *args):
        super().__init__(*args)

class Schedule:
    #pylint disabled as it represents the JSON attributes required for schedules
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes

    #pylint: disable=attribute-defined-outside-init
    #recurrence field can exist in JSON only incase of recurring schedule
    # , hence it is initialised on demand
    """API to schedule data transforms resources. Dataflow or Workflow
    All the schedules created are by default in INACTIVE State, unless explicitly activated by API
    """
    def __init__(self,name):
        self.name=name
        self.logicalAgentName="OracleDIAgent1"
        self.status="INACTIVE"
        self.activeFromDate= ""
        self.activeEndDate= ""
        self.dailyActivationTimeRange= ""
        self.excludeMonthDays= ""
        self.excludeWeekDays= ""
        self.resource=None
        self.designObjectType=None
        self.scenario={}
        self.repetition="None"
        self.project=None


    def workflow(self,project,workflow_name):
        """Adds the given workflow for the schedule

        Arguments:
            project -- Name of the project 
            workflow_name -- name of the workflow to be scheduled

        Raises:
            ScheduleException: When schedule has more than one artifact 

        Returns:
            current object
        """
        if self.designObjectType is not None:
            raise ScheduleException('Only one resource allowed to '
            'schedule, either workflow or dataflow.')

        self.designObjectType=SCHEDULE_RESOURCE_TYPE_WORKFLOW
        self.scenario["designObjectType"]=SCHEDULE_RESOURCE_TYPE_WORKFLOW
        self.resource=workflow_name
        self.project=project
        return self

    def dataflow(self,project,dataflow_name):
        """Adds the given dataflow to schedule event

        Arguments:
            project -- name of the project
            dataflow_name -- name of the dataflow

        Raises:
            ScheduleException: When the schedule object has been 
            already with another artifact

        Returns:
            current object
        """
        if self.designObjectType is not None:
            raise ScheduleException(
                'Only one resource allowed to schedule, either workflow or dataflow.')

        self.designObjectType=SCHEDULE_RESOURCE_TYPE_DATAFLOW
        self.scenario["designObjectType"]=SCHEDULE_RESOURCE_TYPE_DATAFLOW
        self.resource=dataflow_name
        self.project=project
        return self

    def at(self,time):
        """Crates a schedule at given time 
        

        Arguments:
            time -- Time should be of the format YYYY-MM-DDTHH:MM:SS

        Returns:
            current object
        """
        self.recurrence="SIMPLE "+time
        self.repetition="None"
        return self

    def immediate(self,asap_delta=None):

        """Schedules the resource in next 1 minute to customize pass timedelta 
        with desired option as asap_delta

        Returns:
            current object
        """
        logging.debug("Creating immediate schedule for %s" , self.resource)
        immediate_schedule=timedelta(minutes=1) if asap_delta is None else asap_delta
        new_schedule=self.prepare_schedule(immediate_schedule)
        return self.at(new_schedule)

    def hourly(self,hour,minute):
        """Creates an hourly sechedule

        Arguments:
            hour -- at which schedule must be trigerred
            minute -- at which schedule must be trigerred

        Returns:
            current object
        """
        self.recurrence="HOURLY " + f"{hour:02d}" + ":" + f"{minute:02d}"
        return self

    def daily(self,hour,minute,second=00):
        """Create a daily schedule

        Arguments:
            hour -- at which schedule must be trigerred
            minute -- at which schedule must be trigerred
            second -- of schedule expiry, it must be two digit string.  default: 00
            (Eg 01,09 up to 59)

        Returns:
            current object
        """

        self.recurrence="DAILY T" + f"{hour:02d}" + ":" + f"{minute:02d}" +":"+f"{second:02d}"
        return self

    #pylint: disable=unused-argument,possibly-unused-variable
    def weekly(self,days,hh_mm_time):
        """Create a weekly schedule

        Arguments:
            days -- week day
            hh_mm_time -- time of schedule, in hh_mm format.

        Raises:
            ScheduleException: when the system could not create the schedule.

        Returns:
            _description_
        """
        if days is None or len(days) <1:
            raise ScheduleException("Min one day must be provided for schedule")

        day_string=",".join(days)
        self.recurrence= "WEEKLY {day_string} T{hh_mm_time}".format_map(locals())
        return self

    def monthly(self,monthly_date,hh_mm_ss_time):
        """Creates monthly schedule

        Arguments:
            monthly_date -- date at which schedule must be triggerred 
            hh_mm_ss_time -- time of schedule, hh_mm_ss formatted

        Returns:
            current object
        """
        self.recurrence= "MONTHLY {monthly_date} T{hh_mm_ss_time}".format_map(locals())
        return self

    def monthly_by_weekday(self,monthly_date,week_day,hh_mm_ss_time):
        """Creates a monthly schedule that gets executed on given weekday

        Arguments:
            monthly_date -- at which schedule must run
            week_day -- at which schedule must run
            hh_mm_ss_time -- time in hh_mm_ss format 

        Returns:
            current object
        """
        #pylint: disable=line-too-long
        self.recurrence= "MONTHLY_BY_WEEK_DAY {monthly_date} {week_day} T{hh_mm_ss_time}".format_map(locals())
        return self

    def yearly(self,month,date,hh_mm_ss_time):
        """Creates an yearly schedule

        Arguments:
            month -- of schedule 
            date -- of schedule
            hh_mm_ss_time -- time of schedule in hh_mm_ss format

        Returns:
            _description_
        """
        self.recurrence="YEARLY {month} {date} T{hh_mm_ss_time}".format_map(locals())
        return self

    def frequency(self,frequency,schedule_string):
        """Adds frequency to the schedule

        Arguments:
            frequency -- of the schedule 
            schedule_string -- of the schedule

        Returns:
            current object
        """
        self.recurrence="{frequency} {schedule_string}".format_map(locals())
        return self

    def schedule_status(self,status="INACTIVE"):
        """Activates the schedule. Default is INACTIVE

        Keyword Arguments:
            status -- (default: {"INACTIVE"}), possible values ACTIVE|INACTIVE

        Returns:
            current object
        """
        self.status=status
        return self

    def noOfAttemptsAfterFailures(self,attempts):
        """Number of retry attempts to be done for failures

        Arguments:
            attempts -- number of attempts incase of failure

        Returns:
            current object
        """
        self.numberOfAttemptsAfterFailures=attempts
        return self

    def execution_timeout(self,timeout):
        """Adds execution timeout for a schedule. 

        Arguments:
            timeout -- for the schedule job

        Returns:
            current object
        """
        self.maxDuration=timeout
        return self


    def prepare_schedule(self,delta):
        """Prepares the new schedule based on the time delta with repository time"""        
        if isinstance(delta,timedelta):
            client =DataTransformsClient()
            work_bench_time = client.get_current_time_from_deployment()
            work_bench_time_iso = datetime.fromisoformat(work_bench_time)
            new_schedule =work_bench_time_iso+delta
            str_time= new_schedule.strftime(TIME_FORMAT_STR)
            return str_time
        else:
            raise ScheduleException("Preparing schedule must have 'timedelta' instance ")

    def create(self):
        """ Method to create schedule, 
        if the schedule already exists with given name, update will be performed"""
        logging.debug("Creating schedule %s ",self.name)


        if self.resource is None:
            raise ScheduleException(
                "Invalid resource to schedule. Schedule must have valid datalfow or workflow")

        client =DataTransformsClient()
        is_exists,schedule_global_id = client.check_if_schedule_exists(self.name)

        logging.debug("Resolving project")
        projects = client.get_all_projects()
        if self.project not in projects.keys():
            raise ScheduleException(
                "Invalid resource to schedule, project {self.project} not found")

        project_gloabl_id = projects[self.project]
        if self.designObjectType == SCHEDULE_RESOURCE_TYPE_DATAFLOW:
            dataflows = client.get_all_dataflows_from_project(project_gloabl_id)
            if self.resource not in dataflows.keys():
                raise ScheduleException(
                    "Invalid resource to schedule, dataflow {self.resource} not found")
            #name will be swapped with globalID
            self.resource=dataflows[self.resource]
            self.scenario["designObjectType"]=self.designObjectType
            self.scenario["designObjectGlobalId"]=self.resource

        elif self.designObjectType == SCHEDULE_RESOURCE_TYPE_WORKFLOW:
            workflows = client.get_all_workflows_from_project(project_gloabl_id)
            if self.resource not in workflows.keys():
                raise ScheduleException(
                    "Invalid resource to schedule,workflow {self.resource} not found ")
             #name will be swapped with globalID
            self.resource=workflows[self.resource]
            self.scenario["designObjectType"]=self.designObjectType
            self.scenario["designObjectGlobalId"]=self.resource

        else:
            raise ScheduleException(
                "Unknown resource to schedule, Resource must be either dataflow or workflow")

        del self.designObjectType
        del self.project
        del self.resource
        if is_exists:
            self.globalId = schedule_global_id

        schedule_payload=json.dumps(self,default=lambda o: o.__dict__)
        client.create_schedule(schedule_payload,is_exists)
