from typing import Optional, List
from cyjax.resources.model_dto import ModelDto


class MaliciousDomainDto(ModelDto):

    @property
    def domains(self) -> List[str]:
        """
        The list of domains or fully-qualified domains.
        :rtype List[str]:
        """
        return self.get('domains')

    @property
    def matched_domains(self) -> List[str]:
        """
        The list of domains matched by keywords.
        :rtype List[str]:
        """
        return self.get('matched_domains')

    @property
    def unmatched_domains(self) -> List[str]:
        """
        The list of other domains in the SSL certificate.
        :rtype List[str]:
        """
        return self.get('unmatched_domains')

    @property
    def keyword(self) -> List[str]:
        """
        The list of keywords that matched the domain.
        :rtype List[str]:
        """
        return self.get('keyword')

    @property
    def type(self) -> str:
        """
        The type of record. Possible values are: new-domain, ssl-certificate.
        :rtype str:
        """
        return self.get('type')

    @property
    def source(self) -> Optional[str]:
        """
        The source for a SSL certificate.
        :rtype str:
        """
        return self.get('source')

    @property
    def discovery_date(self) -> str:
        """
        The discovery timestamp in ISO8601 format.
        :rtype str:
        """
        return self.get('discovery_date')

    @property
    def create_date(self) -> str:
        """
        The creation date time for a newly registered domain.
        :rtype str:
        """
        return self.get('create_date')

    @property
    def expiration_timestamp(self) -> str:
        """
        The expiration timestamp for a SSL certificate in ISO8601 format.
        :rtype str:
        """
        return self.get('expiration_timestamp')

    def __repr__(self):
        return '<MaliciousDomainDto discovery_date={}>'.format(self.discovery_date)
