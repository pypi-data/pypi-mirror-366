'''
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

Houses data transforms model classes
'''
# pylint: disable=invalid-name

class DataTransformsModelException(Exception):
    """Generic Exception for DataTransforms"""
    def __init__(self, *args):
        super().__init__(*args)

class RefDataEntity:
    """Represents Referenced data entity in dataflows
    """
    def name(self):
        """Returms Data entity name

        Returns:
            data entity name
        """
        return self.data_entity_name

    def alias_name(self):
        """Returns alias name of data entity

        Returns:
            alias name 
        """
        return self.entity_alias_name

    def resolved_name(self):
        """Returns resolved name of the data entity

        Returns:
            resolved name of the data entity
        """
        return self.resolved_store_name

    def load_from_json(self,data_entity_definition,resolved_store_name,entity_alias_name=None):
        """Prepares data entity objecf from existing JSON document

        Arguments:
            data_entity_definition -- _description_
            resolved_store_name -- _description_

        Keyword Arguments:
            entity_alias_name -- _description_ (default: {None})

        Returns:
            _description_
        """
        #pylint: disable=attribute-defined-outside-init
        self.entity_alias_name=entity_alias_name
        self.json_definition = data_entity_definition
        self.data_entity_name=self.json_definition["name"]
        self.global_id=self.json_definition["globalId"]
        self.resolved_store_name=resolved_store_name
        return self

    def column_names(self):
        """Returns columnn names in data entity

        Returns:
            list of column names
        """
        column_names=[]
        columns = self.json_definition["columns"]
        for column in columns:
            column_names.append(column["name"])
        return column_names

    def resolved_columns(self):
        """Returns list of resolved columns

        Returns:
            list of resolved columns
        """
        name=self.name()
        alias_name = self.alias_name()
        if alias_name is not None:
            name=alias_name

        column_names=self.column_names()
        resolved_columns = {}
        for column_name in column_names:
            resolved_columns[column_name]=name+"."+column_name
        return resolved_columns

    def resolve_column_name(self,col_name):
        """Resolves the given column name to fully qualified data entity name

        Arguments:
            col_name -- input column name

        Raises:
            DataTransformsModelException: when column name doesn't exist 

        Returns:
            fully qualified column name (dataentityname.columnname)
        """
        alias_name = self.alias_name()
        if alias_name is not None:
            name=alias_name
        else:
            name=self.name()

        if col_name in self.column_names():
            return name+"."+col_name
        else:
            raise DataTransformsModelException(
                "Invalid column " + col_name + " not found in " + self.name())


class OperatorAttributes:
    """Attribute definitions of the operator
    """
    def __init__(self,operator_name,source_data_entity):
        self.operator_name=operator_name
        self.source_data_entity=source_data_entity
        self.custom_column_map={}

    def override(self,custom_map):
        """Updates the mapping with given one

        Arguments:
            custom_map -- dictionary of column map
        """
        self.custom_column_map.update(custom_map)


class SimpleColumnMapping:
    """Enables column mapping by name
    """
    def __init__(self,target_data_entity,sources):
        self.target_data_entity = target_data_entity
        self.sources = sources

    def prepare_column_mapping(self,auto_map="By Name",fail_if_missing=True):
        """prepare_column_mapping

        Keyword Arguments:
            auto_map -- _description_ (default: {"By Name"})
            fail_if_missing -- _description_ (default: {True})

        Raises:
            DataTransformsModelException: if fail_if_missing is set to True and 
            not all the column(s) have corresponding matching column(s) to map

        Returns:
            dictionary of mapped columns
        """
        #pylint: disable=attribute-defined-outside-init

        self.auto_map=auto_map
        self.fail_if_missing=fail_if_missing

        simple_col_map_by_name = {}
        target_column_names = self.target_data_entity.column_names()
        resolved_source_column_names = {}
        for de in self.sources:
            resolved_source_column_names.update(de.resolved_columns())

        missing=[]
        for e in target_column_names:
            #pylint: disable=consider-iterating-dictionary
            if e not in resolved_source_column_names.keys():
                missing.append(e)
            else:
                target_col_name=self.target_data_entity.resolve_column_name(e)

                simple_col_map_by_name[target_col_name]=resolved_source_column_names[e]

        if len(missing) !=0 and fail_if_missing is True:
            raise DataTransformsModelException(
                "Some of the column(s) in target are not available for automap")

        return simple_col_map_by_name
