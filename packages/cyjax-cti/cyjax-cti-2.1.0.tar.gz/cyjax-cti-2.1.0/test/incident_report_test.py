import datetime
from datetime import timedelta
from unittest.mock import patch, Mock, MagicMock
import types

import responses
import pytest
import pytz

import cyjax
from cyjax import IncidentReport, InvalidDateFormatException
from cyjax.resources.resource import Resource
from cyjax.resources.incident_report import IncidentReportDto
from cyjax.api_client import ApiClient


class TestIncidentReport:

    fake_date = Mock(wraps=datetime.datetime)
    fake_date.now.return_value.astimezone.return_value = datetime.datetime(2020, 5, 2, 12, 0, 0, tzinfo=pytz.UTC)

    def test_instance(self):
        resource = IncidentReport('123', 'test')
        assert isinstance(resource, Resource)
        assert isinstance(resource._api_client, ApiClient)
        assert '123' == resource._api_client.get_api_key()
        assert 'test' == resource._api_client.get_api_url()

    def test_get_incident_reports_without_parameters(self, mocker):
        incident_report = IncidentReport()
        spy_method_paginate = mocker.spy(incident_report, '_paginate')

        incident_report.list()
        spy_method_paginate.assert_called_once_with(endpoint='report/incident',
                                                    params={'excludeIndicators': True},
                                                    dto=IncidentReportDto,
                                                    limit=None)

    def test_get_incident_reports_with_parameters(self, mocker):
        incident_report = IncidentReport()
        spy_method_paginate = mocker.spy(incident_report, '_paginate')

        incident_report.list(query='search-query', since='2020-05-02T07:31:11+00:00', until='2020-07-02T00:00:00+00:00')

        expected_params = {
            'query': 'search-query',
            'since': '2020-05-02T07:31:11+00:00',
            'until': '2020-07-02T00:00:00+00:00',
            'excludeIndicators': True
        }
        spy_method_paginate.assert_called_once_with(endpoint='report/incident',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IncidentReportDto)

    @patch('cyjax.helpers.datetime', fake_date)
    def test_get_incident_reports_with_date_as_timedelta(self, mocker):
        incident_report = IncidentReport()
        spy_method_paginate = mocker.spy(incident_report, '_paginate')

        incident_report.list(since=timedelta(hours=2), until=timedelta(hours=1))

        since = '2020-05-02T10:00:00+00:00'
        until = '2020-05-02T11:00:00+00:00'
        expected_params = {'since': since, 'until': until, 'excludeIndicators': True}

        spy_method_paginate.assert_called_once_with(endpoint='report/incident',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IncidentReportDto)

    def test_get_incident_reports_with_date_as_datetime_without_timezone(self, mocker):
        incident_report = IncidentReport()
        spy_method_paginate = mocker.spy(incident_report, '_paginate')

        incident_report.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0),
                             until=datetime.datetime(2020, 5, 2, 11, 0, 0))

        since = datetime.datetime(2020, 5, 2, 10, 0, 0).astimezone().isoformat()
        until = datetime.datetime(2020, 5, 2, 11, 0, 0).astimezone().isoformat()
        expected_params = {'since': since, 'until': until, 'excludeIndicators': True}

        spy_method_paginate.assert_called_once_with(endpoint='report/incident',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IncidentReportDto)

    def test_get_incident_reports_with_date_as_datetime_with_timezone(self, mocker):
        incident_report = IncidentReport()
        spy_method_paginate = mocker.spy(incident_report, '_paginate')

        incident_report.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0, tzinfo=pytz.UTC),
                             until=datetime.datetime(2020, 5, 2, 11, 0, 0, tzinfo=pytz.UTC))

        expected_params = {'since': '2020-05-02T10:00:00+00:00',
                           'until': '2020-05-02T11:00:00+00:00',
                           'excludeIndicators': True}

        spy_method_paginate.assert_called_once_with(endpoint='report/incident',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IncidentReportDto)

    def test_get_incident_reports_with_date_as_string(self, mocker):
        incident_report = IncidentReport()
        spy_method_paginate = mocker.spy(incident_report, '_paginate')

        incident_report.list(since='2020-05-02T10:00:00+00:00', until='2020-05-02T11:00:00+00:00')

        expected_params = {'since': '2020-05-02T10:00:00+00:00',
                           'until': '2020-05-02T11:00:00+00:00',
                           'excludeIndicators': True}

        spy_method_paginate.assert_called_once_with(endpoint='report/incident',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IncidentReportDto)

    def test_get_incident_reports_with_wrong_date(self):
        incident_report = IncidentReport()
        with pytest.raises(InvalidDateFormatException):
            incident_report.list(since='2020-05', until='2020-05-02T11:00:00+00:00')

        with pytest.raises(InvalidDateFormatException):
            incident_report.list(since='2020-05-02T11:00:00+00:00', until='2020-05')

    def test_setting_client(self):
        cyjax.api_key = None  # reset to defaults

        resource = IncidentReport()
        assert 'https://api.cymon.co/v2' == resource._api_client.get_api_url()
        assert resource._api_client.get_api_key() is None

        resource = IncidentReport('123456', 'https://api.new-address.com')
        assert 'https://api.new-address.com' == resource._api_client.get_api_url()
        assert '123456' == resource._api_client.get_api_key()

        cyjax.api_url = None  # Reset to default

    def test_get_one_by_id(self, mocker):
        incident_report = IncidentReport()
        incident_report._api_client = MagicMock()
        incident_report._api_client.__iter__.return_value = []

        spy_method_get_one_by_id = mocker.spy(incident_report, '_get_one_by_id')

        assert hasattr(incident_report, 'one')
        incident_report.one(400)

        spy_method_get_one_by_id.assert_called_once_with(endpoint='report/incident',
                                                         record_id=400,
                                                         params={'excludeIndicators': True},
                                                         dto=IncidentReportDto)

    def test_get_list_exclude_indicators_filter_default(self, mocker):
        incident_report = IncidentReport()
        spy_method_paginate = mocker.spy(incident_report, '_paginate')

        # default
        incident_report.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0, tzinfo=pytz.UTC),
                             until=datetime.datetime(2020, 5, 2, 11, 0, 0, tzinfo=pytz.UTC))

        expected_params = {'since': '2020-05-02T10:00:00+00:00',
                           'until': '2020-05-02T11:00:00+00:00',
                           'excludeIndicators': True}
        spy_method_paginate.assert_called_once_with(endpoint='report/incident',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IncidentReportDto)

    def test_get_list_without_excluding_indicators_filter(self, mocker):
        incident_report = IncidentReport()
        spy_method_paginate = mocker.spy(incident_report, '_paginate')

        # False
        incident_report.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0, tzinfo=pytz.UTC),
                             until=datetime.datetime(2020, 5, 2, 11, 0, 0, tzinfo=pytz.UTC, ),
                             exclude_indicators=False)

        expected_params = {'since': '2020-05-02T10:00:00+00:00',
                           'until': '2020-05-02T11:00:00+00:00',
                           'excludeIndicators': False}

        spy_method_paginate.assert_called_once_with(endpoint='report/incident',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IncidentReportDto)

    def test_get_list_excluding_indicators_filter(self, mocker):
        incident_report = IncidentReport()
        spy_method_paginate = mocker.spy(incident_report, '_paginate')

        # True
        incident_report.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0, tzinfo=pytz.UTC),
                             until=datetime.datetime(2020, 5, 2, 11, 0, 0, tzinfo=pytz.UTC, ),
                             exclude_indicators=True)

        expected_params = {'since': '2020-05-02T10:00:00+00:00',
                           'until': '2020-05-02T11:00:00+00:00',
                           'excludeIndicators': True}

        spy_method_paginate.assert_called_once_with(endpoint='report/incident',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IncidentReportDto)

    def test_get_one_exclude_indicators_filter(self, mocker):
        incident_report = IncidentReport()
        incident_report._api_client = MagicMock()
        incident_report._api_client.__iter__.return_value = []

        spy_method_get_one_by_id = mocker.spy(incident_report, '_get_one_by_id')

        assert hasattr(incident_report, 'one')
        incident_report.one(400)

        # default
        spy_method_get_one_by_id.assert_called_once_with(endpoint='report/incident',
                                                         record_id=400,
                                                         params={'excludeIndicators': True},
                                                         dto=IncidentReportDto)

        # False
        incident_report.one(400, exclude_indicators=False)
        spy_method_get_one_by_id.assert_called_with(endpoint='report/incident',
                                                    record_id=400,
                                                    params={'excludeIndicators': False},
                                                    dto=IncidentReportDto)

        # True
        incident_report.one(400, exclude_indicators=True)
        spy_method_get_one_by_id.assert_called_with(endpoint='report/incident',
                                                    record_id=400,
                                                    params={'excludeIndicators': True},
                                                    dto=IncidentReportDto)

    def test_list_with_limit(self, mocker):
        resource = IncidentReport()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(limit=300)
        spy_method_paginate.assert_called_once_with(endpoint='report/incident',
                                                    params={'excludeIndicators': True},
                                                    limit=300,
                                                    dto=IncidentReportDto)

    @responses.activate
    def test_get_response(self):
        resource = IncidentReport(api_key='test')

        obj = {
            'id': 1234,
            'title': 'WellMess malware analysis report',
            'source': 'https://example.com',
            'content': 'Lorem ipsum...',
            'severity': 'high',
            'source_evaluation': 'always-reliable',
            'impacts': {
                'government': 'some-impact',
                'infrastructure': 'some-impact',
                'healthcare': 'some-impact',
                'pharmaceutical': 'some-impact',
                'it': 'some-impact',
                'politics': 'some-impact',
                'media': 'some-impact',
                'others': 'minimal-impact',
                'ngo': 'some-impact',
                'education': 'some-impact'
            },
            'tags': [
                'GitHub'
            ],
            'countries': [
                'United States',
            ],
            'techniques': [
                'Malicious File',
                'Process Injection'
            ],
            'technique_ids': [
                'T1003.008',
                'T1540'
            ],
            'software': [
                'Agent.btz'
            ],
            'software_ids': [
                'S0154'
            ],
            'ioc': [],
            'ioc_count': 0,
            'last_update': '2020-10-27T10:57:52+0000'
        }
        responses.add(responses.GET, resource._api_client.get_api_url() + '/report/incident/1234',
                      json=obj,
                      status=200)

        response = resource.one(1234)

        assert isinstance(response, dict) is True
        assert isinstance(response, IncidentReportDto) is True
        assert 1234 == response.id
        assert 0 == response.ioc_count

    @responses.activate
    def test_list_response(self):
        resource = IncidentReport(api_key='test')

        mocked_entries = [
            {
                'id': 1234,
                'title': 'WellMess malware analysis report',
                'source': 'https://example.com',
                'content': 'Lorem ipsum...',
                'severity': 'high',
                'source_evaluation': 'always-reliable',
                'impacts': {
                    'government': 'some-impact',
                    'infrastructure': 'some-impact',
                    'healthcare': 'some-impact',
                    'pharmaceutical': 'some-impact',
                    'it': 'some-impact',
                    'politics': 'some-impact',
                    'media': 'some-impact',
                    'others': 'minimal-impact',
                    'ngo': 'some-impact',
                    'education': 'some-impact'
                },
                'tags': [
                    'GitHub'
                ],
                'countries': [
                    'United States',
                ],
                'techniques': [
                    'Malicious File',
                    'Process Injection'
                ],
                'technique_ids': [
                    'T1003.008',
                    'T1540'
                ],
                'software': [
                    'Agent.btz'
                ],
                'software_ids': [
                    'S0154'
                ],
                'ioc': [],
                'ioc_count': 0,
                'last_update': '2020-10-27T10:57:52+0000'
            }
        ]
        responses.add(responses.GET, resource._api_client.get_api_url() + '/report/incident',
                      json=mocked_entries,
                      status=200)

        response = resource.list()

        assert isinstance(response, types.GeneratorType) is True

        response_list = list(response)
        assert len(response_list) == 1

        assert isinstance(response_list[0], IncidentReportDto) is True
        assert 1234 == response_list[0].id
