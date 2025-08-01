#  CYjAX Limited

import datetime
from datetime import timedelta
from unittest.mock import patch, Mock
import types

import responses
import pytest
import pytz

import cyjax
from cyjax import ThreatActor, InvalidDateFormatException
from cyjax.resources.resource import Resource
from cyjax.resources.threat_actor.dto import ThreatActorDto
from cyjax.api_client import ApiClient


class TestThreatActor:

    fake_date = Mock(wraps=datetime.datetime)
    fake_date.now.return_value.astimezone.return_value = datetime.datetime(2020, 5, 2, 12, 0, 0, tzinfo=pytz.UTC)

    def test_instance(self):
        resource = ThreatActor('123', 'test')
        assert isinstance(resource, Resource)
        assert isinstance(resource._api_client, ApiClient)
        assert '123' == resource._api_client.get_api_key()
        assert 'test' == resource._api_client.get_api_url()

    def test_get_threat_actors_without_parameters(self, mocker):
        resource = ThreatActor()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list()
        spy_method_paginate.assert_called_once_with(endpoint='threat-actor', params={}, limit=None, dto=ThreatActorDto)

    def test_get_threat_actors_with_parameters(self, mocker):
        resource = ThreatActor()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(query='search-query', since='2020-05-02T07:31:11+00:00', until='2020-07-02T00:00:00+00:00')

        expected_params = {
            'query': 'search-query',
            'since': '2020-05-02T07:31:11+00:00',
            'until': '2020-07-02T00:00:00+00:00'
        }
        spy_method_paginate.assert_called_once_with(endpoint='threat-actor',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=ThreatActorDto)

    @patch('cyjax.helpers.datetime', fake_date)
    def test_get_threat_actors_with_date_as_timedelta(self, mocker):
        resource = ThreatActor()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(since=timedelta(hours=2), until=timedelta(hours=1))

        since = '2020-05-02T10:00:00+00:00'
        until = '2020-05-02T11:00:00+00:00'
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='threat-actor',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=ThreatActorDto)

    def test_get_threat_actors_with_date_as_datetime_without_timezone(self, mocker):
        resource = ThreatActor()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0), until=datetime.datetime(2020, 5, 2, 11, 0, 0))

        since = datetime.datetime(2020, 5, 2, 10, 0, 0).astimezone().isoformat()
        until = datetime.datetime(2020, 5, 2, 11, 0, 0).astimezone().isoformat()
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='threat-actor',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=ThreatActorDto)

    def test_get_threat_actors_with_date_as_datetime_with_timezone(self, mocker):
        resource = ThreatActor()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0, tzinfo=pytz.UTC),
                      until=datetime.datetime(2020, 5, 2, 11, 0, 0, tzinfo=pytz.UTC))

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='threat-actor',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=ThreatActorDto)

    def test_get_threat_actors_with_date_as_string(self, mocker):
        resource = ThreatActor()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(since='2020-05-02T10:00:00+00:00', until='2020-05-02T11:00:00+00:00')

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='threat-actor',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=ThreatActorDto)

    def test_get_threat_actors_with_wrong_date(self):
        resource = ThreatActor()
        with pytest.raises(InvalidDateFormatException) as e:
            resource.list(since='2020-05', until='2020-05-02T11:00:00+00:00')
        assert 'since: Incorrect date format, should be %Y-%m-%dT%H:%M:%S%z' == str(e.value)

        with pytest.raises(InvalidDateFormatException) as e:
            resource.list(since='2020-05-02T11:00:00+00:00', until='2020-05')
        assert 'until: Incorrect date format, should be %Y-%m-%dT%H:%M:%S%z' == str(e.value)

    def test_list_with_limit(self, mocker):
        resource = ThreatActor()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(limit=300)
        spy_method_paginate.assert_called_once_with(endpoint='threat-actor',
                                                    params={},
                                                    limit=300,
                                                    dto=ThreatActorDto)

    def test_setting_client(self):
        cyjax.api_key = None  # reset to defaults

        resource = ThreatActor()
        assert 'https://api.cymon.co/v2' == resource._api_client.get_api_url()
        assert resource._api_client.get_api_key() is None

        resource = ThreatActor('123456', 'https://api.new-address.com')
        assert 'https://api.new-address.com' == resource._api_client.get_api_url()
        assert '123456' == resource._api_client.get_api_key()

        cyjax.api_url = None  # Reset to default

    def test_get_one_is_not_implemented(self):
        resource = ThreatActor()

        with pytest.raises(NotImplementedError) as e:
            resource.one(4)
        assert 'This resource does not support one() method' == str(e.value)

    @responses.activate
    def test_list_response(self):
        resource = ThreatActor(api_key='test')

        mocked_entries = [
            {
                'id': '1GoxxHsBJHuZwz72-jG2',
                'name': 'APT-C-37',
                'aliases': [
                    'PaiPaiBear'
                ],
                'description': 'APT-C-37 is believed to be an Syrian cyberespionage group.',
                'notes': '',
                'techniques': [
                    'Bash History',
                    'Command and Scripting Interpreter'
                ],
                'software': [
                    'Emotet'
                ],
                'last_update': '2020-10-27T10:54:23+0000'
            }
        ]
        responses.add(responses.GET, resource._api_client.get_api_url() + '/threat-actor',
                      json=mocked_entries,
                      status=200)

        response = resource.list()

        assert isinstance(response, types.GeneratorType) is True

        response_list = list(response)
        assert len(response_list) == 1
        assert isinstance(response_list[0], ThreatActorDto) is True
        assert '1GoxxHsBJHuZwz72-jG2' == response_list[0].id
