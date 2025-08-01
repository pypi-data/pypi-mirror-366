#  CYjAX Limited
import datetime
from datetime import timedelta
from unittest.mock import patch, Mock
import types

import responses
import pytest
import pytz

import cyjax
from cyjax import Tweet, InvalidDateFormatException
from cyjax.resources.resource import Resource
from cyjax.resources.tweet.dto import TweetDto
from cyjax.api_client import ApiClient


class TestTweet:

    fake_date = Mock(wraps=datetime.datetime)
    fake_date.now.return_value.astimezone.return_value = datetime.datetime(2020, 5, 2, 12, 0, 0, tzinfo=pytz.UTC)

    def test_instance(self):
        resource = Tweet('123', 'test')
        assert isinstance(resource, Resource)
        assert isinstance(resource._api_client, ApiClient)
        assert '123' == resource._api_client.get_api_key()
        assert 'test' == resource._api_client.get_api_url()

    def test_get_tweets_without_parameters(self, mocker):
        tweet = Tweet()
        spy_method_paginate = mocker.spy(tweet, '_paginate')

        tweet.list()
        spy_method_paginate.assert_called_once_with(endpoint='tweet', params={}, limit=None, dto=TweetDto)

    def test_get_tweets_with_parameters(self, mocker):
        tweet = Tweet()
        spy_method_paginate = mocker.spy(tweet, '_paginate')

        tweet.list(query='search-query', since='2020-05-02T07:31:11+00:00', until='2020-07-02T00:00:00+00:00')

        expected_params = {
            'query': 'search-query',
            'since': '2020-05-02T07:31:11+00:00',
            'until': '2020-07-02T00:00:00+00:00'
        }
        spy_method_paginate.assert_called_once_with(endpoint='tweet', params=expected_params, limit=None, dto=TweetDto)

    @patch('cyjax.helpers.datetime', fake_date)
    def test_get_tweets_with_date_as_timedelta(self, mocker):
        tweet = Tweet()
        spy_method_paginate = mocker.spy(tweet, '_paginate')

        tweet.list(since=timedelta(hours=2), until=timedelta(hours=1))

        since = '2020-05-02T10:00:00+00:00'
        until = '2020-05-02T11:00:00+00:00'
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='tweet', params=expected_params, limit=None, dto=TweetDto)

    def test_get_tweets_with_date_as_datetime_without_timezone(self, mocker):
        tweet = Tweet()
        spy_method_paginate = mocker.spy(tweet, '_paginate')

        tweet.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0), until=datetime.datetime(2020, 5, 2, 11, 0, 0))

        since = datetime.datetime(2020, 5, 2, 10, 0, 0).astimezone().isoformat()
        until = datetime.datetime(2020, 5, 2, 11, 0, 0).astimezone().isoformat()
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='tweet', params=expected_params, limit=None, dto=TweetDto)

    def test_get_tweets_with_date_as_datetime_with_timezone(self, mocker):
        tweet = Tweet()
        spy_method_paginate = mocker.spy(tweet, '_paginate')

        tweet.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0, tzinfo=pytz.UTC),
                   until=datetime.datetime(2020, 5, 2, 11, 0, 0, tzinfo=pytz.UTC))

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='tweet', params=expected_params, limit=None, dto=TweetDto)

    def test_get_tweets_with_date_as_string(self, mocker):
        tweet = Tweet()
        spy_method_paginate = mocker.spy(tweet, '_paginate')

        tweet.list(since='2020-05-02T10:00:00+00:00', until='2020-05-02T11:00:00+00:00')

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='tweet', params=expected_params, limit=None, dto=TweetDto)

    def test_get_tweets_with_wrong_date(self):
        tweet = Tweet()
        with pytest.raises(InvalidDateFormatException):
            tweet.list(since='2020-05', until='2020-05-02T11:00:00+00:00')

        with pytest.raises(InvalidDateFormatException):
            tweet.list(since='2020-05-02T11:00:00+00:00', until='2020-05')

    def test_setting_client(self):
        cyjax.api_key = None  # reset to defaults

        resource = Tweet()
        assert 'https://api.cymon.co/v2' == resource._api_client.get_api_url()
        assert resource._api_client.get_api_key() is None

        resource = Tweet('123456', 'https://api.new-address.com')
        assert 'https://api.new-address.com' == resource._api_client.get_api_url()
        assert '123456' == resource._api_client.get_api_key()

        cyjax.api_url = None  # Reset to default

    def test_get_one_is_not_implemented(self):
        resource = Tweet()

        with pytest.raises(NotImplementedError):
            resource.one(4)

    def test_list_with_limit(self, mocker):
        resource = Tweet()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(limit=300)
        spy_method_paginate.assert_called_once_with(endpoint='tweet', params={}, limit=300, dto=TweetDto)

    @responses.activate
    def test_list_response(self):
        resource = Tweet(api_key='test')

        obj = {
            'id': '4BU4B3sBOwKq8pfUK62q',
            'tweet_id': '1461348555919028225',
            'tweet': 'Honeywell Experion PKS vulnerabilities – What are they? How do they affect your business?',
            'author': '@Cyjax_Ltd',
            'link': 'https://twitter.com/Cyjax_Ltd/status/1461348555919028225',
            'timestamp': '2021-11-18T15:00:00+01:00'
        }

        responses.add(responses.GET, resource._api_client.get_api_url() + '/tweet',
                      json=[obj],
                      status=200)

        response = resource.list()

        assert isinstance(response, types.GeneratorType) is True

        response_list = list(response)
        assert len(response_list) == 1

        assert isinstance(response_list[0], TweetDto) is True
        assert '4BU4B3sBOwKq8pfUK62q' == response_list[0].id
        assert obj == dict(response_list[0])
