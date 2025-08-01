from typing import List
from cyjax.resources.model_dto import ModelDto


class ThreatActorDto(ModelDto):

    @property
    def id(self) -> str:
        """
        The model identifier.
        :rtype str:
        """
        return self.get('id')

    @property
    def name(self) -> str:
        """
        The name.
        :rtype str:
        """
        return self.get('name')

    @property
    def description(self) -> str:
        """
        The description.
        :rtype str:
        """
        return self.get('description')

    @property
    def notes(self) -> str:
        """
        Notes from analysts.
        :rtype str:
        """
        return self.get('notes')

    @property
    def aliases(self) -> List[str]:
        """
        A list of aliases the profile is known with.
        :rtype List[str]:
        """
        return self.get('aliases')

    @property
    def techniques(self) -> List[str]:
        """
        A list of techniques from MITRE ATT&CK framework.
        :rtype List[str]:
        """
        return self.get('techniques')

    @property
    def software(self) -> List[str]:
        """
        A list of software from MITRE ATT&CK framework.
        :rtype List[str]:
        """
        return self.get('software')

    @property
    def last_update(self) -> str:
        """
        The update timestamp in ISO8601 format.
        :rtype str:
        """
        return self.get('last_update')

    def __repr__(self):
        return '<ThreatActorDto id={}>'.format(self.id)
