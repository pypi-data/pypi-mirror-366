from typing import Optional

from cyjax.helpers import DateHelper
from cyjax.resources.resource import Resource
from cyjax.types import ApiDateType, PaginationResponseType
from .dto import EnrichmentDto, IndicatorDto


class IndicatorOfCompromise(Resource):

    SUPPORTED_SOURCES = ['incident-report', 'my-report']

    def list(self,
             since: Optional[ApiDateType] = None,
             until: Optional[ApiDateType] = None,
             type: Optional[str] = None,
             source_type: Optional[str] = None,
             source_id: Optional[int] = None,
             limit: Optional[int] = None) -> \
            PaginationResponseType:
        """
        Returns indicators of compromise.

        :param since: The start date time.
        :type since: (datetime, timedelta, str), optional

        :param until: The end date time.
        :type until:  (datetime, timedelta, str), optional

        :param type: A comma-separated list of indicator types. If not specified all indicators are returned.
            Allowed values are: IPv4, IPv6, Domain, Hostname, Email, FileHash-SHA1, FileHash-SHA256, FileHash-MD5,
            FileHash-SSDEEP.
        :type type:  (str), optional

        :param source_type: The indicators source type. Allowed values are: incident-report, my-report.
        :type source_type:  (str), optional

        :param source_id: The indicators source ID.
        :type source_id:  (int), optional

        :param limit: The limit of items to fetch. If limit is None returns all items for a collection.
        :type limit: int

        :return: The list generator for indicators of compromise.
        :rtype PaginationResponseType:
        """

        params = DateHelper.build_date_params(since=since, until=until)

        if type is not None:
            params['type'] = type

        if source_type is not None:
            if source_type in IndicatorOfCompromise.SUPPORTED_SOURCES:
                params['sourceType'] = source_type
            else:
                raise ValueError('Invalid source_type. Please check the list of supported sources.')

        if source_id is not None:
            if source_id > 0:
                params['sourceId'] = source_id
            else:
                raise ValueError('Invalid source_id')

        return self._paginate(endpoint='indicator-of-compromise', params=params, limit=limit, dto=IndicatorDto)

    def enrichment(self, value: str):
        """
        Get the enrichment metadata for the given indicator value

        :param value: The indicator value.
        :type value: str

        :return: The enrichment metadata
        :rtype dict
        """
        if not value or not isinstance(value, str):
            raise ValueError('Indicator value is invalid')

        response = self._api_client.send(method='get', endpoint='indicator-of-compromise/enrichment',
                                         params={'value': value})

        obj = response.json()

        if obj.keys():
            return EnrichmentDto(**obj)
        else:
            return obj
