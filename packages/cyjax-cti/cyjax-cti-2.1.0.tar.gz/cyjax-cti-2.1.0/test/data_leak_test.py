#  CYjAX Limited
import types
import datetime
from datetime import timedelta
from unittest.mock import patch, Mock, MagicMock

import responses
import pytest
import pytz

import cyjax
from cyjax import LeakedEmail, InvalidDateFormatException
from cyjax.resources.resource import Resource
from cyjax.resources.data_breach.dto import LeakedEmailDto, InvestigatorLeakedEmailDto
from cyjax.api_client import ApiClient


class TestLeakedEmail:

    fake_date = Mock(wraps=datetime.datetime)
    fake_date.now.return_value.astimezone.return_value = datetime.datetime(2020, 5, 2, 12, 0, 0, tzinfo=pytz.UTC)

    def test_instance(self):
        resource = LeakedEmail('123', 'test')
        assert isinstance(resource, Resource)
        assert isinstance(resource._api_client, ApiClient)
        assert '123' == resource._api_client.get_api_key()
        assert 'test' == resource._api_client.get_api_url()

    def test_get_leaked_emails_without_parameters(self, mocker):
        leaked_email = LeakedEmail()
        spy_method_paginate = mocker.spy(leaked_email, '_paginate')

        leaked_email.list()
        spy_method_paginate.assert_called_once_with(endpoint='data-leak/credentials',
                                                    params={},
                                                    limit=None,
                                                    dto=LeakedEmailDto)

    def test_get_leaked_emails_with_parameters(self, mocker):
        leaked_email = LeakedEmail()
        spy_method_paginate = mocker.spy(leaked_email, '_paginate')

        leaked_email.list(query='search-query', since='2020-05-02T07:31:11+00:00', until='2020-07-02T00:00:00+00:00')

        expected_params = {
            'query': 'search-query',
            'since': '2020-05-02T07:31:11+00:00',
            'until': '2020-07-02T00:00:00+00:00'
        }
        spy_method_paginate.assert_called_once_with(endpoint='data-leak/credentials',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=LeakedEmailDto)

    def test_get_leaked_emails_with_limit(self, mocker):
        resource = LeakedEmail()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(limit=5)
        spy_method_paginate.assert_called_once_with(endpoint='data-leak/credentials',
                                                    params={},
                                                    limit=5,
                                                    dto=LeakedEmailDto)

    @patch('cyjax.helpers.datetime', fake_date)
    def test_get_leaked_emails_with_date_as_timedelta(self, mocker):
        leaked_email = LeakedEmail()
        spy_method_paginate = mocker.spy(leaked_email, '_paginate')

        leaked_email.list(since=timedelta(hours=2), until=timedelta(hours=1))

        since = '2020-05-02T10:00:00+00:00'
        until = '2020-05-02T11:00:00+00:00'
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='data-leak/credentials',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=LeakedEmailDto)

    def test_get_leaked_emails_with_date_as_datetime_without_timezone(self, mocker):
        leaked_email = LeakedEmail()
        spy_method_paginate = mocker.spy(leaked_email, '_paginate')

        leaked_email.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0), until=datetime.datetime(2020, 5, 2, 11, 0, 0))

        since = datetime.datetime(2020, 5, 2, 10, 0, 0).astimezone().isoformat()
        until = datetime.datetime(2020, 5, 2, 11, 0, 0).astimezone().isoformat()
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='data-leak/credentials',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=LeakedEmailDto)

    def test_get_leaked_emails_with_date_as_datetime_with_timezone(self, mocker):
        leaked_email = LeakedEmail()
        spy_method_paginate = mocker.spy(leaked_email, '_paginate')

        leaked_email.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0, tzinfo=pytz.UTC),
                          until=datetime.datetime(2020, 5, 2, 11, 0, 0, tzinfo=pytz.UTC))

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='data-leak/credentials',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=LeakedEmailDto)

    def test_get_leaked_emails_with_date_as_string(self, mocker):
        leaked_email = LeakedEmail()
        spy_method_paginate = mocker.spy(leaked_email, '_paginate')

        leaked_email.list(since='2020-05-02T10:00:00+00:00', until='2020-05-02T11:00:00+00:00')

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='data-leak/credentials',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=LeakedEmailDto)

    def test_get_leaked_emails_with_wrong_date(self):
        leaked_email = LeakedEmail()
        with pytest.raises(InvalidDateFormatException):
            leaked_email.list(since='2020-05', until='2020-05-02T11:00:00+00:00')

        with pytest.raises(InvalidDateFormatException):
            leaked_email.list(since='2020-05-02T11:00:00+00:00', until='2020-05')

    def test_setting_client(self):
        cyjax.api_key = None  # reset to defaults

        resource = LeakedEmail()
        assert 'https://api.cymon.co/v2' == resource._api_client.get_api_url()
        assert resource._api_client.get_api_key() is None

        resource = LeakedEmail('123456', 'https://api.new-address.com')
        assert 'https://api.new-address.com' == resource._api_client.get_api_url()
        assert '123456' == resource._api_client.get_api_key()

        cyjax.api_url = None  # Reset to default

    def test_get_one_by_id(self, mocker):
        resource = LeakedEmail()
        resource._api_client = MagicMock()
        resource._api_client.__iter__.return_value = []

        spy_method_get_one_by_id = mocker.spy(resource, '_get_one_by_id')

        assert hasattr(resource, 'one')
        resource.one(400)

        spy_method_get_one_by_id.assert_called_once_with(endpoint='data-leak/credentials',
                                                         record_id=400,
                                                         dto=LeakedEmailDto)

    def test_search_invalid_param(self):
        resource = LeakedEmail()

        with pytest.raises(TypeError) as e:
            resource.search({'q': 'test'})

        assert 'Query must be of type string' == str(e.value)

    def test_search_empty_query(self):
        resource = LeakedEmail()

        with pytest.raises(TypeError) as e:
            resource.search(' ')

        assert 'Query can not be empty' == str(e.value)

    def test_search_with_query(self, mocker):
        resource = LeakedEmail()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.search('test-q')
        spy_method_paginate.assert_called_once_with(endpoint='data-leak/investigation',
                                                    params={'query': 'test-q'},
                                                    dto=InvestigatorLeakedEmailDto)

    @responses.activate
    def test_get_one_response(self):
        resource = LeakedEmail(api_key='test')

        obj = {
            'id': 'QEWtqoUB_vzuzQ6c3oBr',
            'email': 'john-doe@example.com',
            'source': 'Example Leak',
            'data_breach': {
                'id': 100,
                'name': 'Hello world',
                'url': 'https://test.cyjax.com/api/cyjax/v2/data-leak/breach/100'
            },
            'data_classes': [
                'Email addresses'
            ],
            'discovered_at': '2023-03-17T11:37:52+0000'
        }
        responses.add(responses.GET, resource._api_client.get_api_url() + '/data-leak/credentials/QEWtqoUB_vzuzQ6c3oBr',
                      json=obj,
                      status=200)

        response = resource.one('QEWtqoUB_vzuzQ6c3oBr')

        assert isinstance(response, dict) is True
        assert isinstance(response, LeakedEmailDto) is True
        assert 'QEWtqoUB_vzuzQ6c3oBr' == response['id']
        assert 'john-doe@example.com' == response.email
        assert 'Example Leak' == response.source

    @responses.activate
    def test_list_response(self):
        resource = LeakedEmail(api_key='test')

        mocked_entries = [
            {
                'id': 'QEWtqoUB_vzuzQ6c3oBr',
                'email': 'john-doe@example.com',
                'source': 'Example Leak',
                'data_breach': {
                    'id': 100,
                    'name': 'Hello world',
                    'url': 'https://test.cyjax.com/api/cyjax/v2/data-leak/breach/100'
                },
                'data_classes': [
                    'Email addresses'
                ],
                'discovered_at': '2023-03-17T11:37:52+0000'
            },
            {
                'id': 'fRWtqoUB_vzuzQ6cJoBr',
                'email': 'carol@example.com',
                'source': 'Second Leak',
                'data_breach': {
                    'id': 101,
                    'name': 'Second Leak',
                    'url': 'https://test.cyjax.com/api/cyjax/v2/data-leak/breach/101'
                },
                'data_classes': [
                    'Email addresses',
                    'IP addresses'
                ],
                'discovered_at': '2023-03-17T10:40:00+0000'
            }
        ]
        responses.add(responses.GET, resource._api_client.get_api_url() + '/data-leak/credentials',
                      json=mocked_entries,
                      status=200)

        response = resource.list()

        assert isinstance(response, types.GeneratorType) is True

        response_list = list(response)
        assert len(response_list) == 2

        assert isinstance(response_list[0], LeakedEmailDto) is True
        assert isinstance(response_list[1], LeakedEmailDto) is True

        assert 'QEWtqoUB_vzuzQ6c3oBr' == response_list[0].id
        assert 'fRWtqoUB_vzuzQ6cJoBr' == response_list[1].id

    @responses.activate
    def test_investigator_search_response(self):
        resource = LeakedEmail(api_key='test')

        mocked_entries = [
            {
                'email': 'john-doe@example.com',
                'domain': 'example.com',
                'full_name': 'John Doe',
                'country': 'Spain',
                'phone_number': '123456789',
                'data_breach': {
                    'id': 100,
                    'name': 'Hello world',
                    'url': 'https://test.cyjax.com/api/cyjax/v2/data-leak/breach/100'
                },
                'discovered_at': '2023-03-17T11:37:52+0000'
            },
            {
                'email': 'john-black@example.com',
                'domain': 'example.com',
                'country': 'Italy',
                'data_breach': {
                    'id': 101,
                    'name': 'Second Leak',
                    'url': 'https://test.cyjax.com/api/cyjax/v2/data-leak/breach/101'
                },
                'discovered_at': '2023-03-17T11:40:00+0000'
            }
        ]
        responses.add(responses.GET, resource._api_client.get_api_url() + '/data-leak/investigation',
                      json=mocked_entries,
                      status=200)

        response = resource.search('john')

        assert isinstance(response, types.GeneratorType) is True

        response_list = list(response)
        assert len(response_list) == 2

        assert isinstance(response_list[0], InvestigatorLeakedEmailDto) is True
        assert isinstance(response_list[1], InvestigatorLeakedEmailDto) is True

        assert 'john-doe@example.com' == response_list[0].email
        assert 'john-black@example.com' == response_list[1].email
