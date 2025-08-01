#  CYjAX Limited
import pytest
import responses
from types import GeneratorType

from unittest.mock import patch, Mock, MagicMock, mock_open
from cyjax.exceptions import NotFoundException

import cyjax
from cyjax.api_client import ApiClient
from cyjax.resources.resource import Resource
from cyjax.resources.model_dto import ModelDto


class TestResourceService:

    @classmethod
    def setup_class(cls):
        api_client = ApiClient(api_key='foo_api_key')
        cls.api_url = api_client.get_api_url()

    def test_setting_client(self):
        resource = Resource()
        assert 'https://api.cymon.co/v2' == resource._api_client.get_api_url()
        assert resource._api_client.get_api_key() is None

        resource = Resource('123456', 'https://api.new-address.com')
        assert 'https://api.new-address.com' == resource._api_client.get_api_url()
        assert '123456' == resource._api_client.get_api_key()

    @responses.activate
    def test_paginate(self):

        responses.add(responses.GET, self.api_url + '/test/endpoint?param1=test&param2=foo&page=1&per-page='
                      + str(Resource.DEFAULT_ITEMS_PER_PAGE),
                      json=[{"1": "a"}, {"2": "b"}],
                      status=200,
                      headers={
                          'Link': self.api_url + '/test/endpoint?param1=test&param2=foo&page=2&per-page=1;rel=next'
                      })

        responses.add(responses.GET, self.api_url + '/test/endpoint?param1=test&param2=foo&page=2&per-page='
                      + str(Resource.DEFAULT_ITEMS_PER_PAGE),
                      json=[{"3": "c"}, {"4": "d"}], status=200)

        resource_service = Resource(api_key='9753b80f76bd4293e8c610b07091a37b')
        for x in resource_service._paginate(endpoint='test/endpoint', params={'param1': 'test', 'param2': 'foo'}):
            continue

        assert len(responses.calls) == 2
        assert responses.calls[0].request.url == self.api_url + \
               '/test/endpoint?param1=test&param2=foo&page=1&per-page=' + str(Resource.DEFAULT_ITEMS_PER_PAGE)
        assert responses.calls[0].response.text == '[{"1": "a"}, {"2": "b"}]'

        assert responses.calls[1].request.url == self.api_url + \
               '/test/endpoint?param1=test&param2=foo&page=2&per-page=' + str(Resource.DEFAULT_ITEMS_PER_PAGE)
        assert responses.calls[1].response.text == '[{"3": "c"}, {"4": "d"}]'

    @responses.activate
    def test_paginate_result(self):
        responses.add(responses.GET, self.api_url + '/test/endpoint?page=1&per-page='
                      + str(Resource.DEFAULT_ITEMS_PER_PAGE),
                      json=[{"1": "a"}, {"2": "b"}],
                      status=200)

        resource_service = Resource(api_key='9753b80f76bd4293e8c610b07091a37b')
        pagination_result = resource_service._paginate(endpoint='test/endpoint')

        assert isinstance(pagination_result, GeneratorType)
        page_as_list = list(pagination_result)
        assert isinstance(page_as_list, list)
        assert 2 == len(page_as_list)
        assert isinstance(page_as_list[0], dict)
        assert isinstance(page_as_list[1], dict)
        assert {"1": "a"} == page_as_list[0]
        assert {"2": "b"} == page_as_list[1]

    @responses.activate
    def test_paginate_apply_dto(self):

        class ColorDto(ModelDto):

            @property
            def id(self) -> int:
                return self.get('id')

            @property
            def color(self) -> int:
                return self.get('color')

        responses.add(responses.GET, self.api_url + '/test/endpoint?page=1&per-page='
                      + str(Resource.DEFAULT_ITEMS_PER_PAGE),
                      json=[
                          {"id": 1, "color": "Red"},
                          {"id": 2, "color": "Yellow"},
                          {"id": 3, "color": "Black"},
                      ],
                      status=200)

        resource_service = Resource(api_key='9753b80f76bd4293e8c610b07091a37b')
        pagination_result = resource_service._paginate(endpoint='test/endpoint', dto=ColorDto)

        assert isinstance(pagination_result, GeneratorType)
        page_as_list = list(pagination_result)
        assert 3 == len(page_as_list)
        assert isinstance(page_as_list[0], ColorDto)
        assert isinstance(page_as_list[1], ColorDto)
        assert isinstance(page_as_list[2], ColorDto)
        assert 'Red' == page_as_list[0].color
        assert 'Yellow' == page_as_list[1].color
        assert 'Black' == page_as_list[2].color

    @responses.activate
    def test_paginate_wont_apply_dto_if_resource_is_empty(self):

        class ColorDto(ModelDto):

            @property
            def id(self) -> int:
                return self.get('id')

            @property
            def color(self) -> int:
                return self.get('color')

        responses.add(responses.GET, self.api_url + '/test/endpoint?page=1&per-page='
                      + str(Resource.DEFAULT_ITEMS_PER_PAGE),
                      json=[
                          {}
                      ],
                      status=200)

        resource_service = Resource(api_key='9753b80f76bd4293e8c610b07091a37b')
        pagination_result = resource_service._paginate(endpoint='test/endpoint', dto=ColorDto)

        assert isinstance(pagination_result, GeneratorType)
        page_as_list = list(pagination_result)
        assert 1 == len(page_as_list)
        assert isinstance(page_as_list[0], dict)
        assert {} == page_as_list[0]

    @responses.activate
    def test_paginate_nothing_found(self):
        responses.add(responses.GET, self.api_url + '/test/endpoint?page=1&per-page='
                      + str(Resource.DEFAULT_ITEMS_PER_PAGE),
                      json=[],
                      status=200)

        resource_service = Resource(api_key='9753b80f76bd4293e8c610b07091a37b')
        pagination_result = resource_service._paginate(endpoint='test/endpoint')

        assert isinstance(pagination_result, GeneratorType)
        assert 0 == len(list(pagination_result))

    @responses.activate
    def test_get_list_empty_result(self):
        cyjax.api_key = 'module_api_key'

        responses.add(responses.GET, self.api_url + '/test-resource', status=200,
                      json=[])

        resource = Resource()
        assert hasattr(resource, '_get_list')

        response = resource._get_list('test-resource')

        assert isinstance(response, list)
        assert len(response) == 0

        cyjax.api_key = None

    @responses.activate
    def test_get_list_without_dto(self):
        cyjax.api_key = 'module_api_key'

        responses.add(responses.GET, self.api_url + '/test-resource', status=200,
                      json=[
                          {'id': 1000, 'name': 'John', 'age': 30},
                          {'id': 1005, 'name': 'Maria', 'age': 78},
                          {'id': 2598, 'name': 'Tom', 'age': 16},
                          {'id': 3974, 'name': 'Anna', 'age': 39},
                          {'id': 4879, 'name': 'Boris', 'age': 58},
                      ])

        resource = Resource()
        assert hasattr(resource, '_get_list')

        response = resource._get_list('test-resource')

        assert isinstance(response, list)
        assert len(response) == 5
        assert isinstance(response[0], dict)
        assert {'id': 1000, 'name': 'John', 'age': 30} == response[0]
        assert {'id': 4879, 'name': 'Boris', 'age': 58} == response[4]

        cyjax.api_key = None

    @responses.activate
    def test_get_list_with_dto(self):
        cyjax.api_key = 'module_api_key'

        class UserDto(ModelDto):

            @property
            def id(self) -> int:
                return self.get('id')

            @property
            def name(self) -> int:
                return self.get('name')

            @property
            def age(self) -> int:
                return self.get('age')

        responses.add(responses.GET, self.api_url + '/test-resource', status=200,
                      json=[
                          {'id': 1000, 'name': 'John', 'age': 30},
                          {'id': 1005, 'name': 'Maria', 'age': 78},
                          {'id': 2598, 'name': 'Tom', 'age': 16},
                          {'id': 3974, 'name': 'Anna', 'age': 39},
                          {'id': 4879, 'name': 'Boris', 'age': 58},
                      ])

        resource = Resource()
        assert hasattr(resource, '_get_list')

        response = resource._get_list('test-resource', dto=UserDto)

        assert isinstance(response, list)
        assert len(response) == 5
        assert isinstance(response[0], UserDto)
        assert 1000 == response[0].get('id')

        cyjax.api_key = None

    def test_one_not_implement_by_default(self):
        resource = Resource()
        assert hasattr(resource, 'one')

        with pytest.raises(NotImplementedError) as e:
            resource.one(1)

        assert 'This resource does not support one() method' == str(e.value)

    @responses.activate
    def test_get_one_by_id(self):
        cyjax.api_key = 'module_api_key'

        responses.add(responses.GET, self.api_url + '/test-resource/7003', status=200,
                      json={'id': 7003,
                            'title': 'Test',
                            'description': 'Hello'})

        resource = Resource()
        assert hasattr(resource, '_get_one_by_id')

        entity = resource._get_one_by_id('test-resource', 7003)
        assert isinstance(entity, dict)
        assert 7003 == entity.get('id')
        assert 'Test' == entity.get('title')
        assert 'Hello' == entity.get('description')

        entity = resource._get_one_by_id('test-resource', '7003')
        assert 7003 == entity.get('id')

        entity = resource._get_one_by_id('test-resource/', '7003')
        assert 7003 == entity.get('id')

        entity = resource._get_one_by_id('/test-resource/', '7003')
        assert 7003 == entity.get('id')

        cyjax.api_key = None

    @responses.activate
    def test_get_one_by_id_apply_dto(self):
        cyjax.api_key = 'module_api_key'

        class HelloDto(ModelDto):

            @property
            def id(self) -> int:
                return self.get('id')

            @property
            def title(self) -> str:
                return self.get('title')

        responses.add(responses.GET, self.api_url + '/test-resource/7003', status=200,
                      json={'id': 7003,
                            'title': 'Test',
                            'description': 'Hello'})

        resource = Resource()
        assert hasattr(resource, '_get_one_by_id')

        entity = resource._get_one_by_id('test-resource', 7003, dto=HelloDto)
        assert isinstance(entity, HelloDto)
        assert isinstance(entity, ModelDto)
        assert isinstance(entity, dict)
        assert hasattr(entity, 'id')
        assert hasattr(entity, 'title')
        assert hasattr(entity, 'description') is False
        assert 7003 == entity.get('id')
        assert 7003 == entity.id
        assert 7003 == entity['id']
        assert 'Test' == entity.get('title')
        assert 'Test' == entity.title
        assert 'Hello' == entity.get('description')

        cyjax.api_key = None

    @responses.activate
    def test_get_one_by_id_apply_dto_when_empty_json(self):
        cyjax.api_key = 'module_api_key'

        class HelloDto(ModelDto):

            @property
            def id(self) -> int:
                return self.get('id')

            @property
            def title(self) -> str:
                return self.get('title')

        responses.add(responses.GET, self.api_url + '/test-resource/7003', status=200,
                      json={})

        resource = Resource()
        assert hasattr(resource, '_get_one_by_id')

        entity = resource._get_one_by_id('test-resource', 7003, dto=HelloDto)
        assert isinstance(entity, HelloDto) is False
        assert isinstance(entity, dict)
        assert entity == {}

        cyjax.api_key = None

    @responses.activate
    def test_get_one_by_id_not_found(self):
        cyjax.api_key = 'module_api_key'

        responses.add(responses.GET, self.api_url + '/test-resource/7004', status=404,
                      json={"message": "Incident report not found",
                            "code": 404,
                            "reason": "Not Found"})

        resource = Resource()

        with pytest.raises(NotFoundException) as e:
            resource._get_one_by_id('test-resource', 7004)

        assert "Not found." == str(e.value)
        cyjax.api_key = None

    def test_default_pagination_limit(self):
        page_response_mock = Mock()
        page_response_mock.json.return_value = [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}, {'id': 5}, {'id': 6}]
        page_response_mock.links = {}

        with patch.object(Resource, '_get_page', return_value=page_response_mock):
            resource_service = Resource(api_key='test-key')

            models = list(resource_service._paginate(endpoint='test/endpoint'))
            assert 6 == len(models)

    def test_supports_pagination_limit(self):
        page_response_mock = Mock()
        page_response_mock.json.return_value = [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}, {'id': 5}, {'id': 6}]
        page_response_mock.links = {'next': {'url': 'https://next-page.com?page=2'}}

        with patch.object(Resource, '_get_page', return_value=page_response_mock):
            resource_service = Resource(api_key='test-key')

            models = list(resource_service._paginate(endpoint='test/endpoint', limit=2))
            assert 2 == len(models)

    @responses.activate
    def test_limit_with_multiple_pages(self):
        models = []
        for i in range(100):
            models.append({'id': i})

        responses.add(responses.GET, self.api_url + '/test/endpoint?page=1&per-page=50',
                      status=200, json=models[:50],
                      headers={'Link': self.api_url + '/test/endpoint?page=2&per-page=50;rel=next'})

        responses.add(responses.GET, self.api_url + '/test/endpoint?page=2&per-page=50',
                      json=models[50:],
                      status=200)

        resource_service = Resource(api_key='test-key')
        found = list(resource_service._paginate(endpoint='test/endpoint', limit=67))
        assert 67 == len(found)
        assert models[0:67] == found

    def _patched_os_exists(*args, **kwarg):
        path = args[0]
        if '/Test/Home/Cyjax/Downloads' == path:
            return True
        return False

    @patch('builtins.open', new_callable=mock_open())
    @patch('os.path.exists', side_effect=_patched_os_exists)
    @patch('os.path.isdir', return_value=True)
    def test_download_from_url(self, os_isdir_mocked, os_path_mocked, open_mocked):
        api_client_mock = MagicMock()
        api_client_mock.send.return_value = MagicMock()

        resource_service = Resource(api_key='test-key')
        resource_service._api_client = api_client_mock

        url = 'https://test.cyjax.com/file/test.jpg'
        download_to = '/Test/Home/Cyjax/Downloads'
        resource_service.download_from_url(url=url, target_folder=download_to)

        open_mocked.assert_called_once()
        api_client_mock.send.assert_called_once_with(method='get',
                                                     endpoint=url,
                                                     stream=True)

    @responses.activate
    @patch('builtins.open', new_callable=mock_open())
    @patch('os.path.exists', side_effect=_patched_os_exists)
    @patch('os.path.isdir', return_value=True)
    def test_download_from_url_with_response_mocked(self, os_isdir_mocked, os_path_mocked, open_mocked):
        resource_service = Resource(api_key='test-key')
        download_to = '/Test/Home/Cyjax/Downloads'

        responses.add(responses.GET, self.api_url + '/file/example.jpg',
                      status=200, body=b'test-image-bytes',
                      headers={'download_file_name': 'file-name-from-header.jpg'})

        response = resource_service.download_from_url(url='file/example.jpg', target_folder=download_to)
        open_mocked.assert_called_once_with('/Test/Home/Cyjax/Downloads/file-name-from-header.jpg', 'wb')
        responses.assert_call_count(self.api_url + '/file/example.jpg', 1)
        assert '/Test/Home/Cyjax/Downloads/file-name-from-header.jpg' == response

    @responses.activate
    @patch('builtins.open', new_callable=mock_open())
    @patch('os.path.exists',
           side_effect=lambda *args: args[0] in ['/Test/Home/Cyjax/Downloads',
                                                 '/Test/Home/Cyjax/Downloads/file-name-from-header.jpg'])
    @patch('os.path.isdir', return_value=True)
    def test_download_from_url_will_add_name_postfix(self, os_isdir_mocked, os_path_mocked, open_mocked):
        resource_service = Resource(api_key='test-key')
        download_to = '/Test/Home/Cyjax/Downloads'

        responses.add(responses.GET, self.api_url + '/file/example.jpg',
                      status=200, body=b'test-image-bytes',
                      headers={'download_file_name': 'file-name-from-header.jpg'})

        response = resource_service.download_from_url(url='file/example.jpg', target_folder=download_to)
        open_mocked.assert_called_once_with('/Test/Home/Cyjax/Downloads/file-name-from-header(2).jpg', 'wb')
        responses.assert_call_count(self.api_url + '/file/example.jpg', 1)
        assert '/Test/Home/Cyjax/Downloads/file-name-from-header(2).jpg' == response

    @responses.activate
    @patch('builtins.open', new_callable=mock_open())
    @patch('os.path.exists',
           side_effect=lambda *args: args[0] in ['/Test/Home/Cyjax/Downloads',
                                                 '/Test/Home/Cyjax/Downloads/file-name-from-header.jpg',
                                                 '/Test/Home/Cyjax/Downloads/file-name-from-header(2).jpg',
                                                 '/Test/Home/Cyjax/Downloads/file-name-from-header(3).jpg'])
    @patch('os.path.isdir', return_value=True)
    def test_download_from_url_will_increment_name_postfix(self, os_isdir_mocked, os_path_mocked, open_mocked):
        resource_service = Resource(api_key='test-key')
        download_to = '/Test/Home/Cyjax/Downloads'

        responses.add(responses.GET, self.api_url + '/file/example.jpg',
                      status=200, body=b'test-image-bytes',
                      headers={'download_file_name': 'file-name-from-header.jpg'})

        response = resource_service.download_from_url(url='file/example.jpg', target_folder=download_to)
        open_mocked.assert_called_once_with('/Test/Home/Cyjax/Downloads/file-name-from-header(4).jpg', 'wb')
        responses.assert_call_count(self.api_url + '/file/example.jpg', 1)
        assert '/Test/Home/Cyjax/Downloads/file-name-from-header(4).jpg' == response

    def test_trim_endpoint(self):
        resource = Resource()
        assert hasattr(resource, '_trim_endpoint')
        assert 'test-testy' == resource._trim_endpoint('test-testy')
        assert 'test-testy' == resource._trim_endpoint('/test-testy')
        assert 'test-testy' == resource._trim_endpoint('test-testy/')
        assert 'test-testy' == resource._trim_endpoint('/test-testy/')
