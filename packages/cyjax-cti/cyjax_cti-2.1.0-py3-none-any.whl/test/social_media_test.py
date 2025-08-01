#  CYjAX Limited
import datetime
import types
from datetime import timedelta
from unittest.mock import patch, Mock, MagicMock

import responses
import pytest
import pytz

import cyjax
from cyjax import SocialMedia, InvalidDateFormatException
from cyjax.resources.social_media import SocialMediaDto
from cyjax.resources.resource import Resource
from cyjax.api_client import ApiClient
from test import api_responses


class TestSocialMedia:

    fake_date = Mock(wraps=datetime.datetime)
    fake_date.now.return_value.astimezone.return_value = datetime.datetime(2020, 5, 2, 12, 0, 0, tzinfo=pytz.UTC)

    def test_instance(self):
        resource = SocialMedia('123', 'test')
        assert isinstance(resource, Resource)
        assert isinstance(resource._api_client, ApiClient)
        assert '123' == resource._api_client.get_api_key()
        assert 'test' == resource._api_client.get_api_url()

    def test_list_without_parameters(self, mocker):
        resource = SocialMedia()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list()
        spy_method_paginate.assert_called_once_with(endpoint='social-media', params={}, limit=None, dto=SocialMediaDto)

    def test_list_with_parameters(self, mocker):
        resource = SocialMedia()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(query='search-query', since='2020-05-02T07:31:11+00:00', until='2020-07-02T00:00:00+00:00')

        expected_params = {
            'query': 'search-query',
            'since': '2020-05-02T07:31:11+00:00',
            'until': '2020-07-02T00:00:00+00:00'
        }
        spy_method_paginate.assert_called_once_with(endpoint='social-media',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=SocialMediaDto)

    @patch('cyjax.helpers.datetime', fake_date)
    def test_list_with_date_as_timedelta(self, mocker):
        resource = SocialMedia()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(since=timedelta(hours=2), until=timedelta(hours=1))

        since = '2020-05-02T10:00:00+00:00'
        until = '2020-05-02T11:00:00+00:00'
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='social-media',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=SocialMediaDto)

    def test_list_with_date_as_datetime_without_timezone(self, mocker):
        resource = SocialMedia()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0), until=datetime.datetime(2020, 5, 2, 11, 0, 0))

        since = datetime.datetime(2020, 5, 2, 10, 0, 0).astimezone().isoformat()
        until = datetime.datetime(2020, 5, 2, 11, 0, 0).astimezone().isoformat()
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='social-media',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=SocialMediaDto)

    def test_list_with_date_as_datetime_with_timezone(self, mocker):
        resource = SocialMedia()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0, tzinfo=pytz.UTC),
                      until=datetime.datetime(2020, 5, 2, 11, 0, 0, tzinfo=pytz.UTC))

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='social-media',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=SocialMediaDto)

    def test_list_with_date_as_string(self, mocker):
        resource = SocialMedia()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(since='2020-05-02T10:00:00+00:00', until='2020-05-02T11:00:00+00:00')

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='social-media',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=SocialMediaDto)

    def test_get_tweets_with_wrong_date(self):
        resource = SocialMedia()
        with pytest.raises(InvalidDateFormatException):
            resource.list(since='2020-05', until='2020-05-02T11:00:00+00:00')

        with pytest.raises(InvalidDateFormatException):
            resource.list(since='2020-05-02T11:00:00+00:00', until='2020-05')

    def test_setting_client(self):
        cyjax.api_key = None  # reset to defaults

        resource = SocialMedia()
        assert 'https://api.cymon.co/v2' == resource._api_client.get_api_url()
        assert resource._api_client.get_api_key() is None

        resource = SocialMedia('123456', 'https://api.new-address.com')
        assert 'https://api.new-address.com' == resource._api_client.get_api_url()
        assert '123456' == resource._api_client.get_api_key()

        cyjax.api_url = None  # Reset to default

    def test_list_with_limit(self, mocker):
        resource = SocialMedia()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(limit=300)
        spy_method_paginate.assert_called_once_with(endpoint='social-media', params={}, limit=300, dto=SocialMediaDto)

    def test_get_one_by_id(self, mocker):
        resource = SocialMedia()
        resource._api_client = MagicMock()
        resource._api_client.__iter__.return_value = []

        spy_method_get_one_by_id = mocker.spy(resource, '_get_one_by_id')

        assert hasattr(resource, 'one')
        resource.one(400)

        spy_method_get_one_by_id.assert_called_once_with(endpoint='social-media', record_id=400, dto=SocialMediaDto)

    @responses.activate
    def test_get_one_by_id_response_not_found(self):
        resource = SocialMedia(api_key='test')

        responses.add(responses.GET, resource._api_client.get_api_url() + '/social-media/5qSi-X8B391kjxB2B0Cd',
                      json=api_responses.get(404),
                      status=404)

        with pytest.raises(cyjax.exceptions.NotFoundException) as e:
            resource.one('5qSi-X8B391kjxB2B0Cd')
        assert 'Not found.' == str(e.value)

    @responses.activate
    def test_one_response(self):
        resource = SocialMedia(api_key='test')

        responses.add(responses.GET, resource._api_client.get_api_url() + '/social-media/5qSi-X8B391kjxB2B0Cd',
                      json={"id": "5qSi-X8B391kjxB2B0Cd",
                            "source": "whatsapp",
                            "username": "@Mario",
                            "content": "<p>hello all people</p>",
                            "priority": "medium",
                            "tags": [
                                "IT"
                            ],
                            "source_timestamp": "2022-04-05T12:10:19+0000",
                            "timestamp": "2022-04-05T12:10:19+0000",
                            "image": "https://test.cyjax.com/api/cyjax/v2/social-media/4qSi-X8B391kjxBBB0Cd/image"
                            },
                      status=200)

        response = resource.one('5qSi-X8B391kjxB2B0Cd')

        assert isinstance(response, dict) is True
        assert isinstance(response, SocialMediaDto) is True

        assert '5qSi-X8B391kjxB2B0Cd' == response.get('id')
        assert 'whatsapp' == response.source
        assert '@Mario' == response['username']
        assert '<p>hello all people</p>' == response.get('content')
        assert 'medium' == response.get('priority')
        assert ['IT'] == response.get('tags')
        assert '2022-04-05T12:10:19+0000' == response.get('source_timestamp')
        assert '2022-04-05T12:10:19+0000' == response.get('timestamp')
        assert 'https://test.cyjax.com/api/cyjax/v2/social-media/4qSi-X8B391kjxBBB0Cd/image' == response.get('image')

    @responses.activate
    def test_list_response(self):
        resource = SocialMedia(api_key='test')

        responses.add(responses.GET, resource._api_client.get_api_url() + '/social-media',
                      json=[
                            {
                                "id": "5qSi-X8B391kjxB2B0Cd",
                                "source": "whatsapp",
                                "username": "@Mario",
                                "content": "<p>hello all people</p>",
                                "priority": "medium",
                                "tags": [
                                    "IT"
                                ],
                                "source_timestamp": "2022-04-05T12:10:19+0000",
                                "timestamp": "2022-04-05T12:10:19+0000",
                                "image": "https://test.cyjax.com/api/cyjax/v2/social-media/4qSi-X8B391kjxBBB0Cd/image"
                            },
                            {
                                "id": "OrT8Zn4BdrjEUmqMBXpe",
                                "source": "instagram",
                                "username": "@Tester-123456",
                                "content": "<p>IG post with a lot of tags for testing</p>",
                                "priority": "low",
                                "tags": [
                                    "ddos",
                                    "hacker",
                                    "instagram",
                                    "facebook",
                                    "social media",
                                    "trojan",
                                    "virus",
                                    "attack",
                                    "injection",
                                    "bank",
                                    "fraud",
                                    "europe",
                                    "uk",
                                    "cards",
                                    "stolen",
                                    "prepay"
                                ],
                                "source_timestamp": "2022-01-17T09:59:45+0000",
                                "timestamp": "2022-04-05T08:59:45+0000",
                                "image": "http://test.cyjax.com/api/cyjax/v2/social-media/OrT8Zn4BdrjEUmqMBXpe/image"
                            },
                            {
                                "id": "FlbuTokB4ev0YSLAOJ-i",
                                "source": "reddit",
                                "username": "@fordeer",
                                "content": "<p>two categories</p>",
                                "priority": "low",
                                "tags": [
                                    "cards"
                                ],
                                "source_timestamp": "2023-07-13T11:06:22+0000",
                                "timestamp": "2023-07-13T11:06:22+0000",
                                "image": "http://test.cyjax.com/api/cyjax/v2/social-media/FlbuTokB4ev0YSLAOJ-i/image"
                            }
                        ],
                      status=200)

        response = resource.list()

        assert isinstance(response, types.GeneratorType) is True

        response_list = list(response)
        assert len(response_list) == 3

        assert isinstance(response_list[0], SocialMediaDto) is True
        assert isinstance(response_list[1], SocialMediaDto) is True
        assert isinstance(response_list[2], SocialMediaDto) is True

        assert '5qSi-X8B391kjxB2B0Cd' == response_list[0].id
        assert 'OrT8Zn4BdrjEUmqMBXpe' == response_list[1].get('id')
        assert 'FlbuTokB4ev0YSLAOJ-i' == response_list[2]['id']

    @responses.activate
    def test_list_without_entries_found_response(self):
        resource = SocialMedia(api_key='test')

        responses.add(responses.GET, resource._api_client.get_api_url() + '/social-media',
                      json=[],
                      status=200)

        response = resource.list()

        assert isinstance(response, types.GeneratorType) is True
        assert len(list(response)) == 0
