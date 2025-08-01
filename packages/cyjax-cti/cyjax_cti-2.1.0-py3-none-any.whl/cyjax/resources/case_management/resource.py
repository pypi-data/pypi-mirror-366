from typing import Optional, List

from cyjax.helpers import DateHelper
from cyjax.types import ApiDateType, PaginationResponseType
from cyjax.resources.resource import Resource
from .dto import CaseActivityDto, CaseDto, CaseListDto


class CaseManagement(Resource):

    def list(self,
             query: Optional[str] = None,
             status: Optional[str] = None,
             priority: Optional[str] = None,
             since: Optional[ApiDateType] = None,
             until: Optional[ApiDateType] = None,
             limit: Optional[int] = None) -> PaginationResponseType:
        """
        Lists cases.

        :param query: The search query.
        :type query: Optional[str]

        :param status: The status filter.
        :type priority: Optional[str]

        :param priority: The priority filter.
        :type priority: Optional[str]

        :param since: The start date time.
        :type since: Optional[ApiDateType]

        :param until: The end date time.
        :type until: Optional[ApiDateType]

        :param limit: The limit of items to fetch. If limit is None returns all items for a collection.
        :type limit: int

        :return: The list generator for cases.
        :rtype PaginationResponseType:
        """
        params = DateHelper.build_date_params(since=since, until=until)
        if query:
            params.update({'query': query})

        if status:
            params.update({'status': status})

        if priority:
            params.update({'priority': priority})

        return self._paginate(endpoint='case',
                              params=params,
                              limit=limit,
                              dto=CaseListDto)

    def one(self, model_id: int):
        """
        Get one case by ID

        :param model_id: The record ID
        :type model_id: int, str

        :return: The record dictionary, raises exception if record not found
        :rtype: CaseListDto:
        """
        return self._get_one_by_id(endpoint='case',
                                   record_id=model_id,
                                   dto=CaseDto)

    def create(self,
               title: str,
               priority: str,
               confidential: Optional[bool] = False,
               description: Optional[str] = None,
               referenceNumber: Optional[str] = None,
               assignees: Optional[List[str]] = None) -> int:
        """
        Create a new case.

        :param title: The case title
        :type title: str

        :param priority: The case priority
        :type priority: str

        :param confidential: Whether the case should be marked as confidential.
        :type confidential: Optional[bool]

        :param description: The case description.
        :type description: Optional[str]

        :param referenceNumber: The case reference number.
        :type referenceNumber: Optional[str]

        :param assignees: The list of email addresses that should be set as assignees.
        :type assignees: Optional[List[str]]

        :return: The created case ID.
        :rtype: int:
        """
        body = {
            'title': title,
            'priority': priority,
            'confidential': confidential
        }

        if description:
            body.update({'description': description})

        if assignees:
            body.update({'assignees': assignees})

        if referenceNumber:
            body.update({'referenceNumber': referenceNumber})

        response = self._api_client.send(endpoint='case',
                                         method='post',
                                         data=body)
        return response.json().get('id')

    def update(self,
               model_id: int,
               title: str,
               priority: str,
               confidential: bool,
               description: Optional[str] = None,
               referenceNumber: Optional[str] = None) -> bool:
        """
        Update existing case data.

        :param model_id: The case ID
        :type model_id: int, str

        :param title: The case title
        :type title: str

        :param priority: The case priority
        :type priority: str

        :param confidential: Whether the case should be marked as confidential.
        :type confidential: bool

        :param description: The case description.
        :type description: Optional[str]

        :param referenceNumber: The case reference number.
        :type referenceNumber: Optional[str]

        :return: Whether the action was successful.
        :rtype: bool:
        """
        body = {
            'title': title,
            'priority': priority,
            'confidential': confidential
        }

        if description:
            body.update({'description': description})

        if referenceNumber:
            body.update({'referenceNumber': referenceNumber})

        response = self._api_client.send(endpoint='case/{}'.format(model_id),
                                         method='put',
                                         data=body)
        return response.json().get('success')

    def change_status(self, model_id: int, status: str) -> bool:
        """
        Change the status for an existing case.

        :param model_id: The case ID
        :type model_id: int, str

        :param status: The new status. Allowed values are: open, in-progress, resolved, closed.
        :type status: str

        :return: Whether the action was successful.
        :rtype: bool:
        """
        response = self._api_client.send(endpoint='case/{}/status/{}'.format(model_id, status.strip()),
                                         method='put')
        return response.json().get('success')

    def add_assignee(self, model_id: int, email: str) -> bool:
        """
        Add a new assignee to an existing case.

        :param model_id: The case ID
        :type model_id: int, str

        :param email: The email address of the user to assign.
        :type email: str

        :return: Whether the action was successful.
        :rtype: bool:
        """
        response = self._api_client.send(endpoint='case/{}/assignee/{}'.format(model_id, email.strip()),
                                         method='put')
        return response.json().get('success')

    def remove_assignee(self, model_id: int, email: str) -> bool:
        """
        Remove an existing assignee for a existing case.

        :param model_id: The case ID
        :type model_id: int, str

        :param email: The email address of the user to remove as assignee.
        :type email: str

        :return: Whether the action was successful.
        :rtype: bool:
        """
        response = self._api_client.send(endpoint='case/{}/assignee/{}'.format(model_id, email.strip()),
                                         method='delete')
        return response.json().get('success')

    def add_comment(self, model_id: int, message: str) -> bool:
        """
        Send a comment for a case.

        :param model_id: The case ID
        :type model_id: int, str

        :param message: The message.
        :type message: str

        :return: Whether the action was successful.
        :rtype: bool:
        """
        response = self._api_client.send(endpoint='case/{}/comment'.format(model_id),
                                         method='post',
                                         data={'message': message})
        return response.json().get('success')

    def download_evidence(self, model_id: int, file_id: int, target_folder: str) -> str:
        """
        Downloads a file that has been added to the case as evidence to the target folder.

        :param model_id: The case ID
        :type model_id: int, str

        :param file_id: The file ID
        :type file_id: int, str

        :param target_folder: The path to the folder where to download the file.
        :type target_folder: str

        :return: The path whether the file was stored.
        :rtype str:
        """
        return self.download_from_url(url='case/{}/file/{}'.format(model_id, file_id),
                                      target_folder=target_folder)

    def activities(self,
                   model_id: int,
                   query: Optional[str] = None,
                   since: Optional[ApiDateType] = None,
                   until: Optional[ApiDateType] = None,
                   limit: Optional[int] = None) -> PaginationResponseType:
        """
        Returns a list of case activities within the search parameter boundaries.

        :param model_id: The case ID
        :type model_id: int, str

        :param query: The search query.
        :type query: Optional[str]

        :param since: The start date time.
        :type since: Optional[ApiDateType]

        :param until: The end date time.
        :type until: Optional[ApiDateType]

        :param limit: The limit of items to fetch. If limit is None returns all items for a collection.
        :type limit: int

        :return: The list generator for cases.
        :rtype PaginationResponseType:
        """
        params = DateHelper.build_date_params(since=since, until=until)
        if query:
            params.update({'query': query})

        return self._paginate(endpoint='case/{}/activity'.format(model_id),
                              params=params,
                              limit=limit,
                              dto=CaseActivityDto)
