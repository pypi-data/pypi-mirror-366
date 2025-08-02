'''
Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/.

Copyright (c) 2023-2025, Oracle and/or its affiliates.

'''
import json
import pandas as pd
from .rest import Rest
from .adp_misc import AdpMisc

class AdpDataframe():
    '''
    classdocs
    '''
    def __init__(self,table_name):
        '''
        Constructor
        '''
        self.utils = AdpMisc()
        self.rest=None
        self.table_name = table_name
        self.query = f"SELECT * FROM {table_name}"  # Default query
        self.conditions = []
        self.selected_columns = ["*"]
        self.group_by_columns = []
        self.aggregations = []
        self.joins = []
        

    def set_rest(self, rest: Rest):
        '''
            Set Rest instance

            @param rest (Rest): rest instance
        '''
        self.rest = rest
        self.utils.set_rest(rest)

    def select(self, *columns):
        """Select specific columns"""
        self.selected_columns = list(columns)
        return self

    def filter(self, condition):
        """Apply a WHERE filter"""
        self.conditions.append(condition)
        return self

    def group_by(self, *columns):
        """Group by specific columns"""
        self.group_by_columns = list(columns)
        return self

    def agg(self, **aggregations):
        """Apply multiple aggregations like SUM, AVG, COUNT"""
    
        if not isinstance(aggregations, dict):
            raise TypeError("Aggregations must be provided as keyword arguments, e.g., total_sales='SUM(SALES)'")

        if not self.aggregations:  
           self.aggregations = {}  # Initialize as a dictionary
    
        self.aggregations.update(aggregations)  # Merge new aggregations with existing ones

        return self


    def join(self, other, condition):
        """Perform SQL JOIN"""
        join_query = f"JOIN {other.table_name} ON {condition}"
        self.joins.append(join_query)
        return self

    def _build_query(self):
        """Build the SQL query dynamically with aggregations, filters, and group by."""
    
        # Default column selection
        select_columns = self.selected_columns if self.selected_columns != ["*"] else []
    
        # Add aggregations if provided
        agg_columns = []
        if isinstance(self.aggregations, dict) and self.aggregations:
           agg_columns = [f"{expr} AS {alias}" for alias, expr in self.aggregations.items()]

        if agg_columns:
           select_columns = self.group_by_columns + agg_columns if self.group_by_columns else agg_columns

        # Convert column selection to SQL format
        select_clause = ", ".join(select_columns) if select_columns else "*"
    
        query = f"SELECT {select_clause} FROM {self.table_name}"
    
        # Apply filters at the database level
        if self.conditions:
            query += " WHERE " + " AND ".join(self.conditions)
    
        # Apply GROUP BY if required
        if self.group_by_columns:
            query += f" GROUP BY {', '.join(self.group_by_columns)}"
    
        return query


    def show(self, limit=10):
        """Execute the query and show results"""
        query = self._build_query() + f" FETCH FIRST {limit} ROWS ONLY"
        js = self.utils.run_query(query)
        tn = pd.DataFrame.from_records(js)
        return tn

    def collect(self, limit=None, offset=0):
        """Execute query and return all results"""
        
        query = self._build_query()
        if limit is not None:
            query += f" OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
        js = self.utils.run_query(query)
        tn = pd.DataFrame.from_records(js)
        return tn

    def explain(self):
        """Show the current SQL query"""
        print("Generated SQL Query:")
        print(self._build_query())

