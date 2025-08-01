from typing import Optional

from cyjax.helpers import DateHelper
from cyjax.resources.resource import Resource
from cyjax.types import ApiDateType, PaginationResponseType, ModelResponseType, ModelIdType
from cyjax.resources.social_media.dto import SocialMediaDto


class SocialMedia(Resource):

    def list(self,
             query: Optional[str] = None,
             since: Optional[ApiDateType] = None,
             until: Optional[ApiDateType] = None,
             limit: Optional[int] = None) -> PaginationResponseType:
        """
        Returns the list of Social media entries.

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

        return self._paginate(endpoint='social-media', params=params, limit=limit, dto=SocialMediaDto)

    def one(self, record_id: ModelIdType) -> ModelResponseType:
        """
        Get one record by ID

        :param record_id: The record ID
        :type record_id: int, str

        :return: The record DTO, raises exception if record not found
        :rtype: SocialMediaDto:
        """
        return self._get_one_by_id(endpoint='social-media', record_id=record_id, dto=SocialMediaDto)
