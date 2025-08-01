#  CYjAX Limited
from unittest.mock import MagicMock
import types
import responses

from cyjax import DataBreach
from cyjax.resources.resource import Resource
from cyjax.resources.data_breach import DataBreachDto, DataBreachListDto
from cyjax.resources.data_breach.dto import IncidentReportMetadataDto
from cyjax.api_client import ApiClient


class TestLeakedEmail:

    def test_instance(self):
        resource = DataBreach('123', 'test')
        assert isinstance(resource, Resource)
        assert isinstance(resource._api_client, ApiClient)
        assert '123' == resource._api_client.get_api_key()
        assert 'test' == resource._api_client.get_api_url()

    def test_list_without_query(self, mocker):
        resource = DataBreach()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list()
        spy_method_paginate.assert_called_once_with(endpoint='data-leak/breach',
                                                    params={},
                                                    limit=None,
                                                    dto=DataBreachListDto)

    def test_list_with_query(self, mocker):
        resource = DataBreach()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list('hello world')
        spy_method_paginate.assert_called_once_with(endpoint='data-leak/breach',
                                                    params={'query': 'hello world'},
                                                    limit=None,
                                                    dto=DataBreachListDto)

    def test_list_with_limit(self, mocker):
        resource = DataBreach()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(limit=36)
        spy_method_paginate.assert_called_once_with(endpoint='data-leak/breach',
                                                    params={},
                                                    limit=36,
                                                    dto=DataBreachListDto)

    def test_get_one_by_id(self, mocker):
        resource = DataBreach()
        resource._api_client = MagicMock()
        resource._api_client.__iter__.return_value = []

        spy_method_get_one_by_id = mocker.spy(resource, '_get_one_by_id')

        assert hasattr(resource, 'one')
        resource.one(400)

        spy_method_get_one_by_id.assert_called_once_with(endpoint='data-leak/breach',
                                                         record_id=400,
                                                         dto=DataBreachDto)

    @responses.activate
    def test_get_one_response(self):
        resource = DataBreach(api_key='test')

        mocked_entry = {"id": 885,
                        "name": "Test-ABC123",
                        "content": "new content 4",
                        "incident_report": {
                            "id": 65303,
                            "title": "Report A1",
                            "url": "https://test.cyjax.com/api/cyjax/v2/report/incident/65303"
                        },
                        "data_classes": [
                            "Full names",
                            "IP addresses",
                            "Addresses"
                        ],
                        "discovered_at": "2023-03-17T11:37:52+0000"
                        }
        responses.add(responses.GET, resource._api_client.get_api_url() + '/data-leak/breach/885',
                      json=mocked_entry,
                      status=200)

        response = resource.one(885)

        assert isinstance(response, dict) is True
        assert isinstance(response, DataBreachDto) is True

        assert 885 == response.get('id')
        assert 885 == response.id
        assert 'Test-ABC123' == response.get('name')
        assert 'new content 4' == response.get('content')
        assert {"id": 65303,
                "title": "Report A1",
                "url": "https://test.cyjax.com/api/cyjax/v2/report/incident/65303"
                } == response.get('incident_report')
        assert ["Full names", "IP addresses", "Addresses"] == response.get('data_classes')
        assert '2023-03-17T11:37:52+0000' == response.get('discovered_at')
        assert mocked_entry == dict(response)

        ir_metadata = response.incident_report
        assert isinstance(ir_metadata, IncidentReportMetadataDto) is True
        assert 65303 == response.incident_report.id
        assert 'Report A1' == response.incident_report.title
        assert 'Report A1' == response.incident_report.get('title')
        assert 'https://test.cyjax.com/api/cyjax/v2/report/incident/65303' == response.incident_report['url']

    @responses.activate
    def test_list_response(self):
        resource = DataBreach(api_key='test')

        mocked_entries = [
            {
                "id": 885,
                "name": "Breach A",
                "data_classes": [
                    "Full names",
                    "IP addresses",
                    "Addresses"
                ],
                "discovered_at": "2023-03-17T11:37:52+0000"
            },
            {
                "id": 884,
                "name": "Breach B",
                "data_classes": [
                    "Passwords",
                    "IP addresses"
                ],
                "discovered_at": "2023-03-17T11:32:20+0000"
            },
            {
                "id": 799,
                "name": "Breach C",
                "data_classes": [],
                "discovered_at": "2021-04-08T16:29:55+0000"
            },
            {
                "id": 877,
                "name": "Breach D",
                "data_classes": [],
                "discovered_at": "2022-01-20T07:35:54+0000"
            }
        ]
        responses.add(responses.GET, resource._api_client.get_api_url() + '/data-leak/breach',
                      json=mocked_entries,
                      status=200)

        response = resource.list()

        assert isinstance(response, types.GeneratorType) is True

        response_list = list(response)
        assert len(response_list) == 4

        assert isinstance(response_list[0], DataBreachListDto) is True
        assert isinstance(response_list[1], DataBreachListDto) is True
        assert isinstance(response_list[2], DataBreachListDto) is True
        assert isinstance(response_list[3], DataBreachListDto) is True

        assert 885 == response_list[0].id
        assert 884 == response_list[1].get('id')
        assert 799 == response_list[2]['id']
        assert 877 == response_list[3].id

        assert hasattr(response_list[0], 'content') is False
        assert hasattr(response_list[0], 'incident_report') is False
