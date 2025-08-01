from typing import Optional

from cyjax.resources.resource import Resource
from cyjax.types import PaginationResponseType, ModelResponseType
from .dto import DataBreachDto, DataBreachListDto


class DataBreach(Resource):

    def list(self,
             query: Optional[str] = None,
             limit: Optional[int] = None) -> PaginationResponseType:
        """
        List data breaches

        :param query: The search query.
        :type query: str, optional

        :param limit: The limit of items to fetch. If limit is None returns all items for a collection.
        :type limit: int

        :return: The list of data breaches.
        :rtype Generator[dict]:
        """
        params = {}
        if query:
            params.update({'query': query})

        return self._paginate(endpoint='data-leak/breach', params=params, limit=limit, dto=DataBreachListDto)

    def one(self, record_id) -> ModelResponseType:
        """
        Get one record by ID

        :param record_id: The record ID
        :type record_id: int, str

        :return: The record dictionary, raises exception if record not found
        :rtype: DataBreachDto:
        """
        return self._get_one_by_id(endpoint='data-leak/breach', record_id=record_id, dto=DataBreachDto)
