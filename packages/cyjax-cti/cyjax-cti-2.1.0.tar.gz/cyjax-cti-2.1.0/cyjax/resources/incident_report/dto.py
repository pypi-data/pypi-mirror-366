from typing import Dict, Optional, List

from cyjax.resources.model_dto import ModelDto


class ReportIndicatorDto(ModelDto):

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

    def __repr__(self):
        return '<ReportIndicatorDto uuid={}>'.format(self.uuid)


class IncidentReportDto(ModelDto):

    @property
    def id(self) -> int:
        """
        The model identifier.
        :rtype int:
        """
        return self.get('id')

    @property
    def title(self) -> str:
        """
        The report title.
        :rtype str:
        """
        return self.get('title')

    @property
    def source(self) -> str:
        """
        The report source.
        :rtype str:
        """
        return self.get('source')

    @property
    def content(self) -> str:
        """
        The report content.
        :rtype str:
        """
        return self.get('content')

    @property
    def severity(self) -> str:
        """
        The report severity.
        :rtype str:
        """
        return self.get('severity')

    @property
    def source_evaluation(self) -> str:
        """
        The report source evaluation.
        :rtype str:
        """
        return self.get('source_evaluation')

    @property
    def impacts(self) -> Dict[str, any]:
        """
        The gradings for affected industry verticals.
        :rtype Dict[str, any]:
        """
        return self.get('impacts')

    @property
    def tags(self) -> List[str]:
        """
        The list of tags.
        :rtype List[str]:
        """
        return self.get('tags')

    @property
    def countries(self) -> List[str]:
        """
        The list country names affected by the incident.
        :rtype List[str]:
        """
        return self.get('countries')

    @property
    def techniques(self) -> List[str]:
        """
        The list of techniques from MITRE ATT&CK framework.
        :rtype List[str]:
        """
        return self.get('techniques')

    @property
    def technique_ids(self) -> List[str]:
        """
        The list of technique IDs from MITRE ATT&CK framework.
        :rtype List[str]:
        """
        return self.get('technique_ids')

    @property
    def software(self) -> List[str]:
        """
        The list of software/tools from MITRE ATT&CK framework.
        :rtype List[str]:
        """
        return self.get('software')

    @property
    def software_ids(self) -> List[str]:
        """
        The list of software/tools IDs from MITRE ATT&CK framework.
        :rtype List[str]:
        """
        return self.get('software_ids')

    @property
    def ioc(self) -> Optional[List[ReportIndicatorDto]]:
        """
        The number of indicators of compromise assigned to the report.
        :rtype Optional[List[ReportIndicatorDto]]:
        """
        # check if IOCs were loaded, they might be not loaded if excludeIndicators=True
        if self.get('ioc') is not None:
            return list(map(lambda ioc_dict: ReportIndicatorDto(**ioc_dict), self.get('ioc')))
        return None

    @property
    def ioc_count(self) -> int:
        """
        The number of indicators of compromise assigned to the report.
        :rtype int:
        """
        return self.get('ioc_count')

    @property
    def last_update(self) -> str:
        """
        The last update date in ISO8601 format.
        :rtype str:
        """
        return self.get('last_update')

    def __repr__(self):
        return '<IncidentReportDto id={}>'.format(self.id)
