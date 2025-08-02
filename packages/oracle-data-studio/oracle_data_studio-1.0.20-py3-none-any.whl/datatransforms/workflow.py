'''
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

APIs for create/change workflow definition in data transforms. 
'''
import uuid
import json
import logging
from enum import Enum

from datatransforms.client import DataTransformsClient,DataTransformsException

from datatransforms.variables import VariableTypes

class WorkflowException(Exception):
    """
    Exception class for workflow operations. 
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class Workflow:
    """
    Enables creation of workflow definition, the workflow defintion is composed of 
    workflow name, project and one ore more execution steps. 
    The execution steps are defined based on its type, Refer WorkflowStep for details.
    """
    def __init__(self,name,project,folder="DefaultFolder"):
        self.name=name
        self.project=project
        self.folder=folder
        self.steps=[]

    def add_execution_steps(self,workflow_steps):
        """
        Add the execution steps to the workflow. 
        """
        self.steps=workflow_steps
        return self

    def executeion_steps(self):
        """
        Returns execution steps from the workflow definition
        """
        return self.steps

    def print_execution_order(self):
        """
        Utility method to visualise the execution order of the workflow.
        Every line of the execution order gives the next step on success and failure 
        Sucess is represented as OK step= and failure is represented as fail KO
        """
        for step in self.steps:
            print ("Step Name=" + step.name + ",start=" + str(step.isFirstStep) +
                    ",OK step=" + step.nextStepAfterSuccess 
                    + " , fail KO=" + step.nextStepAfterFailure)

    def __resolve_ids(self):
        """Internal method to resolve global IDs for the depedant objects in datatransforms.
        Not intended for SDK users. 
        For Internal - 
            Resolves the project ID, through get_all_projects API call, if the project is 
            not found, a new project is created

            Resolves the dataflow, dataload, connection, variable IDs for execution steps.
            WorkflowException is thrown if the given artifact is not found
        """
        client = DataTransformsClient()
        client.load_cache()

        if self.project not in client.projects:
            logging.debug(
                "Project not found, creating one %s",self.project)
            project_code=self.project.replace(" ","").upper()
            client.create_project(name=self.project,code=project_code)
            client.get_all_projects()

        project_id=client.projects[self.project]

        mappings =  client.get_all_dataflows_from_project(project_id)
        dataloads = client.get_all_dataloads_from_project(project_id)

        connections = client.get_all_connections()

        variables,variable_metata = client.get_all_variables(project_id)
        variables_type_dict ={}
        for entry in variable_metata:
            variables_type_dict[entry["variableName"]] = entry["variableType"]

        for step in self.steps:
            if isinstance(step,DataFlowStep):
                if step.mappingName not in mappings:
                    raise WorkflowException(f" Data flow {step.mappingName} could not be resolved ")
                step.mappingGlobalId=mappings[step.mappingName]

            if isinstance(step,SqlStep):
                if step.dataServerName not in connections:
                    raise WorkflowException(f" Connection {step.dataServerName} \
                                            could not be resolved ")

                step.dataServerGlobalId=connections[step.dataServerName]
            if isinstance(step,DataLoadStep):
                if step.bulkLoadName not in dataloads:
                    raise WorkflowException(f" Data load {step.bulkLoadName} \
                                            could not be resolved ")

                step.bulkLoadGlobalId=dataloads[step.bulkLoadName]

            if isinstance(step,VariableStep):
                if step.variableName not in variables:
                    raise WorkflowException (f" Variable {step.variableName} could not be resolved")
                step.variableGlobalId=variables[step.variableName]
                step.variableProject=self.project
                step.variableType=variables_type_dict[step.variableName]

                if isinstance(step,SetVariableStep):
                    varprops=step.setVariableProperties
                    existing_value = varprops["staticValue"]
                    existing_increment = varprops["incrementValue"]

                    if step.variableType == VariableTypes.NUMERIC.value:
                        if existing_value is not None:
                            varprops["staticValue"]=int(existing_value)
                        if existing_increment is not None:
                            varprops["incrementValue"]=int(existing_increment)

                    elif step.variableType in [VariableTypes.SHORT_TEXT.value,
                                               VariableTypes.LONG_TEXT.value]:
                        if existing_value is not None:
                            varprops["staticValue"]=str(existing_value)
                        #increment is not possible for text, hence making explicit
                        if varprops["incrementValue"] is not None:
                            raise DataTransformsException(f"Variable {step.variableName} of type \
                                                          {step.variableType} \
                                                            can't have increment value")
                    step.setVariableProperties=varprops

                if isinstance(step,EvaluateVariableStep):
                    varprops=step.evaluateVariableProperties
                    existing_value = varprops["evaluateValue"]

                    if step.variableType == VariableTypes.NUMERIC.value:
                        if existing_value is not None:
                            varprops["evaluateValue"]=int(existing_value)
                    elif step.variableType in [VariableTypes.SHORT_TEXT,VariableTypes.LONG_TEXT]:
                        if existing_value is not None:
                            varprops["evaluateValue"]=str(existing_value)
                    step.evaluateVariableProperties=varprops

    def create(self):
        #pylint: disable=C0103:invalid-name
        #some of the member variables are aligned with JSON payload definitions of datatransforms
        """Creates workflow in datatransforms. 
        If the workflow already exists, Update (REST PUT) operation is performed
        otherwise create (REST POST) operation is performed
        """
        self.__resolve_ids()
        wfp = WorkflowPayload(self)
        client = DataTransformsClient()
        project_id=client.projects[self.project]
        exists,globalID=client.check_if_workflow_exists(project_id,self.name)
        if exists:
            wfp.globalId=globalID
            #print(wfp.__dict__)
            workflow_json_payload=json.dumps(wfp,default=lambda o: o.__dict__)
            #print(workflow_json_payload)
            client.update_workflow_from_json_payload(workflow_json_payload)
        else:
            workflow_json_payload=json.dumps(wfp,default=lambda o: o.__dict__)
            #print(workflow_json_payload)
            client.create_workflow_from_json_payload(workflow_json_payload)

#This class confirms to JSON payload and requirements of workstep
# pylint: disable=too-many-instance-attributes
class WorkflowStep:
    """
    Enables creation of workflow step for the workflow. 
    Workflow step execution has contracts for further execution on success
    and failure. 
    """
    # pylint: disable=invalid-name
    def __init__(self,name,stepType):
        self.name=name
        self.stepType=stepType
        self.stepGlobalId=str(uuid.uuid1())
        self.nextStepAfterSuccess=""
        self.nextStepAfterFailure=""
        self.isFirstStep=False
        self.failureRetryNumber=3
        self.failureRetryDelay=30
        self.logLevel= "ALWAYS"

    def __on_success(self,next_step):
        if not issubclass(type(next_step),WorkflowStep):
            raise WorkflowException("Step must be of type WorkflowStep")
        self.nextStepAfterSuccess=next_step.name
        return next_step

    def __on_failure(self,next_step):
        if not issubclass(type(next_step),WorkflowStep) :
            raise WorkflowException("Step must be of type WorkflowStep")
        self.nextStepAfterFailure=next_step.name
        return next_step

    def __on_anyways(self,next_step):
        self.__on_success(next_step)
        self.__on_failure(next_step)
        return next_step

    def ok(self,other):
        """API to add the next step on success
        """
        return self.__on_success(other)

    def nok(self,other):
        """API to add the next step on failure
        """
        return self.__on_failure(other)

    def oknok(self,other):
        """API to proceed with next step once the execution is complete.
        """
        return self.__on_anyways(other)

    def __or__(self, other):
        """Transition to next step upcon completion of the step. 

        .. code-block:: python

        #To Transition to step B after completing step A, 
        # irrespective of the result (succes or failure)

        stepA | step B

        Arguments:
            other -- _description_

        Returns:
            _description_
        """
        return self.__on_anyways(other)

    def __rshift__(self,other):
        return self.__on_success(other)

    def __gt__(self,other):
        return self.__on_failure(other)

    def first_step(self,is_start):
        """API to indicate the first step of the workflow
        """
        self.isFirstStep=is_start

class DataFlowStep(WorkflowStep):
    # pylint: disable=invalid-name,too-many-arguments
    # Pylint disabled for naming convention - as this class represents JSON
    #payload fields
    """Represents the dataflow step of a workflow
    """
    def __init__(self,name,
                 data_flow_name,
                 data_flow_project,
                 data_flow_folder="DefaultFolder",
                 firstStep=False):
        super().__init__(name,"StepMapping")
        self.synchronous=True
        self.mappingName=data_flow_name
        self.mappingProject=data_flow_project
        self.mappingFolder=data_flow_folder
        self.mappingGlobalId=""
        super().first_step(firstStep)

class CommandStep(WorkflowStep):
    # pylint: disable=invalid-name,too-many-arguments
    # Pylint disabled for naming convention - as this class represents JSON payload fields
    """Represents the command step of a workflow
    """
    def __init__(self,name,command_name,parameters,firstStep=False):
        super().__init__(name,stepType="StepOdiCommand")
        self.commandName=command_name
        self.parameters=parameters
        super().first_step(firstStep)

class Sleep(CommandStep):
    # pylint: disable=invalid-name,too-many-arguments
    # Pylint disabled for naming convention - as this class represents JSON payload fields
    """Represents the sleep step of a workflow
    """
    def __init__(self,name,delay=1000,firstStep=False):
        super().__init__(name,command_name="OdiSleep",parameters={"-DELAY":"\""+str(delay)+"\""})
        super().first_step(firstStep)

class SqlStep(WorkflowStep):
    # pylint: disable=invalid-name,too-many-arguments
    # Pylint disabled for naming convention - as this class represents JSON payload fields
    """Represents the sqlstep step of a workflow
    """
    def __init__(self,name,connection_name,sql_text,firstStep=False):
        super().__init__(name,stepType="StepSql")
        self.dataServerName=connection_name
        self.dataServerGlobalId=""
        self.sqlText=sql_text
        self.synchronous=True
        super().first_step(firstStep)

class DataLoadStep(WorkflowStep):
    # pylint: disable=invalid-name,too-many-arguments
    # Pylint disabled for naming convention - as this class represents JSON payload fields
    """Represents the dataload step of a workflow
    """
    def __init__(self,name,dataload_name,firstStep=False):
        super().__init__(name,"StepBulkLoad")
        self.bulkLoadGlobalId=""
        self.bulkLoadName=dataload_name
        super().first_step(firstStep)

class VariableStepLogLevel(Enum):
    """Enumeration for variable step
    """
    ALWAYS="ALWAYS"

class VariableStepActions(Enum):
    """Enumeration for variable step actions
    """
    #pylint: disable=C0103:invalid-name
    #Enums aligned with Datatransforms usage
    RefreshVariable="RefreshVariable"
    SetVariable="SetVariable"
    EvaluateVariable="EvaluateVariable"

class VariableStep(WorkflowStep):
    """Enumeration for variable step
    """
    # pylint: disable=invalid-name,too-many-arguments
    def __init__(self,step_name,variable_name,first_step=False):
        super().__init__(step_name,"StepVariable")
        self.variableName=variable_name
        self.variableGlobalId=None
        self.variableProject=None
        self.setVariableProperties=None
        self.logLevel=VariableStepLogLevel.ALWAYS.value
        self.evaluateVariableProperties=None
        self.variableType=None
        self.failure_retry_options(3,30)
        self.action=None
        super().first_step(first_step)

    def log_level(self,step_log_level):
        """Enable provide log levels
        """
        if isinstance(step_log_level,VariableStepLogLevel):
            self.logLevel=step_log_level.value
        elif isinstance(step_log_level,str):
            self.logLevel=step_log_level
        else:
            raise DataTransformsException(
                "invalid log_level, must be valid log level as str or VariableStepLogLevel")

    def project(self,project_name):
        """Project name for variable
        """
        self.variableProject=project_name

    def failure_retry_options(self,no_of_attempts,attempt_interval):
        """API to set failure retry options"""
        self.failureRetryNumber=no_of_attempts
        self.failureRetryDelay=attempt_interval

    def variable_action(self,action_type):
        """Action type of variable"""
        self.action=action_type

    def set_variable(self,setVariableProperties):
        """Update set variable properties"""
        self.setVariableProperties=setVariableProperties

    def eval_properties(self,evaluateVariableProperties):
        """Update evaluate variable properties"""
        self.evaluateVariableProperties=evaluateVariableProperties

class RefreshVariableStep(VariableStep):
    """Represents Variable refresh step"""
    def __init__(self,step_name,variable_name,first_step=False):
        super().__init__(step_name,variable_name,first_step)
        super(RefreshVariableStep,self).variable_action(
            VariableStepActions.RefreshVariable.value)


class SetVariableStep(VariableStep):
    # pylint: disable=invalid-name,too-many-arguments
    """Class that represents variable set operation"""
    ASSIGN="="
    INCREMENT = "++"
    SPACE = " "

    def __init__(self,step_name,variable_expression,first_step=False):

        if SetVariableStep.SPACE not in variable_expression \
            or len(variable_expression.split(SetVariableStep.SPACE)) != 3:

            variable_expression_syntax = "<variable_name><space><action><space><value>. \
                where action is = for assign and ++ for increment"
            logging.error("Variable {step_name} has incorrect \
                          variable expression {variable_expression} \
                          \n Expected {variable_expression_syntax}".format_map(locals))
            raise DataTransformsException("Invalid SetVariable expresssion. \
                                          Expected "+variable_expression_syntax)

        expression_tokens = variable_expression.split(SetVariableStep.SPACE)
        #example: <variable> = <value> or <variable> ++ <value>
        variable_name=expression_tokens[0]
        variable_action=expression_tokens[1]
        variable_value=expression_tokens[2]

        if variable_action not in [SetVariableStep.ASSIGN, SetVariableStep.INCREMENT]:
            raise DataTransformsException("Invalid variable expression {variable_expression}, \
                                          expression must be assign using = or increment using ++"
                                          .format_map(locals()))

        super().__init__(step_name,variable_name,first_step)

        setVariableProperties={}
        if variable_action == SetVariableStep.ASSIGN:
            setVariableProperties["staticValue"]=variable_value
            setVariableProperties["incrementValue"]=None
        elif variable_action == SetVariableStep.INCREMENT:
            setVariableProperties["staticValue"]=None
            setVariableProperties["incrementValue"]=variable_value
        else:
            raise DataTransformsException(
                "Invalid variable action, expression must be assign using = or increment using ++")
        super(SetVariableStep,self).set_variable(setVariableProperties)

        super(SetVariableStep,self).variable_action(VariableStepActions.SetVariable.value)

class EvaluateVariableStep(VariableStep):
    # pylint: disable=invalid-name,too-many-arguments
    """Class that represents the Evaluate Variable step of a workflow."""

    __supported_eval_operators=['=','<>','>','<','>=','<=','IN']

    def __init__(self,step_name,variable_eval_expression,first_step=False):
        """step_name - Name of the step, unique across the workflow
        
        variable_eval_expression - Valid variable expression, must follow the convention
            <variable_name><space><eval_operator><space><value>
            where variable_name is existing variable created in data transforms
            
        eval_operator is one of   '=','<>','>','<','>=','<=','IN'

        """
        if SetVariableStep.SPACE not in variable_eval_expression or \
            len(variable_eval_expression.split(SetVariableStep.SPACE)) != 3:
            variable_expression_syntax = "<variable_name><space><action><space><value>. \
                where action is = for assign and ++ for increment"
            logging.error("Variable {step_name} has incorrect variable \
                          expression {variable_eval_expression} \n \
                          Expected {variable_expression_syntax}"
                    .format_map(locals()))
            raise DataTransformsException("Invalid SetVariable expresssion. \
                                          Expected "+variable_expression_syntax)


        expression_tokens = variable_eval_expression.split(SetVariableStep.SPACE)
        #example: <variable> = <value> or <variable> ++ <value>
        variable_name=expression_tokens[0]
        eval_action=expression_tokens[1]
        variable_value=expression_tokens[2]

        if eval_action not in EvaluateVariableStep.__supported_eval_operators:
            raise DataTransformsException("Invalid expression evaluation, must be one of  "
                                          + str(EvaluateVariableStep.__supported_eval_operators))

        super().__init__(step_name,variable_name,first_step)

        evaluateVariableProperties={}
        evaluateVariableProperties["evaluateValue"]=variable_value
        evaluateVariableProperties["operator"]=eval_action

        super(EvaluateVariableStep,self).eval_properties(evaluateVariableProperties)
        super(EvaluateVariableStep,self).variable_action(
            VariableStepActions.EvaluateVariable.value)

#pylint: disable=R0903:too-few-public-methods
class VariableStepFactory:
    """Factory class that enables variable step creation through create_variable_step function
    """
    @staticmethod
    def create_variable_step(step_action,step_name,variable_expression,first_step=False):
        """
        Function to create instance of variable step in a workflow. 
        based on the parameter step_action, step instance is created.
        Exception is thrown if the step_action is not available under VariableStepActions Enum
        step_action - must be one of VariableStepActions enum, 
        step_name- Name of the workflow step. Must be unique across workflow,
        variable_expression 
            - for refresh action step, it must be just a variable
            - for update/increment it must be <variable><space><operator><space><value>
                where operator is ++ for increment and = for assign/update
            - for evaluate step it must be <variable><space><eval_operator><space><value>
                where eval_operator is one of '=','<>','>','<','>=','<=','IN'
        """

        step_action = step_action.value if isinstance(
            step_action,VariableStepActions) else step_action
        if step_action == VariableStepActions.SetVariable.value:
            set_variable = SetVariableStep(step_name,variable_expression,first_step)
            return set_variable
        elif step_action == VariableStepActions.RefreshVariable.value:
            refresh_variable = RefreshVariableStep(step_name,variable_expression,first_step)
            return refresh_variable
        elif step_action == VariableStepActions.EvaluateVariable.value:
            evaluate_variable= EvaluateVariableStep(step_name,variable_expression,first_step)
            return evaluate_variable
        else:
            raise DataTransformsException(
                "Invalid action {step_action} for workflow step".format_map(locals()))

#-------------------------------------------------
#payload abstractions
#-------------------------------------------------

class WorkflowPayload:
    # pylint: disable=invalid-name,too-few-public-methods
    """Class that represents Workflow JSON payload for datatransforms"""

    # pylint: disable=invalid-name,too-many-arguments
    def __init__(self,workflow_obj):
        self.name=workflow_obj.name
        self.projectCode=workflow_obj.project.replace(" ","").upper()
        self.parentFolder=workflow_obj.folder
        self.globalId=str(uuid.uuid1())
        steps =workflow_obj.executeion_steps()
        self.mappingSteps=self.filter_step_types(steps,DataFlowStep)
        self.odiCommandSteps=self.filter_step_types(steps,Sleep)
        self.sqlSteps=self.filter_step_types(steps,SqlStep)
        self.bulkLoadSteps=self.filter_step_types(steps,DataLoadStep)
        self.variableSteps=self.filter_step_types(steps,VariableStep)


    def filter_step_types(self,workflow_steps,stepclass):
        """Filters only the workflow step(s) of given step class
        """
        filtered_steps=[]
        for step in workflow_steps:
            if isinstance(step,stepclass):
                filtered_steps.append(step)
        return filtered_steps
