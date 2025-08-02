'''
    Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

    Copyright (c) 2023-2025, Oracle and/or its affiliates.

'''

import json
from typing import Tuple, List
from .adp_misc import AdpMisc
from .rest import Rest

class AdpAI():
    '''
    Class to interact with DBMS_CLOUD_AI via REST and generate AI-based SQL or insights.
    '''
    def __init__(self) -> None:
        self.response_format = {
            'resultSetMetadata': False,
            'statementInformation': False,
            'statementText': False,
            'binds': False,
            'result': True,
            'response': False
        }
        self.utils = AdpMisc()
        self.rest = None
        self.profile = None
        self.tables = None  # List of (owner, table) tuples

    def set_rest(self, rest: Rest) -> None:
        '''
        Set Rest instance and pass it to utility functions.
        '''
        self.rest = rest
        self.utils.set_rest(rest)

    def setProfile(self, profile_name: str) -> None:
        '''
        Set default select AI profile name to use (e.g., "OPENAI")
        '''
        self.profile = profile_name

    def setTables(self, tables: List[Tuple[str, str]]) -> None:
        '''
        Set default list of tables for context.

        @param tables: List of (owner, table_name) tuples
        '''
        self.tables = tables

    def setTable(self, table_name: str, table_owner: str = None) -> None:
        '''
        Backward-compatible method for setting a single table.

        @param table_name: Table name
        @param table_owner: Schema/Owner (defaults to rest.username)
        '''
        if table_owner is None:
            table_owner = self.rest.username
        self.tables = [(table_owner, table_name)]

    def _format_object_list(self, tables: List[Tuple[str, str]] = None) -> str:
        '''
        Format tables into JSON string for DBMS_CLOUD_AI attributes.

        @param tables: Optional list of (owner, table_name) tuples
        @return: JSON string for object_list
        '''
        if tables is None:
            tables = self.tables
        if not tables:
            raise ValueError("No tables provided or set with setTables().")
        obj_list = [{"owner": owner, "name": name} for owner, name in tables]
        return json.dumps({"object_list": obj_list})

    def generate_sql_query(self, prompt: str, tables: List[Tuple[str, str]] = None, profile_name: str = None) -> str:
        '''
        Generate an AI-based SQL query.

        @param prompt: Instruction or question for AI
        @param tables: List of (owner, table) tuples
        @param profile_name: AI profile to use
        @return: SQL string
        '''
        if profile_name is None:
            profile_name = self.profile
        attributes_json = self._format_object_list(tables)
        statement = f"""
        SELECT DBMS_CLOUD_AI.GENERATE(
            prompt => '{prompt}',
            profile_name => '{profile_name}',
            action => 'showsql',
            attributes => '{attributes_json}'
        ) FROM dual;
        """
        response = self.utils.run_query(statement)
        return self._extract_result(response)

    def generate_insight(self, prompt: str, tables: List[Tuple[str, str]] = None, profile_name: str = None) -> str:
        '''
        Generate AI-based insights from tables.

        @param prompt: Insight instruction
        @param tables: List of (owner, table) tuples
        @param profile_name: AI profile
        @return: AI-generated insights
        '''
        if profile_name is None:
            profile_name = self.profile
        attributes_json = self._format_object_list(tables)
        statement = f"""
        SELECT DBMS_CLOUD_AI.GENERATE(
            prompt => '{prompt}',
            profile_name => '{profile_name}',
            action => 'chat',
            attributes => '{attributes_json}'
        ) FROM dual;
        """
        response = self.utils.run_query(statement)
        return self._extract_result(response)

    def chat_with_db(self, prompt: str, tables: List[Tuple[str, str]] = None, profile_name: str = None) -> str:
        '''
        Chat with the database using AI on specified tables.

        @param prompt: Instruction or question
        @param tables: List of (owner, table) tuples
        @param profile_name: AI profile
        @return: AI response
        '''
        if profile_name is None:
            profile_name = self.profile
        attributes_json = self._format_object_list(tables)
        self.utils.run_query(
            f"SELECT DBMS_CLOUD_AI.SET_ATTRIBUTE('{profile_name}', 'conversation', 'true') FROM dual"
        )
        statement = f"""
        SELECT DBMS_CLOUD_AI.GENERATE(
            prompt => '{prompt}',
            profile_name => '{profile_name}',
            attributes => '{attributes_json}'
        ) FROM dual;
        """
        response = self.utils.run_query(statement)
        response = self.utils.run_query(self._extract_result(response))
        return response

    def chat(self, prompt: str, profile_name: str = None) -> str:
        '''
        Generic chat with AI, not tied to specific tables.

        @param prompt: Chat prompt
        @param profile_name: AI profile
        @return: AI response
        '''
        if profile_name is None:
            profile_name = self.profile
        statement = f"""
        SELECT DBMS_CLOUD_AI.GENERATE(
            prompt => '{prompt}',
            profile_name => '{profile_name}',
            action => 'chat'
        ) FROM dual;
        """
        response = self.utils.run_query(statement)
        return self._extract_result(response)

    def _extract_result(self, response: list) -> str:
        '''
        Extract result from DBMS_CLOUD_AI response.

        @param response: ORDS-style list of dictionaries
        @return: Extracted result string
        '''
        try:
            if isinstance(response, list) and len(response) > 0:
                first_dict = response[0]
                return list(first_dict.values())[0]
            return "No valid response received from AI."
        except (IndexError, TypeError):
            return "No valid response received from AI."

