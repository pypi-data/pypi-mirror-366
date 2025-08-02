'''
Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/.

Copyright (c) 2023-2025, Oracle and/or its affiliates.

'''

import json
from threading import Thread
from datetime import datetime, timedelta
import base64
import requests
from requests.exceptions import HTTPError
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

class Rest(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.username = None
        self.base_url = None
        self.session = None
        self.token = None
        self.expired = None
        self.status = 0

    def get_prefix(self) -> str:
        '''
            Get prefix of the url
        '''
        return "ords/{}".format(self.username.lower())

    def _get_token(self, client_credentials : str) -> None:

        client_enc = base64.b64encode(client_credentials.encode()).decode()
        self.token = None
        self.expired = None
        url = '{0}/ords/{1}/oauth/token'.format(self.base_url, self.username.lower())
        payload='grant_type=client_credentials'
        headers_auth = {
            'Authorization': 'Basic '+ str(client_enc),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", url, headers=headers_auth, data=payload, timeout=180)
        #print(response.status_code)
        if response.ok:
            j = response.json()
            self.token = j.get('access_token')
            self.expired = datetime.now() + timedelta(seconds=j.get('expires_in'))
        else:
            print(response.status_code)
            raise HTTPError('Token cannot be obtained')

    def _add_client_param(self, url: str) -> str:
        parsed = urlparse(url)
        query_params = dict(parse_qsl(parsed.query))
        query_params['client'] = 'dspython'
        new_query = urlencode(query_params)
        return urlunparse(parsed._replace(query=new_query))

    def get(self,path : str) -> str:
        '''
            Do Get REST call
        '''
        url = self._add_client_param(self.base_url + "/" + path)
        header = {'Content-Type': "application/json"}
        self._add_bearer_auth(header)

        try:
            response = self.session.get(url, headers=header)
            self.status = response.status_code
        except HTTPError:
            response.raise_for_status()

        #print(status)

        #print('Status Code:', status)
        if self.status==401:
            message = self._generate_error_message()
            raise HTTPError(message)
        if self.status > 500:
            raise HTTPError('Error:' + self.status)

        return response.text

    def post(self,path : str, payload, timeout = 180) -> str:
        '''
            Do Post REST call
        '''
        url = self._add_client_param(self.base_url + "/" + path)
        header = {'Content-Type': "application/json"}
        self._add_bearer_auth(header)

        try:
            response = self.session.post(url, json=payload,timeout=timeout,headers=header)
            self.status = response.status_code
        except HTTPError:
            response.raise_for_status()

        #print('Status Code:', status)
        if self.status == 401:
            message = self._generate_error_message()
            raise HTTPError(message)
        if self.status > 500:
            raise HTTPError('Error:' + str(self.status) + ', data: ' + json.dumps(payload))

        #print('Status:',status)

        return response.text


    def delete(self,path : str, data = None) -> str:
        '''
            Do Delete REST call
        '''

        url = self.base_url +"/"+path
        header = {'Content-Type': "application/json"}
        self._add_bearer_auth(header)

        try:
            response = self.session.delete(url, headers=header, json=data)
            self.status = response.status_code
        except HTTPError:
            response.raise_for_status()


        #print('Status Code:', status)
        if self.status==401:
            message = self._generate_error_message()
            raise HTTPError(message)
        if self.status > 500:
            raise HTTPError('Error:' + self.status)


        return response.text

    def get_obj(self,
            path     : str,
            payload : dict=None) -> object:
        '''
        GET rest object response
        @param payload (Dictionary): request payload
        '''
        # fixed url with (+ "/" +)
        url = self.base_url  + "/" + self.get_prefix() + path
        header = {'Content-Type':"application/json"}
        self._add_bearer_auth(header)
        try:
            if not payload:
                res = self.session.get(
                                    url     = url,
                                    headers = header)
            else:
                res = self.session.get(
                                    url     = url,
                                    headers = header,
                                    params  = payload)
            self.status = res.status_code
        except HTTPError:
            res.raise_for_status()

        if self.status == 401:
            message = self._generate_error_message()
            raise HTTPError(message)
        if self.status > 500:
            raise HTTPError('Error: {0}'.format(self.status))
        return res

    def post_obj(self,
            path     : str,
            payload : dict=None,
            timeout : int=180) -> object:
        '''
        POST rest object response
        @param payload (Dictionary): request payload
        @param timeout (int): timeout integer
        '''
        # fixed url with (+ "/" +)
        url = self.base_url + "/" + self.get_prefix() + path
        header = {'Content-Type':"application/json"}
        self._add_bearer_auth(header)
        try:
            res = self.session.post(
                                    url     = url,
                                    json    = payload,
                                    timeout = timeout,
                                    headers = header)
            self.status = res.status_code
        except HTTPError:
            res.raise_for_status()

        if self.status == 401:
            message = self._generate_error_message()
            raise HTTPError(message)
        if self.status > 500:
            raise HTTPError('Error: {0}'.format(self.status))
        return res

    def delete_obj(self,path : str, data = None) -> object:
        '''
            Do Delete REST call
        '''
        # fixed url with (+ "/" +)
        url = self.base_url + "/" + self.get_prefix() + path
        header = {'Content-Type': "application/json"}
        self._add_bearer_auth(header)

        try:
            response = self.session.delete(url, headers=header, json=data)
            self.status = response.status_code
        except HTTPError:
            response.raise_for_status()


        #print('Status Code:', status)
        if self.status==401:
            message = self._generate_error_message()
            raise HTTPError(message)
        if self.status > 500:
            raise HTTPError('Error:' + self.status)


        return response


    def connect(self,url : str, username : str, client_credentials : str) -> None:
        '''
            Connection using client credentials
        '''
        self.base_url = url
        self.session = requests.Session()
        self.session.headers.update({"client": "Python"})
        self.username=username
        self._get_token(client_credentials)
        print("Login success!")

    def login(self,url : str, username : str, password : str) -> str:
        '''
            Login to the ORDS
        '''
        self.base_url = url
        self.session = requests.Session()
        self.session.headers.update({"client": "Python"})
        self.username=username
        self.expired = None
        self.token = None

        url_sign_in_sdw = self.base_url + '/{0}/sign-in/?username={1}&r=_sdw'
        url_sign_in_check = self.base_url +'/{0}/sign-in/check'
        url_sign_in_success = self.base_url +'/{0}/sign-in/success'
        url_sign_in_test = self.base_url +'/{0}/_sdw/_services/whoami/'

        #SIGN IN
        response1 = self.session.get(url_sign_in_sdw.format(self.get_prefix(),self.username.lower()))
        if not response1.ok:
            raise HTTPError('Login is failed. Try again')

        #print(str(response1.status_code))
        #print(response1.headers)


        #CHECK
        payload = {'j_username':self.username,'j_password': password,'csrf_token':response1.headers['CSRF-Token']}
        response2 = self.session.post(url_sign_in_check.format(self.get_prefix()),data=payload)
        #print(response2.headers)
        #print(str(response2.status_code))
        if not response2.ok:
            raise HTTPError('Login is failed. Try again')

        #SUCCESS
        response3 = self.session.get(url_sign_in_success.format(self.get_prefix()))
        #print(str(response3.status_code))
        if not response3.ok:
            response3.raise_for_status()

        #TEST
        #print('[GET] /ords/{}/_adpanalytics/_services/objects/getAVMetadata::'.format(username))
        response4 = self.session.get(url_sign_in_test.format(self.get_prefix()))
        #print(str(response4.status_code))

        if response4.ok:
            print("Login success!")
        else:
            raise HTTPError('Credentials are wrong. Check username and password')

    def _add_bearer_auth(self, headers : list) -> list:
        if self.token is not None:
            headers['Authorization'] = 'Bearer {}'.format(self.token)
        return headers

    def _generate_error_message(self) -> str:
        if self.token is None:
            return 'Connection is expired. Call login() again.'
        return 'Connection is expired. Call connect() again.'

    def stringify(self, mylist) -> str:
        '''
            Convert json to string
        '''
        return json.dumps(mylist, separators=(',', ':'))

    def encode(self, text) -> str:
        '''
            Encode string for url parameter
        '''
        return requests.utils.quote(text)


class ThreadWithResult(Thread):
    '''
        Subclass of thread
    '''
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None ):
        '''
        initialize
        '''
        if kwargs is None:
            kwargs = {}
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def get(self):
        '''
        return the results
        '''
        return self._return

