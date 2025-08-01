from typing import Optional, List
from urllib.parse import urlparse, parse_qs

from cyjax.resources.model_dto import ModelDto
from cyjax.resources.incident_report.resource import IncidentReport
from cyjax.resources.incident_report.dto import IncidentReportDto


class IndicatorDto(ModelDto):

    def __init__(self, **kwargs):
        super(IndicatorDto, self).__init__(**kwargs)
        self.__incident_report = None

    @property
    def uuid(self) -> str:
        """
        The model UUID v4.
        :rtype str:
        """
        return self.get('uuid')

    @property
    def type(self) -> str:
        """
        The indicator type.
        :rtype str:
        """
        return self.get('type')

    @property
    def value(self) -> str:
        """
        The indicator value.
        :rtype str:
        """
        return self.get('value')

    @property
    def description(self) -> str:
        """
        The indicator description.
        :rtype str:
        """
        return self.get('description')

    @property
    def source(self) -> str:
        """
        The indicator source.
        :rtype str:
        """
        return self.get('source')

    @property
    def handling_condition(self) -> str:
        """
        The handling condition.
        :rtype str:
        """
        return self.get('handling_condition')

    @property
    def ttp(self) -> List[str]:
        """
        The list of techniques and software from MITRE ATT&CK framework.
        :rtype List[str]:
        """
        return self.get('ttp')

    @property
    def industry_type(self) -> List[str]:
        """
        The list of affected industry verticals.
        :rtype List[str]:
        """
        return self.get('industry_type')

    @property
    def discovered_at(self) -> str:
        """
        The discovery timestamp in ISO8601 format.
        :rtype str:
        """
        return self.get('discovered_at')

    def get_incident_report(self) -> IncidentReportDto:
        """
        Get the incident report linked with this indicator.
        :rtype IncidentReportDto:
        """

        if self.__incident_report is None:
            report_url = self.source

            if 'id=' in report_url:
                parse_result = urlparse(report_url)
                dict_result = parse_qs(parse_result.query)
                report_id = dict_result['id'][0]
            else:
                report_id = report_url.split('/')[-1]

            if report_id:
                report_resource = IncidentReport()
                self.__incident_report = report_resource.one(report_id)

        return self.__incident_report

    def __repr__(self):
        return '<IndicatorDto uuid={}>'.format(self.uuid)


class GeoIpDto(ModelDto):
    @property
    def country_code(self) -> Optional[str]:
        """
        The country code.
        :rtype Optional[str]:
        """
        return self.get('country_code')

    @property
    def country_name(self) -> Optional[str]:
        """
        The country name.
        :rtype Optional[str]:
        """
        return self.get('country_name')

    @property
    def city(self) -> Optional[str]:
        """
        The city.
        :rtype Optional[str]:
        """
        return self.get('city')

    @property
    def ip_address(self) -> Optional[str]:
        """
        The ip address.
        :rtype Optional[str]:
        """
        return self.get('ip_address')


class AsnDto(ModelDto):
    @property
    def organization(self) -> Optional[str]:
        """
        The organization name.
        :rtype Optional[str]:
        """
        return self.get('organization')

    @property
    def number(self) -> Optional[str]:
        """
        The organization number.
        :rtype Optional[str]:
        """
        return self.get('number')


class SightingDto(ModelDto):
    @property
    def count(self) -> int:
        """
        The number of events.
        :rtype int:
        """
        return self.get('count')

    @property
    def description(self) -> str:
        """
        The event description.
        :rtype str:
        """
        return self.get('description')

    @property
    def source(self) -> str:
        """
        The event source.
        :rtype str:
        """
        return self.get('source')

    @property
    def last_seen_timestamp(self) -> str:
        """
        The last seen timestamp of the source in ISO format.
        :rtype str:
        """
        return self.get('last_seen_timestamp')


class EnrichmentDto(ModelDto):

    @property
    def type(self) -> str:
        """
        The type of the indicator.
        :rtype str:
        """
        return self.get('type')

    @property
    def last_seen_timestamp(self) -> str:
        """
        The last seen timestamp in ISO8601 format.
        :rtype str:
        """
        return self.get('last_seen_timestamp')

    @property
    def geoip(self) -> Optional[GeoIpDto]:
        """
        The GeoIP information.
        :rtype Optional[GeoIpMetadataDto]:
        """
        geoip_obj = self.get('geoip')

        if geoip_obj is not None and len(geoip_obj.keys()):
            return GeoIpDto(**geoip_obj)
        return None

    @property
    def asn(self) -> Optional[AsnDto]:
        """
        The autonomous system information.
        :rtype Optional[AsnMetadataDto]:
        """
        asn_obj = self.get('asn')

        if asn_obj is not None and len(asn_obj.keys()):
            return AsnDto(**asn_obj)
        return None

    @property
    def sightings(self) -> List[SightingDto]:
        """
        The list of sightings from sources.
        :rtype List[SightingDto]:
        """
        return list(map(lambda sighting: SightingDto(**sighting), self.get('sightings')))

    def __repr__(self):
        return '<EnrichmentDto type={}>'.format(self.type)
