from cyjax.resources.model_dto import ModelDto


class TailoredReportDto(ModelDto):

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
        The grading (source evaluation).
        :rtype str:
        """
        return self.get('source_evaluation')

    @property
    def impact(self) -> str:
        """
        The report impact.
        :rtype str:
        """
        return self.get('impact')

    @property
    def last_update(self) -> str:
        """
        The update timestamp in ISO8601 format.
        :rtype str:
        """
        return self.get('last_update')

    def __repr__(self):
        return '<TailoredReportDto id={}>'.format(self.id)
