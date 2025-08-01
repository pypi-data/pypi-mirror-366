from typing import Optional

from cyjax.helpers import DateHelper
from cyjax.resources.resource import Resource
from cyjax.types import ApiDateType, PaginationResponseType, ModelResponseType
from cyjax.resources.incident_report.dto import IncidentReportDto


class IncidentReport(Resource):

    def list(self,
             query: Optional[str] = None,
             since: Optional[ApiDateType] = None,
             until: Optional[ApiDateType] = None,
             exclude_indicators: Optional[bool] = True,
             limit: Optional[int] = None) -> PaginationResponseType:
        """
        Returns incident reports.

        :param query: The search query.
        :type query: str, optional

        :param since: The start date time.
        :type since: (datetime, timedelta, str), optional

        :param until: The end date time.
        :type until:  (datetime, timedelta, str), optional

        :param exclude_indicators: Whether to exclude indicators from Api response. Defaults to True
        :type exclude_indicators:  bool, optional

        :param limit: The limit of items to fetch. If limit is None returns all items for a collection.
        :type limit: int

        :return: The list generator for incident reports.
        :rtype PaginationResponseType:
        """
        params = DateHelper.build_date_params(since=since, until=until)
        if query:
            params.update({'query': query})

        params['excludeIndicators'] = exclude_indicators

        return self._paginate(endpoint='report/incident', params=params, limit=limit, dto=IncidentReportDto)

    def one(self,
            report_id: int,
            exclude_indicators: Optional[bool] = True) -> ModelResponseType:
        """
        Get one record by ID

        :param report_id: The record ID
        :type report_id: int, str

        :param exclude_indicators: Whether to exclude indicators from Api response. Defaults to True
        :type exclude_indicators:  bool, optional

        :return: The record dictionary, raises exception if record not found
        :rtype: IncidentReportDto:
        """

        params = {'excludeIndicators': exclude_indicators}

        return self._get_one_by_id(endpoint='report/incident',
                                   record_id=report_id,
                                   params=params,
                                   dto=IncidentReportDto)
