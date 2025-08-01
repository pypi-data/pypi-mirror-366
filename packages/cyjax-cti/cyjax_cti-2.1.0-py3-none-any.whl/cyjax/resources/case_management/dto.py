from typing import Optional, List

from cyjax.resources.model_dto import ModelDto


class CaseEvidenceFileDto(ModelDto):

    @property
    def name(self) -> str:
        """
        The file name.
        :rtype str:
        """
        return self.get('name')

    @property
    def url(self) -> str:
        """
        The URL to download the file.
        :rtype str:
        """
        return self.get('url')

    def __repr__(self):
        return '<CaseEvidenceFileDto name={}>'.format(self.name)


class CaseEvidenceDto(ModelDto):

    @property
    def author(self) -> str:
        """
        The user email who added the evidence.
        :rtype str:
        """
        return self.get('author')

    @property
    def note(self) -> Optional[str]:
        """
        The evidence note.
        :rtype Optional[str]:
        """
        return self.get('note')

    @property
    def files(self) -> Optional[List[CaseEvidenceFileDto]]:
        """
        The list of files attached to the evidence.
        :rtype Optional[List[EvidenceFileDto]]:
        """
        if self.get('files'):
            return list(map(lambda file: CaseEvidenceFileDto(**file), self.get('files')))
        else:
            return None

    @property
    def createdDate(self) -> str:
        """
        The date when the evidence has been added.
        :rtype str:
        """
        return self.get('createdDate')

    def __repr__(self):
        return '<CaseEvidenceDto>'


class CaseActivityDto(ModelDto):

    @property
    def description(self) -> str:
        """
        The description.
        :rtype str:
        """
        return self.get('description')

    @property
    def comment(self) -> Optional[str]:
        """
        The comment.
        :rtype Optional[str]:
        """
        return self.get('comment')

    @property
    def createdBy(self) -> Optional[str]:
        """
        The user's email address that craeted the case.
        :rtype Optional[str]:
        """
        return self.get('createdBy')

    @property
    def createdDate(self) -> str:
        """
        The creation date time in ISO 8601 format.
        :rtype str:
        """
        return self.get('createdDate')

    def __repr__(self):
        return '<CaseActivityDto>'


class CaseListDto(ModelDto):

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
        The case title.
        :rtype str:
        """
        return self.get('title')

    @property
    def referenceNumber(self) -> Optional[str]:
        """
        The case reference number.
        :rtype str:
        """
        return self.get('referenceNumber')

    @property
    def status(self) -> str:
        """
        The case status.
        :rtype str:
        """
        return self.get('status')

    @property
    def priority(self) -> str:
        """
        The case priority.
        :rtype str:
        """
        return self.get('priority')

    @property
    def isConfidential(self) -> bool:
        """
        Whether the case is confidential.
        :rtype str:
        """
        return self.get('isConfidential')

    @property
    def createdDate(self) -> str:
        """
        The creation date time in ISO 8601 format.
        :rtype str:
        """
        return self.get('createdDate')

    @property
    def updatedDate(self) -> str:
        """
        The last update date time in ISO 8601 format.
        :rtype str:
        """
        return self.get('updatedDate')

    def __repr__(self):
        return '<CaseListDto id={}>'.format(self.id)


class CaseDto(CaseListDto):

    @property
    def description(self) -> str:
        """
        The case description.
        :rtype str:
        """
        return self.get('description')

    @property
    def createdBy(self) -> Optional[str]:
        """
        The user's email address who created the case.
        :rtype Optional[str]:
        """
        return self.get('createdBy')

    @property
    def assignees(self) -> List[str]:
        """
        The list of email addresses of users assigned to the case.
        :rtype List[str]:
        """
        return self.get('assignees')

    @property
    def evidences(self) -> List[CaseEvidenceDto]:
        """
        The list of case evidences.
        :rtype List[CaseEvidenceDto]:
        """
        return list(map(lambda evidence: CaseEvidenceDto(**evidence), self.get('evidences')))

    @property
    def activitiesUrl(self) -> str:
        """
        The URL to get the case activities.
        :rtype str:
        """
        return self.get('activitiesUrl')

    def __repr__(self):
        return '<CaseDto id={}>'.format(self.id)
