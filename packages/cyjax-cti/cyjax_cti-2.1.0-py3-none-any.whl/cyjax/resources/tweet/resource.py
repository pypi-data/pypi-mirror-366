from typing import Optional

from cyjax.helpers import DateHelper
from cyjax.resources.resource import Resource
from cyjax.types import ApiDateType, PaginationResponseType
from .dto import TweetDto


class Tweet(Resource):

    def list(self,
             query: Optional[str] = None,
             since: Optional[ApiDateType] = None,
             until: Optional[ApiDateType] = None,
             limit: Optional[int] = None) -> PaginationResponseType:
        """
        Returns tweets.

        :param query: The search query.
        :type query: str, optional

        :param since: The start date time.
        :type since: (datetime, timedelta, str), optional

        :param until: The end date time.
        :type until:  (datetime, timedelta, str), optional

        :param limit: The limit of items to fetch. If limit is None returns all items for a collection.
        :type limit: int

        :return: The list generator for tweets.
        :rtype PaginationResponseType:
        """

        params = DateHelper.build_date_params(since=since, until=until)
        if query:
            params.update({'query': query})

        return self._paginate(endpoint='tweet', params=params, limit=limit, dto=TweetDto)
