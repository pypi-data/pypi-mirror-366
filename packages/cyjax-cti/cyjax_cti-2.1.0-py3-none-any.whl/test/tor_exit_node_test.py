#  CYjAX Limited
import datetime
from datetime import timedelta
from unittest.mock import patch, Mock, MagicMock
import types

import responses
import pytest
import pytz

import cyjax
from cyjax import TorExitNode, InvalidDateFormatException
from cyjax.resources.resource import Resource
from cyjax.resources.tor_exit_node.dto import TorExitNodeDto
from cyjax.api_client import ApiClient


class TestTorExitNode:

    fake_date = Mock(wraps=datetime.datetime)
    fake_date.now.return_value.astimezone.return_value = datetime.datetime(2020, 5, 2, 12, 0, 0, tzinfo=pytz.UTC)

    def test_instance(self):
        resource = TorExitNode('123', 'test')
        assert isinstance(resource, Resource)
        assert isinstance(resource._api_client, ApiClient)
        assert '123' == resource._api_client.get_api_key()
        assert 'test' == resource._api_client.get_api_url()

    def test_get_tor_exit_nodes_without_parameters(self, mocker):
        tor_exit_node = TorExitNode()
        spy_method_paginate = mocker.spy(tor_exit_node, '_paginate')

        tor_exit_node.list()
        spy_method_paginate.assert_called_once_with(endpoint='blacklists/tor-node',
                                                    params={},
                                                    limit=None,
                                                    dto=TorExitNodeDto)

    def test_get_tor_exit_nodes_with_parameters(self, mocker):
        tor_exit_node = TorExitNode()
        spy_method_paginate = mocker.spy(tor_exit_node, '_paginate')

        tor_exit_node.list(query='search-query', since='2020-05-02T07:31:11+00:00', until='2020-07-02T00:00:00+00:00')

        expected_params = {
            'query': 'search-query',
            'since': '2020-05-02T07:31:11+00:00',
            'until': '2020-07-02T00:00:00+00:00'
        }
        spy_method_paginate.assert_called_once_with(endpoint='blacklists/tor-node',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=TorExitNodeDto)

    @patch('cyjax.helpers.datetime', fake_date)
    def test_get_tor_exit_nodes_with_date_as_timedelta(self, mocker):
        tor_exit_node = TorExitNode()
        spy_method_paginate = mocker.spy(tor_exit_node, '_paginate')

        tor_exit_node.list(since=timedelta(hours=2), until=timedelta(hours=1))

        since = '2020-05-02T10:00:00+00:00'
        until = '2020-05-02T11:00:00+00:00'
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='blacklists/tor-node',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=TorExitNodeDto)

    def test_get_tor_exit_nodes_with_date_as_datetime_without_timezone(self, mocker):
        tor_exit_node = TorExitNode()
        spy_method_paginate = mocker.spy(tor_exit_node, '_paginate')

        tor_exit_node.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0), until=datetime.datetime(2020, 5, 2, 11, 0, 0))

        since = datetime.datetime(2020, 5, 2, 10, 0, 0).astimezone().isoformat()
        until = datetime.datetime(2020, 5, 2, 11, 0, 0).astimezone().isoformat()
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='blacklists/tor-node',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=TorExitNodeDto)

    def test_get_tor_exit_nodes_with_date_as_datetime_with_timezone(self, mocker):
        tor_exit_node = TorExitNode()
        spy_method_paginate = mocker.spy(tor_exit_node, '_paginate')

        tor_exit_node.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0, tzinfo=pytz.UTC),
                           until=datetime.datetime(2020, 5, 2, 11, 0, 0, tzinfo=pytz.UTC))

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='blacklists/tor-node',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=TorExitNodeDto)

    def test_get_tor_exit_nodes_with_date_as_string(self, mocker):
        tor_exit_node = TorExitNode()
        spy_method_paginate = mocker.spy(tor_exit_node, '_paginate')

        tor_exit_node.list(since='2020-05-02T10:00:00+00:00', until='2020-05-02T11:00:00+00:00')

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='blacklists/tor-node',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=TorExitNodeDto)

    def test_get_tor_exit_nodes_with_wrong_date(self):
        tor_exit_node = TorExitNode()
        with pytest.raises(InvalidDateFormatException):
            tor_exit_node.list(since='2020-05', until='2020-05-02T11:00:00+00:00')

        with pytest.raises(InvalidDateFormatException):
            tor_exit_node.list(since='2020-05-02T11:00:00+00:00', until='2020-05')

    def test_setting_client(self):
        cyjax.api_key = None  # reset to defaults

        resource = TorExitNode()
        assert 'https://api.cymon.co/v2' == resource._api_client.get_api_url()
        assert resource._api_client.get_api_key() is None

        resource = TorExitNode('123456', 'https://api.new-address.com')
        assert 'https://api.new-address.com' == resource._api_client.get_api_url()
        assert '123456' == resource._api_client.get_api_key()

        cyjax.api_url = None  # Reset to default

    def test_get_one_by_id(self, mocker):
        tor_exit_node = TorExitNode()
        tor_exit_node._api_client = MagicMock()
        tor_exit_node._api_client.__iter__.return_value = []

        spy_method_get_one_by_id = mocker.spy(tor_exit_node, '_get_one_by_id')

        assert hasattr(tor_exit_node, 'one')
        tor_exit_node.one(401)

        spy_method_get_one_by_id.assert_called_once_with(endpoint='blacklists/tor-node',
                                                         record_id=401,
                                                         dto=TorExitNodeDto)

    def test_list_with_limit(self, mocker):
        resource = TorExitNode()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(limit=300)
        spy_method_paginate.assert_called_once_with(endpoint='blacklists/tor-node',
                                                    params={},
                                                    limit=300,
                                                    dto=TorExitNodeDto)

    @responses.activate
    def test_list_response(self):
        resource = TorExitNode(api_key='test')

        obj = {
            'id': '915ff901bd4f9310c8055ec157ac6d6fba52a5855ead80c966bdcaab0c298ea0',
            'ip': '97.103.2.110',
            'discovered_at': '2020-10-28T11:01:01+0000'
        }

        responses.add(responses.GET, resource._api_client.get_api_url() + '/blacklists/tor-node',
                      json=[obj],
                      status=200)

        response = resource.list()

        assert isinstance(response, types.GeneratorType) is True

        response_list = list(response)
        assert len(response_list) == 1

        assert isinstance(response_list[0], TorExitNodeDto) is True
        assert '915ff901bd4f9310c8055ec157ac6d6fba52a5855ead80c966bdcaab0c298ea0' == response_list[0].id

    @responses.activate
    def test_get_one_response(self):
        resource = TorExitNode(api_key='test')

        obj = {
            'id': 'abc123',
            'ip': '97.103.2.110',
            'discovered_at': '2020-10-28T11:01:01+0000'
        }

        responses.add(responses.GET, resource._api_client.get_api_url() + '/blacklists/tor-node/abc123',
                      json=obj,
                      status=200)

        response = resource.one('abc123')

        assert isinstance(response, TorExitNodeDto) is True
        assert 'abc123' == response.id
        assert '97.103.2.110' == response.ip
        assert '2020-10-28T11:01:01+0000' == response.discovered_at
