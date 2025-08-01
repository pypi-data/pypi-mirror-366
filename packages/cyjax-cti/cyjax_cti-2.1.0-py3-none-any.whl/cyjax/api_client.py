from typing import Optional, Union
from json.decoder import JSONDecodeError
import requests

import cyjax
from .exceptions import ApiKeyNotFoundException, ForbiddenException, NotFoundException, ResponseErrorException, \
    TooManyRequestsException, UnauthorizedException, ValidationException


class ApiClient(object):
    """
    The Cyjax REST API URL.
    """
    BASE_URI = 'https://api.cymon.co/v2'
    TIMEOUT = 15

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        :param api_key: The API key.
        :param api_url: The API URL. If not set uses the default API URL.
        """
        self.__api_key = api_key if api_key else cyjax.api_key
        self.__api_url = api_url if api_url is not None else \
            cyjax.api_url if cyjax.api_url is not None else ApiClient.BASE_URI
        self.__proxies = cyjax.proxy_settings
        self.__verify = cyjax.verify_ssl

    def send(self,
             method,
             endpoint,
             params=None,
             data=None,
             **kwargs
             ) -> requests.Response:
        """
        Send a request to an endpoint.

        :param method: The request method: ``GET``, ``OPTIONS``, ``HEAD``, ``POST``, ``PUT``, ``PATCH``, or ``DELETE``
        :type method: str

        :param endpoint: The endpoint.
        :type endpoint: str

        :param params: The list of tuples or bytes to send in the query string for the request
        :type params:  Dictionary, optional

        :param data: The list of tuples, bytes, or file-like object to send in the body of the request
        :return: :class:`Response <Response>` object
        :rtype: requests.Response

        :raises ResponseErrorException: Whether the request fails.
        :raises ApiKeyNotFoundException: Whether the API key is not provided.
        :raises UnauthorizedException: Whether the API key is not authorized to perform the request.
        :raises TooManyRequestsException: Whether the API key exceeds the rate limit.
        """

        if data is None:
            data = {}
        if params is None:
            params = {}
        if not self.__api_key:
            raise ApiKeyNotFoundException()

        if endpoint.startswith(('http://', 'https://')):
            url = endpoint
        else:
            url = self.get_api_url() + '/' + endpoint

        if 'timeout' not in kwargs:
            kwargs['timeout'] = ApiClient.TIMEOUT

        response = requests.api.request(method=method,
                                        url=url,
                                        params=params,
                                        data=data,
                                        headers={'Authorization': 'Bearer ' + self.__api_key,
                                                 'User-Agent': self.__get_user_agent()},
                                        proxies=self._get_proxies(),
                                        verify=self._get_verify(),
                                        **kwargs)

        if response.status_code == 401:
            raise UnauthorizedException()
        elif response.status_code == 403:
            raise ForbiddenException()
        elif response.status_code == 404:
            raise NotFoundException()
        elif response.status_code == 422:
            raise ValidationException(response.json())
        elif response.status_code == 429:
            raise TooManyRequestsException()
        elif response.status_code != 200 and response.status_code != 201:
            try:
                json_data = response.json()
                raise ResponseErrorException(response.status_code,
                                             json_data['message'] if 'message' in json_data else 'Unknown')
            except JSONDecodeError:
                raise ResponseErrorException(response.status_code, 'Error parsing response %s' % response.text)

        return response

    def get_api_key(self) -> str:
        """
        Get API key.
        :return: The API key.
        :rtype: str
        """
        return self.__api_key

    def _get_proxies(self) -> Optional[dict]:
        """
        Get the proxies dictionary with proxy settings.
        :return: The proxies dictionary.
        :rtype: dict|None
        """
        if isinstance(self.__proxies, dict):
            return self.__proxies

        return None

    def _get_verify(self) -> Union[bool, str]:
        """
        Get the verify SSL option for the request module.

        :return: The verify option which controls whether we verify the server's TLS certificate
        :rtype: bool
        """
        return self.__verify

    def __get_user_agent(self) -> str:
        """
        Get the User-Agent header value

        :return: The User-Agent header value
        :rtype: str
        """
        user_agent = 'CyjaxPythonSDK/{}'.format(cyjax.__version__)

        if cyjax.client_name is not None:
            user_agent = '{} ({})'.format(user_agent, str(cyjax.client_name)[:30])

        return user_agent

    def get_api_url(self) -> str:
        """
                Get the API url.
                :return: The API url.
                :rtype: str
                """
        return self.__api_url
