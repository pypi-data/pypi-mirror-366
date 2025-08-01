import pytest
import requests
import responses

import cyjax
from cyjax import ApiKeyNotFoundException
from cyjax.api_client import ApiClient
from cyjax.exceptions import UnauthorizedException, TooManyRequestsException, ForbiddenException, NotFoundException, \
    ValidationException
from test import api_responses


class TestApiClient:

    CURRENT_APP_VERSION = '2.1.0'
    DEFAULT_TIMEOUT = 15

    def test_current_app_version(self):
        assert self.CURRENT_APP_VERSION == cyjax.__version__

    def test_api_key_is_not_set(self):
        api_client = ApiClient()
        with pytest.raises(ApiKeyNotFoundException) as e:
            api_client.send(method='get', endpoint='test/endpoint')
        assert 'API key not found. Please set API key.' == str(e.value)

    def test_set_api_key_on_module(self):
        cyjax.api_key = 'module_api_key'
        api_client = ApiClient()
        assert api_client.get_api_key() == 'module_api_key'

    def test_set_api_key_on_constructor(self):
        api_client = ApiClient(api_key='constructor_api_key')
        assert api_client.get_api_key() == 'constructor_api_key'

    def test_set_api_key_on_constructor_has_preferences_over_module(self):
        cyjax.api_key = 'module_api_key'
        api_client = ApiClient(api_key='constructor_api_key')
        assert api_client.get_api_key() == 'constructor_api_key'

    def test_default_proxy_settings(self):
        api_client = ApiClient()
        assert api_client._get_proxies() is None

    def test_set_proxy_settings_on_module(self):
        test_proxies = {'http': 'http://user:pass@10.10.1.0:3333',
                        'https': 'https://user:pass@10.10.1.0:3333'}
        cyjax.proxy_settings = test_proxies
        api_client = ApiClient()
        proxies = api_client._get_proxies()
        assert proxies is not None
        assert test_proxies == proxies

        cyjax.proxy_settings = None

    def test_default_verify_ssl_settings(self):
        api_client = ApiClient()
        assert api_client._get_verify() is True

    def test_set_verify_sll_settings_on_module(self):
        cyjax.verify_ssl = False
        api_client = ApiClient()
        assert api_client._get_verify() is False
        cyjax.verify_ssl = True

    def test_default_api_url(self):
        assert 'https://api.cymon.co/v2' == ApiClient.BASE_URI
        api_clinet = ApiClient(api_key='constructor_api_key')
        assert 'https://api.cymon.co/v2' == api_clinet.get_api_url()

    def test_default_timeout(self):
        assert self.DEFAULT_TIMEOUT == 15
        assert self.DEFAULT_TIMEOUT == ApiClient.TIMEOUT

    def test_set_api_url_on_module(self):
        cyjax.api_url = 'https://api.module-api-url.com'
        api_client = ApiClient()
        assert api_client.get_api_url() == 'https://api.module-api-url.com'
        cyjax.api_url = None  # Reset to default

    def test_set_api_url_on_client_constructor(self):
        api_clinet = ApiClient(api_key='constructor_api_key', api_url='https://api.new-url-cyjax.com')
        assert 'https://api.new-url-cyjax.com' == api_clinet.get_api_url()

    def test_set_api_url_on_constructor_has_preferences_over_module(self):
        cyjax.api_url = 'https://api.module-api-url.com'
        api_client = ApiClient(None, api_url='http://api.constructor-api-url.com')
        assert api_client.get_api_url() == 'http://api.constructor-api-url.com'
        cyjax.api_url = None  # Reset to default

    @responses.activate
    def test_send(self,):
        api_client = ApiClient(api_key='foo_api_key')
        api_url = api_client.get_api_url()

        responses.add(responses.GET, api_url + '/test/endpoint?param1=test&param2=foo',
                      json=[{'1': 'a', '2': 'b', '3': [1, 2, 3]}], status=200)

        response = api_client.send(method='get', endpoint='test/endpoint', params={'param1': 'test', 'param2': 'foo'},
                                   data={'foo': 'test'})

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == api_url + '/test/endpoint?param1=test&param2=foo'
        assert responses.calls[0].request.body == "foo=test"
        assert responses.calls[0].response.text == '[{"1": "a", "2": "b", "3": [1, 2, 3]}]'

        assert response.status_code == 200
        assert response.json() == [{'1': 'a', '2': 'b', '3': [1, 2, 3]}]

    @responses.activate
    def test_send_compare_request_params(self, mocker):
        api_client = ApiClient(api_key='foo_api_key')
        responses.add(responses.GET, ApiClient.BASE_URI + '/test/endpoint',
                      json={'success': True}, status=200)
        request_method = mocker.spy(requests.api, 'request')

        response = api_client.send(method='get', endpoint='test/endpoint', params={'param1': 'test', 'param2': 'foo'},
                                   data={'foo': 'test'})

        assert response.status_code == 200
        assert response.json().get('success') is True

        request_method.assert_called_once_with(method='get',
                                               url=ApiClient.BASE_URI + '/test/endpoint',
                                               data={'foo': 'test'},
                                               params={'param1': 'test', 'param2': 'foo'},
                                               headers={'Authorization': 'Bearer foo_api_key',
                                                        'User-Agent': 'CyjaxPythonSDK/' + self.CURRENT_APP_VERSION},
                                               proxies=None,
                                               timeout=self.DEFAULT_TIMEOUT,
                                               verify=True)

    @responses.activate
    def test_send_with_proxies(self, mocker):
        assert cyjax.proxy_settings is None

        test_proxies = {'http': 'http://user:pass@10.10.1.0:3333',
                        'https': 'https://user:pass@10.10.1.0:3333'}
        cyjax.proxy_settings = test_proxies

        api_client = ApiClient(api_key='foo_api_key')
        responses.add(responses.GET, ApiClient.BASE_URI + '/test/endpoint',
                      json={'success': True}, status=200)
        request_method = mocker.spy(requests.api, 'request')

        # with requests
        response = api_client.send(method='get', endpoint='test/endpoint')

        assert response.status_code == 200
        assert response.json().get('success') is True

        request_method.assert_called_once_with(method='get',
                                               url=ApiClient.BASE_URI + '/test/endpoint',
                                               data={},
                                               params={},
                                               headers={'Authorization': 'Bearer foo_api_key',
                                                        'User-Agent': 'CyjaxPythonSDK/' + self.CURRENT_APP_VERSION},
                                               proxies=test_proxies,
                                               timeout=self.DEFAULT_TIMEOUT,
                                               verify=True)

        cyjax.proxy_settings = None

    @responses.activate
    def test_rest_request_throw_exception(self):
        api_client = ApiClient(api_key='foo_api_key')

        responses.add(responses.GET, api_client.get_api_url() + '/test/unauthorized',
                      json=api_responses.get(401),
                      status=401)
        responses.add(responses.GET, api_client.get_api_url() + '/test/forbidden',
                      json=api_responses.get(403),
                      status=403)
        responses.add(responses.GET, api_client.get_api_url() + '/test/not-found',
                      json=api_responses.get(404),
                      status=404)
        responses.add(responses.GET, api_client.get_api_url() + '/test/too-many',
                      json=api_responses.get(429),
                      status=429)
        responses.add(responses.GET, api_client.get_api_url() + '/test/validation',
                      json=api_responses.get(422),
                      status=422)

        with pytest.raises(UnauthorizedException) as e:
            api_client.send(method='get', endpoint='test/unauthorized')
        assert 'You are unauthorized to perform this request.' == str(e.value)

        with pytest.raises(TooManyRequestsException) as e:
            api_client.send(method='get', endpoint='test/too-many')
        assert 'Too many requests sent.' == str(e.value)

        with pytest.raises(ForbiddenException) as e:
            api_client.send(method='get', endpoint='test/forbidden')
        assert 'You do not have enough permission to access this resource.' == str(e.value)

        with pytest.raises(NotFoundException) as e:
            api_client.send(method='get', endpoint='test/not-found')
        assert 'Not found.' == str(e.value)

        with pytest.raises(ValidationException) as e:
            api_client.send(method='get', endpoint='test/validation')
        assert 'Validation error: Missing login param' == str(e.value)

    @responses.activate
    def test_call_with_default_ssl_verify_settings(self, mocker):
        assert cyjax.verify_ssl is True

        api_client = ApiClient(api_key='foo_api_key')
        responses.add(responses.GET, ApiClient.BASE_URI + '/test/endpoint',
                      json={'success': True}, status=200)

        request_method = mocker.spy(requests.api, 'request')

        response = api_client.send(method='get', endpoint='test/endpoint')

        assert response.status_code == 200
        assert response.json().get('success') is True

        request_method.assert_called_once_with(method='get',
                                               url=ApiClient.BASE_URI + '/test/endpoint',
                                               data={},
                                               params={},
                                               headers={'Authorization': 'Bearer foo_api_key',
                                                        'User-Agent': 'CyjaxPythonSDK/' + self.CURRENT_APP_VERSION},
                                               proxies=None,
                                               timeout=self.DEFAULT_TIMEOUT,
                                               verify=True)

    @responses.activate
    def test_call_with_disabled_ssl_verify(self, mocker):
        assert cyjax.verify_ssl is True
        cyjax.verify_ssl = False

        api_client = ApiClient(api_key='foo_api_key')
        responses.add(responses.GET, ApiClient.BASE_URI + '/test/endpoint',
                      json={'success': True}, status=200)

        request_method = mocker.spy(requests.api, 'request')

        response = api_client.send(method='get', endpoint='test/endpoint')

        assert response.status_code == 200
        assert response.json().get('success') is True

        request_method.assert_called_once_with(method='get',
                                               url=ApiClient.BASE_URI + '/test/endpoint',
                                               data={},
                                               params={},
                                               headers={'Authorization': 'Bearer foo_api_key',
                                                        'User-Agent': 'CyjaxPythonSDK/' + self.CURRENT_APP_VERSION},
                                               proxies=None,
                                               timeout=self.DEFAULT_TIMEOUT,
                                               verify=False)

        cyjax.verify_ssl = True

    @responses.activate
    def test_default_user_agent(self,):
        api_client = ApiClient(api_key='foo_api_key')
        api_url = api_client.get_api_url()

        responses.add(responses.GET, api_url + '/test/endpoint', status=200)

        response = api_client.send(method='get', endpoint='test/endpoint')

        assert len(responses.calls) == 1
        assert 'CyjaxPythonSDK/{}'.format(self.CURRENT_APP_VERSION) == response.request.headers.get('User-Agent')

    @responses.activate
    def test_bespoke_client_user_agent_header(self,):
        cyjax.client_name = 'BespokeApp 1.0'

        api_client = ApiClient(api_key='foo_api_key')
        api_url = api_client.get_api_url()

        responses.add(responses.GET, api_url + '/test/endpoint', status=200)

        response = api_client.send(method='get', endpoint='test/endpoint')

        assert len(responses.calls) == 1
        assert 'CyjaxPythonSDK/{} (BespokeApp 1.0)'.format(self.CURRENT_APP_VERSION) == \
               response.request.headers.get('User-Agent')
        cyjax.client_name = None  # revert back
