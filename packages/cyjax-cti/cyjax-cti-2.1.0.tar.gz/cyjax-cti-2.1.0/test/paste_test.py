#  CYjAX Limited
import datetime
from datetime import timedelta
from unittest.mock import patch, Mock, MagicMock
import types

import responses
import pytest
import pytz

import cyjax
from cyjax import Paste, InvalidDateFormatException
from cyjax.resources.resource import Resource
from cyjax.resources.paste import PasteDto
from cyjax.api_client import ApiClient


class TestPaste:

    fake_date = Mock(wraps=datetime.datetime)
    fake_date.now.return_value.astimezone.return_value = datetime.datetime(2020, 5, 2, 12, 0, 0, tzinfo=pytz.UTC)

    def test_instance(self):
        resource = Paste('123', 'test')
        assert isinstance(resource, Resource)
        assert isinstance(resource._api_client, ApiClient)
        assert '123' == resource._api_client.get_api_key()
        assert 'test' == resource._api_client.get_api_url()

    def test_get_pastes_without_parameters(self, mocker):
        paste = Paste()
        spy_method_paginate = mocker.spy(paste, '_paginate')

        paste.list()
        spy_method_paginate.assert_called_once_with(endpoint='paste', params={}, limit=None, dto=PasteDto)

    def test_get_pastes_with_parameters(self, mocker):
        paste = Paste()
        spy_method_paginate = mocker.spy(paste, '_paginate')

        paste.list(query='search-query', since='2020-05-02T07:31:11+00:00', until='2020-07-02T00:00:00+00:00')

        expected_params = {
            'query': 'search-query',
            'since': '2020-05-02T07:31:11+00:00',
            'until': '2020-07-02T00:00:00+00:00'
        }
        spy_method_paginate.assert_called_once_with(endpoint='paste', params=expected_params, limit=None, dto=PasteDto)

    @patch('cyjax.helpers.datetime', fake_date)
    def test_get_pastes_with_date_as_timedelta(self, mocker):
        paste = Paste()
        spy_method_paginate = mocker.spy(paste, '_paginate')

        paste.list(since=timedelta(hours=2), until=timedelta(hours=1))

        since = '2020-05-02T10:00:00+00:00'
        until = '2020-05-02T11:00:00+00:00'
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='paste', params=expected_params, limit=None, dto=PasteDto)

    def test_get_pastes_with_date_as_datetime_without_timezone(self, mocker):
        paste = Paste()
        spy_method_paginate = mocker.spy(paste, '_paginate')

        paste.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0), until=datetime.datetime(2020, 5, 2, 11, 0, 0))

        since = datetime.datetime(2020, 5, 2, 10, 0, 0).astimezone().isoformat()
        until = datetime.datetime(2020, 5, 2, 11, 0, 0).astimezone().isoformat()
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='paste', params=expected_params, limit=None, dto=PasteDto)

    def test_get_pastes_with_date_as_datetime_with_timezone(self, mocker):
        paste = Paste()
        spy_method_paginate = mocker.spy(paste, '_paginate')

        paste.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0, tzinfo=pytz.UTC),
                   until=datetime.datetime(2020, 5, 2, 11, 0, 0, tzinfo=pytz.UTC))

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='paste', params=expected_params, limit=None, dto=PasteDto)

    def test_get_pastes_with_date_as_string(self, mocker):
        paste = Paste()
        spy_method_paginate = mocker.spy(paste, '_paginate')

        paste.list(since='2020-05-02T10:00:00+00:00', until='2020-05-02T11:00:00+00:00')

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='paste', params=expected_params, limit=None, dto=PasteDto)

    def test_get_pastes_with_wrong_date(self):
        paste = Paste()
        with pytest.raises(InvalidDateFormatException):
            paste.list(since='2020-05', until='2020-05-02T11:00:00+00:00')

        with pytest.raises(InvalidDateFormatException):
            paste.list(since='2020-05-02T11:00:00+00:00', until='2020-05')

    def test_setting_client(self):
        cyjax.api_key = None  # reset to defaults

        resource = Paste()
        assert 'https://api.cymon.co/v2' == resource._api_client.get_api_url()
        assert resource._api_client.get_api_key() is None

        resource = Paste('123456', 'https://api.new-address.com')
        assert 'https://api.new-address.com' == resource._api_client.get_api_url()
        assert '123456' == resource._api_client.get_api_key()

        cyjax.api_url = None  # Reset to default

    def test_get_one_by_id(self, mocker):
        resource = Paste()
        resource._api_client = MagicMock()
        resource._api_client.__iter__.return_value = []

        spy_method_get_one_by_id = mocker.spy(resource, '_get_one_by_id')

        assert hasattr(resource, 'one')
        resource.one('595c3bc02e3eac24ceab86')

        spy_method_get_one_by_id.assert_called_once_with(endpoint='paste',
                                                         record_id='595c3bc02e3eac24ceab86',
                                                         dto=PasteDto)

    def test_list_with_limit(self, mocker):
        resource = Paste()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(limit=300)
        spy_method_paginate.assert_called_once_with(endpoint='paste', params={}, limit=300, dto=PasteDto)

    @responses.activate
    def test_list_response(self):
        resource = Paste(api_key='test')
        mocked_entries = [
            {
                "id": "126ec717874595c3bc02e3eac24ceab861013e8b",
                "paste_id": "cRK1nFrw",
                "title": "https://pastebin.com/cRK1nFrw",
                "url": "https://pastebin.com/cRK1nFrw",
                "content": "pi@raspi2:~ $ sudo ./czadsb-install.sh",
                "discovered_at": "2020-10-28T11:06:58+0000"
            }
        ]
        responses.add(responses.GET, resource._api_client.get_api_url() + '/paste',
                      json=mocked_entries,
                      status=200)

        response = resource.list()

        assert isinstance(response, types.GeneratorType) is True

        response_list = list(response)
        assert len(response_list) == 1

        assert isinstance(response_list[0], PasteDto) is True
        assert '126ec717874595c3bc02e3eac24ceab861013e8b' == response_list[0].id

    @responses.activate
    def test_one_response(self):
        resource = Paste(api_key='test')
        obj = {
            "id": "126ec717874595c3bc02e3eac24ceab861013e8b",
            "paste_id": "cRK1nFrw",
            "title": "https://pastebin.com/cRK1nFrw",
            "url": "https://pastebin.com/cRK1nFrw",
            "content": "pi@raspi2:~ $ sudo ./czadsb-install.sh",
            "discovered_at": "2020-10-28T11:06:58+0000"
        }
        responses.add(responses.GET, resource._api_client.get_api_url() +
                      '/paste/126ec717874595c3bc02e3eac24ceab861013e8b',
                      json=obj,
                      status=200)

        response = resource.one('126ec717874595c3bc02e3eac24ceab861013e8b')

        assert isinstance(response, PasteDto) is True
        assert '126ec717874595c3bc02e3eac24ceab861013e8b' == response.id
