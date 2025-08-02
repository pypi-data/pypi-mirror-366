'''
Licensed under the Universal Permissive License v 1.0 as shown at
https://oss.oracle.com/licenses/upl/.

Copyright (c) 2024-2025, Oracle and/or its affiliates.

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
        _url = "/_adpshr/_services/objects"
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

    def __is_json(self, string : str) -> bool:
        '''
            Check if string is json object
            @param string (str): json object string
        '''
        r = False
        try:
            json.loads(string)
            r = True
            return r
        except ValueError:
            r = False
            return r

    def __chk_share_obj(self,
                    name  : str,
                    owner : str,
                    type_ : str,
                    share_object : str) -> dict:
        '''
            Check share object
            @param name (String): share object name
            @param owner (String): share object owner
            @param name (String): share object type :
                share, recipient, provider
            @param name (String): share object details
        '''
        m = '{0} name {1} exists in {2} database schema.'
        d = json.loads(share_object)
        b = False
        if 'id' in d:
            b = True
            s = m.format(type_, name.upper(), owner)
        else :
            s = d['reason']
        r = {"exist" : b, "msg" : s, "cnt" : share_object, "o" : owner}
        return r

    def __exist_share_obj(self, name :str, owner : str, type_ : str) -> dict:
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
        return self.__chk_share_obj (name, o, t, obj)

    def __exist_storage_link_access (self, name : str) -> dict:
        """
            Check storage link access permissions
            @param name (String): storage link name
        """
        url = '/testcloudstoreaccess/'
        e = False

        payload = {
            "storage_link_name" : name
        }

        m = ("Storage Link access error : "
                     "Choose a Cloud Non Swift Storage Link having "
                     "access to Read, Write and Delete")
        try:
            o = self.__rest_post_txt(self.__set_url(url),
                                    self.__set_payload(payload))
            o = json.loads(o)
            if o["write"] and o["read"] and o ["delete"] :
                m = "Access exist."
                e = True
            else:
                e = False
        except Exception:
            o = {}
        return {"exist" : e, "msg" : m, "obj" : o}

    def __rest_post_txt (self, url : str, payload : dict = None) -> str:
        """
        Transforms rest post_obj dictionary into text
        @param url (String): url rest path
        @param payload (Dictionary): payload dictionary object
        """
        d = self.rest.post_obj(url, payload)
        return d.text

    def __rest_delete_txt (self, url : str, payload : dict = None) -> str:
        """
        Transforms rest delete_obj dictionary into text
        @param url (String): url rest path
        @param payload (Dictionary): payload dictionary object
        """
        d = self.rest.delete_obj(url, payload)
        return d.text

    def __rest_get_txt (self, url : str, payload : dict = None) -> str:
        """
        Transforms rest get_obj dictionary into text
        @param url (String): url rest path
        @param payload (Dictionary): payload dictionary object
        """
        d = self.rest.get_obj(url, payload)
        return d.text

    #-----------------------------------------------------------
    #                    Share API
    #-----------------------------------------------------------

    def create_share (self,
        name                : str,
        objects             : str,
        storage_link_name   : str,
        publish_job_details : str  = None,
        owner               : str  = None,
        type                : str  = None,
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
        # storage link validation
        v = self.__exist_storage_link_access(storage_link_name)
        if not v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        # share validation
        v = self.__exist_share_obj(name, owner, 'share')
        if v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        url = '/share/create/'
        o = self.__set_none(owner, self.rest.username)
        t = self.__set_none(type, 'VERSIONED')
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
        r = self.__rest_post_txt(self.__set_url(url),
                                self.__set_payload(payload))
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
        v = self.__exist_share_obj(name, owner, 'share')
        if not v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        url = '/share/update/'
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"                : name,
            "owner"               : o,
            "description"         : description,
            "publish_job_details" : publish_job_details,
            "objects"             : objects
        }
        r = self.__rest_post_txt(self.__set_url(url),
                                self.__set_payload(payload))
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
        return self.__rest_delete_txt(self.__set_url(url), payload)

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
        v = self.__exist_share_obj(name, owner, 'share')
        if not v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        v = self.__exist_share_obj(new_name, owner, 'share')
        if v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        url = '/share/rename/'
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"     : name,
            "new_name" : new_name,
            "owner"    : o
        }
        return self.__rest_post_txt(self.__set_url(url), payload)

    def publish_share (self, name : str, owner : str = None) -> str:
        '''
            Publish data share
            @param name (String): share name
            @param owner (String): share owner
        '''
        v = self.__exist_share_obj(name, owner, 'share')
        if not v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        url = '/share/publish/'
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"  : name,
            "owner" : o
        }
        return self.__rest_post_txt(self.__set_url(url), payload)

    def unpublish_share (self, name : str, owner : str = None) -> str:
        '''
            Unpublish data share
            @param name (String): share name
            @param owner (String): share owner
        '''
        v = self.__exist_share_obj(name, owner, 'share')
        if not v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        url = '/share/unpublish/'
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"  : name,
            "owner" : o
        }
        return self.__rest_post_txt(self.__set_url(url), payload)

    def get_shares (self, owner : str = None) -> str:
        '''
            Get data shares by owner name
            @param owner (String): shares owner name
        '''
        o = self.__set_none(owner, self.rest.username)
        url = "/shares/?owner={0}".format(o)
        r = self.__rest_get_txt(self.__set_url(url))
        return r

    def get_share (self, name : str, owner : str = None) -> str:
        '''
            Get data share by share and owner name
            @param name (String): share name
            @param owner (String): share owner name
        '''
        o = self.__set_none(owner, self.rest.username)
        url = "/share/?name={0}&owner={1}".format(name, o)
        r = self.__rest_get_txt(self.__set_url(url))
        return r

    def get_share_objects (self, name : str, owner : str = None) -> str:
        '''
            Get data share objects by share and owner name
            @param name (String): share name
            @param owner (String): share owner name
        '''
        v = self.__exist_share_obj(name, owner, 'share')
        if not v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        o = self.__set_none(owner, self.rest.username)
        url = "/share/objects/?name={0}&owner={1}".format(name, o)
        r = self.__rest_get_txt(self.__set_url(url))
        return r

    def get_share_jobs (self, name : str, owner : str = None) -> str:
        '''
            Get data share jobs by share and owner name
            @param name (String): share name
            @param owner (String): share owner name
        '''
        v = self.__exist_share_obj(name, owner, 'share')
        if not v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        o = self.__set_none(owner, self.rest.username)
        url = "/share/jobs/?name={0}&owner={1}".format(name, o)
        r = self.__rest_get_txt(self.__set_url(url))
        return r

    #-----------------------------------------------------------
    #                    Recipient API
    #-----------------------------------------------------------

    #---Recipient util functions ---

    def __validate_recipient_user_shares(self, shares : str) -> dict:
        '''
            Validate recipient user shares json string input parameter
            @param shares (String): recipient shares
        '''
        r = {'valid' : False , 'msg' : None, 'shares' : None}
        if shares is None :
            r['valid'] = True
            r['msg'] = 'Shares parameter is None.'
            return r
        if not self.__is_json(shares) :
            r['msg'] = 'Shares parameter has invalid json representation.'
            return r
        s = json.loads(shares)
        try :
            s = [item.get('name') for item in s]
            s = [v for v in s if v is not None]
            if len(s) > 0:
                r['valid'] = True
                r['shares'] = s
                return r
            else :
                r['msg'] = ('Shares parameter json array is empty'
                  ' or "name" key does not found.')
                return r
        except Exception :
            r['msg'] = ('Shares parameter has invalid '
                        'json array representation.'
                        '"name" key does not found.')
            return r

    def __validate_recipient_system_shares (self, owner : str) -> dict:
        '''
            Validate recipient owner shares
            @param owner (String): recipient owner name
        '''
        r = {'valid' : False , 'msg' : None, 'shares' : None}
        try :
            s = self.get_shares(owner)
            s = json.loads(s)
            s = [item.get('name') for item in s]
            s = [v for v in s if v is not None]
            if len(s) > 0:
                r['valid'] = True
                r['shares'] = s
            else :
                r['msg'] = 'Ownner schema share list is empty.'
            return r
        except Exception:
            r['msg'] = 'Shares http connection error.'
        return r

    def __validate_recipient_shares (self, shares : str, owner : str) -> dict:
        '''
            Validate recipient shares json string input parameter and
            recipient owner shares
            @param shares (String): recipient shares
            @param owner (String): recipient owner name
        '''
        r = {'valid' : False , 'msg' : None, 'shares' : None}
        u = self.__validate_recipient_user_shares(shares)
        if u['valid'] is False:
            r['msg'] = u['msg']
            return r
        if u['valid'] is True and u['shares'] is None:
            r['valid'] = True
            return r
        s = self.__validate_recipient_system_shares(owner)
        if u['valid'] is False:
            r['msg'] = u['msg']
            return r
        d = set(u['shares']).difference(set(s['shares']))
        d = list(d)
        if len(d) == 0 :
            r['valid'] = True
        else :
            r['msg'] = ('Shares {0} does not exist '
                'in owner {1} database').format (str(d), owner)
        return r

    #--------------------------------------------------------

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
        o = self.__set_none(owner, self.rest.username)

        v = self.__validate_recipient_shares(shares, o)
        if v['valid'] is False:
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        v = self.__exist_share_obj(name, o, 'recipient')
        if v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        url = "/recipient/create/"
        profile_url = '{0}/{1}'.format(self.rest.base_url, 'ords')
        payload = {
            "name"           : name,
            "email"          : email,
            "description"    : description,
            "shares"         : shares,
            "profile_url"    : profile_url,
            "token_lifetime" : token_lifetime,
            "owner"          : o}
        r = self.__rest_post_txt(self.__set_url(url),
                            self.__set_payload(payload))
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
        o = self.__set_none(owner, self.rest.username)

        v = self.__validate_recipient_shares(shares, o)
        if v['valid'] is False:
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        if shares is None:
            m = 'Please provide shares.'
            e = {"status" : False, "reason" : m}
            return json.dumps(e)

        v = self.__exist_share_obj(name, o, 'recipient')
        if not v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        url = "/recipient/shares/update/"
        payload = {
            "name"   : name,
            "shares" : shares,
            "owner"  : o
        }
        r = self.__rest_post_txt(self.__set_url(url), payload)
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
        return self.__rest_delete_txt(self.__set_url(url), payload)

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
        v = self.__exist_share_obj(name, owner, 'recipient')
        if not v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        v = self.__exist_share_obj(new_name, owner, 'recipient')
        if v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        url = "/recipient/rename/"
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"     : name,
            "new_name" : new_name,
            "owner"    : o
        }
        return self.__rest_post_txt(self.__set_url(url), payload)

    def get_recipients (self, owner : str = None) -> str:
        '''
            Get recipients by owner name
            @param owner (String): recipient owner name
        '''
        url = "/recipients/?owner={0}".format(self.__set_none(owner,
                                                        self.rest.username))
        t = self.__rest_get_txt(self.__set_url(url))
        d = json.loads(t)
        d = [v for v in d if v['type'] == 'DELTA_SHARING']
        r = json.dumps(d)
        return r

    def get_recipient (self, name : str, owner : str = None) -> str:
        '''
            Get recipient by recipient and owner name
            @param name (String): recipient name
            @param owner (String): recipient owner name
        '''
        o = self.__set_none(owner, self.rest.username)
        url = "/recipient/?name={0}&owner={1}".format(name, o)
        r = self.__rest_get_txt(self.__set_url(url))
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
        v = self.__exist_share_obj(name, owner, 'recipient')
        if not v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        dct = {}
        o = self.__set_none(owner, self.rest.username)
        url = '{0}{1}{2}'.format(self.rest.base_url, '/ords/', o.lower())
        dct['shareCredentialsVersion'] = 2
        # fixed type for delta sharing
        # dct['type'] = 'persistent_oauth2.0'
        dct['type'] = 'oauth_client_credentials'
        dct['endpoint'] = '{0}{1}'.format(url, '/_delta_sharing')
        dct['tokenEndpoint'] = '{0}{1}'.format(url, '/oauth/token')

        s = self.get_recipient(name, owner)
        r = json.loads(s)
        dct['clientId'] = r['clientId']
        dct['clientSecret']  = r['clientSecret']
        return json.dumps(dct, indent = 4)

    def get_recipient_profile_activation_key (self, name : str,
                                              owner : str = None) -> str:
        '''
            Get delta sharing recipient profile activation key
            by recipient name and owner name
            @param name (String): recipient name
            @param owner (String): recipient owner name
        '''
        v = self.__exist_share_obj(name, owner, 'recipient')
        if not v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)
        o  = self.__set_none(owner, self.rest.username)
        r  = self.get_recipient(name, o)
        id = json.loads(r)['id']
        url = "/recipient/getprofiledownloadkey/?id={0}".format(id)
        r = self.__rest_get_txt(self.__set_url(url))
        return r

    def get_recipient_profile_activation_info (self, name : str,
                                              owner : str = None) -> str:
        '''
            Get delta sharing recipient profile activation info
            by recipient name and owner name
            @param name (String): recipient name
            @param owner (String): recipient owner name
        '''
        v = self.__exist_share_obj(name, owner, 'recipient')
        if not v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)
        o  = self.__set_none(owner, self.rest.username)
        r  = self.get_recipient(name, o)
        id = json.loads(r)['id']
        url = "/recipient/?id={0}&supports_oracle_live=true".format(id)
        r = self.__rest_get_txt(self.__set_url(url))
        return r
    #-----------------------------------------------------------
    #                    Provider API
    #-----------------------------------------------------------

    def __exist_provider_share_link (
        self,
        name      : str,
        providers : dict) -> dict:
        '''
            Check provider share link name in providers list
            @param name (String): provider name
            @param providers (Dict): providers dictionary
        '''
        r = {'exist' : False, 'provider' : None}
        for p in providers :
            n = p ['name']
            o = p ['owner']
            sja = json.loads(self.get_provider (n, o))
            shl = sja ['shareLinks']
            if shl is not None:
                for s in shl :
                    if name.upper() == s ['name'] :
                        r['exist'] = True
                        r['provider'] = p
                        break
                if r['exist'] :
                    break
        return r

    def __exist_provider_share_links (self,
                            share_links   : str,
                            provider_type : str,
                            owner         : str) -> dict:
        '''
            Check provider share link names
            @param share_links (String): provider share links
            @param owner (String): provider owner name
        '''
        r = {'exist' : False, 'provider' : None, 'share' : None}
        if share_links is None:
            return r
        pja = json.loads(self.get_providers (owner))
        pja = [v for v in pja if v['shareType'] == provider_type]

        sja = json.loads(share_links)
        for s in sja :
            e = self.__exist_provider_share_link (s['shareLinkName'], pja)
            if e['exist']:
                r['exist'] = True
                r['provider'] = e['provider']
                r['share'] = s
                break
        return r

    def create_provider (self,
        name               : str,
        endpoint           : str,
        share_links        : str = None,
        provider_type      : str = None,
        bearer             : str = None,
        client_id          : str = None,
        client_secret      : str = None,
        token_endpoint     : str = None,
        description        : str = None,
        owner              : str = None) -> str:
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
        o = self.__set_none(owner, self.rest.username)

        v = self.__exist_share_obj(name, o, 'provider')
        if v ['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        pt = self.__set_none(provider_type, 'DELTA')
        v = self.__exist_provider_share_links(
            share_links   = share_links,
            provider_type = pt,
            owner         = o)

        if v ['exist'] :
            m = 'Share link name {0} exists in provider {1}'.format(
                v.get('share')['shareLinkName'],
                v.get('provider')['name'])
            e = {"status" : False, "reason" : m}
            return json.dumps(e)

        if share_links is None :
            sl = self.available_provider_shares(
                endpoint,
                name,
                provider_type,
                bearer,
                client_id,
                client_secret,
                token_endpoint,
                owner)
            print('Share links detected {0}'.format(sl))
        else :
            sl = share_links

        url = "/provider/create/"
        payload = {
            "name"               : name,
            "owner"              : o,
            "description"        : description,
            "bearer_token"       : bearer,
            "client_id"          : client_id,
            "client_secret"      : client_secret,
            "endpoint"           : endpoint,
            "provider_type"      : pt,
            "share_links"        : sl,
            "token_endpoint"     : token_endpoint
        }
        r = self.__rest_post_txt(self.__set_url(url), self.__set_payload(payload))
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
        return self.__rest_delete_txt(self.__set_url(url), payload)

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
        v = self.__exist_share_obj(name, owner, 'provider')
        if not v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        v = self.__exist_share_obj(new_name, owner, 'provider')
        if v['exist'] :
            e = {"status" : False, "reason" : v['msg']}
            return json.dumps(e)

        url = "/provider/rename/"
        o = self.__set_none(owner, self.rest.username)
        payload = {
            "name"     : name,
            "new_name" : new_name,
            "owner"    : o
        }
        return self.__rest_post_txt(self.__set_url(url), payload)

    def get_providers (self, owner : str = None) -> str:
        '''
            Get providers by owner name
            @param owner (String): provider owner name
        '''
        o = self.__set_none(owner, self.rest.username)
        url = "/providers/?owner={0}".format(o)
        r = self.__rest_get_txt(self.__set_url(url))
        return r

    def get_provider (self, name : str, owner : str = None) -> str:
        '''
            Get provider by recipient and owner name
            @param name (String): provider name
            @param owner (String): provider owner name
        '''
        o = self.__set_none(owner, self.rest.username)
        url = "/provider/?name={0}&owner={1}".format(name, o)
        r = self.__rest_get_txt(self.__set_url(url))
        return r

    def available_provider_shares(self,
        endpoint       : str,
        provider_name  : str = None,
        provider_type  : str = None,
        bearer_token   : str = None,
        client_id      : str = None,
        client_secret  : str = None,
        token_endpoint : str = None,
        owner          : str = None) -> str:
        '''
            Check available providers shares
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
        url = "/provider/available/"
        if provider_name is None:
            pn = 'test'
        else:
            pn = provider_name
        ow = self.__set_none(owner, self.rest.username)
        pt = self.__set_none(provider_type, 'DELTA')
        payload = {
            "bearer_token"       : bearer_token,
            "client_id"          : client_id,
            "client_secret"      : client_secret,
            "endpoint"           : endpoint,
            "name"               : pn,
            "owner"              : ow,
            "provider_type"      : pt,
            "token_endpoint"     : token_endpoint
        }
        r = self.__rest_post_txt(self.__set_url(url), self.__set_payload(payload))

        try :
            j = json.loads(r)
            if len(j) > 0:
                d = []
                for x in j:
                    v = {}
                    v["shareName"] = x
                    v["shareLinkName"] = 'LINK_{0}_{1}'.format(provider_name,
                                                               x).upper()
                d.append(v)
                return json.dumps(d)
        except Exception:
            return None

    def __get(self, url : str, payload : dict) -> object:
        '''
        GET rest object response
        @param payload (Dictionary): request payload
        '''
        res = self.rest.get_obj(url, payload)
        self.status = res.status_code
        return res

    def __get_objects (self,
                        url          : str,
                        search_query : str,
                        searchscope  : str = None,
                        scopeowner   : str = None) -> dict:
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
        searchscope = self.__set_none(searchscope, 'ALL_OBJECTS')
        scopeowner  = self.__set_none(scopeowner,  'C##ADP$SERVICE')
        #"sortjson"    : [{"column":"entity_name","direction":"asc"}]
        payload = {
            "search"      : search_query,
            "searchscope" : searchscope,
            "scopeowner"  : scopeowner,
            "rowstart"    : 0,
            "hideprivate" : False,
            "hidesys"     : True,
            "numrows"     : 5001,
            "maxlimit"    : 5001
        }
        res = self.__get (url, payload)
        res = res.json()
        return res

    def get_provider_share_tables (self,
            provider_name : str,
            owner         : str = None) -> str:
        '''
        Get provider share tables by share link name
        @param share_link_name (String): provider share link name
        @param owner (String): share link owner name
        '''
        url = "/_adplmd/_services/objects/search/"
        owner    = self.__set_none(owner, self.rest.username)
        provider = self.get_provider(provider_name, owner)
        provider = json.loads(provider)
        share_links = provider.get('shareLinks', [])
        share_links_names = [e.get('name') for e in share_links]
        print('Share link names : {0}'.format(share_links))

        ## parentPath~={parent_path}
        search_query = f'''owner:{owner} application:SHARE
                           enable:available_shares
                           enable:caching'''
        res = self.__get_objects(url, search_query)
        res = res.get('nodes', [])
        pattern = '|'.join(share_links_names)

        out = []
        for r in res:
            _a = r['id'].split(".")
            _v = _a[2]
            _v = _v.replace('"', '')
            if _v in share_links_names:
                out.append(r)
        out = json.dumps(out)
        return out

    def _analyze_provider_share_table(self,
                        provider_name   : str,
                        share_link_name : str,
                        schema_name     : str,
                        table_name      : str,
                        owner           : str  = None,
                        type            : str  = None,
                        check_pii       : bool = None) -> object:
        '''
        Analyze provider share table
        @param provider_name (String): provider name
        @param share_link_name (String): provider share link name
        @param schema_name (String): share table schema name
        @param table_name (String): share table name
        @param owner (String): share link owner name
        @param type (String): share table type (DELTA, PARQUET)
        @param check_pii (Boolean): check PII data
        '''
        url = "/_adpdi/_services/objects/ingest_cloud_object_analyze/"
        owner = self.__set_none(owner, self.rest.username)
        type = self.__set_none(type, 'DELTA')
        check_pii = self.__set_none(check_pii, True)
        _share = {"share":{
                    "provider_name" : provider_name,
                    "link_name"     : share_link_name,
                    "schema_name"   : schema_name,
                    "table_name"    : table_name,
                    "type"          : type},
            "checkPII" : check_pii}
        share = json.dumps(_share)
        _job = {"postJobTransforms":[{"type":"trimcolumns"}]}
        job  = json.dumps(_job)
        payload = {"ingest_manifest_json": share, "options_json": job}
        post_obj = self.rest.post_obj(url, payload)
        return post_obj

    def analyze_provider_share_table(self,
                        provider_name   : str,
                        share_link_name : str,
                        schema_name     : str,
                        table_name      : str,
                        owner           : str  = None,
                        type            : str  = None,
                        check_pii       : bool = None) -> object:
        '''
        Analyze provider share table
        @param provider_name (String): provider name
        @param share_link_name (String): provider share link name
        @param schema_name (String): share table schema name
        @param table_name (String): share table name
        @param owner (String): share link owner name
        @param type (String): share table type (DELTA, PARQUET)
        @param check_pii (Boolean): check PII data
        '''
        apst = self._analyze_provider_share_table(
            provider_name,
            share_link_name,
            schema_name,
            table_name,
            owner,
            type,
            check_pii
        )
        return apst.text

    def link_provider_share_table(self,
                        provider_name   : str,
                        share_link_name : str,
                        schema_name     : str,
                        table_name      : str,
                        table_name_new  : str  = None,
                        owner           : str  = None,
                        type            : str  = None,
                        check_pii       : bool = None) -> str:
        '''
        Link provider share table
        @param provider_name (String): provider name
        @param share_link_name (String): provider share link name
        @param schema_name (String): share table schema name
        @param table_name (String): share table name
        @param table_name_new (String): new share table name
        @param owner (String): share link owner name
        @param type (String): share table type (DELTA, PARQUET)
        @param check_pii (Boolean): check PII data
        '''
        # Set default values
        owner = self.__set_none(owner, self.rest.username)
        type = self.__set_none(type, 'DELTA')
        check_pii = self.__set_none(check_pii, True)
        table_name_new = self.__set_none(table_name_new, table_name)

        # Analyze provider share table
        apst = self._analyze_provider_share_table(
            provider_name,
            share_link_name,
            schema_name,
            table_name,
            owner,
            type,
            check_pii)
        # Check if the analysis was successful
        if apst.status_code != 200:
            return apst.text

        # Prepare the ingest manifest JSON
        url = "/_adpdi/_services/objects/ingest_cloud_object/"

        # Get metadata source from the analysis response
        apst_j = json.loads(apst.text)
        metadataSource = apst_j[0]['metadataSource']

        # Prepare the ingest manifest JSON
        ingest_manifest_json = {
        "tables":[
        {"objectList":[
        {"overwriteOption":"SKIP",
        "tableName":table_name_new,
        "loadMethod":"AUTO",
        "headerStartRow":1,
        "ingestOption":"EXTERNALVIEW",
        "useSimpleColumnNames":True,
        "objectDesc":
          {"metadataSourceType":"INLINE",
          "metadataSourceOwner":None,
          "metadataSource":metadataSource},
            "runAsBackgroundJob":"Y",
            "noCollectionSource":True,
            "checkPII":True,
            "share":{
              "provider_name":provider_name,
              "link_name":share_link_name,
              "schema_name":schema_name,
              "table_name":table_name,
              "type":"DELTA"},
            "objectType":"PARQUET"}]}]}

        ingest_manifest_json = json.dumps(ingest_manifest_json)
        payload = {
            "bucket_name"          : None,
            "credential_name"      : None,
            "ingest_manifest_json" : ingest_manifest_json}

        # payload = {"ingest_manifest_json": s, "options_json": o}
        return self.__rest_post_txt(url, payload)