from typing import List

from cyjax.resources.model_dto import ModelDto


class SocialMediaDto(ModelDto):

    @property
    def id(self) -> str:
        """
        The model identifier.
        :rtype str:
        """
        return self.get('id')

    @property
    def source(self) -> str:
        """
        The source
        :rtype str:
        """
        return self.get('source')

    @property
    def username(self) -> str:
        """
        The username
        :rtype str:
        """
        return self.get('username')

    @property
    def content(self) -> str:
        """
        The content
        :rtype str:
        """
        return self.get('content')

    @property
    def priority(self) -> str:
        """
        The priority
        :rtype str:
        """
        return self.get('priority')

    @property
    def image(self) -> str:
        """
        The API endpoint to download the image associated with the entry.
        :rtype str:
        """
        return self.get('image')

    @property
    def tags(self) -> List[str]:
        """
        The list of tags
        :rtype List[str]:
        """
        return self.get('tags')

    @property
    def source_timestamp(self) -> str:
        """
        The source timestamp in ISO8601 format.
        :rtype str:
        """
        return self.get('source_timestamp')

    @property
    def timestamp(self) -> str:
        """
        The post timestamp in ISO8601 format.
        :rtype str:
        """
        return self.get('timestamp')

    def __repr__(self):
        return '<SocialMediaDto id={}>'.format(self.id)
