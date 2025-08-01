from typing import Optional

from cyjax.helpers import DateHelper
from cyjax.resources.resource import Resource
from cyjax.types import PaginationResponseType, ModelResponseType, ApiDateType
from .dto import LeakedEmailDto, InvestigatorLeakedEmailDto


class LeakedEmail(Resource):

    def list(self,
             query: Optional[str] = None,
             since: Optional[ApiDateType] = None,
             until: Optional[ApiDateType] = None,
             limit: Optional[int] = None) -> PaginationResponseType:
        """
        Returns leaked emails.

        :param query: The search query.
        :type query: str, optional

        :param since: The start date time. time.
        :type since: (datetime, timedelta, str), optional

        :param until: The end date time.
        :type until:  (datetime, timedelta, str), optional

        :param limit: The limit of items to fetch. If limit is None returns all items for a collection.
        :type limit: int

        :return: The list of leaked emails.
        :rtype PaginationResponseType:
        """

        params = DateHelper.build_date_params(since=since, until=until)
        if query:
            params.update({'query': query})

        return self._paginate(endpoint='data-leak/credentials', params=params, limit=limit, dto=LeakedEmailDto)

    def one(self, record_id: int) -> ModelResponseType:
        """
        Get one record by ID

        :param record_id: The record ID
        :type record_id: int, str

        :return: The record dictionary, raises exception if record not found
        :rtype: LeakedEmailDto:
        """
        return self._get_one_by_id(endpoint='data-leak/credentials', record_id=record_id, dto=LeakedEmailDto)

    def search(self, query) -> PaginationResponseType:
        """
        Search for leaked emails.

        :param query: The search query
        :type query: str

        :return: The list of leaked emails.
        :rtype PaginationResponseType:
        """

        if not isinstance(query, str):
            raise TypeError('Query must be of type string')
        elif query.strip() == '':
            raise TypeError('Query can not be empty')

        params = {'query': query.strip()}

        return self._paginate(endpoint='data-leak/investigation', params=params, dto=InvestigatorLeakedEmailDto)
