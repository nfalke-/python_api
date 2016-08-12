import json
import os
import sys
from requests import Request
from nose.tools import assert_equal
from mock import patch
sys.path = [
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
] + sys.path
from riskiq.api import Client


class MockClient(Client):
    def mock_get(self, endpoint, action, *url_args, **url_params):
        """
        Request API Endpoint - for GET methods.
        :param endpoint: Endpoint
        :param action: Endpoint Action
        :param url_args: Additional endpoints(for endpoints that take part of
            the url as option)
        :param url_params: Parameters to pass to url, typically query string
        :return: response deserialized from JSON
        """
        api_url = self._endpoint(endpoint, action, *url_args)
        if 'timeout' in url_params:
            timeout = url_params['timeout']
            del url_params['timeout']
        else:
            timeout = Client.TIMEOUT
        url_params = [(i, url_params[i]) for i in sorted(url_params.keys())]
        kwargs = {'auth': self.auth, 'headers': self.headers,
                  'params': url_params,
                 }#'timeout': timeout, 'verify': True}
        if self.proxies:
            kwargs['proxies'] = self.proxies
        response = Request('GET', api_url, **kwargs).prepare()
        return {'response':response}
    def mock_post(self, endpoint, action, data, *url_args, **url_params):
        """
        Submit to API Endpoint - for POST methods.
        :param endpoint: Endpoint
        :param action: Endpoint Action
        :param url_args: Additional endpoints(for endpoints that take part of
            the url as option)
        :param url_params: Parameters to pass to url, typically query string
        :return: response deserialized from JSON
        """
        api_url = self._endpoint(endpoint, action, *url_args)
        data = json.dumps(data, sort_keys=True)
        url_params = [(i, url_params[i]) for i in sorted(url_params.keys())]
        kwargs = {'auth': self.auth, 'headers': self.headers,
                  'params': url_params, 'data': data}#, 'verify': True}
        if self.proxies:
            kwargs['proxies'] = self.proxies
        response = Request('POST', api_url, **kwargs).prepare()
        return {'response':response}


def get_result(function, args, kwargs):
    '''
    run function with args and kwargs and mocked _get and _post
    '''
    result = function(*args, **kwargs)
    if isinstance(result, dict):
        if 'response' in result:
            #print these to see expected results
            return result['response'].url
        else:
            #happens with private methods sometimes
            #print name, result
            #print "failed"
            pass
    else:
        #get_blacklist_lookup_bulk returns a list
        #from_config returns the client
        #
        return None


def isequal(result, expected_result, _):
    '''
    assertion to test results against expected results
    used for nosetests
    '''
    assert_equal(result, expected_result)



SET_RESULTS = True
def run_tests():
    '''
    test generator
    '''
    client = Client.from_config()
    with patch.object(client, '_get', MockClient.from_config().mock_get) as mock_get, \
         patch.object(client, '_post', MockClient.from_config().mock_post) as mock_post:
        all_functions = json.load(open("all_tests_with_results.json"))
        for function_num, function in enumerate(all_functions):
            name = function['name']
            if not name.startswith('_'):
                func = getattr(client, name)
                for test_num, test in enumerate(function['tests']):
                    result = get_result(func, test['args'], test['kwargs'])
                    if SET_RESULTS:
                        all_functions[function_num]['tests'][test_num]['expected_result'] = result
                    yield isequal, result, test['expected_result'], name
    if SET_RESULTS:
        json.dump(all_functions, open("all_tests_with_results.json", 'w'), indent=4)
