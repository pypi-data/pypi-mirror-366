from typing import Optional

from cyjax.helpers import DateHelper
from cyjax.resources.resource import Resource
from cyjax.types import ApiDateType, PaginationResponseType
from .dto import MaliciousDomainDto


class MaliciousDomain(Resource):

    def list(self,
             since: Optional[ApiDateType] = None,
             until: Optional[ApiDateType] = None,
             limit: Optional[int] = None) -> PaginationResponseType:
        """
        Returns potential malicious domains.

        :param since: The start date time.
        :type since: (datetime, timedelta, str), optional

        :param until: The end date time.
        :type until:  (datetime, timedelta, str), optional

        :param limit: The limit of items to fetch. If limit is None returns all items for a collection.
        :type limit: int

        :return: The list generator for potential malicious domains.
        :rtype PaginationResponseType:
        """

        params = DateHelper.build_date_params(since=since, until=until)
        return self._paginate(endpoint='domain-monitor/potential-malicious-domain',
                              params=params,
                              limit=limit,
                              dto=MaliciousDomainDto)
