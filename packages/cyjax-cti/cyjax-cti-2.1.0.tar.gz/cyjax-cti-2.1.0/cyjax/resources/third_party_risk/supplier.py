from typing import Optional

from cyjax.helpers import DateHelper
from cyjax.resources.resource import Resource
from cyjax.types import ApiDateType, PaginationResponseType, ModelResponseType
from .dto import SupplierDto, SupplierListDto


class Supplier(Resource):

    def list(self,
             query: Optional[str] = None,
             tier: Optional[int] = None,
             risk: Optional[str] = None,
             since: Optional[ApiDateType] = None,
             until: Optional[ApiDateType] = None,
             limit: Optional[int] = None) -> PaginationResponseType:
        """
        Lists third party suppliers.

        :param query: The search query.
        :type query: Optional[str]

        :param tier: The tier ID to filter suppliers by.
        :type tier: int, optional

        :param risk: The risk range to filter suppliers by
        :type risk: Optional[str]

        :param since: The start date time.
        :type since: Optional[ApiDateType]

        :param until: The end date time.
        :type until: Optional[ApiDateType]

        :param limit: The limit of items to fetch. If limit is None returns all items for a collection.
        :type limit: int

        :return: The list generator for third party risk suppliers.
        :rtype PaginationResponseType:
        """
        params = DateHelper.build_date_params(since=since, until=until)
        if query:
            params.update({'query': query})

        if tier:
            params.update({'tier': tier})

        if risk:
            params.update({'risk': risk})

        return self._paginate(endpoint='third-party-risk/supplier',
                              params=params,
                              limit=limit,
                              dto=SupplierListDto)

    def one(self, model_id: int) -> ModelResponseType:
        """
        Get one record by ID

        :param model_id: The supplier ID
        :type model_id: int, str

        :return: The record dictionary, raises exception if record not found
        :rtype: ModelResponseType:
        """
        return self._get_one_by_id(endpoint='third-party-risk/supplier',
                                   record_id=model_id,
                                   params={},
                                   dto=SupplierDto)

    def create(self,
               name: str,
               tier: int,
               url: str,
               referenceNumber: Optional[str] = None) -> int:
        """
        Create a new supplier.

        :param name: The supplier name
        :type name: str

        :param tier: The supplier tier ID
        :type tier: int

        :param url: The supplier website URL.
        :type url: int

        :param referenceNumber: The supplier reference number.
        :type referenceNumber: str

        :return: The created supplier ID.
        :rtype: int:
        """
        body = {
            'name': name,
            'tier': tier,
            'url': url,
            'referenceNumber': referenceNumber
        }
        response = self._api_client.send(endpoint='third-party-risk/supplier',
                                         method='post',
                                         params={},
                                         data=body)
        return response.json().get('id')

    def update(self,
               model_id: int,
               name: str,
               tier: int,
               url: str,
               referenceNumber: Optional[str] = None) -> bool:
        """
        Update existing supplier data.

        :param model_id: The supplier ID
        :type model_id: int, str

        :param name: The supplier name
        :type name: str

        :param tier: The supplier tier ID
        :type tier: int

        :param url: The supplier website URL.
        :type url: int

        :param referenceNumber: The supplier reference number.
        :type referenceNumber: str

        :return: Whether the action was successful.
        :rtype: bool:
        """
        body = {
            'name': name,
            'tier': tier,
            'url': url,
            'referenceNumber': referenceNumber
        }
        response = self._api_client.send(endpoint='third-party-risk/supplier/{}'.format(model_id),
                                         method='put',
                                         params={},
                                         data=body)
        return response.json().get('success')

    def delete(self, model_id: int) -> bool:
        """
        Delete a supplier by ID

        :param model_id: The supplier ID
        :type model_id: int, str

        :return: Whether the action was successful.
        :rtype: bool:
        """
        response = self._api_client.send(endpoint='third-party-risk/supplier/{}'.format(model_id),
                                         method='delete')
        return response.json().get('success')
