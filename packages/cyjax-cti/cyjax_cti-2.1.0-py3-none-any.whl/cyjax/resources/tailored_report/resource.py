from typing import Optional

from cyjax.helpers import DateHelper
from cyjax.resources.resource import Resource
from cyjax.types import ApiDateType, PaginationResponseType, ModelResponseType
from .dto import TailoredReportDto


class TailoredReport(Resource):

    def list(self,
             query: Optional[str] = None,
             since: Optional[ApiDateType] = None,
             until: Optional[ApiDateType] = None,
             limit: Optional[int] = None) -> PaginationResponseType:
        """
        Returns my tailored reports.

        :param query: The search query.
        :type query: str, optional

        :param since: The start date time.
        :type since: (datetime, timedelta, str), optional

        :param until: The end date time.
        :type until:  (datetime, timedelta, str), optional

        :param limit: The limit of items to fetch. If limit is None returns all items for a collection.
        :type limit: int

        :return: The list generator for incident reports.
        :rtype PaginationResponseType:
        """
        params = DateHelper.build_date_params(since=since, until=until)
        if query:
            params.update({'query': query})

        return self._paginate(endpoint='report/my-report', params=params, limit=limit, dto=TailoredReportDto)

    def one(self, report_id: int) -> ModelResponseType:
        """
        Get one record by ID

        :param report_id: live intelligence report ID
        :type report_id: int, str

        :return: The record dictionary, raises exception if record not found
        :rtype: ModelResponseType:
        """
        return self._get_one_by_id(endpoint='report/my-report', record_id=report_id, dto=TailoredReportDto)
