#  CYjAX Limited
import datetime
from datetime import timedelta
from unittest.mock import patch, Mock
import types

import responses
import pytest
import pytz

import cyjax
from cyjax import MaliciousDomain, InvalidDateFormatException
from cyjax.resources.resource import Resource
from cyjax.resources.malicious_domain import MaliciousDomainDto
from cyjax.api_client import ApiClient


class TestMaliciousDomain:

    fake_date = Mock(wraps=datetime.datetime)
    fake_date.now.return_value.astimezone.return_value = datetime.datetime(2020, 5, 2, 12, 0, 0, tzinfo=pytz.UTC)

    def test_instance(self):
        resource = MaliciousDomain('123', 'test')
        assert isinstance(resource, Resource)
        assert isinstance(resource._api_client, ApiClient)
        assert '123' == resource._api_client.get_api_key()
        assert 'test' == resource._api_client.get_api_url()

    def test_get_malicious_domain_without_parameters(self, mocker):
        malicious_domain = MaliciousDomain()
        spy_method_paginate = mocker.spy(malicious_domain, '_paginate')

        malicious_domain.list()
        spy_method_paginate.assert_called_once_with(endpoint='domain-monitor/potential-malicious-domain',
                                                    params={},
                                                    limit=None,
                                                    dto=MaliciousDomainDto)

    def test_get_malicious_domain_with_parameters(self, mocker):
        malicious_domain = MaliciousDomain()
        spy_method_paginate = mocker.spy(malicious_domain, '_paginate')

        malicious_domain.list(since='2020-05-02T07:31:11+00:00', until='2020-07-02T00:00:00+00:00')

        expected_params = {'since': '2020-05-02T07:31:11+00:00', 'until': '2020-07-02T00:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='domain-monitor/potential-malicious-domain',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=MaliciousDomainDto)

    @patch('cyjax.helpers.datetime', fake_date)
    def test_get_malicious_domain_with_date_as_timedelta(self, mocker):
        malicious_domain = MaliciousDomain()
        spy_method_paginate = mocker.spy(malicious_domain, '_paginate')

        malicious_domain.list(since=timedelta(hours=2), until=timedelta(hours=1))

        since = '2020-05-02T10:00:00+00:00'
        until = '2020-05-02T11:00:00+00:00'
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='domain-monitor/potential-malicious-domain',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=MaliciousDomainDto)

    def test_get_malicious_domain_with_date_as_datetime_without_timezone(self, mocker):
        malicious_domain = MaliciousDomain()
        spy_method_paginate = mocker.spy(malicious_domain, '_paginate')

        malicious_domain.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0),
                              until=datetime.datetime(2020, 5, 2, 11, 0, 0))

        since = datetime.datetime(2020, 5, 2, 10, 0, 0).astimezone().isoformat()
        until = datetime.datetime(2020, 5, 2, 11, 0, 0).astimezone().isoformat()
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='domain-monitor/potential-malicious-domain',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=MaliciousDomainDto)

    def test_get_malicious_domain_with_date_as_datetime_with_timezone(self, mocker):
        malicious_domain = MaliciousDomain()
        spy_method_paginate = mocker.spy(malicious_domain, '_paginate')

        malicious_domain.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0, tzinfo=pytz.UTC),
                              until=datetime.datetime(2020, 5, 2, 11, 0, 0, tzinfo=pytz.UTC))

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='domain-monitor/potential-malicious-domain',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=MaliciousDomainDto)

    def test_get_malicious_domain_with_date_as_string(self, mocker):
        malicious_domain = MaliciousDomain()
        spy_method_paginate = mocker.spy(malicious_domain, '_paginate')

        malicious_domain.list(since='2020-05-02T10:00:00+00:00', until='2020-05-02T11:00:00+00:00')

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='domain-monitor/potential-malicious-domain',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=MaliciousDomainDto)

    def test_get_malicious_domain_with_wrong_date(self):
        malicious_domain = MaliciousDomain()
        with pytest.raises(InvalidDateFormatException):
            malicious_domain.list(since='2020-05', until='2020-05-02T11:00:00+00:00')

        with pytest.raises(InvalidDateFormatException):
            malicious_domain.list(since='2020-05-02T11:00:00+00:00', until='2020-05')

    def test_setting_client(self):
        cyjax.api_key = None  # reset to defaults

        resource = MaliciousDomain()
        assert 'https://api.cymon.co/v2' == resource._api_client.get_api_url()
        assert resource._api_client.get_api_key() is None

        resource = MaliciousDomain('123456', 'https://api.new-address.com')
        assert 'https://api.new-address.com' == resource._api_client.get_api_url()
        assert '123456' == resource._api_client.get_api_key()

        cyjax.api_url = None  # Reset to default

    def test_get_one_is_not_implemented(self):
        resource = MaliciousDomain()

        with pytest.raises(NotImplementedError):
            resource.one(4)

    def test_list_with_limit(self, mocker):
        resource = MaliciousDomain()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(limit=300)
        spy_method_paginate.assert_called_once_with(endpoint='domain-monitor/potential-malicious-domain',
                                                    params={},
                                                    limit=300,
                                                    dto=MaliciousDomainDto)

    @responses.activate
    def test_list_response(self):
        resource = MaliciousDomain(api_key='test')

        mocked_entries = [
            {
                "domains": [
                    "autodiscover.coronavirusepicenter.com",
                    "coronavirusepicenter.com",
                    "cpanel.coronavirusepicenter.com",
                    "cpcalendars.coronavirusepicenter.com",
                    "cpcontacts.coronavirusepicenter.com",
                    "mail.coronavirusepicenter.com",
                    "webdisk.coronavirusepicenter.com",
                    "webmail.coronavirusepicenter.com",
                    "www.coronavirusepicenter.com"
                ],
                "matched_domains": [
                    "autodiscover.coronavirusepicenter.com"
                ],
                "unmatched_domains": [
                    "mail.coronavirusepicenter.com"
                ],
                "keyword": [
                    "covid"
                ],
                "type": "ssl-certificate",
                "discovery_date": "2020-10-25T10:31:45+0100",
                "create_date": "",
                "expiration_timestamp": "2021-10-25T10:31:45+0100",
                "source": "Let's Encrypt 'Sapling 2023h1' log"
            },
            {
                "domains": [
                    "example2.com",
                ],
                "matched_domains": [
                    "example.com"
                ],
                "unmatched_domains": [
                    "test.com"
                ],
                "keyword": [
                    "example"
                ],
                "type": "ssl-certificate",
                "discovery_date": "2020-10-25T10:31:45+0100",
                "create_date": "",
                "expiration_timestamp": "2021-10-25T10:31:45+0100",
                "source": "Let's Encrypt 'Sapling 2023h1' log"
            }
        ]

        responses.add(responses.GET, resource._api_client.get_api_url() + '/domain-monitor/potential-malicious-domain',
                      json=mocked_entries,
                      status=200)

        response = resource.list()

        assert isinstance(response, types.GeneratorType) is True

        response_list = list(response)
        assert len(response_list) == 2

        assert isinstance(response_list[0], MaliciousDomainDto) is True
        assert isinstance(response_list[1], MaliciousDomainDto) is True
