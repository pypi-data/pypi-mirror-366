'''
Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/.

Copyright (c) 2023-2025, Oracle and/or its affiliates.

'''

import os

class DbUtils():
    '''
    Class for working with client credentials
    '''

    def __init__(self):
        self.cursor = None

    def set_cursor(self, cursor) ->None:
        '''
            Set DB cursor instance
        '''
        self.cursor = cursor


    def get_client(self) -> str:
        '''
            Get creadentials. If it does not exist, create new one
        '''
        text = self._select_client()
        if text is None:
            try:
                sql = """
                    BEGIN
                        OAUTH.create_client(
                            p_name            => 'python_client',
                            p_grant_type      => 'client_credentials',
                            p_owner           => '{0}',
                            p_description     => 'A client for ORDS Python REST resources',
                            p_support_email   => 'support@oracle.com',
                            p_privilege_names => 'my_priv'
                        );

                        OAUTH.grant_client_role(
                            p_client_name => 'python_client',
                            p_role_name   => 'SQL Developer'
                        );

                        OAUTH.grant_client_role(
                            p_client_name => 'python_client',
                            p_role_name   => 'SODA Developer'
                        );
                        COMMIT;
                        END;"""
                self.cursor.execute(sql.format(self.get_username()))

            except Exception as exp:
                raise AdpError('Creating Client Id and client secret is faiied') from exp

            return self._select_client()
        return text

    def _select_client(self) ->str:
        '''
            get client id and client secret
        '''

        try:
            client_id = None
            client_secret  = None
            sql = "select client_id, client_secret from ords_metadata.user_ords_clients where name='python_client'"
            self.cursor.execute(sql)
            for client_id, client_secret in self.cursor:
                text = client_id + ":" + client_secret
                return text
        except Exception as exp:
            raise AdpError('Client Id and/or client secret are not defined') from exp
        return None

    def get_url(self) -> str:
        '''
            Construct Url
        '''
        try:
            sql = "SELECT SYS_CONTEXT('USERENV', 'CON_NAME') PDB_NAME, SYS_CONTEXT('USERENV','CLOUD_DOMAIN') PUBLIC_DOMAIN_NAME FROM SYS.DUAL"
            self.cursor.execute(sql)
            columns = [col[0] for col in self.cursor.description]
            self.cursor.rowfactory = lambda *args: dict(zip(columns, args))
            row = self.cursor.fetchone()
            first_part = row["PDB_NAME"]
            second_part = row["PUBLIC_DOMAIN_NAME"]
            url = "https://" + first_part.replace("_", "-").lower() + "." + second_part.replace("oraclecloud","oraclecloudapps")

        except Exception:
            url = os.environ['ORDS_URL']
        return url


    def get_username(self) -> str:
        '''
            Get username
        '''

        sql = "SELECT USER FROM SYS.DUAL"
        self.cursor.execute(sql)
        columns = [col[0] for col in self.cursor.description]
        self.cursor.rowfactory = lambda *args: dict(zip(columns, args))
        row = self.cursor.fetchone()

        user = row["USER"]

        return user


class AdpError(Exception):
    '''
    Class to raise exceptions
    '''
