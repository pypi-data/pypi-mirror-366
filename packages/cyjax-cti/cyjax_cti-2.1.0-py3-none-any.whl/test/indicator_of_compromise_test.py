#  CYjAX Limited

import datetime
from datetime import timedelta
from unittest.mock import patch, Mock
import types

import responses
import pytest
import pytz

import cyjax
from cyjax.api_client import ApiClient
from cyjax import IndicatorOfCompromise, InvalidDateFormatException
from cyjax.resources.resource import Resource
from cyjax.resources.indicator_of_compromise import IndicatorDto, EnrichmentDto
from cyjax.resources.incident_report import IncidentReportDto


class TestIndicatorOfCompromise:

    fake_date = Mock(wraps=datetime.datetime)
    fake_date.now.return_value.astimezone.return_value = datetime.datetime(2020, 5, 2, 12, 0, 0, tzinfo=pytz.UTC)

    @classmethod
    def setup_class(cls):
        api_client = ApiClient(api_key='foo_api_key')
        cls.api_url = api_client.get_api_url()

    def test_instance(self):
        resource = IndicatorOfCompromise('123', 'test')
        assert isinstance(resource, Resource)
        assert isinstance(resource._api_client, ApiClient)
        assert '123' == resource._api_client.get_api_key()
        assert 'test' == resource._api_client.get_api_url()

    def test_class_constants(self):
        assert 'incident-report' in IndicatorOfCompromise.SUPPORTED_SOURCES
        assert 'my-report' in IndicatorOfCompromise.SUPPORTED_SOURCES

    def test_get_indicator_of_compromise_without_parameters(self, mocker):
        indicator_of_compromise = IndicatorOfCompromise()
        spy_method_paginate = mocker.spy(indicator_of_compromise, '_paginate')

        indicator_of_compromise.list()
        spy_method_paginate.assert_called_once_with(endpoint='indicator-of-compromise',
                                                    params={},
                                                    limit=None,
                                                    dto=IndicatorDto)

    def test_get_indicator_of_compromise_with_parameters(self, mocker):
        indicator_of_compromise = IndicatorOfCompromise()
        spy_method_paginate = mocker.spy(indicator_of_compromise, '_paginate')

        indicator_of_compromise.list(since='2020-05-02T07:31:11+00:00', until='2020-07-02T00:00:00+00:00')

        expected_params = {'since': '2020-05-02T07:31:11+00:00', 'until': '2020-07-02T00:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='indicator-of-compromise',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IndicatorDto)

    @patch('cyjax.helpers.datetime', fake_date)
    def test_get_indicator_of_compromise_with_date_as_timedelta(self, mocker):
        indicator_of_compromise = IndicatorOfCompromise()
        spy_method_paginate = mocker.spy(indicator_of_compromise, '_paginate')

        indicator_of_compromise.list(since=timedelta(hours=2), until=timedelta(hours=1))

        since = '2020-05-02T10:00:00+00:00'
        until = '2020-05-02T11:00:00+00:00'
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='indicator-of-compromise',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IndicatorDto)

    def test_get_indicator_of_compromise_with_date_as_datetime_without_timezone(self, mocker):
        indicator_of_compromise = IndicatorOfCompromise()
        spy_method_paginate = mocker.spy(indicator_of_compromise, '_paginate')

        indicator_of_compromise.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0),
                                     until=datetime.datetime(2020, 5, 2, 11, 0, 0))

        since = datetime.datetime(2020, 5, 2, 10, 0, 0).astimezone().isoformat()
        until = datetime.datetime(2020, 5, 2, 11, 0, 0).astimezone().isoformat()
        expected_params = {'since': since, 'until': until}

        spy_method_paginate.assert_called_once_with(endpoint='indicator-of-compromise',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IndicatorDto)

    def test_get_indicator_of_compromise_with_date_as_datetime_with_timezone(self, mocker):
        indicator_of_compromise = IndicatorOfCompromise()
        spy_method_paginate = mocker.spy(indicator_of_compromise, '_paginate')

        indicator_of_compromise.list(since=datetime.datetime(2020, 5, 2, 10, 0, 0, tzinfo=pytz.UTC),
                                     until=datetime.datetime(2020, 5, 2, 11, 0, 0, tzinfo=pytz.UTC))

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='indicator-of-compromise',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IndicatorDto)

    def test_get_indicator_of_compromise_with_date_as_string(self, mocker):
        indicator_of_compromise = IndicatorOfCompromise()
        spy_method_paginate = mocker.spy(indicator_of_compromise, '_paginate')

        indicator_of_compromise.list(since='2020-05-02T10:00:00+00:00', until='2020-05-02T11:00:00+00:00')

        expected_params = {'since': '2020-05-02T10:00:00+00:00', 'until': '2020-05-02T11:00:00+00:00'}

        spy_method_paginate.assert_called_once_with(endpoint='indicator-of-compromise',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IndicatorDto)

    def test_get_indicator_of_compromise_with_wrong_date(self):
        indicator_of_compromise = IndicatorOfCompromise()
        with pytest.raises(InvalidDateFormatException):
            indicator_of_compromise.list(since='2020-05', until='2020-05-02T11:00:00+00:00')

        with pytest.raises(InvalidDateFormatException):
            indicator_of_compromise.list(since='2020-05-02T11:00:00+00:00', until='2020-05')

    def test_setting_client(self):
        cyjax.api_key = None  # reset to defaults

        resource = IndicatorOfCompromise()
        assert 'https://api.cymon.co/v2' == resource._api_client.get_api_url()
        assert resource._api_client.get_api_key() is None

        resource = IndicatorOfCompromise('123456', 'https://api.new-address.com')
        assert 'https://api.new-address.com' == resource._api_client.get_api_url()
        assert '123456' == resource._api_client.get_api_key()

        cyjax.api_url = None  # Reset to default

    def test_get_one_is_not_implemented(self):
        resource = IndicatorOfCompromise()

        with pytest.raises(NotImplementedError):
            resource.one(4)

    def test_get_indicators_with_type_filter(self, mocker):
        indicator_of_compromise = IndicatorOfCompromise()
        spy_method_paginate = mocker.spy(indicator_of_compromise, '_paginate')

        indicator_of_compromise.list(type='Email,Domain,IPv6')
        expected_params = {'type': 'Email,Domain,IPv6'}
        spy_method_paginate.assert_called_once_with(endpoint='indicator-of-compromise',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IndicatorDto)

    def test_get_indicators_with_source_type_filter(self, mocker):
        indicator_of_compromise = IndicatorOfCompromise()
        spy_method_paginate = mocker.spy(indicator_of_compromise, '_paginate')

        indicator_of_compromise.list(source_type='incident-report')
        expected_params = {'sourceType': 'incident-report'}
        spy_method_paginate.assert_called_once_with(endpoint='indicator-of-compromise',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IndicatorDto)

    def test_get_indicators_with_invalid_source_type_filter(self, mocker):
        indicator_of_compromise = IndicatorOfCompromise()
        spy_method_paginate = mocker.spy(indicator_of_compromise, '_paginate')

        with pytest.raises(ValueError):
            indicator_of_compromise.list(source_type='incidents')

        spy_method_paginate.assert_not_called()

    def test_get_indicators_with_source_id_filter(self, mocker):
        indicator_of_compromise = IndicatorOfCompromise()
        spy_method_paginate = mocker.spy(indicator_of_compromise, '_paginate')

        indicator_of_compromise.list(source_id=123)
        expected_params = {'sourceId': 123}
        spy_method_paginate.assert_called_once_with(endpoint='indicator-of-compromise',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=IndicatorDto)

    def test_get_indicators_with_invalid_source_id_filter(self, mocker):
        indicator_of_compromise = IndicatorOfCompromise()
        spy_method_paginate = mocker.spy(indicator_of_compromise, '_paginate')

        with pytest.raises(ValueError):
            indicator_of_compromise.list(source_id=0)

        spy_method_paginate.assert_not_called()

    def test_enrichment_invalid_value(self):
        indicator_of_compromise = IndicatorOfCompromise()

        with pytest.raises(ValueError):
            indicator_of_compromise.enrichment('')

        with pytest.raises(ValueError):
            indicator_of_compromise.enrichment(0)

        with pytest.raises(ValueError):
            indicator_of_compromise.enrichment(None)

        with pytest.raises(ValueError):
            indicator_of_compromise.enrichment(False)

        with pytest.raises(ValueError):
            indicator_of_compromise.enrichment(123456)

    @responses.activate
    def test_indicator_enrichment(self):
        ioc_value = '236.516.247.352'

        mocked_response = {
            "last_seen_timestamp": "2021-01-21T04:32:16Z",
            "geoip": {
                "country_name": "Argentina",
                "country_code": "AR"
            },
            "asn": {
                "name": "Telecom Argentina S.A",
                "number": "10318"
            },
            "sightings": [
                {
                    "count": 6,
                    "last_seen_timestamp": "2020-09-03T08:00:00Z",
                    "description": "Daily Emotet IOCs - 02 September 2020",
                    "source": {
                        "name": "Cyjax",
                        "id": "212",
                        "type": "incident-report"
                    }
                },
                {
                    "count": 3,
                    "last_seen_timestamp": "2021-01-21T04:32:16Z",
                    "description": "Heodo malware",
                    "source": {
                        "name": "Feodo Tracker (abuse.ch)",
                        "type": "csv"
                    }
                }
            ]
        }

        responses.add(responses.GET, self.api_url + '/indicator-of-compromise/enrichment',
                      status=200,
                      json=mocked_response)

        indicator_of_compromise = IndicatorOfCompromise(api_key='123456')

        enrichment = indicator_of_compromise.enrichment(ioc_value)
        assert mocked_response == enrichment

    def test_list_with_limit(self, mocker):
        resource = IndicatorOfCompromise()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(source_id=123, limit=300)
        expected_params = {'sourceId': 123}
        spy_method_paginate.assert_called_once_with(endpoint='indicator-of-compromise',
                                                    params=expected_params,
                                                    limit=300,
                                                    dto=IndicatorDto)

    @responses.activate
    def test_list_response(self):
        resource = IndicatorOfCompromise(api_key='test')

        mocked_entries = [
            {
                'uuid': 'w86e9b2d-214b-42d0-sd01-c296972d05b4',
                'value': '23873bf2670cf64c2440058130548d4e4da412dd',
                'type': 'FileHash-SHA1',
                'industry_type': [
                    'Financial'
                ],
                'handling_condition': 'GREEN',
                'ttp': [
                    'Malicious File'
                ],
                'description': 'WellMess malware analysis report',
                'source': 'https://api.cymon.co/v2/report/incident/1000000',
                'discovered_at': '2022-10-13T09:25:36+0000',
            },
            {
                'uuid': '0429144c-a615-4dc5-8827-f6e9a48c63a8',
                'value': 'ce3e12f0d69b47e49ff8f6ddd1268125',
                'type': 'FileHash-SHA1',
                'industry_type': [
                    'Financial'
                ],
                'handling_condition': 'GREEN',
                'ttp': [
                    'Malicious File'
                ],
                'description': 'WellMess malware analysis report',
                'source': 'https://api.cymon.co/v2/report/incident/1000000',
                'discovered_at': '2022-10-13T09:25:37+0000',
            },
        ]

        responses.add(responses.GET, resource._api_client.get_api_url() + '/indicator-of-compromise',
                      json=mocked_entries,
                      status=200)

        response = resource.list()

        assert isinstance(response, types.GeneratorType) is True

        response_list = list(response)
        assert len(response_list) == 2

        assert isinstance(response_list[0], IndicatorDto) is True
        assert 'w86e9b2d-214b-42d0-sd01-c296972d05b4' == response_list[0].uuid
        assert '0429144c-a615-4dc5-8827-f6e9a48c63a8' == response_list[1].uuid

    @responses.activate
    def test_enrichment_response(self):
        resource = IndicatorOfCompromise(api_key='test')

        obj = {
            "type": "IPv4",
            "last_seen_timestamp": "2022-10-13T04:32:16Z",
            "geoip": {
                "ip_address": "185.129.62.62",
                "city": "Buenos Aires",
                "country_name": "Argentina",
                "country_code": "AR"
            },
            "asn": {
                "organization": "Telecom Argentina S.A",
                "number": "10318"
            },
            "sightings": [
                {
                    "count": 421,
                    "last_seen_timestamp": "2022-10-13T04:32:16Z",
                    "description": "Blacklisted IP",
                    "source": "Talos (Cisco)"
                },
                {
                    "count": 1,
                    "last_seen_timestamp": "2022-10-15T10:52:00Z",
                    "description": "Ransom Cartel ransomware possibly connected with REvil",
                    "source": "Cyjax"
                },
                {
                    "count": 4,
                    "last_seen_timestamp": "2020-08-28T18:08:00Z",
                    "description": "STIX package",
                    "source": "DHS AIS"
                }
            ]
        }

        responses.add(responses.GET, resource._api_client.get_api_url() +
                      '/indicator-of-compromise/enrichment?value=185.129.62.62',
                      json=obj,
                      status=200)

        response = resource.enrichment('185.129.62.62')

        assert isinstance(response, EnrichmentDto) is True
        assert 'IPv4' == response.get('type')
        assert '2022-10-13T04:32:16Z' == response.last_seen_timestamp
        assert '185.129.62.62' == response.geoip.ip_address
        assert '10318' == response.asn.number
        assert 3 == len(response.sightings)
        assert 'Talos (Cisco)' == response.sightings[0].source

    @responses.activate
    def test_get_incident_report_from_indicator_dto_new_link_structure(self):
        cyjax.api_key = 'test'

        indicator = IndicatorDto(**{
            'uuid': 'w86e9b2d-214b-42d0-sd01-c296972d05b4',
            'value': '23873bf2670cf64c2440058130548d4e4da412dd',
            'type': 'FileHash-SHA1',
            'industry_type': [
                'Financial'
            ],
            'handling_condition': 'GREEN',
            'ttp': [
                'Malicious File'
            ],
            'description': 'WellMess malware analysis report',
            'source': 'https://api.cymon.co/v2/report/incident/123',
            'discovered_at': '2022-10-13T09:25:36+0000',
        })

        report_obj = {
            'id': 123,
            'title': 'WellMess malware analysis report',
            'source': 'https://example.com',
            'content': 'Lorem ipsum...',
            'severity': 'high',
            'source_evaluation': 'always-reliable',
            'impacts': {
                'government': 'some-impact',

            },
            'tags': [],
            'countries': [],
            'techniques': [],
            'technique_ids': [],
            'software': [],
            'software_ids': [],
            'ioc_count': 0,
            'last_update': '2020-10-27T10:57:52+0000'
        }

        resource = IndicatorOfCompromise(api_key='test')
        responses.add(responses.GET, resource._api_client.get_api_url() + '/report/incident/123',
                      json=report_obj,
                      status=200)

        report = indicator.get_incident_report()
        assert isinstance(report, IncidentReportDto)
        assert 123 == report.id

        # assert is cached
        assert 1 == len(responses.calls)
        indicator.get_incident_report()
        indicator.get_incident_report()
        indicator.get_incident_report()
        indicator.get_incident_report()
        assert 1 == len(responses.calls)

        cyjax.api_url = None  # Reset to default

    @responses.activate
    def test_get_incident_report_from_indicator_dto_old_link_structure(self):
        cyjax.api_key = 'test'

        indicator = IndicatorDto(**{
            'uuid': 'w86e9b2d-214b-42d0-sd01-c296972d05b4',
            'value': '23873bf2670cf64c2440058130548d4e4da412dd',
            'type': 'FileHash-SHA1',
            'industry_type': [
                'Financial'
            ],
            'handling_condition': 'GREEN',
            'ttp': [
                'Malicious File'
            ],
            'description': 'WellMess malware analysis report',
            'source': 'https://api.cymon.co/v2/report/incident?id=123',
            'discovered_at': '2022-10-13T09:25:36+0000',
        })

        report_obj = {
            'id': 123,
            'title': 'WellMess malware analysis report',
            'source': 'https://example.com',
            'content': 'Lorem ipsum...',
            'severity': 'high',
            'source_evaluation': 'always-reliable',
            'impacts': {
                'government': 'some-impact',

            },
            'tags': [],
            'countries': [],
            'techniques': [],
            'technique_ids': [],
            'software': [],
            'software_ids': [],
            'ioc_count': 0,
            'last_update': '2020-10-27T10:57:52+0000'
        }

        resource = IndicatorOfCompromise(api_key='test')
        responses.add(responses.GET, resource._api_client.get_api_url() + '/report/incident/123',
                      json=report_obj,
                      status=200)

        report = indicator.get_incident_report()
        assert isinstance(report, IncidentReportDto)
        assert 123 == report.id

        cyjax.api_url = None  # Reset to default
