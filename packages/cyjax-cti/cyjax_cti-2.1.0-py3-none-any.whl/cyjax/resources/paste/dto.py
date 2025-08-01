from cyjax.resources.model_dto import ModelDto


class PasteDto(ModelDto):

    @property
    def id(self) -> str:
        """
        The model identifier.
        :rtype str:
        """
        return self.get('id')

    @property
    def paste_id(self) -> str:
        """
        The paste ID.
        :rtype str:
        """
        return self.get('paste_id')

    @property
    def title(self) -> str:
        """
        The title.
        :rtype str:
        """
        return self.get('title')

    @property
    def url(self) -> str:
        """
        The url.
        :rtype str:
        """
        return self.get('url')

    @property
    def content(self) -> str:
        """
        The content.
        :rtype str:
        """
        return self.get('content')

    @property
    def discovered_at(self) -> str:
        """
        The discovered at timestamp in ISO8601 format.
        :rtype str:
        """
        return self.get('discovered_at')

    def __repr__(self):
        return '<PasteDto id={}>'.format(self.id)
