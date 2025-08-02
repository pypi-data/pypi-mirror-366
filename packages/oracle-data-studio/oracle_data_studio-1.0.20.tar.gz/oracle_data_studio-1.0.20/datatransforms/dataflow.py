"""Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

APIs for create/change dataflow definition in data transforms. 
"""

import json
import logging
import copy
from enum import Enum

from datatransforms.client import DataTransformsClient

from datatransforms.models import RefDataEntity,SimpleColumnMapping

from datatransforms.payloadutil.dataflow_payload import DataFlowPayload,\
    DataFlowSource,DataStoreAttributes,DataFlowTarget,DataFlowJoin,DataFlowFilter,\
        DataFlowSorter,DataFlowExpression,DataFlowAggregate,DataFlowAggregateAtributes,\
            DataFlowSet,DataFlowSetOperator,DataFlowDataCleanse,\
            DataFlowMLPredict,DataFlowLag

from datatransforms.workbench import DataTransformsWorkbench

#pylint: disable=too-many-lines,invalid-name,line-too-long
#pylint: disable=super-init-not-called
#pylint: disable=attribute-defined-outside-init,consider-using-enumerate

class Project:
    """Model that reprepsetns Data transforms Project"""
    def __init__(self,name,folder,code=None):
        self.name=name
        self.folder=folder
        if code is not None:
            self.code=code.upper()
        else:
            self.code=name.upper()

class Operator:
    """Model that reprepsetns Data transforms Operatior, base for all the operators"""
    name=""
    connected_to=[]
    connected_from=[]
    type_name=""
    def __init__(self,name):
        self.name=name

class SourceDataStore(Operator):
    """Model represents the source data asset in a dataflow"""
    data_entity_name = ""
    def __init__(self,operator_name,data_entity_name,options=None):
        self.data_entity_name=data_entity_name
        self.type_name="SOURCE"
        Operator.__init__(self,operator_name)

class TargetDataStore(Operator):
    """Model represents the target data asset in a dataflow"""
    data_entity_name=""
    options=None
    def __init__(self,operator_name,data_entity_name,options=None):
        self.data_entity_name=data_entity_name
        self.type_name="TARGET"
        self.options=options
        if options is not None:
            self.__repair_integration_type()

        Operator.__init__(self, operator_name)

    def __repair_integration_type(self):
        #this is done to change the integration type enum as per REST payload definitions
        integrationType=str(self.options["integrationType"])
        integrationType=integrationType.strip().lower()
        if "append" == integrationType:
            integrationType="CONTROL_APPEND"
        elif integrationType in ("incremental","increental update"):
            integrationType="INCREMENTAL_UPDATE"
            self.options["integrationType"]=integrationType

    def store_options(self):
        """Returns the store options on target node
        """
        return self.options

class Join(Operator):
    """Model that represents JOIN in a dataflow"""
    join_name=""
    joinexpression = ""
    join_type = ""
    #pylint: disable=super-init-not-called
    #causes invalid JSON for Join, to be investigated
    def __init__(self,join_name,join_type,joinexpression):
        self.name=join_name
        self.type_name="JOIN"
        self.join_name=join_name
        self.join_type=join_type
        self.joinexpression=joinexpression

    def get_connected_from(self):
        """Parses JOIN Expresstion by token '=', and 
        left token is the operator JOIN was connected from
        right token is the operator to which JOIN is connecting to in a dataflow
        """
        expression = self.joinexpression
        stores = expression.split("=")
        left = stores[0].strip().split(".")[0]
        right = stores[1].strip().split(".")[0]
        return [left,right],left,right

class Filter(Operator):
    """Represents Filter JSON model in dataflow"""
    filter_name=""
    filter_condition=""

    def __init__(self,filter_name,filter_condition):
        self.filter_condition=filter_condition
        self.filter_name=filter_name
        self.type_name="FILTER"
        self.name=filter_name

class Sorter(Operator):
    """Represents Sorter JSON model in dataflow"""
    sorter_name=""
    sorter_condition=""

    def __init__(self,sorter_name,sorter_condition):
        self.sorter_condition=sorter_condition
        self.sorter_name=sorter_name
        self.type_name="SORTER"
        self.name=sorter_name

class Aggregate(Operator):
    """Represents Aggregate JSON model in dataflow"""
    def __init__(self,aggregate_name,having_condition,manual_groupby,custom_aggrregate_attributes,column_map):
        self.name=aggregate_name
        self.aggregate_name=aggregate_name
        self.having_condition=having_condition
        self.manual_groupby=manual_groupby
        self.custom_aggrregate_attributes=custom_aggrregate_attributes
        self.type_name="AGGREGATE"
        self.column_map=column_map

class AggregateAttribute:
    """Represents AggregateAttribute JSON model in dataflow"""
    def __init__(self,attribute_name,data_type,length,expression,is_group_by="NO"):
        self.attribute_name=attribute_name
        self.data_type=data_type
        self.length=length
        self.is_group_by=is_group_by
        self.expression = expression

    def set_scale(self,scale):
        """Updates the scale for aggregate attribute

        Arguments:
            scale -- _description_
        """
        self.scale=scale

    def get_scale(self):
        """_summary_

        Returns:
            _description_
        """
        return self.scale

class SetGroup(Operator):
    """Represents SetGroup JSON model in dataflow"""
    def __init__(self,set_name,set_expression,column_mappings):
        self.name = set_name
        self.type_name="SET"
        self.set_expression=set_expression
        self.column_mappings=column_mappings

class Expression(Operator):
    """Represents Expression JSON model in dataflow"""
    def __init__(self,expression_name,expression_attributes,retain_projected_cols=False):
        self.name=expression_name
        self.type_name="EXPESSION"

        self.expression_name=expression_name
        self.expression_attributes=expression_attributes
        self.retain_projected_cols=retain_projected_cols

class DataCleanse(Operator):
    """Represents DataCleanse JSON model in dataflow"""
    REPLACE_NULL_STRING_WITH_BLANKS="Replace Null Strings with blanks (\"\")"

    REPLACE_NULL_NUMERIC_WITH_ZERO="Replace Null Numeric Fields with 0"
    REPLACE_NULL_NUMERIC_WITH_MEAN="Replace Null Numeric Fields with Mean"
    REPLACE_NULL_NUMERIC_WITH_MEDIAN= "Replace Null Numeric Fields with Median"

    REMOVE_LEADING_TRAILING_WHITESPACE="Leading and Trailing Whitespace"
    REMOVE_TABS_LINEBREAKS_DUP_WHITESPACE="Tabs, Linebreaks and duplicate Whitespace"
    REMOVE_ALL_WHITESPACE="All Whitespace"
    REMOVE_LETTERS="Letters"
    REMOVE_NUMBERS="Numbers"

    REMOVE_PUNCTUATION="Punctuation"
    MODIFY_CASE_TITLE="Uppercase"
    MODIFY_CASE_LOWER="Lowercase"
    MODIFY_CASE_UPPER="Title Case"

    cleanse_options_list=[
        REPLACE_NULL_STRING_WITH_BLANKS,
        REPLACE_NULL_NUMERIC_WITH_ZERO,
        REPLACE_NULL_NUMERIC_WITH_MEDIAN,
        REPLACE_NULL_NUMERIC_WITH_MEAN,
        REMOVE_LEADING_TRAILING_WHITESPACE,
        REMOVE_TABS_LINEBREAKS_DUP_WHITESPACE,
        REMOVE_ALL_WHITESPACE,
        REMOVE_LETTERS,
        REMOVE_NUMBERS,
        REMOVE_PUNCTUATION,
        MODIFY_CASE_TITLE,
        MODIFY_CASE_LOWER,
        MODIFY_CASE_UPPER
    ]
    def __init__(self,cleanse_name,participating_columns,cleanse_options):
        self.name=cleanse_name
        self.participating_columns=participating_columns
        self.cleanse_options = cleanse_options

    def prepare_cleanse_dict(self):
        """Prepares the data clenase dictionary based on updated values"""
        cleanse_dict={}
        if self.cleanse_options:
            for entry in DataCleanse.cleanse_options_list:
                cleanse_entry_option=False
                if entry in self.cleanse_options:
                    cleanse_entry_option=True
                cleanse_dict[entry]=cleanse_entry_option
        return cleanse_dict

class MLPredict(Operator):
    """Represents MLPredict JSON model in dataflow"""
    def __init__(self,predict_name,prediction_attribute,parameters):
        self.name=predict_name
        self.prediction_attribute = prediction_attribute
        self.parameters=parameters

class Lag(Operator):
    """Represents Lag JSON model in dataflow"""
    LAG_PARAM_EXPRESSION="expression"
    LAG_PARAM_PARTITION="[partition]"
    LAG_PARAM_ORDER="order"

    def __init__(self,lag_name,lag_params):
        self.name=lag_name
        self.lag_params=lag_params

class Lookup(Operator):
    """Represents Lookup operator in DataFlow. """

    MULTIPLE_MATCH_ROWS="MULTIPLE_MATCH_ROWS"
    NTH_ROW="NTH_ROW"
    NO_MATCH_ROWS ="NO_MATCH_ROWS"
    LOOKUP_CONDITION="LOOKUP_CONDITION"
    DRIVING_SOURCE="DRIVING_SOURCE"
    LOOKUP_SOURCE="LOOKUP_SOURCE"
    DEFAULT_VALUES="DEFAULT_VALUES"

    class MultipleMatchRowsOptions(Enum):
        "List of enums supported for Multiple Match Row case in lookup"
        ERROR_WHEN_MULTIPLE_ROW="ERROR_WHEN_MULTIPLE_ROW"
        ALL_ROWS="ALL_ROWS"

    class NoMatchRowsOptions(Enum):
        "List of enums supported for No Mathing row in lookup"
        DEFAULT_VALUE="DEFAULT_VALUES"

    def __init__(self, name, lookup_options):
        super().__init__(name)
        self.update_lookup_options(lookup_options)

    def update_lookup_options(self,lookup_options):
        """Prepares lookup options from the dectionary
        lookup options must have following keys 

        Lookup.MULTIPLE_MATCH_ROWS
        Lookup.NO_MATCH_ROWS
        Lookup.NTH_ROW
        Lookup.LOOKUP_CONDITION
        Lookup.DRIVING_SOURCE
        Lookup.LOOKUP_SOURCE
        """

        if Lookup.MULTIPLE_MATCH_ROWS not in lookup_options:
            lookup_options[Lookup.MULTIPLE_MATCH_ROWS]="ALL_ROWS"

        if Lookup.NO_MATCH_ROWS not in lookup_options:
            lookup_options[Lookup.NO_MATCH_ROWS]="DEFAULT_VALUES"

        if Lookup.NTH_ROW not in lookup_options:
            lookup_options[Lookup.NTH_ROW]=""

        self.multipleMatchRows=lookup_options[Lookup.MULTIPLE_MATCH_ROWS]
        self.noMatchRows=lookup_options[Lookup.NO_MATCH_ROWS]
        self.nthRowNumber=lookup_options[Lookup.NTH_ROW]
        self.lookupCondition=lookup_options[Lookup.LOOKUP_CONDITION]
        self.driverInputConnection=lookup_options[Lookup.DRIVING_SOURCE]
        self.lookupInputConnection=lookup_options[Lookup.LOOKUP_SOURCE]
        self.default_values=lookup_options[Lookup.DEFAULT_VALUES]

class ExpressionAttributes:
    """Represents the attributes in an expression node"""
    def __init__(self,data_entities=None,source_from=None,project_to=None):
        """Create Expression attributes with data entities or source 
        if data_entities is passed, it must be a valid data entity from 
        where all the column(s) are sourced if source_from is passed it must be a 
        valid operator that is defined in the data flow from where
        the projected column(s) are sourced
        When source_from is None, by default the column(s) from the previous 
        operator are projected by default

        """
        self.new_columns=[]
        self.source_de=[]
        if data_entities is not None:
            for entity in data_entities:
                self.source_de.append(entity)
        if source_from is not None:
            self.source_from=source_from
        if project_to is not None:
            self.project_to=project_to
        self.column_maping=None


    def new_column(self,column_defintion):
        """Adds new column for expression operator"""
        self.new_columns.append(column_defintion)

    def columns(self):
        """returns list of columns available in expression"""
        return self.new_columns

    def add_column_mapping(self,column_maping):
        """adds new column mapping"""
        self.column_maping = column_maping

class ColumnDefinition:
    """Represents the ColumnDefinition in an expression node"""
    def __init__(self,name,globalId,data_type,length,scale,position,expression=None):
        self.name=name
        self.globalId=globalId
        self.position=position

        self.dataType=data_type
        self.dataTypeCode=data_type

        self.length=length
        self.scale=scale

        self.format=None
        self.boundTo=""
        self.expressions={}
        self.connectedFrom=[]
        self.expression=expression
        if self.expression is not None:
            self.expressions={}
            self.expressions["ANNUAL_PACKAGE"]=self.expression

    def custom_expressions(self,custom_expressions):
        """Adds expression to the column definition.
        This is useful when developer adds the expression later to object creaation.

        Arguments:
            custom_expressions -- _description_
        """
        self.expressions={}
        self.expressions=custom_expressions

    def connected_from(self,connectedFrom):
        self.connectedFrom.extend(connectedFrom)

    def to_data_store_attribute(self):
        ds_attr= DataStoreAttributes(name=self.name,globalId=self.globalId, position=self.position,dataType=self.dataType,\
                dataTypeCode=self.dataTypeCode,length=self.length,scale=self.scale)
        ds_attr.column_mapping_expression(self.expressions)
        ds_attr.connected_from(self.connectedFrom)

class DataFlowException(Exception):
    """Exception class for DataFlow operations"""
    pass

class OperatorResolver:
    """Resolves the operator and its payload definition on dataflow"""
    operator_count=0
    operator_stack =[]
    operator_stack_dict={}
    resolved_operator_stack_dict={}

    #operator_stack_order={}
    operator_stack_order_name={}
    operator_stack_order_type={}

    path_override={}

    def __init__(self,client):
        self.client = client

 #when an operator is pushed to the stack, some preprocessing steps are 
 # done (to generate faster/avoid search)
    def load_operator_stack(self,operator_object):
        """_summary_

        Arguments:
            operator_object -- _description_
        """
        self.operator_count = self.operator_count + 1
        operator_count=self.operator_count
        self.operator_stack.append(operator_object)
        self.operator_stack_dict[operator_count]=operator_object
        #self.operator_stack_order[operator_count]=operator_object.name+":"+operator_object.type_name
        self.operator_stack_order_name[operator_count]=operator_object.name
        self.operator_stack_order_type[operator_count]=operator_object.type_name

        #logging.debug(self.operator_stack_dict)
        #logging.debug("Operator added")

    def resolve_operator_payload(self):
        """Returns the payload for the operator"""
        payload_resolvers = self.__get_operator_processors()
        #print(payload_resolvers.keys())
        resolved_operators={}
        for key,value in self.operator_stack_dict.items():
            resolved_operator=payload_resolvers[type(value).__name__](key,value)
            self.resolved_operator_stack_dict[key]=resolved_operator

            resolved_operator_type = type(resolved_operator).__name__

            if resolved_operator_type in resolved_operators.keys():
                existing_operators=resolved_operators[resolved_operator_type]
                existing_operators.append(resolved_operator)
            else:
                existing_operators=[]
                existing_operators.append(resolved_operator)
                resolved_operators[resolved_operator_type]=existing_operators

        return resolved_operators

    def __get_operator_processors(self):
        opertor_processors={}
        opertor_processors[SourceDataStore.__name__]=self.__resolve_source_obj
        opertor_processors[TargetDataStore.__name__]=self.__resolve_target_obj
        opertor_processors[Join.__name__]=self.__resolve_join_obj
        opertor_processors[Filter.__name__]=self.__resolve_filter_obj
        opertor_processors[Sorter.__name__]=self.__resolve_sorter_obj
        opertor_processors[Expression.__name__]=self.__resolve_expression_obj
        opertor_processors[Aggregate.__name__]=self.__resolve_aggregate_obj
        opertor_processors[SetGroup.__name__]=self.__resolve_set_obj
        opertor_processors[DataCleanse.__name__]=self.__resolve_data_cleanse_obj
        opertor_processors[MLPredict.__name__]=self.__resolve_ml_predict_obj
        opertor_processors[Lag.__name__]=self.__resolve_lag_obj

        return opertor_processors

    def __resolve_source_obj(self,operator_position,operator_obj):
        #print(type(operator_obj).__name__)
        if not isinstance(operator_obj,SourceDataStore) :
            raise DataFlowException("Invalid Operator, this method can resolve only Source")

        source_data_entity = self.client.get_dataentity_by_name(operator_obj.data_entity_name)

        total_operators = len(self.operator_stack_order_type.keys())

        connected_to=""
        for i in range(operator_position+1,total_operators+1):
            type_name = self.operator_stack_order_type[i]
            if "SOURCE" != type_name:
                connected_to = self.operator_stack_order_name[i]
                break

        source_node = DataFlowSource(operator_obj.name,"DATASTORE",source_data_entity["schemaName"],\
                    source_data_entity["dataServerName"],source_data_entity['name'],source_data_entity['globalId'],\
                        connected_to)
        source_node.add_attributes(self.__resolve_attributes_for_target(operator_obj.name,source_data_entity))

        return source_node

    def __resolve_target_obj(self,operator_position,operator_obj):
        if not isinstance(operator_obj,TargetDataStore):
            raise DataFlowException("Invalid Operator, this method can resolve only Target")

        target_data_entity = self.client.get_dataentity_by_name(operator_obj.data_entity_name)
        connected_from = self.operator_stack_order_name[operator_position-1]

        options= operator_obj.options
        if(options is not None and "integrationType" not in options.keys()):
            options["integrationType"]="CONTROL_APPEND"

        target_node = DataFlowTarget(operator_obj.name,"DATASTORE",target_data_entity["schemaName"],\
                    target_data_entity["dataServerName"],target_data_entity['name'],target_data_entity['globalId'],\
                        [connected_from])
        target_node.integration_type(options["integrationType"])

        projected_attributes=self.__resolve_projected_attributes_by_name(operator_position)

        target_node.add_attributes(
            self.__resolve_attributes_for_target(
                operator_obj.name,target_data_entity,options,projected_attributes))

        return target_node

    def __resolve_attributes_for_target(self,operator_name,target_data_entity,options=None,projected_attributes=None):
        data_entity_name = target_data_entity["name"]
        columns = target_data_entity["columns"]

        target_attributes=[]

        for column in columns:
            data_entity_column = data_entity_name + "." + column["name"]
            bound_to = "undefined." + data_entity_column
            key=False

            if options is not None and "key_columns" in options.keys() and column["name"] in options["key_columns"]:
                key=True

            attribute = DataStoreAttributes(column["name"],column["globalId"],column["position"],column["dataType"],\
                column["dataTypeCode"],column["length"],column["scale"],column["defaultValue"],column["isMandatory"],\
                    bound_to,key,True,False)

            if projected_attributes is not None:
                column_name=column["name"]
                if column_name in projected_attributes.keys():
                    attribute.column_mapping_expression({"INPUT1":projected_attributes[column_name]})

                if options is not None and "column_mappings" in options:
                    column_mappings = options["column_mappings"]
                    key=operator_name+"."+column["name"]
                    if key in column_mappings:
                        column_mapping = column_mappings[key]
                        attribute.column_mapping_expression({"INPUT1":column_mapping})

            target_attributes.append(attribute)

        return target_attributes

    def __resolve_join_obj(self,operator_position,operator_obj):
        if not isinstance(operator_obj,Join):
            raise DataFlowException("Invalid Operator, this method can resolve only Join")
        joinNode = DataFlowJoin(operator_obj.join_name,operator_obj.joinexpression,operator_obj.join_type)

        i = operator_position+1
        for i in range (operator_position+1,len(self.operator_stack_order_type)):
            if self.operator_stack_order_type[i] != "SOURCE": # A join output can't be a source
                break
        joinNode.add_connected_to(self.operator_stack_order_name[i])

        prev_operator = self.operator_stack_order_name[operator_position-1]
        second_prev_operator = self.operator_stack_order_name[operator_position-2]

        joinNode.add_join_source(prev_operator,"LEFT")
        joinNode.add_join_source(second_prev_operator,"RIGHT")

        receiving_from =self.__pathOverride(operator_obj.join_name)

        if  receiving_from is not None:
            joinNode.connectedFrom.clear()
            joinNode.connectedFrom.extend(receiving_from)
            #joinNode.add_connected_to(self.operator_stack_order_name[operator_position+1])
        else:
            logging.debug("\nNO PATH OVERRIDE EXISTS !! ")

        #print(joinNode.name + " is " + str(joinNode.connectedFrom) + " " + str(joinNode.connectedTo) )
        return joinNode

    def __pathOverride(self,current_operator_name):

        if hasattr(self,"path_override"):
            receiving_from=[]
            #print(self.path_override)
            for key in self.path_override.keys():
                path_to_nodes = self.path_override[key]
                if current_operator_name in path_to_nodes:
                    #current operator is defined as TO node.
                    receiving_from.append(key)
            #print(current_operator_name + " Receiving from " + str(receiving_from))
            return receiving_from
        return None


    def __resolve_filter_obj(self,operator_position,operator_obj):

        if not isinstance(operator_obj,Filter):
            raise DataFlowException("Invalid Operator, this method can resolve only Filter")

        filter_node = DataFlowFilter(operator_obj.filter_name,operator_obj.filter_condition)
        connected_from,connected_to=self.__resolve_1_to_1_links(operator_position)
        filter_node.add_connected_from(connected_from)
        filter_node.add_connected_to(connected_to)
        return filter_node   

    def __resolve_sorter_obj(self,operator_position,operator_obj):

        if not isinstance(operator_obj,Sorter):
            raise DataFlowException("Invalid Operator, this method can resolve only sorter")

        sorterNode = DataFlowSorter(operator_obj.sorter_name,operator_obj.sorter_condition)
        connected_from,connected_to=self.__resolve_1_to_1_links(operator_position)
        #print(connected_from,connected_to)
        sorterNode.add_connected_from(connected_from)
        sorterNode.add_connected_to(connected_to)
        return sorterNode

    #returns from and two names - should be called only if 
    #operator accept one and produce one output
    def __resolve_1_to_1_links(self,opertor_position):

        #print("Operator Position " + str(opertor_position))
        #print(self.operator_stack_order_name)
        #print("**"*50)
        i=opertor_position+1
        for i in range(opertor_position+1,len(self.operator_stack_order_type)):
            if self.operator_stack_order_type[i] != "SOURCE":
                break
            #else:
                #print("Skipping source as connected to...")
        #return self.operator_stack_order_name[opertor_position-1],self.operator_stack_order_name[opertor_position+1]
        prev_pos=self.operator_stack_order_name[opertor_position-1]
        next_pos=self.operator_stack_order_name[i]
        logging.debug("Current position %s From= %s to = %s",opertor_position,prev_pos,next_pos)
        return prev_pos,next_pos

    def __resolve_projected_attributes_by_name(self,operator_position):
        projected_columns={}

        for i in range(operator_position-1,0,-1):
            #print(i)
            previous_operator=self.resolved_operator_stack_dict[i]
            #print(previous_operator.type)
            attributes = previous_operator.get_attributes()

            if previous_operator.type == "AGGREGATE":
                attributes=previous_operator.get_projected_attributes()

            if attributes is not None:
                for attribute in attributes:
                    #print(type(attribute))
                    column_mapping=previous_operator.name+"."+attribute.name
                    #print(column_mapping)
                    if attribute.name not in projected_columns:
                        projected_columns[attribute.name]=column_mapping
            else:
                pass
                #print(previous_operator.type)

                # aggregateNode.add_aggregate_attributes(aggregate_attributes)
                #aggregateNode.add_group_by_attributes(groupby_attributes)
        return projected_columns

    def __resolve_attributes_and_column_mapping(self,operator_position):
        new_attributes=[]
        for i in range(operator_position-1,0,-1):
            previous_operator=self.resolved_operator_stack_dict[i]
            attributes = previous_operator.get_attributes()
            if attributes is not None:
                #new_attributes=[]
                for attribute in attributes:
                    new_attribute = copy.deepcopy(attribute)
                    new_attribute.globalId=""
                    new_attribute.boundTo=""
                    column_mapping=previous_operator.name+"."+attribute.name
                    new_attribute.column_mapping_expression({"INPUT1":column_mapping})
                    new_attribute.connected_from(column_mapping)
                    new_attributes.append(new_attribute)

        return new_attributes

    def __resolve_attributes_and_column_mapping_for_expression(self,operator_position,connected_from,custom_mapping):
        """Resolves the attributes that are expected to be projected and custom mappings
        """
        new_attributes=[]
        for i in range(operator_position-1,0,-1):
            previous_operator=self.resolved_operator_stack_dict[i]
            logging.debug("Previous operator " + previous_operator.name + "from " + connected_from)
            #if previous_operator.name == connected_from: 
            attributes = previous_operator.get_attributes()
            if attributes is not None:
                #new_attributes=[]
                for attribute in attributes:
                    new_attribute = copy.deepcopy(attribute)
                    new_attribute.globalId=""
                    new_attribute.boundTo=""
                    column_mapping=previous_operator.name+"."+attribute.name
                    if custom_mapping is not None and attribute.name in custom_mapping:
                        column_mapping=custom_mapping[attribute.name]

                    new_attribute.column_mapping_expression({"INPUT1":column_mapping})
                    new_attribute.connected_from(column_mapping)
                    new_attributes.append(new_attribute)
                #break #We are projecting all the attributes to expression from prev. node(s)

        return new_attributes

    def __resolve_expression_obj(self,operator_position,operator_obj):

        if not isinstance(operator_obj,Expression):
            raise DataFlowException("Invalid Operator, this method can resolve only sorter")

        expressionNode = DataFlowExpression(operator_obj.expression_name)
        connected_from,connected_to=None,None

        if operator_obj.expression_attributes is not None:
            attributes = operator_obj.expression_attributes
            if hasattr(attributes, 'source_from') and hasattr(attributes, 'project_to'):
                connected_from,connected_to=attributes.source_from,attributes.project_to
            else:
                connected_from,connected_to = None,None

            #column_mapping = attributes.column_maping

        if connected_from is None or connected_to is None:
            connected_from,connected_to=self.__resolve_1_to_1_links(operator_position)
        expressionNode.connected_from(connected_from)
        expressionNode.connected_to(connected_to)
        attributes=[]
        if operator_obj.retain_projected_cols:
            column_mapping=None #Future case...
            attributes = self.__resolve_attributes_and_column_mapping_for_expression(
                operator_position,connected_from,column_mapping)

        #custom_columns = operator_obj.expression_attributes.columns()
        custom_columns = operator_obj.expression_attributes

        for custom_column in custom_columns:
            custom_column.to_data_store_attribute()
            attributes.append(custom_column)

        expressionNode.expression_attributes(attributes)
        #print("\n\n\n Expression attributes " + str(len(attributes) ))
        return expressionNode


    def __resolve_aggregate_obj(self,operator_position,operator_obj):

        if not isinstance(operator_obj,Aggregate):
            raise DataFlowException("Invalid operator, this method can resolve only sorter")

        aggregateNode = DataFlowAggregate(operator_obj.name)
        aggregateNode.havingCondition=operator_obj.having_condition
        aggregateNode.manualGroupBy=operator_obj.manual_groupby

        connected_from,connected_to=self.__resolve_1_to_1_links(operator_position)
        aggregateNode.connected_from(connected_from)
        aggregateNode.connected_to(connected_to)

        retain_projected_cols=operator_obj.column_map["retain_projected_cols"]
        del operator_obj.column_map["retain_projected_cols"]
        attributes=[]
        if retain_projected_cols:
            attributes = self.__resolve_attributes_and_column_mapping(operator_position)

        aggregate_attributes = []
        groupby_attributes = []

        for attribute in attributes:
            aggregate_attribute = DataFlowAggregateAtributes()

            aggregate_attribute.from_data_store_attribute(attribute)
            custom_mapping_entry = operator_obj.name+"."+aggregate_attribute.name
            group_indicator="*"
            if custom_mapping_entry+group_indicator in operator_obj.column_map.keys():
                aggregate_attribute.isGroupBy="AUTO"
                expression={}
                expression["INPUT1"]=operator_obj.column_map[custom_mapping_entry+group_indicator]

                aggregate_attribute.expressions=expression
                aggregate_attributes.append(aggregate_attribute)
            elif custom_mapping_entry in operator_obj.column_map.keys():
                aggregate_attribute.isGroupBy="NO"
                expression={}
                expression["INPUT1"]=operator_obj.column_map[custom_mapping_entry]

                aggregate_attribute.expressions=expression
                aggregate_attributes.append(aggregate_attribute)

            else:
                aggregate_attribute.isGroupBy="NO"
                groupby_attributes.append(aggregate_attribute)

        if operator_obj.custom_aggrregate_attributes:
            for custom_attribute in operator_obj.custom_aggrregate_attributes:
                custom_dfaggregate_attribute = self.from_custom_aggregate_attribute(custom_attribute)
                if custom_attribute.is_group_by != "NO":
                    groupby_attributes.append(custom_dfaggregate_attribute)
                else:
                    aggregate_attributes.append(custom_dfaggregate_attribute)


        aggregateNode.add_aggregate_attributes(aggregate_attributes)
        aggregateNode.add_group_by_attributes(groupby_attributes)
        return aggregateNode

    def from_custom_aggregate_attribute(self,custom_aggregate_attribute):
        """"""
        if isinstance(custom_aggregate_attribute,AggregateAttribute):
            aggregate_attribute = DataFlowAggregateAtributes()
            aggregate_attribute.name=custom_aggregate_attribute.attribute_name
            aggregate_attribute.dataType=custom_aggregate_attribute.data_type
            aggregate_attribute.length=custom_aggregate_attribute.length
            aggregate_attribute.isGroupBy=custom_aggregate_attribute.is_group_by
            expression={}
            expression["INPUT1"]=custom_aggregate_attribute.expression

            aggregate_attribute.expressions=expression

            return aggregate_attribute

    def __resolve_set_obj(self,operator_position,operator_obj):

        if not isinstance(operator_obj,SetGroup):
            raise DataFlowException("Invalid operator, this method can resolve only Set")

        setNode = DataFlowSet(operator_obj.name)
        expression = operator_obj.set_expression
        set_expression_tokens = expression.split()
        input_nodes=[]
        set_operator_objs=[]
        operator_input_count=0
        for i in range(0,len(set_expression_tokens)):

            operator=None
            if i % 2 == 0:
                operator_input_count+=1
                #print("Connector " + set_expression_tokens[i])
                input_nodes.append(set_expression_tokens[i])
                if i==0:
                    operator = None
                else:
                    operator=set_expression_tokens[i-1]
                    #print("Operator =======>" + operator)
                set_operator_obj=DataFlowSetOperator("INPUT"+str(operator_input_count),set_expression_tokens[i],operator)
                set_operator_objs.append(set_operator_obj)

        setNode.connected_from(input_nodes)
        setNode.connected_to([self.operator_stack_order_name[operator_position+1]])
        setNode.set_operators(set_operator_objs)

        return setNode
        #connected_from,connected_to=self.__resolve_1_to_1_links(operator_position)
        #aggregateNode.connected_from(connected_from)
        #aggregateNode.connected_to(connected_to)

        #attributes = self.__resolve_attributes_and_column_mapping(operator_position)

    def __resolve_data_cleanse_obj(self,operator_position,operator_obj):

        if not isinstance(operator_obj,DataCleanse):
            raise DataFlowException("Invalid operator, this method can resolve only DataCleanse")

        cleanseNode = DataFlowDataCleanse(operator_obj.name)
        cleanseNode.cleansingOptions=operator_obj.prepare_cleanse_dict()

        connected_from,connected_to=self.__resolve_1_to_1_links(operator_position)
        cleanseNode.connected_from(connected_from)
        cleanseNode.connected_to(connected_to)
        attributes = self.__resolve_attributes_and_column_mapping(operator_position)

        cleanseNode.cleanse_attributes(attributes,operator_obj.participating_columns)

        return cleanseNode

    def __resolve_ml_predict_obj(self,operator_position,operator_obj):

        if not isinstance(operator_obj,MLPredict):
            raise DataFlowException("Invalid operator, this method can resolve only Predict")

        ml_predict_node=DataFlowMLPredict(operator_obj.name)
        connected_from,connected_to=self.__resolve_1_to_1_links(operator_position)
        ml_predict_node.connected_from(connected_from)
        ml_predict_node.connected_to(connected_to)
        ml_predict_node.predict_attributes(operator_obj.prediction_attribute,operator_obj.parameters)

        return ml_predict_node

    def __resolve_lag_obj(self,operator_position,operator_obj):

        if not isinstance(operator_obj,Lag):
            raise DataFlowException("Invalid operator, this method can resolve only Lag")

        lag_node=DataFlowLag(operator_obj.name)
        connected_from,connected_to=self.__resolve_1_to_1_links(operator_position)
        lag_node.connected_from(connected_from)
        lag_node.connected_to(connected_to)
        lag_node.process_lag_attributes(operator_obj.lag_params)
        return lag_node

class DataFlow:
    """Creates Dataflow in Data Transforms. 
    Dataflow represents an ELT or ETL pipeline, involves multiple sources, list of tranformation 
    operators and a target.
    """
    project = ""
    parentFolder = ""
    data_flow_name = ""
    client = None
    description=None
    attached_schemas=[]
    resolved_schemas={}
    description = None 
    path_dict={}

    def __init__(self,name,project,parentFolder=None):
        """Creates dataflow instance
        :parm name: unique name of the dataflow
        :param project: The project name where the dataflow belongs to, if the project 
        doesn't exist in Data Transforms, it will be created before creation of DataFlow
        :param parentFolder: Optional project folder. if not provided 'Default' 
        folder will be considered"""
        self.name=name
        self.project=project
        if parentFolder is None:
            parentFolder="DefaultFolder"
            logging.debug("Project folder default to %s" , parentFolder)

        self.parentFolder=parentFolder
        self.data_flow_name=name
        self.load_options=None
        if not DataTransformsWorkbench.client is None:
            logging.debug("Re-using workbench client")
            if DataTransformsWorkbench.active_workbench is None:
                self.client = DataTransformsClient()
            else:
                self.client = DataTransformsWorkbench.active_workbench.client
        else :
            self.client = DataTransformsClient()

        self.client.load_cache()
        self.description=None
        self.resolver=OperatorResolver(self.client)

    def __resolve_schema_references(self):
        #print("Resolving schema references")
        resolved_schemas=self.client.resolve_connection_schema_ref_from_cache(self.attached_schemas)
        #print("Resolved attached schema" + str(resolved_schemas))
        return resolved_schemas

    def create(self):
        """Creates the dataflow using the operators and its options provided"""
        #print(self.project + " " + self.parentFolder + " " + self.data_flow_name)
        self.client.create_project(name=self.project,folder=self.parentFolder)

        #TODO FIX PROJECT WITH SPACE
        code = self.project.replace(" ","").upper()
        project_id=self.client.projects[self.project]
        df_exists,df_id=self.client.check_if_df_exists(project_id,self.data_flow_name)
        payload = DataFlowPayload(self.data_flow_name,self.parentFolder,code)
        if df_exists:
            logging.debug("DataFlow already exists, Resolving the ID")
            payload.globalId=df_id

        payload.add_attached_schemas(self.__resolve_schema_references().values())

        self.resolver.path_override=self.path_dict
        resolved_payload = self.resolver.resolve_operator_payload()

        fx = lambda x : resolved_payload[x] if x in resolved_payload.keys() else []

        payload.add_sources(fx(DataFlowSource.__name__))
        payload.add_targets(fx(DataFlowTarget.__name__))
        payload.add_sorters(fx(DataFlowSorter.__name__))
        payload.add_filters(fx(DataFlowFilter.__name__))
        payload.add_joins(fx(DataFlowJoin.__name__))
        payload.add_aggregates(fx(DataFlowAggregate.__name__))
        payload.add_sets(fx(DataFlowSet.__name__))
        payload.add_datacleanse(fx(DataFlowDataCleanse.__name__))
        payload.add_predicts(fx(DataFlowMLPredict.__name__))
        payload.add_lags(fx(DataFlowLag.__name__))
        payload.add_expressions(fx(DataFlowExpression.__name__))
        
        if df_exists:
            result=False
            if len(self.load_options.keys()) > 1:
                result,payload=self.__prepare_target_km_options(payload)
            result=self.__update_dataflow_from_payload(payload)
            self.data_flow_id=df_id
            return result
        else:
            #updating KM options require dataflow to be saved, 
            #Save the dataflow and use it for updates.

            result,df_global_id=self.__create_dataflow_from_payload(payload)

            self.data_flow_id=df_global_id
            #check if there are options set by developer
            if len(self.load_options.keys()) > 1: 
                logging.info("Load options available for update result {result}")
                if result:
                    payload.globalId=df_global_id
                    result,payload=self.__prepare_target_km_options(payload)
                    result=self.__update_dataflow_from_payload(payload)
                    logging.info("Dataflow {self.data_flow_name} Created, Load options merged")
                    return result
                else:
                    logging.error("Skipping update of load options, as dataflow save is " + str(result))
                    return False
            else:
                logging.info("No custom load options found, skipped load options update")
                return result

    def __prepare_target_km_options(self,payload):
        df_payload_string=json.dumps(payload,default=lambda o: o.__dict__)
        df_json_doc=json.loads(df_payload_string)
        result,km_options_doc =self.client.fetch_km_options(df_json_doc["targets"][0]["name"],df_payload_string)

        if result:
            if self.load_options is not None:
                #print("Merging load options -------------"+str(type(km_options_doc)))
                km_options=km_options_doc[0]["kmOptions"]

                for key,value in self.load_options.items():
                    for km_option in km_options:
                        if key == km_option["optionName"]:
                            km_option["optionValue"]=value
                            km_option["optionNameUI"]=key.replace("_"," ").lower().capitalize()
                            km_option["descriptionUI"]=km_option["description"]
                            km_option["helpUI"]=km_option["help"]
                            km_option["setAsDefault"]=False
                            logging.debug("KM Option "+km_option["optionName"]+" updated " + km_option["optionValue"])
                            logging.debug(km_option["optionNameUI"])

            #print(km_options_doc)
            df_json_doc["targets"][0]["options"]=km_options_doc
            return result,df_json_doc        
        else:
            #raise Exception("Failed to fetch KM Options for dataflow")
            return False,None

    def __create_dataflow_from_payload(self,payload):
        logging.debug("Creating dataflow {self.data_flow_name}")
        #logging.debug(json.dumps(payload,default=lambda o: o.__dict__))
        result,df_global_id=self.client.create_dataflow_from_json_payload(json.dumps(payload,default=lambda o: o.__dict__))
        return result,df_global_id

    def __update_dataflow_from_payload(self,payload):
        logging.debug("Updating dataflow %s", self.data_flow_name)
        # f=open("dataflow.json","w",encoding="UTF-8")
        # f.write(json.dumps(payload,default=lambda o: o.__dict__))
        # f.close()
        #logging.debug(json.dumps(payload,default=lambda o: o.__dict__))
        result=self.client.update_dataflow_from_json_payload(json.dumps(payload,default=lambda o: o.__dict__))
        return result

    def prepare_column_mapping(self,target_data_entity,sources,auto_map="By Name",fail_if_missing=True):
        """Prepares the dataload column mapping for tareget data entity"""
        return SimpleColumnMapping(target_data_entity,sources).prepare_column_mapping(auto_map,fail_if_missing)

    #developer exposed method, loads the connection, schema, data entities used by the data flow
    def use(self,connection_name,schema_name,data_entity_name,alias_name=None):
        """Adds the data entity in the dataflow , it could be used as source or target
        """
        #internally attached schemas are computed based on connection and schema name
        resolved_schema_name =connection_name+"."+schema_name
        self.attached_schemas.append(resolved_schema_name)
        resolved_store_name= resolved_schema_name+"."+data_entity_name
        #returns the data entity detail - this can be used for preparing column mapping
        entity_def= self.client.get_dataentity_by_name(resolved_store_name)
        return RefDataEntity().load_from_json(entity_def,resolved_store_name,alias_name)

    def __load_operator_stack(self,operator_obj):
        self.resolver.load_operator_stack(operator_obj)

    def update_custom_options(self, source_operator,target_operator,options):
        '''
        Updates the custom options between the nodes. 
        Options are updated between source and target operators that are defined in the dataflow
        '''
        #print("options " + str(options))

        if self.data_flow_id is None:
            logging.error("Dataflow ID is not resolved, invalid operation performed at this time")
            raise DataFlowException("Invalid operation, custom operations should be performed after save")

        payload_text = self.client.get_dataflow_by_id(self.data_flow_id)
        payload_doc = json.loads(payload_text)

        physical_nodes = payload_doc["lkm_options"]["Physical"]
        target_node=None
        for node in physical_nodes:
            lkmSource = node["lkmSource"]["connectedFromLogicalNode"]
            lkmTarget = node["lkmTarget"]["connectedToLogicalNode"]

            if (lkmSource == source_operator) and ( lkmTarget == target_operator):
                #print("Node found ")
                target_node=node
                break
        if target_node is None:
            logging.error(" Source {source_operator}  target {target_operator} Options not found")
            return False

        else:
            #print("\n\n")
            #print(node["kmOptions"])
            kmOptions = node["kmOptions"]
            for kmOption in kmOptions:
                kmOptionName = kmOption["optionName"]

                if kmOptionName in options.keys():
                    kmOption["optionValue"]=options[kmOptionName]
                    #logging.debug("KM Option updated with " + kmOptionName + "=" + str(kmOption["optionValue"]))
                else:
                    #logging.debug("KM option " + kmOptionName + " Not changed")
                    pass

            #print(payload_doc)
            self.__update_dataflow_from_payload(payload_doc)

    #All the operators are pushed to a stack as and when they are called. 
    def from_source(self,operator_name,data_entity_name):
        """Defines the source data entity in data flow

        Arguments:
            operator_name -- source operator name
            data_entity_name -- fully qualified data entity name

        Returns:
            current object
        """
        logging.debug("data_entity_name {data_entity_name}")
        self.__load_operator_stack(SourceDataStore(operator_name,data_entity_name))
        return self

    def load(self,operator_name,data_entity_name,load_options=None):
        """Adds the target data entity to the data flow

        Arguments:
            operator_name -- target operator name
            data_entity_name -- fully qualified data entity name
                data entity to be used for loading to target

        Keyword Arguments:
            load_options -- _description_ (default: {None})

        Returns:
            current object
        """
        if load_options is None:
            load_options={}
            load_options[ "integrationType"]= "append"

        self.load_options=load_options

        self.__load_operator_stack(TargetDataStore(operator_name,data_entity_name,load_options))
        return self

    def join(self,join_name,join_type,join_condition):
        """Adds join operation in data flow

        Arguments:
            join_name -- operator name 
            join_type -- Must be one of JointType enum
            join_condition -- condition expression for JOIN operation

        Returns:
            _description_
        """
        self.__load_operator_stack(Join(join_name,join_type,join_condition))
        return self

    def filter_by(self,filter_name,filter_condition):
        """Adds filter operation in dataflow

        Arguments:
            filter_name -- operator name
            filter_condition -- condition expression for filter operation

        Returns:
            current object
        """
        self.__load_operator_stack(Filter(filter_name,filter_condition))
        return self

    def sort_by(self,sorter_name,sorter_condition):
        """Adds sorter operation in dataflow

        Arguments:
            sorter_name -- operator name
            sorter_condition -- condition for sorter operation

        Returns:
            current object
        """
        self.__load_operator_stack(Sorter(sorter_name,sorter_condition))
        return self

    def expression(self,expression_name,expression_attributes,retain_projected_cols=False):
        """Adds expression operation in dataflow

        Arguments:
            expression_name -- operator name
            expression_attributes -- List of expression attributes

        Returns:
            current object
        """
        self.__load_operator_stack(Expression(expression_name,expression_attributes,retain_projected_cols))
        return self

    def aggregate(self,aggregate_name,having_condition,manual_groupby,aggrregate_attributes,column_map,retain_projected_cols=False):
        """Adds aggregate operator in dataflow

        Arguments:
            aggregate_name -- operator name
            having_condition -- for aggregate operation
            manual_groupby -- group by column for aggregate operation
            aggrregate_attributes -- list of aggregate columns
            column_map -- dictionary of column map with aggregate expression

        Returns:
            current object
        """
        column_map["retain_projected_cols"]=retain_projected_cols
        self.__load_operator_stack(
            Aggregate(aggregate_name,having_condition,
                      manual_groupby,aggrregate_attributes,column_map))
        return self

    #set group expression
    #data entity UNION|+ data_entity MINUS|- data_entity
    def set_group(self,set_name,set_grouping_expression,colum_mappings):
        """Not certified"""
        self.__load_operator_stack(SetGroup(set_name,set_grouping_expression,colum_mappings))
        return self

    def data_cleanse(self,cleanse_name,participating_columns,cleanse_options):
        """Adds Data Cleanse operation in dataflow
        param: cleanse_name unique name of the datacleanse operation
        param: participating_columns list of columns involved in cleanse operation
        param: cleanse_options data cleaning strategies
        """
        self.__load_operator_stack(
            DataCleanse(cleanse_name=cleanse_name,participating_columns=participating_columns,
                        cleanse_options=cleanse_options))
        return self

    def predict(self,predict_name,prediction_attribute,paramters):
        """
        Adds predit operation in the datalfow 
        :param predit_name: unique name of the prediction step
        :param prediction_attribute: which need to be predicted
        :param parameters - required for predication operation
        """
        self.__load_operator_stack(MLPredict(predict_name,prediction_attribute,paramters))
        return self

    def lag(self,lag_name,lag_paramters):
        """Add lag operator with parameters in to dataflow
        :param lag_name: unique name given for the lag operation in dataflow
        """
        self.__load_operator_stack(Lag(lag_name,lag_paramters))
        return self

    def lookup(self,lookup_name,lookup_options):
        """Adds lookup operator the dataflow. Lookup must be provided with lookup_options
        dictionary, where set of options as key and value
        Lookup dictionary must have below items
        - Action to be taken when there are multiple matches (Default ALL ROWS )
        - Action to be taken when there are no matches (Default DEFAULT_VALUES)
        - Lookup condition
        - Driving Source
        - Lookup Source
        - Default Values - dictionary of column_name and default value for each column 
        """
        self.__load_operator_stack(Lookup(lookup_name,lookup_options))

    def path(self,from_operator,to_operator,options=None):
        """Adds the flow path from operator to another operator.
        SDK auto resolves the links between operations performed when it has max of two data sources.
        When dealing with more than two data sources, developer must explicitly specifiy the flow execution
        
        Note - options argument is ignored in current release. 

        Arguments:
            from_operator -- source operator 
            to_operator -- to operator to project

        Keyword Arguments:
            options -- _description_ (default: {None})
        """
        if not hasattr(self,"path_dict"):
            self.path_dict={}

        #get the list
        if not from_operator in self.path_dict.keys():
            self.path_dict[from_operator] = [to_operator]
            logging.debug("Path from " + from_operator + " added to " + to_operator)
            logging.debug(self.path_dict)
        else:
            to_nodes=self.path_dict[from_operator]
            to_nodes.append(to_operator)
            self.path_dict[from_operator] =to_nodes
            logging.debug("Path from " + from_operator + " added to " + to_operator)
            logging.debug(self.path_dict)
