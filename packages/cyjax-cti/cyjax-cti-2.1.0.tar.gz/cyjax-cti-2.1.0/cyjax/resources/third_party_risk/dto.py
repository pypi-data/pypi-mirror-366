from typing import Optional

from cyjax.resources.model_dto import ModelDto


class SupplierTierDto(ModelDto):

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
        The tier name.
        :rtype str:
        """
        return self.get('name')

    def __repr__(self):
        return '<SupplierTierDto id={}>'.format(self.id)


class TierDto(SupplierTierDto):

    @property
    def description(self) -> Optional[str]:
        """
        The tier description.
        :rtype Optional[str]:
        """
        return self.get('description')

    @property
    def suppliers(self) -> str:
        """
        The number of suppliers that belongs to this tier.
        :rtype str:
        """
        return self.get('suppliers')

    def __repr__(self):
        return '<TierDto id={}>'.format(self.id)


class SupplierListDto(ModelDto):

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
        The supplier name.
        :rtype str:
        """
        return self.get('name')

    @property
    def referenceNumber(self) -> Optional[str]:
        """
        The supplier reference number.
        :rtype Optional[str]:
        """
        return self.get('referenceNumber')

    @property
    def risk(self) -> int:
        """
        The supplier risk score. From 0 to 100.
        :rtype int:
        """
        return self.get('risk')

    @property
    def url(self) -> str:
        """
        The supplier website url.
        :rtype str:
        """
        return self.get('url')

    @property
    def createdDate(self) -> str:
        """
        The creation date.
        :rtype str:
        """
        return self.get('createdDate')

    @property
    def tier(self) -> Optional[SupplierTierDto]:
        """
        The tier that supplier belongs to.
        :rtype Optional[SupplierTierDto]:
        """
        return self._prop_to_dto('tier', SupplierTierDto)

    def __repr__(self):
        return '<SupplierListDto id={}>'.format(self.id)


class EventsSummaryDto(ModelDto):

    @property
    def last7days(self) -> int:
        """
        Number of events in the last 7 days.
        :rtype int:
        """
        return self.get('last7days')

    @property
    def last30days(self) -> int:
        """
        Number of events in the last 30 days.
        :rtype int:
        """
        return self.get('last30days')

    @property
    def overall(self) -> int:
        """
        Number of events overall.
        :rtype int:
        """
        return self.get('overall')

    def __repr__(self):
        return '<EventsSummaryDto>'


class LastEventDto(ModelDto):

    @property
    def id(self) -> str:
        """
        The model identifier.
        :rtype str:
        """
        return self.get('id')

    @property
    def date(self) -> str:
        """
        The event date in ISO8601 format.
        :rtype str:
        """
        return self.get('date')

    @property
    def type(self) -> str:
        """
        The event type.
        :rtype str:
        """
        return self.get('type')

    @property
    def description(self) -> str:
        """
        The event description.
        :rtype str:
        """
        return self.get('description')

    def __repr__(self):
        return '<LastEventDto>'


class SupplierDto(SupplierListDto):

    @property
    def updatedDate(self) -> str:
        """
        The last update date in ISO8601 format.
        :rtype str:
        """
        return self.get('updatedDate')

    @property
    def lastEvent(self) -> Optional[LastEventDto]:
        """
        The last event metadata.
        :rtype Optional[LastEventDto]:
        """
        return self._prop_to_dto('lastEvent', LastEventDto)

    @property
    def events(self) -> Optional[EventsSummaryDto]:
        """
        The counts of supplier events within the given periods.
        :rtype Optional[EventsSummaryDto]:
        """
        return self._prop_to_dto('events', EventsSummaryDto)

    def __repr__(self):
        return '<SupplierDto id={}>'.format(self.id)
