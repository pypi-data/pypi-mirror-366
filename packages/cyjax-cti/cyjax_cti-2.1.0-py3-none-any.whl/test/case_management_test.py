#  CYjAX Limited
import datetime
import types
from unittest.mock import Mock, MagicMock, patch, mock_open

import responses
import pytz

from cyjax import CaseManagement
from cyjax.resources.case_management import CaseActivityDto, CaseDto, CaseListDto
from cyjax.resources.resource import Resource
from cyjax.api_client import ApiClient


class TestCaseManagement:

    fake_date = Mock(wraps=datetime.datetime)
    fake_date.now.return_value.astimezone.return_value = datetime.datetime(2020, 5, 2, 12, 0, 0, tzinfo=pytz.UTC)

    def test_instance(self):
        resource = CaseManagement('123', 'test')
        assert isinstance(resource, Resource)
        assert isinstance(resource._api_client, ApiClient)
        assert '123' == resource._api_client.get_api_key()
        assert 'test' == resource._api_client.get_api_url()

    def test_list_without_parameters(self, mocker):
        resource = CaseManagement()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list()
        spy_method_paginate.assert_called_once_with(endpoint='case',
                                                    params={},
                                                    limit=None,
                                                    dto=CaseListDto)

    def test_list_with_parameters(self, mocker):
        resource = CaseManagement()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(query='search-query',
                      since='2020-05-02T07:31:11+00:00',
                      until='2020-07-02T00:00:00+00:00',
                      status='Open',
                      priority='Low')

        expected_params = {
            'query': 'search-query',
            'since': '2020-05-02T07:31:11+00:00',
            'until': '2020-07-02T00:00:00+00:00',
            'status': 'Open',
            'priority': 'Low'
        }
        spy_method_paginate.assert_called_once_with(endpoint='case',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=CaseListDto)

    def test_activities_with_parameters(self, mocker):
        resource = CaseManagement()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.activities(model_id=40,
                            query='search-query',
                            since='2020-05-02T07:31:11+00:00',
                            until='2020-07-02T00:00:00+00:00')

        expected_params = {
            'query': 'search-query',
            'since': '2020-05-02T07:31:11+00:00',
            'until': '2020-07-02T00:00:00+00:00',

        }
        spy_method_paginate.assert_called_once_with(endpoint='case/40/activity',
                                                    params=expected_params,
                                                    limit=None,
                                                    dto=CaseActivityDto)

    def test_list_with_limit(self, mocker):
        resource = CaseManagement()
        spy_method_paginate = mocker.spy(resource, '_paginate')

        resource.list(limit=4)
        spy_method_paginate.assert_called_once_with(endpoint='case',
                                                    params={},
                                                    limit=4,
                                                    dto=CaseListDto)

    def test_get_one_by_id(self, mocker):
        resource = CaseManagement()
        resource._api_client = MagicMock()
        resource._api_client.__iter__.return_value = []

        spy_method_get_one_by_id = mocker.spy(resource, '_get_one_by_id')

        assert hasattr(resource, 'one')
        resource.one(400)

        spy_method_get_one_by_id.assert_called_once_with(endpoint='case',
                                                         record_id=400,
                                                         dto=CaseDto)

    def test_create_api_call_use_defaults(self):
        api_client_mock = MagicMock()
        api_client_mock.send.return_value = MagicMock()

        resource = CaseManagement(api_key='test')
        resource._api_client = api_client_mock

        resource.create(title='Example', priority='Low')

        api_client_mock.send.assert_called_once_with(method='post',
                                                     endpoint='case',
                                                     data={
                                                         'title': 'Example',
                                                         'priority': 'Low',
                                                         'confidential': False
                                                     })

    def test_create_api_call_with_all_props(self):
        api_client_mock = MagicMock()
        api_client_mock.send.return_value = MagicMock()

        resource = CaseManagement(api_key='test')
        resource._api_client = api_client_mock

        resource.create(title='Example',
                        priority='Low',
                        confidential=True,
                        description='Hello world',
                        referenceNumber='132',
                        assignees=['one@example.com', 'two@example.com'])

        api_client_mock.send.assert_called_once_with(method='post',
                                                     endpoint='case',
                                                     data={
                                                         'title': 'Example',
                                                         'priority': 'Low',
                                                         'confidential': True,
                                                         'description': 'Hello world',
                                                         'referenceNumber': '132',
                                                         'assignees': ['one@example.com', 'two@example.com']})

    def test_update_api_call_use_defaults(self):
        api_client_mock = MagicMock()
        api_client_mock.send.return_value = MagicMock()

        resource = CaseManagement(api_key='test')
        resource._api_client = api_client_mock

        resource.update(model_id=70, title='Example', priority='Low', confidential=False)

        api_client_mock.send.assert_called_once_with(method='put',
                                                     endpoint='case/70',
                                                     data={
                                                         'title': 'Example',
                                                         'priority': 'Low',
                                                         'confidential': False
                                                     })

    def test_update_api_call_with_all_props(self):
        api_client_mock = MagicMock()
        api_client_mock.send.return_value = MagicMock()

        resource = CaseManagement(api_key='test')
        resource._api_client = api_client_mock

        resource.update(model_id=7,
                        title='Example',
                        priority='Low',
                        confidential=True,
                        description='Hello world',
                        referenceNumber='132')

        api_client_mock.send.assert_called_once_with(method='put',
                                                     endpoint='case/7',
                                                     data={
                                                         'title': 'Example',
                                                         'priority': 'Low',
                                                         'confidential': True,
                                                         'description': 'Hello world',
                                                         'referenceNumber': '132'})

    def test_change_status_api_call(self):
        api_client_mock = MagicMock()
        api_client_mock.send.return_value = MagicMock()

        resource = CaseManagement(api_key='test')
        resource._api_client = api_client_mock

        resource.change_status(model_id=70, status='in-progress')

        api_client_mock.send.assert_called_once_with(method='put',
                                                     endpoint='case/70/status/in-progress')

    def test_remove_assignee_api_call(self):
        api_client_mock = MagicMock()
        api_client_mock.send.return_value = MagicMock()

        resource = CaseManagement(api_key='test')
        resource._api_client = api_client_mock

        resource.remove_assignee(model_id=70, email='johhn-doe@example.com')

        api_client_mock.send.assert_called_once_with(method='delete',
                                                     endpoint='case/70/assignee/johhn-doe@example.com')

    def test_add_assignee_api_call(self):
        api_client_mock = MagicMock()
        api_client_mock.send.return_value = MagicMock()

        resource = CaseManagement(api_key='test')
        resource._api_client = api_client_mock

        resource.add_assignee(model_id=70, email='johhn-doe@example.com')

        api_client_mock.send.assert_called_once_with(method='put',
                                                     endpoint='case/70/assignee/johhn-doe@example.com')

    def test_add_comment_api_call(self):
        api_client_mock = MagicMock()
        api_client_mock.send.return_value = MagicMock()

        resource = CaseManagement(api_key='test')
        resource._api_client = api_client_mock

        resource.add_comment(model_id=70, message='Lorem ipsum')

        api_client_mock.send.assert_called_once_with(method='post',
                                                     endpoint='case/70/comment',
                                                     data={'message': 'Lorem ipsum'})

    def _patched_os_exists(*args, **kwarg):
        path = args[0]
        if '/Home/Downloads' == path:
            return True
        return False

    @patch('builtins.open', new_callable=mock_open())
    @patch('os.path.exists', side_effect=_patched_os_exists)
    @patch('os.path.isdir', return_value=True)
    def test_download_evidence_api_call(self, os_isdir_mocked, os_path_mocked, open_mocked):
        api_client_mock = MagicMock()
        api_client_mock.send.return_value = MagicMock()

        resource = CaseManagement(api_key='test')
        resource._api_client = api_client_mock

        resource.download_evidence(model_id=70, file_id=100, target_folder='/Home/Downloads')

        api_client_mock.send.assert_called_once_with(method='get',
                                                     endpoint='case/70/file/100',
                                                     stream=True)

        open_mocked.assert_called_once()

    @responses.activate
    def test_one_response(self):
        resource = CaseManagement(api_key='test')

        mocked_entry = {
            'id': 100,
            'title': 'Example case',
            'referenceNumber': None,
            'status': 'Open',
            'priority': 'Low',
            'isConfidential': False,
            'createdDate': '2022-10-27T11:16:45+0000',
            'updatedDate': '2022-10-27T11:16:45+0000'
        }
        responses.add(responses.GET, resource._api_client.get_api_url() + '/case/100',
                      json=mocked_entry,
                      status=200)

        response = resource.one(100)

        assert isinstance(response, CaseDto) is True
        assert 100 == response.id
        assert response.isConfidential is False
        assert response.referenceNumber is None

    @responses.activate
    def test_list_response(self):
        resource = CaseManagement(api_key='test')

        mocked_entries = [
            {
                'id': 100,
                'title': 'Example case',
                'referenceNumber': 'ABC-123',
                'status': 'Open',
                'priority': 'Low',
                'isConfidential': True,
                'createdDate': '2022-10-27T11:16:45+0000',
                'updatedDate': '2022-10-27T11:16:45+0000'
            },
            {
                'id': 103,
                'title': 'Another case',
                'status': 'Closed',
                'priority': 'High',
                'isConfidential': False,
                'createdDate': '2022-10-27T10:00:00+0000',
                'updatedDate': '2022-10-27T10:00:00+0000'
            }
        ]
        responses.add(responses.GET, resource._api_client.get_api_url() + '/case',
                      json=mocked_entries,
                      status=200)

        response = resource.list()

        assert isinstance(response, types.GeneratorType) is True

        response_list = list(response)
        assert len(response_list) == 2

        assert isinstance(response_list[0], CaseListDto) is True
        assert isinstance(response_list[1], CaseListDto) is True

        assert 100 == response_list[0].id
        assert 'ABC-123' == response_list[0].referenceNumber
        assert 103 == response_list[1].get('id')
        assert response_list[1].get('referenceNumber') is None

    @responses.activate
    def test_create_response(self):
        resource = CaseManagement(api_key='test')

        responses.add(responses.POST, resource._api_client.get_api_url() + '/case',
                      json={
                          'success': True,
                          'id': 789
                      },
                      status=201)

        response = resource.create('Test test', 'low')

        assert isinstance(response, int) is True
        assert 789 == response

    @responses.activate
    def test_update_response(self):
        resource = CaseManagement(api_key='test')

        responses.add(responses.PUT, resource._api_client.get_api_url() + '/case/34',
                      json={
                          'success': True,
                          'id': 789
                      },
                      status=200)

        response = resource.update(34, 'Test test', 'low', True)

        assert isinstance(response, bool) is True
        assert response is True

    @responses.activate
    def test_change_status_response(self):
        resource = CaseManagement(api_key='test')

        responses.add(responses.PUT, resource._api_client.get_api_url() + '/case/34/status/closed',
                      json={
                          'success': True,
                      },
                      status=200)

        response = resource.change_status(34, 'closed')

        assert isinstance(response, bool) is True
        assert response is True

    @responses.activate
    def test_add_assignee_response(self):
        resource = CaseManagement(api_key='test')

        responses.add(responses.PUT, resource._api_client.get_api_url() + '/case/34/assignee/john-doe@example.com',
                      json={
                          'success': True,
                      },
                      status=200)

        response = resource.add_assignee(34, 'john-doe@example.com')

        assert isinstance(response, bool) is True
        assert response is True

    @responses.activate
    def test_remove_assignee_response(self):
        resource = CaseManagement(api_key='test')

        responses.add(responses.DELETE, resource._api_client.get_api_url() + '/case/34/assignee/john-doe@example.com',
                      json={
                          'success': True,
                      },
                      status=200)

        response = resource.remove_assignee(34, 'john-doe@example.com')

        assert isinstance(response, bool) is True
        assert response is True

    @responses.activate
    def test_add_comment_response(self):
        resource = CaseManagement(api_key='test')

        responses.add(responses.POST, resource._api_client.get_api_url() + '/case/34/comment',
                      json={
                          'success': True,
                      },
                      status=201)

        response = resource.add_comment(34, 'Lorem ipsum')

        assert isinstance(response, bool) is True
        assert response is True

    @responses.activate
    def test_activities_response(self):
        resource = CaseManagement(api_key='test')

        mocked_entries = [
            {
                'description': 'Added a new comment',
                'comment': 'Lorem ipsum...',
                'createdBy': 'john-doe@example.com',
                'createdDate': '2022-10-27T11:16:45+0000'
            }
        ]
        responses.add(responses.GET, resource._api_client.get_api_url() + '/case/3/activity',
                      json=mocked_entries,
                      status=200)

        response = resource.activities(3)

        assert isinstance(response, types.GeneratorType) is True

        response_list = list(response)
        assert len(response_list) == 1

        assert isinstance(response_list[0], CaseActivityDto) is True

        assert 'Added a new comment' == response_list[0].description
        assert 'Lorem ipsum...' == response_list[0].comment
        assert 'john-doe@example.com' == response_list[0].createdBy
        assert '2022-10-27T11:16:45+0000' == response_list[0].createdDate
