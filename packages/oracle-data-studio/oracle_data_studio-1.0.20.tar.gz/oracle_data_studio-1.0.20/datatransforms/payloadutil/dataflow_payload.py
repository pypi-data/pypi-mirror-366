'''
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

Class that generates payload JSON for the respective operators in data flow. 
Houses data flow payload model classes, that enable JSON payload generation

All the APIs provided here might change, hence it is not exposed for external developers
DataFlow operations must be used through DataFlow and Workbech APIs
'''

import uuid

# The class memebers directly conform to JSON payload needs of DataTransforms,
# not as per python variable conventions.
#Below line is to force pylint to ignore camel-case or snack-case style for this class

# pylint: disable=all
# pylint: disable=too-many-instance-attributes
class DataFlowPayload:
    """
    Represents the DataFlow JSON payload definition as per the DataTransforms contracts.
    """
    cleanupOnError=True
    attachedSchemas = []
    sources=[]
    targets=[]
    globalId=""
    sorters=[]

    def __init__(self,name,folder,project):
        """creates DataFlow JSON Representation 

        Arguments:
            name -- _description_
            folder -- _description_
            project -- _description_
        """
        self.description=None
        self.cleanupOnError=True
        self.name=name
        self.projectCode=project.upper()
        self.parentFolder=folder
        #self.project=project
        self.attachedSchemas=[]
        self.sources=[]
        self.targets=[]
        self.globalId=str(uuid.uuid4())
        self.joins=[]
        self.filters=[]
        self.sorters=[]
        self.expressions=[]
        self.aggregations=[]
        self.sets=[]
        self.dbfunc_datacleanses=[]
        self.dbfunc_decorators=[]
        self.lookups=[]

    def add_attached_schemas(self,schema):
        """Add the schemas referred in the Dataflow to JSON

        Arguments:
            schema -- the schema referenced by dataflow (as source or target)
        """
        self.attachedSchemas.extend(schema)

    def add_sources(self,sources):
        self.sources.extend(sources)

    def add_targets(self,targets):
        self.targets.extend(targets)

    def add_joins(self,joins):
        self.joins.extend(joins)

    def add_filters(self,filters):
        self.filters.extend(filters)

    def add_sorters(self,sorters):
        self.sorters.extend(sorters)

    def add_expressions(self,expressions):
        self.expressions.extend(expressions)

    def add_aggregates(self,aggregates):
        self.aggregations.extend(aggregates)

    def add_sets(self,set_operator):
        self.sets.extend(set_operator)

    def add_datacleanse(self,datacleanse_operator):
        self.dbfunc_datacleanses.extend(datacleanse_operator)

    def add_predicts(self,ml_predict_operator):
        self.dbfunc_decorators.extend(ml_predict_operator)

    def add_lags(self,lag_operator):
        self.dbfunc_decorators.extend(lag_operator)

    def add_lookup(self,lookup_operator):
        self.lookups.extend(lookup_operator)

class DataFlowSource:
    name=""
    type="DATASTORE",
    schemaName=""
    dataServerName=""
    boundToDataStoreName=""
    boundToDataStoreId=""
    connectedTo=[]
    attributes=[]

    def __init__(self,name="",type="DATASTORE",schemaName="",dataServerName="",boundToDataStoreName="",boundToDataStoreId="",connectedTo=""):
        self.name=name
        self.type=type
        self.schemaName=schemaName
        self.dataServerName=dataServerName
        self.boundToDataStoreName=boundToDataStoreName
        self.boundToDataStoreId=boundToDataStoreId
        self.attributes=[]
        self.connectedTo=[connectedTo]

    def add_attributes(self,attributes):
        self.attributes.extend(attributes)
    
    def get_attributes(self):
        return self.attributes
    
class DataFlowTarget:
    name=""
    type="DATASTORE",
    schemaName=""
    dataServerName=""
    boundToDataStoreName=""
    boundToDataStoreId=""
    connectedFrom=[]
    attributes=[]
    integrationType="CONTROL_APPEND"
    def __init__(self,name="",type="DATASTORE",schemaName="",dataServerName="",boundToDataStoreName="",boundToDataStoreId="",connectedFrom=[]):
        self.name=name
        self.schemaName=schemaName
        self.dataServerName=dataServerName
        self.boundToDataStoreName=boundToDataStoreName
        self.boundToDataStoreId=boundToDataStoreId
        self.connectedFrom=connectedFrom
        self.attributes=[]
        self.integrationType="CONTROL_APPEND"
        
    def add_attributes(self,attributes):
            self.attributes.extend(attributes)
    def integration_type(self,integration_type_value):
        self.integrationType=integration_type_value
        
class DataStoreAttributes:
    name=""
    globalId= None
    position=" 1"
    dataType=" VARCHAR2"
    dataTypeCode=" VARCHAR2"
    length=" 15"
    scale=None
    defaultValue=None
    isMandatory=False
    description=None
    shortDescription=""
    fileDescriptor=None
    boundTo=""
    expressions= {}
    key=None
    insert=True
    update=True
    checkNotNull=False
    
    def __init__(self,name,globalId= None,position="1",dataType=" VARCHAR2",dataTypeCode=" VARCHAR2", length=1,scale=None,defaultValue=None,isMandatory=None,boundTo=None,key=None,insert=True,update=True,checkNotNull=False):
        self.name=name
        self.globalId= None
        self.position=position
        self.dataType=dataType
        self.dataTypeCode=dataTypeCode
        self.length=length
        self.scale=scale
        self.defaultValue=defaultValue
        self.isMandatory=isMandatory
        self.description=None
        self.shortDescription=name
        self.fileDescriptor=None
        self.boundTo=boundTo
        self.expressions= {}
        self.key=key
        self.insert=insert
        self.update=update
        self.checkNotNull=checkNotNull
    
    def connected_from(self,connecting_attributes):
        self.connectedFrom=[]
        self.connectedFrom.append(connecting_attributes)

    def column_mapping_expression(self, col_mapping):
        self.expressions.update(col_mapping)

class DataFlowJoin:
    name=""
    type="JOIN"
    connectedTo=[]
    connectedFrom=[]
    joinCondition=""
    joinType=""
    joinSources=[]
    
    def __init__(self,name,joinCondition,joinType):
        self.name=name
        self.type="JOIN"
        self.connectedTo=[]
        joinSources,connectedFrom = self.__prepare_joinSources(joinCondition);
        #self.connectedFrom=connectedFrom
        self.joinCondition=joinCondition
        self.joinType=joinType
        self.joinSources=joinSources
        
    def add_connected_to(self,connectedTo):
        self.connectedTo.append(connectedTo)
        
    def __prepare_joinSources(self,joinCondition):
        joinSources=[]
        connectedFrom=[]
        
        joinCondition_array=joinCondition.split("=")
        left_component=joinCondition_array[0].strip().split(".")
        right_component=joinCondition_array[1].strip().split(".")

        connectedFrom.append(left_component[0])
        connectedFrom.append(right_component[0])
        
        #COmplex mapping - dont assume left and right are based on expressions.
        #joinSources.append(JoinSources("INPUT1",left_component[0],"LEFT"))
        #joinSources.append(JoinSources("INPUT2",right_component[0],"RIGHT"))
        
        return joinSources,connectedFrom
    
    def add_join_source(self, source_operator, left_or_right):
        input="INPUT"+str(len(self.joinSources)+1)
        self.joinSources.append(JoinSources(input,source_operator,left_or_right))

    def get_attributes(self):
        return None
    
class JoinSources:
        
        inputConnectorPoint=""
        inputComponentName=""
        sourceSide=""
        
        def __init__(self,inputConnectorPoint,inputComponentName,sourceSide):
            self.inputConnectorPoint=inputConnectorPoint
            self.inputComponentName=inputComponentName
            self.sourceSide=sourceSide
            

class DataFlowFilter:
    name=""
    type="FILTER"
    connectedTo=[]
    connectedFrom=[]
    filterCondition=""
    
    def __init__(self,name,filterCondition):
        self.name=name
        self.type="FILTER"
        self.filterCondition=filterCondition
        self.connectedFrom=[]
        self.connectedTo=[]

    def add_connected_to(self,connectedTo):
        self.connectedTo.append(connectedTo)
    
    def add_connected_from(self,connectedFrom):
        self.connectedFrom.append(connectedFrom)

    def get_attributes(self):
        return None
    
class DataFlowSorter:
    name=""
    type="SORTER"
    connectedTo=[]
    connectedFrom=[]
    sorterCondition=""

    def __init__(self,name,sorterCondition):
        self.name=name
        self.type="SORTER"
        self.sorterCondition=sorterCondition
        self.connectedFrom=[]
        self.connectedTo=[]
        
    def add_connected_to(self,connectedTo):
        self.connectedTo.append(connectedTo)
    
    def add_connected_from(self,connectedFrom):
        self.connectedFrom.append(connectedFrom)

    def get_attributes(self):
        return None
    
class DataFlowAggregateAtributes:
    
    def __init__(self):
        self.name=""
        self.globalId=""
        self.position=0
        self.description=""
        self.dataType=""
        self.dataTypeCode=""
        self.length=0
        self.scale=0
        self.format=""
        self.boundTo=""
        self.expressions={}
        self.isGroupBy="AUTO"

    def __init(self,name,globalId,position,description,dataType,dataTypeCode,length,scale,format,boundTo,expressions,isGroupBy):
        self.name=name
        self.globalId=globalId
        self.position=position
        self.description=description
        self.dataType=dataType
        self.dataTypeCode=dataTypeCode
        self.length=length
        self.scale=scale
        self.format=format
        self.boundTo=boundTo
        self.expressions={}
        self.expressions["INPUT1"]=expressions
        self.isGroupBy=isGroupBy

    def from_data_store_attribute(self,data_store_attribute):
        if isinstance(data_store_attribute,DataStoreAttributes):
            self.name=data_store_attribute.name
            self.globalId=data_store_attribute.globalId
            self.position=data_store_attribute.position
            self.description=data_store_attribute.description
            self.dataType=data_store_attribute.dataType
            self.dataTypeCode=data_store_attribute.dataTypeCode
            self.length=data_store_attribute.length
            self.scale=data_store_attribute.scale
            #self.format=data_store_attribute.format
            self.boundTo=data_store_attribute.boundTo
            self.expressions=data_store_attribute.expressions
            self.isGroupBy="NO"

    
    def to_data_store_attribute(self):
        datastoreattribute = DataStoreAttributes(self.name,self.globalId,self.position,self.dataType,self.dataTypeCode,self.length,self.scale,
                                                 None,None,self.boundTo)
        return datastoreattribute
    
class DataFlowAggregate:
    name=""
    type="AGGREGATE"
    connectedTo=[]
    connectedFrom=[]
    havingCondition=""
    manualGroupBy=""
    aggregateAttributes=[]
    groupByAttributes=[]

    def __init__(self,name):
        self.name=name
        self.globalId=""
        self.type="AGGREGATE"
        self.connectedFrom=[]
        self.connectedTo=[]
        self.havingCondition=""
        self.manualGroupBy=""
        self.aggregateAttributes=[]
        self.groupByAttributes=[]
    
    def connected_from(self,connectedFrom):
        self.connectedFrom.append(connectedFrom)
    
    def connected_to(self,connectedTo):
        self.connectedTo.append(connectedTo)

    def add_aggregate_attributes(self,dataflowAggregateAttributes):
        self.aggregateAttributes.extend(dataflowAggregateAttributes)
    
    def add_group_by_attributes(self,group_by_attributes):
        self.groupByAttributes.extend(group_by_attributes)

    def having_condition(self,having_condition):
        self.havingCondition=having_condition
    
    def manual_group_by(self,manual_group_by):
        self.manualGroupBy=manual_group_by

    def get_attributes(self):
        #TODO 
        return None

    def get_projected_attributes(self):
        attributes=[]
        for attribute in self.aggregateAttributes:
            attributes.append(attribute.to_data_store_attribute())
        
        for attribute in self.groupByAttributes:
            attributes.append(attribute.to_data_store_attribute())
        
        return attributes

class DataFlowSetOperator:
    def __init__(self,inputConnectorPoint,inputComponentName,setOperator):
        self.inputConnectorPoint=inputConnectorPoint
        self.inputComponentName=inputComponentName
        self.setOperator=setOperator

class DataFlowSet:

    def __init__(self,name):
        self.name=name
        self.globalId=None
        self.type="SET"
        self.connectedFrom=[]
        self.connectedTo=[]
        self.attributes=[]
        self.setOperators=[]
        self.globalId=str(uuid.uuid4())
        
    def set_operators(self,setOperators):
        self.setOperators=setOperators

    def connected_from(self,connectedFrom):
        self.connectedFrom=connectedFrom
    
    def connected_to(self,connectedTo):
        self.connectedTo=connectedTo

    def set_attributes(self,attributes):
        self.attributes.extend(attributes)

    def set_attributes(self,attributes):
        self.attributes.extend(attributes)

    def get_attributes(self):
        #TODO
        return None

class DataFlowDataCleanse:
    def __init__(self,name):
        self.name=name
        self.type="EXPRESSION"
        self.connectedFrom=[]
        self.connectedTo=[]
        self.attributes=[]
        self.cleansingOptions={}
        self.globalId=str(uuid.uuid4())

    def connected_from(self,connectedFrom):
        self.connectedFrom.append(connectedFrom)
    
    def connected_to(self,connectedTo):
        self.connectedTo.append(connectedTo)

    def cleanse_attributes(self,attributes,participating_columns):
        new_attrs=[]
        for attr in attributes:
            setattr(attr,"title",attr.name)
            setattr(attr,"code",attr.expressions["INPUT1"])
            if participating_columns!= None and attr.name in participating_columns:
                setattr(attr,"includeForCleanse",True)
            else:
                setattr(attr,"includeForCleanse",False)

            delattr (attr, "insert")
            delattr (attr, "update")
            delattr (attr, "checkNotNull")
            delattr (attr, "defaultValue")
            delattr (attr, "isMandatory")
            delattr (attr, "description")
            delattr (attr, "shortDescription")
            delattr (attr, "fileDescriptor")
            delattr (attr, "boundTo")
            delattr (attr, "position")
            
            new_attrs.append(attr)
                    
        self.attributes.extend(new_attrs)

    def get_attributes(self):
        #return None
    
        #print("Returning attribute from Cleanse")
        #print(str(type(self.attributes)))
        # for entry in self.attributes:
        #     print(str(entry))
        return self.attributes


class DataFlowMLPredict:
    def __init__(self,name):
        self.name=name
        self.type="DATABASEFUNCTION_DECORATOR"
        self.functionName= "Prediction"
        self.functionSignature= "PREDICTION(FOR prediction attribute USING prediction parameters) over()"
        self.connectedFrom=[]
        self.connectedTo=[]
        self.inputConnections=[]
        self.outputAttributes=[]
        self.globalId=str(uuid.uuid4())

    def connected_from(self,connectedFrom):
        self.connectedFrom.append(connectedFrom)
    
    def connected_to(self,connectedTo):
        self.connectedTo.append(connectedTo)

    def predict_attributes(self,prediction_attribute,parameters):
        input_attrs=[self.__prepare_inputs(prediction_attribute),
                         self.__prepare_inputs2(parameters)]

        inputAttributes={
            "inputAttributes" : input_attrs,
            "inputConnectorPoint": "INPUT1",
            "inputComponentName": self.connectedFrom[0]
        }

        self.inputConnections.append(inputAttributes)
        self.outputAttributes.append(self.__get_output_attrs())

    def __prepare_inputs(self,prediction_attribute):
        input_dict={}
        input_dict["dataType"]="VARCHAR2"
        input_dict["dataTypeCode"]="VARCHAR"
        input_dict["name"]="prediction attribute"
        input_dict["expressions"]={"INPUT1": prediction_attribute }
        return input_dict

    def __prepare_inputs2(self,params):
        input_dict={}
        input_dict["dataType"]="VARCHAR2"
        input_dict["dataTypeCode"]="VARCHAR"
        input_dict["name"]="prediction parameters"
        input_dict["expressions"]={"INPUT1":  params }
        return input_dict
    
    def __get_output_attrs(self):
        output_attr={
                    "Help": "refers to the output of prediction",
                    "dataType": "VARCHAR2",
                    "name": "predicted",
                    "expressions": {
                        "INPUT1": None
                    },
                    "dataTypeCode": "VARCHAR"
                }
        return output_attr
    
    def get_attributes(self):
        return None
    
        # print("Returning attribute from Cleanse")
        # print(str(type(self.attributes)))
        # for entry in self.attributes:
        #     print(str(entry))
        return self.attributes

class DataFlowLag:

    def __init__(self,name):
        self.name=name
        self.type="DATABASEFUNCTION_DECORATOR"
        self.functionName= "Lag"
        self.functionSignature= "LAG(expression,[offset],[default]) OVER (PARTITION BY [partition] ORDER BY order)"
        self.connectedFrom=[]
        self.connectedTo=[]
        self.inputConnections=[]
        self.outputAttributes=[]
        self.globalId=str(uuid.uuid4())

    def connected_from(self,connectedFrom):
        self.connectedFrom.append(connectedFrom)
    
    def connected_to(self,connectedTo):
        self.connectedTo.append(connectedTo)

    def process_lag_attributes(self,lag_params):
        input_attrs=[self.__prepare_inputs(lag_params),
                         self.__prepare_inputs2(lag_params),
                         self.__prepare_order(lag_params)]

        inputAttributes={
            "inputAttributes" : input_attrs,
            "inputConnectorPoint": "INPUT1",
            "inputComponentName": self.connectedFrom[0]
        }

        self.inputConnections.append(inputAttributes)
        self.outputAttributes.append(self.__get_output_attrs())


    def __prepare_inputs(self,params):
        input_dict={}
        input_dict["dataType"]="VARCHAR2"
        input_dict["dataTypeCode"]="VARCHAR"
        input_dict["name"]="expression"
        input_dict["expressions"]={"INPUT1": params["expression"] }
        return input_dict

    def __prepare_inputs2(self,params):
        input_dict={}
        input_dict["dataType"]="VARCHAR2"
        input_dict["dataTypeCode"]="VARCHAR"
        input_dict["name"]="[partition]"
        input_dict["expressions"]={"INPUT1":  params["[partition]"] }
        return input_dict

    def __prepare_order(self,params):
        input_dict={}
        input_dict["dataType"]="VARCHAR2"
        input_dict["dataTypeCode"]="VARCHAR"
        input_dict["name"]="order"
        input_dict["expressions"]={"INPUT1":  params["order"] }

        return input_dict
    def __get_output_attrs(self):
        output_attr={
                    "Help": "refers to the output of prediction",
                    "dataType": "VARCHAR2",
                    "name": "predicted",
                    "expressions": {
                        "INPUT1": None
                    },
                    "dataTypeCode": "VARCHAR"
                }
        return output_attr

    def get_attributes(self):
        return None
class DataFlowExpressionAttributes:
    
    def __init__(self,name,dataType,dataTypeCode,position,length,scale,connectedFrom):

        self.name=name
        self.globalId=None
        self.dataType=dataType
        self.dataTypeCode=dataTypeCode
        self.position=position
        self.length=length
        self.scale=scale
        self.format=None
        self.boundTo=""
        self.expressions={}
        self.expressions["INPUT1"]=connectedFrom
        self.connectedFrom=connectedFrom

    def connected_from(self,connectedFrom):
        self.connectedFrom=connectedFrom
    
    def custom_expression(self,expression):
        expression_key="INPUT" + str(len(self.expressions.keys())+1)
        self.expressions[expression_key]=expression

class DataFlowExpression:

    def __init__(self,name):
        self.name=name
        self.globalId=None
        self.type="EXPRESSION"
        self.connectedFrom=[]
        self.connectedTo=[]
        self.attributes=[]

    def connected_from(self,connectedFrom):
        self.connectedFrom.append(connectedFrom)

    def connected_to(self,connectedTo):
        self.connectedTo.append(connectedTo)

    def expression_attributes(self,attributes):
        self.attributes.extend(attributes)

    def get_attributes(self):
        return self.attributes

class ColumnDefinition:

    """Creates column representation in expression. Typically used 
    when a expression node is introduced in dataflow and a new column is created from 
    existing column or a column is changed using an expression
    """
    def __init__(self,name,globalId,data_type,length,scale,position):
        """Prepares column definition model for expression

        Arguments:
            name -- name of the expression column
            globalId -- If it is already available, otherwise None
            data_type -- data type of the newly introduced column 
            length -- max length of the column 
            scale -- scale of the column 
            position -- Order in which it appears in payload
        """
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

    def custom_expressions(self,custom_expressions):
        """Prepares custom expression nodes 

        Arguments:
            custom_expressions -- array of expressions defined by the developers
        """
        self.expressions={}
        self.expressions=custom_expressions

    def expression_source_column(self,connectedFrom):
        """Attaches source node to expression

        Arguments:
            connectedFrom -- operator name which is source for expression
        """
        self.connectedFrom.extend(connectedFrom)
