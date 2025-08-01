import os
import logging
import uuid
from typing import Optional, Type
from mimetypes import guess_extension

from requests import Response
from urllib.parse import urlparse, parse_qs

from cyjax.api_client import ApiClient
from cyjax.types import PaginationResponseType, ModelResponseType, ModelIdType, ListResponseType
from cyjax.resources.model_dto import ModelDto


class Resource(object):

    DEFAULT_ITEMS_PER_PAGE = 50

    def __init__(self, api_key=None, api_url=None):
        """
        :param api_key: The API key.
        :param api_url: The Cyjax API url.
        """
        self._api_client = ApiClient(api_key=api_key, api_url=api_url)
        self.__total_results_count = None

    def one(self, record_id: ModelIdType) -> ModelResponseType:
        """
        Base method to get one by id, should be implemented in child resource class.
        If a resource does not support getting one record by id, raise NotImplement exception.
        """
        raise NotImplementedError('This resource does not support one() method')

    def download_from_url(self, url: str, target_folder: str) -> str:
        """
        Download file from a given url and store it to the target folder.

        :param url: The URL to download the file from
        :type url: str

        :param target_folder: The path to the folder where to download the file.
        :type target_folder: str

        :return: The path whether the file was stored.
        :rtype str:
        """
        response = self._api_client.send(method='get', endpoint=url, stream=True)
        download_target = self.__get_download_target_file_path(response, target_folder)

        with open(download_target, 'wb') as handle:
            for chunk in response.iter_content():
                handle.write(chunk)

        return download_target

    def _paginate(self,
                  endpoint: str,
                  params: Optional[dict] = None,
                  data: Optional[dict] = None,
                  limit: Optional[int] = None,
                  dto: Optional[Type[ModelDto]] = None) -> PaginationResponseType:
        """
        Returns (all) items for the given endpoint.

        :param endpoint: The endpoint.
        :type endpoint: str

        :param params: The list of tuples or bytes to send in the query string for the request.
        :type params:  dict, optional

        :param data: The list of tuples, bytes, or file-like object to send in the body of the request.
        :type data: dict

        :param limit: The limit of items to fetch. If limit is None returns all items for a collection.
        :type limit: int

        :param dto: The DTO class to apply to the items.
        :type dto: Optional[Type[ModelDto]]

        :return: The list generator.
        :rtype PaginationResponseType:
        """

        if data is None:
            data = {}
        if params is None:
            params = {}
        if limit is not None:
            limit = int(limit)

        endpoint = self._trim_endpoint(endpoint)

        logging.debug('Sending request to endpoint %s...' % endpoint)
        has_next = True
        page = 1
        found = 0

        while has_next:
            logging.debug('Processing page %d...' % page)
            response = self._get_page(endpoint=endpoint, params=params, data=data, page=page)
            logging.debug('Found %d results...' % len(response.json()))

            for entry in response.json():
                if limit is None or found < limit:
                    found += 1

                    if dto is not None and len(entry.keys()):
                        entry = dto(**entry)

                    yield entry
                else:
                    has_next = False
                    break

            if has_next and 'next' in response.links:
                parsed = urlparse(response.links['next']['url'])
                page = int(parse_qs(parsed.query)['page'][0])
            else:
                has_next = False

    def _get_list(self,
                  endpoint: str,
                  params: Optional[dict] = None,
                  dto: Optional[Type[ModelDto]] = None) -> ListResponseType:
        """
        Get the list of entries from the endpoint.

        :param endpoint: The resource endpoint.
        :type endpoint: str

        :param params: The list of tuples or bytes to send in the query string for the request.
        :type params: dict, optional

        :param dto: The DTO class to apply to the model.
        :type dto: Optional[Type[ModelDto]]

        :return: The list of entries.
        :rtype List[ListResponseType]:
        """
        response = self._api_client.send(method='get',
                                         endpoint=self._trim_endpoint(endpoint),
                                         params=params)
        response_list = response.json()

        if len(response_list) and dto is not None:
            return list(map(lambda model_dict: dto(**model_dict), response_list))
        else:
            return response_list

    def _get_one_by_id(self,
                       endpoint: str,
                       record_id: ModelIdType,
                       params: Optional[dict] = None,
                       dto: Optional[Type[ModelDto]] = None) -> ModelResponseType:
        """
        Returns one record by ID.

        :param endpoint: The resource endpoint.
        :type endpoint: str

        :param record_id: The record ID.
        :type record_id: int, str

        :param params: The list of tuples or bytes to send in the query string for the request.
        :type params: dict, optional

        :param dto: The DTO class to apply to the model.
        :type dto: Optional[Type[ModelDto]]

        :return: The record model response, raises exception if record not found
        :rtype: ModelResponseType:
        """
        if params is None:
            params = {}

        url = self._trim_endpoint(endpoint) + '/' + str(record_id)

        response = self._api_client.send(method='get', endpoint=url, params=params)

        if response:
            obj = response.json()
            if dto is not None and len(obj.keys()):
                return dto(**obj)
            else:
                return obj

    def _get_page(self,
                  endpoint: str,
                  params: Optional[dict] = None,
                  data: Optional[dict] = None,
                  page: Optional[int] = 1,
                  per_page: int = DEFAULT_ITEMS_PER_PAGE) -> Response:
        """
        Returns all items in a page for the given endpoint.

        :param endpoint: The endpoint.
        :type endpoint: str

        :param params: The list of tuples or bytes to send in the query string for the request.
        :type params: dict, optional

        :param data: The list of tuples, bytes, or file-like object to send in the body of the request.
        :return: :class:`Response <Response>` object

        :param page: The page.
        :type page: int, optional

        :param per_page: The number of items per page.
        :type per_page: int, optional

        :return: The list of items.
        :rtype Response:

        :raises ResponseErrorException: Whether the response cannot be parsed.
        :raises ApiKeyNotFoundException: Whether the API key is not provider.
        """
        if params is None:
            params = {}
        if data is None:
            data = {}
        params.update({'page': page, 'per-page': per_page})

        return self._api_client.send(method='get', endpoint=endpoint, params=params, data=data)

    def _trim_endpoint(self, endpoint: str) -> str:
        """Trim slashes from start and end of the given endpoint

        :param endpoint: The endpoint.
        :type endpoint: str

        :return: The endpoint.
        :rtype: str
        """
        if endpoint.startswith('/'):
            endpoint = endpoint[1:]

        if endpoint.endswith('/'):
            endpoint = endpoint[:-1]

        return endpoint

    def __get_download_target_file_path(self, response: Response, target_folder: str) -> str:
        """
        Get the file name from the response and return the path where the file should be stored.

        :param response: The Response object.
        :type response: Response

        :param target_folder: The path to the folder where to download the file.
        :type target_folder: str

        :return: The path whether the file should be stored.
        :rtype str:
        """
        # Check if folder exists
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        if not os.path.isdir(target_folder):
            raise AttributeError('The target folder is not a directory')

        # Get the file name from the header
        file_name = response.headers.get('download_file_name')
        if file_name is None:
            ext = guess_extension(response.headers.get('Content-Type'))
            if ext:
                file_name = '{}{}'.format(str(uuid.uuid4()), ext)

        if file_name is None:
            raise Exception('Unable to detect file type')

        download_target = '{}/{}'.format(target_folder, file_name)
        download_target_path_valid = not os.path.exists(download_target)
        next_file_index = 2

        # Check if file with the same name already exists, if so add the index the suffix
        while download_target_path_valid is False:
            if os.path.exists(download_target):
                old_file_name, file_ext = os.path.splitext(file_name)
                next_file_suffix = '({})'.format(next_file_index)

                if old_file_name.endswith(next_file_suffix):
                    old_file_name = old_file_name.replace(next_file_suffix, '')
                    next_file_index += 1

                file_name = '{}({}){}'.format(old_file_name, next_file_index, file_ext)
                download_target = '{}/{}'.format(target_folder, file_name)

            else:
                download_target_path_valid = True

        return download_target
