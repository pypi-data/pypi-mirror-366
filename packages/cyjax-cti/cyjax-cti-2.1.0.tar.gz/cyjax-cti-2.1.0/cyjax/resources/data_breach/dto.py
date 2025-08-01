from typing import Optional, List

from cyjax.resources.model_dto import ModelDto


class DataBreachListDto(ModelDto):

    @property
    def id(self) -> int:
        """
        The model identifier.
        :rtype int:
        """
        return self.get('id')

    @property
    def name(self) -> str:
        """
        The breach name.
        :rtype str:
        """
        return self.get('name')

    @property
    def data_classes(self) -> List[str]:
        """
        The list of data classes.
        :rtype List[str]:
        """
        return self.get('data_classes')

    @property
    def discovered_at(self) -> str:
        """
        The discovery timestamp in ISO8601 format.
        :rtype str:
        """
        return self.get('discovered_at')

    def __repr__(self):
        return '<DataBreachListDto id={}>'.format(self.id)


class IncidentReportMetadataDto(ModelDto):

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
    def url(self) -> str:
        """
        The API URL to the report.
        :rtype str:
        """
        return self.get('url')

    def __repr__(self):
        return '<IncidentReportMetadataDto id={}>'.format(self.id)


class DataBreachDto(DataBreachListDto):

    @property
    def content(self) -> str:
        """
        The breach description.
        :rtype str:
        """
        return self.get('content')

    @property
    def incident_report(self) -> IncidentReportMetadataDto:
        """
        The incident report Metadata.
        :rtype IncidentReportMetadataDto:
        """
        return IncidentReportMetadataDto(**self.get('incident_report'))

    def __repr__(self):
        return '<DataBreachDto id={}>'.format(self.id)


class DataBreachMetadataDto(ModelDto):

    @property
    def id(self) -> int:
        """
        The model identifier.
        :rtype int:
        """
        return self.get('id')

    @property
    def name(self) -> str:
        """
        The breach name.
        :rtype str:
        """
        return self.get('name')

    @property
    def url(self) -> str:
        """
        The API URL to the breach.
        :rtype str:
        """
        return self.get('url')

    def __repr__(self):
        return '<DataBreachMetadataDto id={}>'.format(self.id)


class LeakedEmailDto(ModelDto):

    @property
    def id(self) -> str:
        """
        The model identifier.
        :rtype str:
        """
        return self.get('id')

    @property
    def email(self) -> str:
        """
        The email address.
        :rtype str:
        """
        return self.get('email')

    @property
    def source(self) -> str:
        """
        The source name.
        :rtype str:
        """
        return self.get('source')

    @property
    def data_breach(self) -> DataBreachMetadataDto:
        """
        The linked data breach Metadata.
        :rtype DataBreachMetadataDto:
        """
        return DataBreachMetadataDto(**self.get('data_breach'))

    @property
    def data_classes(self) -> List[str]:
        """
        The list of data classes.
        :rtype List[str]:
        """
        return self.get('data_classes')

    @property
    def discovered_at(self) -> str:
        """
        The discovery timestamp in ISO8601 format.
        :rtype str:
        """
        return self.get('discovered_at')

    def __repr__(self):
        return '<LeakedEmailDto id={}>'.format(self.id)


class InvestigatorLeakedEmailDto(ModelDto):

    @property
    def email(self) -> str:
        """
        The email address.
        :rtype str:
        """
        return self.get('email')

    @property
    def data_breach(self) -> DataBreachMetadataDto:
        """
        The linked data breach Metadata.
        :rtype DataBreachMetadataDto:
        """
        return DataBreachMetadataDto(**self.get('data_breach'))

    @property
    def discovered_at(self) -> str:
        """
        The discovery timestamp in ISO8601 format.
        :rtype str:
        """
        return self.get('discovered_at')

    @property
    def domain(self) -> Optional[str]:
        """
        The email domain.
        :rtype Optional[str]:
        """
        return self.get('domain')

    @property
    def full_name(self) -> Optional[str]:
        """
        The full name.
        :rtype Optional[str]:
        """
        return self.get('full_name')

    @property
    def username(self) -> Optional[str]:
        """
        The username.
        :rtype Optional[str]:
        """
        return self.get('username')

    @property
    def password(self) -> Optional[str]:
        """
        The password.
        :rtype Optional[str]:
        """
        return self.get('password')

    @property
    def address(self) -> Optional[str]:
        """
        The address.
        :rtype Optional[str]:
        """
        return self.get('address')

    @property
    def country(self) -> Optional[str]:
        """
        The country.
        :rtype Optional[str]:
        """
        return self.get('country')

    @property
    def ip_address(self) -> Optional[str]:
        """
        The ip address.
        :rtype Optional[str]:
        """
        return self.get('ip_address')

    @property
    def date_of_birth(self) -> Optional[str]:
        """
        The date of birth.
        :rtype Optional[str]:
        """
        return self.get('date_of_birth')

    @property
    def gender(self) -> Optional[str]:
        """
        The gender.
        :rtype Optional[str]:
        """
        return self.get('gender')

    @property
    def phone_number(self) -> Optional[str]:
        """
        The phone number.
        :rtype Optional[str]:
        """
        return self.get('phone_number')

    def __repr__(self):
        return '<InvestigatorLeakedEmailDto email={}>'.format(self.email)
