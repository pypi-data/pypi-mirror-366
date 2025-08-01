from typing import Optional

from cyjax.helpers import DateHelper
from cyjax.resources.resource import Resource
from cyjax.types import ApiDateType, PaginationResponseType, ModelResponseType, ModelIdType
from .dto import TorExitNodeDto


class TorExitNode(Resource):

    def list(self,
             query: Optional[str] = None,
             since: Optional[ApiDateType] = None,
             until: Optional[ApiDateType] = None,
             limit: Optional[int] = None) -> PaginationResponseType:
        """
        Returns TOR exit nodes.

        :param query: The search query.
        :type query: str, optional

        :param since: The start date time.
        :type since: (datetime, timedelta, str), optional

        :param until: The end date time.
        :type until:  (datetime, timedelta, str), optional

        :param limit: The limit of items to fetch. If limit is None returns all items for a collection.
        :type limit: int

        :return: The list generator for TOR exit nodes.
        :rtype PaginationResponseType:
        """

        params = DateHelper.build_date_params(since=since, until=until)
        if query:
            params.update({'query': query})

        return self._paginate(endpoint='blacklists/tor-node', params=params, limit=limit, dto=TorExitNodeDto)

    def one(self, record_id: ModelIdType) -> ModelResponseType:
        """
        Get one record by ID

        :param record_id: The record ID
        :type record_id: int, str

        :return: The record dictionary, raises exception if record not found
        :rtype: ModelResponseType:
        """
        return self._get_one_by_id(endpoint='blacklists/tor-node', record_id=record_id, dto=TorExitNodeDto)
