from cyjax.resources.model_dto import ModelDto


class TorExitNodeDto(ModelDto):

    @property
    def id(self) -> str:
        """
        The model identifier.
        :rtype str:
        """
        return self.get('id')

    @property
    def ip(self) -> str:
        """
        The IP address.
        :rtype str:
        """
        return self.get('ip')

    @property
    def discovered_at(self) -> str:
        """
        The discovery timestamp in ISO 8601 format.
        :rtype str:
        """
        return self.get('discovered_at')

    def __repr__(self):
        return '<TorExitNodeDto id={}>'.format(self.id)
