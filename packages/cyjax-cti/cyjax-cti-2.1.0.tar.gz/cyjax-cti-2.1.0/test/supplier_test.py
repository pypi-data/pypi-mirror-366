#  CYjAX Limited
import pytest
from unittest.mock import MagicMock
import types

import responses

from cyjax.resources.resource import Resource
from cyjax.resources.third_party_risk import Supplier, SupplierDto, SupplierListDto
from cyjax.api_client import ApiClient
from cyjax.exceptions import NotFoundException
from test import api_responses


class TestSupplier:

    def test_instance(self):
        resource = Supplier('123', 'test')
        assert isinstance(resource, Resource)
        assert isinstance(resource._api_client, ApiClient)
        assert '123' == resource._api_client.get_api_key()
        assert 'test' == resource._api_client.get_api_url()

    def test_get_supplier_list_without_parameters(self, mocker):
        resource = Supplier()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list()
        spy_method_paginate.assert_called_once_with(endpoint='third-party-risk/supplier',
                                                    params={},
                                                    dto=SupplierListDto,
                                                    limit=None)

    def test_get_supplier_list_with_parameters(self, mocker):
        resource = Supplier()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(query='search-query',
                      tier=1,
                      risk='low',
                      since='2020-05-02T07:31:11+00:00',
                      until='2020-07-02T00:00:00+00:00')
        expected_params = {'since': '2020-05-02T07:31:11+00:00',
                           'until': '2020-07-02T00:00:00+00:00',
                           'query': 'search-query',
                           'tier': 1,
                           'risk': 'low'}
        spy_method_paginate.assert_called_once_with(endpoint='third-party-risk/supplier',
                                                    params=expected_params,
                                                    dto=SupplierListDto,
                                                    limit=None)

    def test_get_one_by_id(self, mocker):
        resource = Supplier()
        resource._api_client = MagicMock()
        resource._api_client.__iter__.return_value = []

        spy_method_get_one_by_id = mocker.spy(resource, '_get_one_by_id')

        assert hasattr(resource, 'one')
        resource.one(400)

        spy_method_get_one_by_id.assert_called_once_with(endpoint='third-party-risk/supplier',
                                                         record_id=400,
                                                         params={},
                                                         dto=SupplierDto)

    def test_create_supplier_api_call(self):
        api_client_mock = MagicMock()
        api_client_mock.send.return_value = MagicMock()

        resource = Supplier(api_key='test')
        resource._api_client = api_client_mock

        resource.create('New supplier name', 2, 'https://new-supplier.com')

        api_client_mock.send.assert_called_once_with(method='post',
                                                     endpoint='third-party-risk/supplier',
                                                     params={},
                                                     data={
                                                         'name': 'New supplier name',
                                                         'tier': 2,
                                                         'url': 'https://new-supplier.com',
                                                         'referenceNumber': None
                                                     })

    def test_update_supplier_api_call(self):
        api_client_mock = MagicMock()
        api_client_mock.send.return_value = MagicMock()

        resource = Supplier(api_key='test')
        resource._api_client = api_client_mock

        resource.update(7, 'New supplier name', 2, 'https://new-supplier.com', 'ABC3')

        api_client_mock.send.assert_called_once_with(method='put',
                                                     endpoint='third-party-risk/supplier/7',
                                                     params={},
                                                     data={
                                                         'name': 'New supplier name',
                                                         'tier': 2,
                                                         'url': 'https://new-supplier.com',
                                                         'referenceNumber': 'ABC3'
                                                     })

    def test_delete_supplier_api_call(self):
        api_client_mock = MagicMock()
        api_client_mock.send.return_value = MagicMock()

        resource = Supplier(api_key='test')
        resource._api_client = api_client_mock

        resource.delete(743)

        api_client_mock.send.assert_called_once_with(method='delete',
                                                     endpoint='third-party-risk/supplier/743')

    @responses.activate
    def test_list_suppliers_when_no_suppliers(self):
        resource = Supplier(api_key='test')

        responses.add(responses.GET, resource._api_client.get_api_url() + '/third-party-risk/supplier',
                      json=[],
                      status=200)

        response = resource.list()

        assert isinstance(response, types.GeneratorType) is True

        response_list = list(response)
        assert len(response_list) == 0

    @responses.activate
    def test_list_suppliers(self):
        resource = Supplier(api_key='test')

        responses.add(responses.GET, resource._api_client.get_api_url() + '/third-party-risk/supplier',
                      json=[
                          {
                              'id': 1,
                              'name': 'RedCompany',
                              'risk': 50,
                              'url': 'https://example.com',
                              'tier': {
                                  'id': 2,
                                  'name': 'Tier A'
                              },
                              'createdDate': '2020-10-28T11:06:58+0000',
                              'updatedDate': '2020-10-29T13:16:12+0000',
                              'events': {
                                  'last7days': 0,
                                  'last30days': 0,
                                  'overall': 0
                              },
                              'lastEvent': None
                          },
                          {
                              'id': 258741,
                              'name': 'Silver Ltd.',
                              'risk': 0,
                              'url': 'https://siver.com',
                              'tier': {
                                  'id': 3,
                                  'name': 'Tier C'
                              },
                              'createdDate': '2020-10-28T11:06:58+0000',
                              'updatedDate': '2020-10-29T13:16:12+0000',
                              'events': {
                                  'last7days': 0,
                                  'last30days': 0,
                                  'overall': 67
                              },
                              'lastEvent': {
                                  'id': '3e89c9d8-eeb7-41cc-be5d-b68a58c14569',
                                  'date': '2022-12-13T10:10:00+0000',
                                  'type': 'Data breach',
                                  'description': 'Email addresses found in the data breach Foobar.'
                              }
                          }
                      ],
                      status=200)

        response = resource.list()

        assert isinstance(response, types.GeneratorType) is True
        response_list = list(response)
        assert len(response_list) == 2

        assert isinstance(response_list[0], SupplierListDto) is True
        assert isinstance(response_list[1], SupplierListDto) is True
        assert 1 == response_list[0].id
        assert 258741 == response_list[1].id

    @responses.activate
    def test_get_one_supplier(self):
        resource = Supplier(api_key='test')

        responses.add(responses.GET, resource._api_client.get_api_url() + '/third-party-risk/supplier/788',
                      json={
                          'id': 788,
                          'name': 'Silver Ltd.',
                          'risk': 0,
                          'url': 'https://siver.com',
                          'tier': {
                              'id': 3,
                              'name': 'Tier C'
                          },
                          'createdDate': '2020-10-28T11:06:58+0000',
                          'updatedDate': '2020-10-29T13:16:12+0000',
                          'events': {
                              'last7days': 0,
                              'last30days': 0,
                              'overall': 67
                          },
                          'lastEvent': {
                              'id': '3e89c9d8-eeb7-41cc-be5d-b68a58c14569',
                              'date': '2022-12-13T10:10:00+0000',
                              'type': 'Data breach',
                              'description': 'Email addresses found in the data breach Foobar.'
                          }
                      },
                      status=200)

        response = resource.one(788)

        assert isinstance(response, SupplierDto) is True
        assert 788 == response.id
        assert '3e89c9d8-eeb7-41cc-be5d-b68a58c14569' == response.lastEvent.id

    @responses.activate
    def test_create_supplier(self):
        resource = Supplier(api_key='test')

        responses.add(responses.POST, resource._api_client.get_api_url() + '/third-party-risk/supplier',
                      json={
                          'success': True,
                          'id': 8003
                      },
                      status=201)

        response = resource.create('tester', 500, 'https://example.com', 'RTE.123451.5434Q')

        assert isinstance(response, int) is True
        assert 8003 == response

    @responses.activate
    def test_update_supplier_than_not_exists(self):
        resource = Supplier(api_key='test')

        responses.add(responses.PUT, resource._api_client.get_api_url() + '/third-party-risk/supplier/1',
                      json=api_responses.get(404),
                      status=404)

        with pytest.raises(NotFoundException):
            resource.update(1, 'tester', 500, 'https://example.com', 'RTE.123451.5434Q')

    @responses.activate
    def test_update_supplier(self):
        resource = Supplier(api_key='test')

        responses.add(responses.PUT, resource._api_client.get_api_url() + '/third-party-risk/supplier/300',
                      json={
                          'success': True
                      },
                      status=200)

        response = resource.update(300, 'tester', 500, 'https://example.com', 'RTE.123451.5434Q')

        assert isinstance(response, bool) is True
        assert response is True

    @responses.activate
    def test_delete_supplier(self):
        resource = Supplier(api_key='test')

        responses.add(responses.DELETE, resource._api_client.get_api_url() + '/third-party-risk/supplier/300',
                      json={
                          'success': True
                      },
                      status=200)

        response = resource.delete(300)

        assert isinstance(response, bool) is True
        assert response is True
