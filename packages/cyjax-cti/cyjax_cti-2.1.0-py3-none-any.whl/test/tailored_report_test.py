import datetime
from datetime import timedelta
from unittest.mock import patch, Mock, MagicMock

import types
import pytest
import pytz
import responses

import cyjax
from cyjax import TailoredReport, InvalidDateFormatException
from cyjax.resources.resource import Resource
from cyjax.resources.tailored_report.dto import TailoredReportDto
from cyjax.api_client import ApiClient


class TestMyReport:

    fake_date = Mock(wraps=datetime.datetime)
    fake_date.now.return_value.astimezone.return_value = datetime.datetime(2020, 5, 2, 12, 0, 0, tzinfo=pytz.UTC)

    def test_instance(self):
        resource = TailoredReport('123', 'test')
        assert isinstance(resource, Resource)
        assert isinstance(resource._api_client, ApiClient)
        assert '123' == resource._api_client.get_api_key()
        assert 'test' == resource._api_client.get_api_url()

    def test_get_my_reports_without_parameters(self, mocker):
        my_report = TailoredReport()
        spy_method_paginate = mocker.spy(my_report, '_paginate')

        my_report.list()
        spy_method_paginate.assert_called_once_with(endpoint='report/my-report',
                                                    params={},
                                                    limit=None,
                                                    dto=TailoredReportDto)

    def test_get_tailored_reports_with_parameters(self, mocker):
        my_report = TailoredReport()
        spy_method_paginate = mocker.spy(my_report, '_paginate')

        my_report.list(query='search-query', since='2020-05-02T07:31:11+00:00', until='2020-07-02T00:00:00+00:00')

        expected_params = {
            'query': 'search-query',
            'since': '2020-05-02T07:31:11+00:00',
            'until': '2020-07-02T00:00:00+00:00'
        }
        spy_method_paginate.assert_called_once_with(endpoint='report/my-report',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=TailoredReportDto)

    @patch('cyjax.helpers.datetime', fake_date)
    def test_get_tailored_reports_with_date_as_timedelta(self, mocker):
        my_report = TailoredReport()
        spy_method_paginate = mocker.spy(my_report, '_paginate')

        my_report.list(since=timedelta(hours=2), until=timedelta(hours=1))

        since = '2020-05-02T10:00:00+00:00'
        until = '2020-05-02T11:00:00+00:00'
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='report/my-report',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=TailoredReportDto)

    def test_get_tailored_reports_with_date_as_datetime_without_timezone(self, mocker):
        my_report = TailoredReport()
        spy_method_paginate = mocker.spy(my_report, '_paginate')

        my_report.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0), until=datetime.datetime(2020, 5, 2, 11, 0, 0))

        since = datetime.datetime(2020, 5, 2, 10, 0, 0).astimezone().isoformat()
        until = datetime.datetime(2020, 5, 2, 11, 0, 0).astimezone().isoformat()
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='report/my-report',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=TailoredReportDto)

    def test_get_tailored_reports_with_date_as_datetime_with_timezone(self, mocker):
        my_report = TailoredReport()
        spy_method_paginate = mocker.spy(my_report, '_paginate')

        my_report.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0, tzinfo=pytz.UTC),
                       until=datetime.datetime(2020, 5, 2, 11, 0, 0, tzinfo=pytz.UTC))

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='report/my-report',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=TailoredReportDto)

    def test_get_tailored_reports_with_date_as_string(self, mocker):
        my_report = TailoredReport()
        spy_method_paginate = mocker.spy(my_report, '_paginate')

        my_report.list(since='2020-05-02T10:00:00+00:00', until='2020-05-02T11:00:00+00:00')

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='report/my-report',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=TailoredReportDto)

    def test_get_tailored_reports_with_wrong_date(self):
        my_report = TailoredReport()
        with pytest.raises(InvalidDateFormatException):
            my_report.list(since='2020-05', until='2020-05-02T11:00:00+00:00')

        with pytest.raises(InvalidDateFormatException):
            my_report.list(since='2020-05-02T11:00:00+00:00', until='2020-05')

    def test_setting_client(self):
        cyjax.api_key = None  # reset to defaults

        my_report = TailoredReport()
        assert 'https://api.cymon.co/v2' == my_report._api_client.get_api_url()
        assert my_report._api_client.get_api_key() is None

        my_report = TailoredReport('123456', 'https://api.new-address.com')
        assert 'https://api.new-address.com' == my_report._api_client.get_api_url()
        assert '123456' == my_report._api_client.get_api_key()

        cyjax.api_url = None  # Reset to default

    def test_get_one_by_id(self, mocker):
        my_report = TailoredReport()
        my_report._api_client = MagicMock()
        my_report._api_client.__iter__.return_value = []

        spy_method_get_one_by_id = mocker.spy(my_report, '_get_one_by_id')

        assert hasattr(my_report, 'one')
        my_report.one(400)

        spy_method_get_one_by_id.assert_called_once_with(endpoint='report/my-report',
                                                         record_id=400,
                                                         dto=TailoredReportDto)

    def test_list_with_limit(self, mocker):
        resource = TailoredReport()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(limit=300)
        spy_method_paginate.assert_called_once_with(endpoint='report/my-report',
                                                    params={},
                                                    limit=300,
                                                    dto=TailoredReportDto)

    @responses.activate
    def test_get_one_response(self):
        resource = TailoredReport(api_key='test')

        obj = {
            "id": 123456,
            "title": "Example my report title",
            "content": "<p>Lorem ipsum dolor sit amet, constur lus pretium. Mattis pellentesque id nibh...</p>",
            "severity": "low",
            "source_evaluation": "mostly-reliable",
            "impact": "some-impact",
            "last_update": "2020-10-27T10:54:23+0000"
        }

        responses.add(responses.GET, resource._api_client.get_api_url() + '/report/my-report/123456',
                      json=obj,
                      status=200)

        response = resource.one(123456)

        assert isinstance(response, TailoredReportDto) is True
        assert 123456 == response.id
        assert 'Example my report title' == response.title

    @responses.activate
    def test_list_response(self):
        resource = TailoredReport(api_key='test')

        obj = [
            {
                "id": 123456,
                "title": "Example my report title",
                "content": "<p>Lorem ipsum dolor sit amet, constur lus pretium. Mattis pellentesque id nibh...</p>",
                "severity": "low",
                "source_evaluation": "mostly-reliable",
                "impact": "some-impact",
                "last_update": "2020-10-27T10:54:23+0000"
            },
            {
                "id": 300000,
                "title": "Example 2",
                "content": "<p>Lorem ipsum dolor 2...</p>",
                "severity": "high",
                "source_evaluation": "mostly-reliable",
                "impact": "some-impact",
                "last_update": "2020-10-27T10:55:00+0000"
            }
        ]

        responses.add(responses.GET, resource._api_client.get_api_url() + '/report/my-report',
                      json=obj,
                      status=200)

        response = resource.list()

        assert isinstance(response, types.GeneratorType) is True

        response_list = list(response)
        assert len(response_list) == 2

        assert isinstance(response_list[0], TailoredReportDto) is True
        assert isinstance(response_list[1], TailoredReportDto) is True

        assert 123456 == response_list[0].id
        assert 300000 == response_list[1].id
