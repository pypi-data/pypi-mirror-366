'''
Licensed under the Universal Permissive License v 1.0 as shown at
https://oss.oracle.com/licenses/upl/.

Copyright (c) 2025, Oracle and/or its affiliates.

'''

import json
from typing import Union
from .rest import Rest
from .adp_misc import AdpMisc
from requests.exceptions import HTTPError

class AdpCatalog():
    '''
    classdocs
    '''
    def __init__(self) -> None:
        '''
        Constructor
        '''
        self.rest = None
        self.misc = None
        self.status = 0

    def set_rest(self, rest : Rest) -> None:
        '''
        Set Rest instance
        @param rest (Rest): rest instance
        '''
        self.rest = rest
        self.misc = AdpMisc()
        self.misc.set_rest(rest)

    def __set_none (self, type_ : str, val_ : str) -> str:
        '''
            Set none or missing value
            @param type (String): none or missing value
            @param value (String): default value
        '''
        _type = val_ if type_ is None else type_
        return _type

    def __get(self, url : str, payload : dict) -> object:
        '''
        GET rest object response
        @param payload (Dictionary): request payload
        '''
        res = self.rest.get_obj(url, payload)
        self.status = res.status_code
        return res

    def __post(self, url : str, payload : dict, timeout : int = 180) -> object:
        '''
        POST rest object response
        @param payload (Dictionary): request payload
        @param timeout (int): timeout integer
        '''
        res = self.rest.post_obj(url, payload, timeout)
        self.status = res.status_code
        return res

    def __find(self,
               element : str,
               json_    : dict) -> object:
        '''
        Get json dictionary value by element path
        @param element (String): element path 'x.y.z'
        @param json (Dictionary): json object
        '''
        try:
            keys = element.split('.')
            rv = json_
            for key in keys:
                rv = rv[key]
        except KeyError:
            rv = None
        return rv

    def __frmt_jsn_arr(self,
                       jsn_arr : dict,
                       val_lst : list,
                       sep     : str = '.') -> dict:
        '''
        Reformat json array by provided list of values
        @param jsn_arr (Dictionary): json dictionary array
        @param val_lst (List): json keys array
        @param sep (String): Keys separator
        '''
        a_tmp = []
        for x in jsn_arr :
            d_tmp = {}
            for l in val_lst:
                d_tmp_val = self.__find(l, x)
                if d_tmp_val is not None:
                    keys = l.split(sep)
                    key  = keys[len(keys) - 1]
                    d_tmp[key] = d_tmp_val
            if bool(d_tmp):
                a_tmp.append(d_tmp)
        return a_tmp

    def __f_catalogs_cols (self, res : dict) -> dict :
        '''
        Filter catalogs columns
        @param res (String): Rest response dictionary object
        '''
        res_ = res['nodes']
        cols = ['label',
                'type',
                'id',
                'data.annotation.details',
                'data.annotation.enabled',
                'data.created',
                'data.updated']
        _res = self.__frmt_jsn_arr(res_, cols)
        return _res

    def __f_catalog_ent_cols (self, res : dict) -> dict :
        '''
        Filter catalog entities columns
        @param res (String): Rest response dictionary object
        '''
        res_ = res['nodes']
        cols = ['label',
                 'type',
                 'data.schema',
                 'id',
                 'data.annotation.details',
                 'data.annotation.enabled',
                 'data.created',
                 'data.updated']
        _res = self.__frmt_jsn_arr(res_, cols)
        return _res

    def __f_db_links_cols (self, res : dict) -> dict :
        '''
        Filter db links columns
        @param res (String): Rest response dictionary object
        '''
        res_ = res['nodes']
        cols = ['label',
                'type',
                'data.catalog',
                'data.application',
                'data.annotation.credentialName',
                'data.annotation.credentialOwner',
                'data.annotation.hidden',
                'data.annotation.valid',
                'data.created',
                'data.updated']
        _res = self.__frmt_jsn_arr(res_, cols)
        return _res

    def __f_adb_cols (self, res : dict) -> dict :
        '''
        Filter adb columns
        @param res (String): Rest response dictionary object
        '''
        res_ = res['nodes']
        # 'data.compartment',
        cols = ['label',
                'type',
                'data.catalog',
                'data.application',
                'data.schema',
                'data.annotation.workloadType',
                'data.annotation.adbType',
                'data.annotation.lifecycleState',
                'data.annotation.ocid',
                'data.created',
                'data.updated']
        _res = self.__frmt_jsn_arr(res_, cols)
        return _res

    #----------------------------------------------------------------------------

    #-- Catalog API

    #----------------------------------------------------------------------------

    def __get_objects (self,
                        url          : str,
                        search_query : str,
                        searchscope  : str = 'ALL_OBJECTS',
                        scopeowner   : str = 'C##ADP$SERVICE') -> dict:
        '''
        List objects
        @param url (String): url string
            - _adplmd/_services/objects/search/
            - _adplmd/_services/objects/v2/search/
        @param search_query (String): search query text
        examples:
            - (owner: ADMIN type: DB_LINK, CATALOG) OR type: AUTONOMOUS_DATABASE
            - catalog: LOCAL owner: ADMIN type: DB_LINK
            - type: CATALOG
        @param searchscope (String): catalog searchscope
        '''
        payload = {
            "search"      : search_query,
            "searchscope" : searchscope,
            "rowstart"    : 1,
            "hideprivate" : True,
            "hidesys"     : True,
            "scopeowner"  : scopeowner,
            "numrows"     : 1000,
            "maxlimit"    : 1000
        }
        res = self.__get (url, payload)
        res = res.json()
        return res

    def get_catalogs (self, search : str = None) -> str:
        '''
        Get catalogs
        @param search (String): catalog name search parameter
        '''
        url = "/_adplmd/_services/objects/search/"
        o = self.rest.username
        s = 'owner : {0} type: CATALOG'.format(o.upper())
        s = s + ' {0}'.format(str(search)) if search is not None else s
        res = self.__get_objects(url, s)
        res = self.__f_catalogs_cols(res) if self.status == 200 else res
        res = json.dumps(res)
        return res

    def get_catalog_entities (self,
                               catalog_name : str,
                               type         : str = 'TABLE',
                               search       : str = None) -> str:
        '''
        Get catalog entities
        @param catalog_name (String): catalog name
        @param type (String): entity type (TABLE, SCHEMA, etc.)
        @param search (String): search text
        '''
        url = "/_adplmd/_services/objects/v2/search/"
        s = 'catalog: {0} type: {1}'.format(
            str(catalog_name).strip().upper(),
            str(type).strip().upper())
        s = s + ' {0}'.format(str(search)) if search is not None else s
        res = self.__get_objects(url, s)
        res = self.__f_catalog_ent_cols(res) if self.status == 200 else res
        res = json.dumps(res)
        return res

    def get_database_links (self,
                        catalog_name : str = None,
                        owner        : str = None,
                        search       : str = None) -> str:
        '''
        Get database links
        @param catalog_name (String): catalog name
        @param owner (String): catalog owner
        @param search (String): search text
        '''
        url = "/_adplmd/_services/objects/search/"
        s = 'catalog: {0} owner: {1} type: DB_LINK'
        c = self.__set_none(catalog_name, 'LOCAL')
        o = self.__set_none(owner, self.rest.username)
        s = s.format(c, o)
        s = s + ' {0}'.format(str(search)) if search is not None else s
        res = self.__get_objects(url, s)
        res = self.__f_db_links_cols(res) if self.status == 200 else res
        res = json.dumps(res)
        return res

    def get_autonomous_databases (self, search : str = None) -> str:
        '''
        Get autonomous databases
        @param catalog_name (String): catalog name
        @param type (String): entity type (TABLE, SCHEMA, etc.)
        @param search (String): search text
        '''
        url = "/_adplmd/_services/objects/search/"
        s = 'type: AUTONOMOUS_DATABASE'
        s = s + ' {0}'.format(str(search)) if search is not None else s
        res = self.__get_objects(url, s)
        res = self.__f_adb_cols(res) if self.status == 200 else res
        res = json.dumps(res)
        return res

    def __get_oci_data_catalogs (self, credential_name: str) -> object:
        '''
        Get data catalogs object id for user specified credential
        @param credential_name (String): credential name
        '''
        url = '/_adpdi/_services/data-catalogs/catalogs/'
        payload = {
            "credentialName" : credential_name
        }
        res = self.__get (url, payload)
        return res

    def get_oci_data_catalogs (self, credential_name: str) -> str:
        '''
        Get data catalogs string for user specified credential
        @param credential_name (String): credential name
        '''
        res = self.__get_oci_data_catalogs (credential_name)
        return res.text

    def preview_catalog_table (self,
                            catalog_name : str,
                            table_name   : str,
                            schema_name  : str = None,
                            row_limit    : int = 100) -> Union[str, list]:
        '''
        List catalogs
        @param catalog_name (String): catalog name
        @param table_name (String): table name
        @param schema_name (String): schema name
        @param row_limit (String): row limit
        '''
        url = '/_adplmd/_services/objects/generate-table-select/'
        sch = self.__set_none(schema_name, self.rest.username)
        payload = {
            "catalog_name" : catalog_name,
            "table_name"   : table_name,
            "schema_name"  : sch,
            "row_limit"    : row_limit
        }
        get = self.__get(url, payload)
        get = get.json()
        if self.status == 200:
            qry = get['statement']
            res = self.misc.run_query(qry)
        else:
            res = json.dumps(get)
        return res

    def enable_catalog(self, catalog_name : str) -> str:
        '''
        Enable catalog
        @param catalog_name (String): catalog name
        '''
        url = '/_adplmd/_services/objects/catalog/enable'
        payload = {
            "catalog_name" : catalog_name,
            "public"       : False
        }
        res = self.__post(url, payload)
        return res.text

    def disable_catalog(self, catalog_name : str) -> str:
        '''
        Disable catalog
        @param catalog_name (String): catalog name
        '''
        url = '/_adplmd/_services/objects/catalog/disable'
        payload = {
            "catalog_name" : catalog_name,
            "public"       : False
        }
        res = self.__post(url, payload)
        return res.text

    def unmount_catalog(self, catalog_name : str) -> str:
        '''
        Unmount (remove) catalog
        @param catalog_name (String): catalog name
        '''
        url = '/_adplmd/_services/objects/catalog/unmount'
        payload = {
            "catalog_name" : catalog_name,
            "public"       : False
        }
        res = self.__post(url, payload)
        return res.text

    #---------------------------------------------------------------------------
    #-- Database link functions
    #-- Mount Database Link Catalog
    #---------------------------------------------------------------------------
    def exist_database_link (self,
        database_link_name) -> str:
        '''
        Get database link
        @param database_link_name (String): database link name
        '''
        sts = False
        l = database_link_name
        try :
            s = self.get_database_links()
            j = json.loads(s)
            f = next(filter(lambda x: x['label'] == l, j), None)
        except :
            res = {"status" : sts, "message" : s}
            return json.dumps(res)
        else :
            if f is None:
                m = f'The Database link {l} does not exist.'
            else :
                sts = True
                m = f'The Database link {l} exist.'
            res = {"status" : sts, "message" : m}
            return json.dumps(res)

    def check_database_link (self,
        database_link_name) -> str:
        '''
        Check database link
        @param database_link_name (String): database link name
        '''
        s = False
        l = database_link_name
        m = f'The database link {l} is not valid.'
        g = self.exist_database_link(l)
        j = json.loads(g)
        if j["status"]:
            try :
                q = f'select 2 from dual@{l}'
                q = self.misc.run_query(q)
            except :
                r = {"status" : s, "message" : q}
                return json.dumps(r)
            else :
                s = True
                q = q[0]
                q = q["2"]
                if q == 2 :
                    m = f'The database link {l} is valid.'
                    r = {"status" : s, "message" : m}
                else :
                    m = f'The database link {l} is not valid.'
                    r = {"status" : s, "message" : m}
                return json.dumps(r)
        r = {"status" : s, "message" : j["message"]}
        return json.dumps(r)

    def drop_database_link (self,
        database_link_name) -> str:
        '''
        Drop database link
        @param database_link_name (String): database link name
        '''
        s = self.check_database_link(database_link_name)
        s = json.loads(s)
        if s["status"] :
            try :
                l = database_link_name
                q = f'''
                BEGIN
                "C##CLOUD$SERVICE".DBMS_CLOUD_ADMIN.DROP_DATABASE_LINK(\'{l}\');
                END;
                /'''
                r = self.misc.run_query(q)
            except :
                r = {"status"  : False,
                     "message" : "An unexpected error occurred."}
            else :
                r = {"status" : True, "message" : r}
        else :
            r = {"status" : False, "message" : s["message"]}
        return json.dumps(r)

    #----------------------------------------------------------------------------
    #-- Mount Database link Catalog
    #-- Mount Autonomous Database Catalog
    #----------------------------------------------------------------------------

    def __set_adb_link (self,
                    database_link   : str,
                    database_name   : str,
                    credential_name : str) -> str:
        '''
        Set data base link to autonomous database
        @param database_link (String): database link name
        @param database_name (String): autonomous database name
        @param credential_name (String): credential name
        '''

        #extract adb ocid value
        adbl = json.loads(self.get_autonomous_databases())
        ocid = None
        for adb in adbl:
            if 'label' in adb:
                lbl = adb['label']
                if lbl.strip().lower() == database_name.strip().lower():
                    ocid = adb['ocid']
                    break
        # create db link
        res = None
        url = '/_adplmd/_services/objects/database-links/'
        payload = {
            "name"            : database_link,
            "credential_name" : credential_name,
            "ocid"            : ocid,
            "run_mode"        : 'codeRun'}
        res = self.__post(url, payload)
        return res.text

    def __mount_database_link_catalog (self,
                            catalog_name       : str,
                            database_link_name : str) -> str:
        '''
        Mount data catalog
        @param catalog_name (String): catalog name
        @param database_link_name (String): database link name
        @param run mode (String): function run mode 'codeRun' or 'codeTest'
        '''
        url = '/_adplmd/_services/objects/database-links/mount'
        payload = {
            "catalog_name" : catalog_name,
            "name"         : database_link_name,
            "public"       : False,
            "run_mode"     : 'codeRun'
        }
        res = self.__post(url, payload)
        return res.text

    def mount_autonomous_database_catalog (self,
                        catalog_name         : str,
                        database_name        : str,
                        database_link_name   : str,
                        create_database_link : bool = False,
                        credential_name      : str  = None) -> str:
        '''
        Mount data catalog
        @param catalog_name (String): catalog name
        @param database_name (String): database name
        @param database_link_name (String): database link name
        @param create_database_link (String): create database link status
        @param credential_name (String): database swift credential name
            identified by username and password
        '''
        if create_database_link:
            res = self.__set_adb_link(database_link_name,
                                    database_name,
                                    credential_name)

            #get adb list => retrieve ocid
            if self.status == 200 :
                res = self.__mount_database_link_catalog(
                                            catalog_name,
                                            database_link_name)
        else:
            res = self.__mount_database_link_catalog(
                                            catalog_name,
                                            database_link_name)
        return res

    #----------------------------------------------------------------------------
    #-- Mount OCI Data Catalog
    #-- Mount Amazon Glue Catalog
    #----------------------------------------------------------------------------

    def __mount_data_catalog (self,
                            catalog_name        : str,
                            catalog_credential  : str,
                            catalog_region      : str,
                            catalog_id          : str,
                            catalog_type        : str = 'OCI_DCAT',
                            storage_credential  : str = None) -> str:
        '''
        Mount data catalog
        @param catalog_name (String): catalog name
        @param region (String): catalog cloud resource region
        @param catalog_credential (String): catalog access local credential
        @param catalog_id (String): catalog name or identifier
        @param catalog_type (String): catalog type (OCI_DCAT/AWS_GLUE)
        @param storage_credential (String): optional local storage credential
        '''
        url = '/_adplmd/_services/objects/catalog/mount/datacatalog'
        payload = {
            "catalog_type"       : catalog_type,
            "catalog_name"       : catalog_name,
            "region"             : catalog_region,
            "catalog_credential" : catalog_credential,
            "catalog_id"         : catalog_id,
            "storage_credential" : storage_credential
        }
        res = self.__post(url, payload)
        return res.text

    def __get_oci_data_catalog_id (self,
                                oci_catalog_credential : str,
                                oci_catalog_region : str,
                                oci_catalog_name : str) -> dict:
        c = self.__get_oci_data_catalogs(oci_catalog_credential)
        id_ = {"status_code" : 100,
              "error"       : 'oci data catalog id not found.'}
        if c.status_code == 200:
            j = json.loads(c.text)
            if len(j) > 0:
                for e in j:
                    r = e['catalog_region']
                    n = e['catalog_nm']
                    if (r.lower() == oci_catalog_region.lower()
                        and n.lower() == oci_catalog_name.lower()):
                        id_ = {"status_code" : c.status_code,
                              "id"          : e['catalog_id']}
                        break
            else :
                id_ = {"status_code" : 250,
                    "error" : 'oci data catalogs array is empty.'}
        else:
            id_ = {"status_code" : c.status_code,
                  "error"       : json.loads(c.text)}
        return id_

    def mount_oci_data_catalog (self,
                            catalog_name           : str,
                            oci_catalog_credential : str,
                            oci_catalog_region     : str,
                            oci_catalog_name       : str,
                            oci_storage_credential : str = None) -> str:
        '''
        Mount OCI data catalog as catalog
        @param catalog_name (String): catalog name
        @param oci_catalog_credential (String): OCI catalog credential
        @param oci_catalog_region (String): OCI catalog region
        @param oci_catalog_name (String): OCI catalog name
        @param oci_storage_credential (String): OCI object storage credential
        '''
        d = self.__get_oci_data_catalog_id(oci_catalog_credential,
                                         oci_catalog_region,
                                         oci_catalog_name)
        if d["status_code"] == 200:
            oci_catalog_id = d["id"]
        else:
            return json.dumps(d)
        res = self.__mount_data_catalog(catalog_name,
                                    oci_catalog_credential,
                                    oci_catalog_region,
                                    oci_catalog_id,
                                    'OCI_DCAT',
                                    oci_storage_credential)
        return res

    def mount_aws_glue_catalog (self,
                            catalog_name           : str,
                            aws_catalog_credential : str,
                            aws_catalog_region     : str) -> str:
        '''
        Mount Amazon (AWS) glue as catalog
        @param catalog_name (String): catalog name
        @param aws_catalog_credential (String): AWS catalog credential
        @param aws_catalog_region (String): AWS catalog region
        '''
        res = self.__mount_data_catalog(catalog_name,
                                aws_catalog_credential,
                                aws_catalog_region,
                                '',
                                'AWS_GLUE',
                                None)
        return res

    #----------------------------------------------------------------------------
    #-- Mount Data Share Catalog
    #----------------------------------------------------------------------------

    def mount_data_share_catalog (self,
                            catalog_name   : str,
                            share_provider : str,
                            share_name     : str = None) -> str:
        '''
        Mount shares catalog
        @param catalog_name (String): catalog name
        @param share_provider (String): share provider name
        @param share_name (String): share name
        '''
        url = '/_adplmd/_services/objects/catalog/mount/shares'
        snm = self.__set_none(share_name, 'DELTA_SHARING')
        sha = [{"catalogName"   : catalog_name,
                "shareName"     : snm,
                "shareNameRule" : "="}]
        payload = {
            "share_provider" : share_provider,
            "shares"         : json.dumps(sha)
        }
        res = self.__post(url, payload)
        return res.text
