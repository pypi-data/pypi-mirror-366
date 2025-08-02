'''
Licensed under the Universal Permissive License v 1.0 as shown at
https://oss.oracle.com/licenses/upl/.

Copyright (c) 2023-2025, Oracle and/or its affiliates.

'''

import json
from .rest import Rest

class AdpShare():
    '''
    classdocs
    '''
    def __init__(self) -> None:
        '''
        Constructor
        '''
        self.rest = None

    def set_rest(self, rest : Rest) -> None:
        '''
            Set Rest instance
            @param rest (Rest): rest instance
        '''
        self.rest = rest

    def __set_none (self, type_ : str, value : str) -> str:
        '''
            Set none or missing value
            @param type (String): none or missing value
            @param value (String): corresponding value
        '''
        if type_ is None:
            type_ = value
        return type_

    def __set_url(self, url : str) -> str:
        '''
            Set url path
            @param url (String): url rest fragment
        '''
        _url = "{0}/_adpshr/_services/objects".format(self.rest.get_prefix())
        url  = "{0}{1}".format(_url, url)
        return url

    def __set_payload(self, payload : dict) -> dict:
        '''
            Set payload object
            @param payload (Dictionary): payload dictionary object
        '''
        for key, val in list(payload.items()):
            if val is None:
                payload.pop(key, None)
        return payload


    def _chk_share_obj(self, name :str, owner : str, type_ : str,
                       share_object : str) -> dict:
        '''
            Check share object
            @param name (String): share object name
            @param owner (String): share object owner
            @param name (String): share object type :
                share, recipient, provider
            @param name (String): share object details
        '''
        share_obj_exist = '{0} name {1} exists in {2} database schema.'
        d = json.loads(share_object)
        b = False
        if 'id' in d:
            b = True
            s = share_obj_exist.format(type_, name.upper(), owner)
        else :
            s = d['reason']
        r = {"exist" : b, "msg" : s, "cnt" : share_object, "o" : owner}
        return r

    def _val_share_obj(self, name :str, owner : str, type_ : str) -> dict:
        '''
            Validate share object
            @param name (String): share object name
            @param owner (String): share object owner
            @param name (String): share object type :
                [p]rovider, [r]ecipient, share
        '''
        o = self.__set_none(owner, self.rest.username)
        t = self.__set_none(type_, 'share').lower()
        if t[0] == 'p':
            obj = self.get_provider(name, owner)
        elif t[0] == 'r':
            obj = self.get_recipient(name, owner)
        else :
            obj = self.get_share(name, owner)
        return self._chk_share_obj (name, o, t, obj)

    #-----------------------------------------------------------
    #                    Share API
    #-----------------------------------------------------------

    def create_share (self,
        name                : str,
        objects             : str,
        storage_link_name   : str,
        publish_job_details : str  = None,
        owner               : str  = None,
        type_                : str  = None,
        storage_link_owner  : str  = None,
        description         : str  = None) -> str:
        '''
        Create new data share
            @param name (String): share name
            @param storage_link_name (String): storage link name
            @param objects (String): data objects list
            @param publish_job_details (String): publish job details
            @param owner (String): share owner
            @param type (String): share type (*VERSIONED, LIVE)
            @param storage_link_owner (String): storage link owner
            @param description (String): share description
        '''
        v = self._val_share_obj(name, owner, 'share')
        if v['exist'] :
            return v['msg']

        url = '/share/create/'
        o = self.__set_none(owner, self.rest.username)
        t = self.__set_none(type_, 'VERSIONED')
        s = self.__set_none(storage_link_owner, self.rest.username)
        p = self.__set_none(publish_job_details,
                            json.dumps({"enabled" : False}))
        payload = {
            "name"                : name,
            "storage_link_name"   : storage_link_name,
            "description"         : description,
            "public_description"  : description,
            "objects"             : objects,
            "owner"               : o,
            "type"                : t,
            "storage_link_owner"  : s,
            "publish_job_details" : p
        }
        r = self.rest.post(self.__set_url(url), self.__set_payload(payload))
        return r

    def update_share_objects (self,
        name                : str,
        objects             : str,
        publish_job_details : str = None,
        owner               : str = None,
        description         : str = None) -> str:
        '''
            Update data share
            @param name (String): share name
            @param owner (String): share owner
            @param description (String): share description
            @param objects (String): data objects list
            @param publish_job_details (String): publish job details
        '''
        v = self._val_share_obj(name, owner, 'share')
        if not v['exist'] :
            return v['msg']

        url = '/share/update/'
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"                : name,
            "owner"               : o,
            "description"         : description,
            "publish_job_details" : publish_job_details,
            "objects"             : objects
        }
        r = self.rest.post(self.__set_url(url), self.__set_payload(payload))
        return r

    def delete_share (self, name : str, owner : str = None) -> str:
        '''
            Delete data share
            @param name (String): share name
            @param owner (String): share owner
        '''
        url = '/share/delete/'
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"  : name,
            "owner" : o
        }
        return self.rest.delete(self.__set_url(url), payload)

    def rename_share (self,
        name     : str,
        new_name : str,
        owner    : str = None) -> str:
        '''
            Rename data share
            @param name (String): share name
            @param new_name (String): new share name
            @param owner (String): share owner
        '''
        v = self._val_share_obj(name, owner, 'share')
        if not v['exist'] :
            return v['msg']

        v = self._val_share_obj(new_name, owner, 'share')
        if v['exist'] :
            return v['msg']

        url = '/share/rename/'
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"     : name,
            "new_name" : new_name,
            "owner"    : o
        }
        return self.rest.post(self.__set_url(url), payload)

    def publish_share (self, name : str, owner : str = None) -> str:
        '''
            Publish data share
            @param name (String): share name
            @param owner (String): share owner
        '''
        v = self._val_share_obj(name, owner, 'share')
        if not v['exist'] :
            return v['msg']

        url = '/share/publish/'
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"  : name,
            "owner" : o
        }
        return self.rest.post(self.__set_url(url), payload)

    def unpublish_share (self, name : str, owner : str = None) -> str:
        '''
            Unpublish data share
            @param name (String): share name
            @param owner (String): share owner
        '''
        v = self._val_share_obj(name, owner, 'share')
        if not v['exist'] :
            return v['msg']

        url = '/share/unpublish/'
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"  : name,
            "owner" : o
        }
        return self.rest.post(self.__set_url(url), payload)

    def get_shares (self, owner : str = None) -> str:
        '''
            Get data shares by owner name
            @param owner (String): shares owner name
        '''
        o = self.__set_none(owner, self.rest.username)
        url = "/shares/?owner={0}".format(o)
        r = self.rest.get(self.__set_url(url))
        return r

    def get_share (self, name : str, owner : str = None) -> str:
        '''
            Get data share by share and owner name
            @param name (String): share name
            @param owner (String): share owner name
        '''
        o = self.__set_none(owner, self.rest.username)
        url = "/share/?name={0}&owner={1}".format(name, o)
        r = self.rest.get(self.__set_url(url))
        return r

    def get_share_objects (self, name : str, owner : str = None) -> str:
        '''
            Get data share objects by share and owner name
            @param name (String): share name
            @param owner (String): share owner name
        '''
        v = self._val_share_obj(name, owner, 'share')
        if not v['exist'] :
            return v['msg']

        o = self.__set_none(owner, self.rest.username)
        url = "/share/objects/?name={0}&owner={1}".format(name, o)
        r = self.rest.get(self.__set_url(url))
        return r

    def get_share_jobs (self, name : str, owner : str = None) -> str:
        '''
            Get data share jobs by share and owner name
            @param name (String): share name
            @param owner (String): share owner name
        '''
        v = self._val_share_obj(name, owner, 'share')
        if not v['exist'] :
            return v['msg']

        o = self.__set_none(owner, self.rest.username)
        url = "/share/jobs/?name={0}&owner={1}".format(name, o)
        r = self.rest.get(self.__set_url(url))
        return r

    #-----------------------------------------------------------
    #                    Recipient API
    #-----------------------------------------------------------

    def create_recipient (self,
        name           : str,
        email          : str,
        description    : str = None,
        owner          : str = None,
        shares         : str = None,
        token_lifetime : str = None) -> str:
        '''
            Create new recipient
            @param name (String): recipient name
            @param email (String): recipient email address
            @param description (String): recipient description
            @param owner (String): recipient owner name
            @param shares (String): recipient shares
            @param token_lifetime (String): token lifetime "D HH:MM:SS"
        '''
        v = self._val_share_obj(name, owner, 'recipient')
        if v['exist'] :
            return v['msg']

        url = "/recipient/create/"
        o = self.__set_none(owner, self.rest.username)
        profile_url = '{0}/{1}'.format(self.rest.base_url, 'ords')
        payload = {
            "name"           : name,
            "email"          : email,
            "description"    : description,
            "shares"         : shares,
            "profile_url"    : profile_url,
            "token_lifetime" : token_lifetime,
            "owner"          : o}
        r = self.rest.post(self.__set_url(url), self.__set_payload(payload))
        return r

    def update_recipient_shares (self,
        name   : str,
        shares : str,
        owner  : str = None) -> str:
        '''
            Update recipient shares by name and owner name
            @param name (String): recipient name
            @param shares (String): recipient shares
            @param owner (String): recipient owner name
        '''
        v = self._val_share_obj(name, owner, 'recipient')
        if not v['exist'] :
            return v['msg']

        url = "/recipient/shares/update/"
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"   : name,
            "shares" : shares,
            "owner"  : o
        }
        r = self.rest.post(self.__set_url(url), payload)
        return r

    def delete_recipient (self, name : str, owner : str = None) -> str:
        '''
            Delete recipient by name and owner name
            @param name (String): recipient name
            @param owner (String): recipient owner name
        '''
        url = "/recipient/delete/"
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"  : name,
            "owner" : o
        }
        return self.rest.delete(self.__set_url(url), payload)

    def rename_recipient (self,
        name     : str,
        new_name : str,
        owner    : str = None) -> str:
        '''
            Rename recipient
            @param name (String): recipient name
            @param new_name (String): recipient new name
            @param owner (String): recipient owner name
        '''
        v = self._val_share_obj(name, owner, 'recipient')
        if not v['exist'] :
            return v['msg']

        v = self._val_share_obj(new_name, owner, 'recipient')
        if v['exist'] :
            return v['msg']

        url = "/recipient/rename/"
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"     : name,
            "new_name" : new_name,
            "owner"    : o
        }
        return self.rest.post(self.__set_url(url), payload)

    def get_recipients (self, owner : str = None) -> str:
        '''
            Get recipients by owner name
            @param owner (String): recipient owner name
        '''
        url = "/recipients/?owner={0}".format(self.__set_none(owner,
                                                        self.rest.username))
        r = self.rest.get(self.__set_url(url))
        return r

    def get_recipient (self, name : str, owner : str = None) -> str:
        '''
            Get recipient by recipient and owner name
            @param name (String): recipient name
            @param owner (String): recipient owner name
        '''
        o = self.__set_none(owner, self.rest.username)
        url = "/recipient/?name={0}&owner={1}".format(name, o)
        r = self.rest.get(self.__set_url(url))
        return r

    def get_recipient_sharing_profile (self,
                                   name  : str,
                                   owner : str = None) -> str:
        '''
            Get delta sharing recipient profile by recipient name
            and owner name
            @param name (String): recipient name
            @param owner (String): recipient owner name
        '''
        v = self._val_share_obj(name, owner, 'recipient')
        if not v['exist'] :
            return v['msg']

        dct = {}
        o = self.__set_none(owner, self.rest.username)
        url = '{0}{1}{2}'.format(self.rest.base_url, '/ords/', o.lower())
        dct['shareCredentialsVersion'] = 2
        dct['type'] = 'persistent_oauth2.0'
        dct['endpoint'] = '{0}{1}'.format(url, '/_delta_sharing')
        dct['tokenEndpoint'] = '{0}{1}'.format(url, '/oauth/token')

        s = self.get_recipient(name, owner)
        r = json.loads(s)
        dct['clientId'] = r['clientId']
        dct['clientSecret']  = r['clientSecret']
        return json.dumps(dct, indent = 4)

    #-----------------------------------------------------------
    #                    Provider API
    #-----------------------------------------------------------

    def create_provider (self,
        name           : str,
        endpoint       : str,
        share_links    : str,
        provider_type  : str = None,
        bearer         : str = None,
        client_id      : str = None,
        client_secret  : str = None,
        token_endpoint : str = None,
        description    : str = None,
        owner          : str = None) -> str:
        '''
            Create new provider
            @param name (String): provider name
            @param endpoint (String): provider endpoint address
            @param share_links (String): provider share links
            @param provider_type (String): provider type
            @param bearer (String): provider bearer id
            @param client_id (String): provider client id
            @param client_secret (String): provider client secret id
            @param token_endpoint (String): provider token endpoint address
            @param description (String): provider description
            @param owner (String): provider owner name
        '''
        v = self._val_share_obj(name, owner, 'provider')
        if v['exist'] :
            return v['msg']

        url = "/provider/create/"
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"           : name,
            "owner"          : o,
            "description"    : description,
            "bearer_token"   : bearer,
            "client_id"      : client_id,
            "client_secret"  : client_secret,
            "endpoint"       : endpoint,
            "provider_type"  : self.__set_none(provider_type, 'DELTA'),
            "share_links"    : share_links,
            "token_endpoint" : token_endpoint
        }
        r = self.rest.post(self.__set_url(url), self.__set_payload(payload))
        return r

    def delete_provider (self, name : str, owner : str = None) -> str:
        '''
            Delete provider by name and owner name
            @param name (String): provider name
            @param owner (String): provider owner name
        '''
        url = "/provider/delete/"
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"  : name,
            "owner" : o
        }
        return self.rest.delete(self.__set_url(url), payload)

    def rename_provider (self,
        name     : str,
        new_name : str,
        owner    : str = None) -> str:
        '''
            Rename provider
            @param name (String): provider name
            @param new_name (String): provider new name
            @param owner (String): provider owner name
        '''
        v = self._val_share_obj(name, owner, 'provider')
        if not v['exist'] :
            return v['msg']

        v = self._val_share_obj(new_name, owner, 'provider')
        if v['exist'] :
            return v['msg']

        url = "/provider/rename/"
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"     : name,
            "new_name" : new_name,
            "owner"    : o
        }
        return self.rest.post(self.__set_url(url), payload)

    def get_providers (self, owner : str = None) -> str:
        '''
            Get providers by owner name
            @param owner (String): provider owner name
        '''
        o = self.__set_none(owner, self.rest.username)
        url = "/providers/?owner={0}".format(o)
        r = self.rest.get(self.__set_url(url))
        return r

    def get_provider (self, name : str, owner : str = None) -> str:
        '''
            Get provider by recipient and owner name
            @param name (String): provider name
            @param owner (String): provider owner name
        '''
        o = self.__set_none(owner, self.rest.username)
        url = "/provider/?name={0}&owner={1}".format(name, o)
        r = self.rest.get(self.__set_url(url))
        return r

    def analyze_provider_share(self, parameters : dict) -> str:
        '''
            Get the metadata for provider share table
            @param parameters (dict): parameters for provider share table
        '''
        manifest = {}
        for key in parameters.keys():
            value = parameters[key]
            manifest[key] = value

        options = {'postJobTransforms':[{'type':'trimcolumns'}]}
        payload = {'ingest_manifest_json': self.rest.stringify(manifest),
                   'options_json': self.rest.stringify(options) }

        lnk = "/_adpdi/_services/objects/ingest_cloud_object_analyze/"
        url = "{0}{1}".format(self.rest.get_prefix(), lnk)
        return self.rest.post(url, payload)
