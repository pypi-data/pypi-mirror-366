import unittest

from cyjax.resources.third_party_risk.dto import TierDto, SupplierDto, SupplierListDto
from cyjax.resources.model_dto import ModelDto


class ThirdPartyRiskDtoTest(unittest.TestCase):

    def test_tier_dto_instance(self):
        dto = TierDto()

        self.assertIsInstance(dto, dict)
        self.assertIsInstance(dto, ModelDto)

    def test_supplier_list_dto_instance(self):
        dto = SupplierListDto()

        self.assertIsInstance(dto, dict)
        self.assertIsInstance(dto, ModelDto)

    def test_supplier_dto_instance(self):
        dto = SupplierDto()

        self.assertIsInstance(dto, dict)
        self.assertIsInstance(dto, ModelDto)

    def test_tier_dto_schema(self):
        obj = {
            'id': 1,
            'name': 'Tier 1',
            'description': 'High level suppliers',
            'suppliers': 123
        }
        dto = TierDto(**obj)

        self.assertEqual(obj, dict(obj))

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'name'))
        self.assertTrue(hasattr(dto, 'description'))
        self.assertTrue(hasattr(dto, 'suppliers'))

        self.assertEqual(1, dto.id)
        self.assertEqual('Tier 1', dto.name)
        self.assertEqual('High level suppliers', dto.description)
        self.assertEqual(123, dto.suppliers)

    def test_supplier_list_dto_schema(self):
        obj = {
            'id': 1,
            'name': 'RedCompany',
            'referenceNumber': 'ABC-123',
            'risk': 50,
            'url': 'https://example.com',
            'tier': {
                'id': 2,
                'name': 'Tier A'
            },
            'createdDate': '2020-10-28T11:06:58+0000'
        }
        dto = SupplierListDto(**obj)

        self.assertEqual(obj, dict(obj))

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'name'))
        self.assertTrue(hasattr(dto, 'referenceNumber'))
        self.assertTrue(hasattr(dto, 'risk'))
        self.assertTrue(hasattr(dto, 'tier'))
        self.assertTrue(hasattr(dto, 'createdDate'))

        self.assertEqual(1, dto.id)
        self.assertEqual('RedCompany', dto.name)
        self.assertEqual('ABC-123', dto.referenceNumber)
        self.assertEqual('https://example.com', dto.url)
        self.assertEqual('2020-10-28T11:06:58+0000', dto.createdDate)
        self.assertEqual({
                'id': 2,
                'name': 'Tier A'
            }, dto.tier)
        self.assertEqual(2, dto.tier.id)
        self.assertEqual('Tier A', dto.tier.name)

    def test_supplier_dto_without_events_schema(self):
        obj = {
            'id': 1,
            'name': 'RedCompany',
            'risk': 50,
            'url': 'https://example.com',
            'tier': {
                'id': 2,
                'name': 'Tier A'
            },
            'createdDate': '2020-10-28T11:06:58+0000',
            'updatedDate': '2020-10-29T13:16:12+0000',
            'events': {
                'last7days': 0,
                'last30days': 0,
                'overall': 0
            },
            'lastEvent': None
        }
        dto = SupplierDto(**obj)

        self.assertEqual(obj, dict(obj))

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'name'))
        self.assertTrue(hasattr(dto, 'referenceNumber'))
        self.assertTrue(hasattr(dto, 'risk'))
        self.assertTrue(hasattr(dto, 'tier'))
        self.assertTrue(hasattr(dto, 'createdDate'))
        self.assertTrue(hasattr(dto, 'updatedDate'))
        self.assertTrue(hasattr(dto, 'events'))
        self.assertTrue(hasattr(dto, 'lastEvent'))

        self.assertEqual(1, dto.id)
        self.assertEqual('RedCompany', dto.name)
        self.assertEqual(None, dto.referenceNumber)
        self.assertEqual('https://example.com', dto.url)
        self.assertEqual('2020-10-28T11:06:58+0000', dto.createdDate)
        self.assertEqual('2020-10-29T13:16:12+0000', dto.updatedDate)
        self.assertEqual({
                'id': 2,
                'name': 'Tier A'
            }, dto.tier)
        self.assertEqual(2, dto.tier.id)
        self.assertEqual('Tier A', dto.tier.name)
        self.assertEqual(None, dto.lastEvent)
        self.assertEqual(0, dto.events.last7days)
        self.assertEqual(0, dto.events.last30days)
        self.assertEqual(0, dto.events.overall)
        self.assertEqual({
                'last7days': 0,
                'last30days': 0,
                'overall': 0
            }, dto.events)

    def test_supplier_dto_with_events_schema(self):
        obj = {
            'id': 1,
            'name': 'RedCompany',
            'risk': 50,
            'url': 'https://example.com',
            'tier': {
                'id': 2,
                'name': 'Tier A'
            },
            'createdDate': '2020-10-28T11:06:58+0000',
            'updatedDate': '2020-10-29T13:16:12+0000',
            'events': {
                'last7days': 2,
                'last30days': 6,
                'overall': 120
            },
            'lastEvent': {
                'id': 'aba57eb1-3efe-4867-a0b4-c8d52232ce3d',
                'date': '2020-12-13T10:10:00+0000',
                'type': 'Data breach',
                'description': 'Email addresses found in the data breach Foobar.'
            }
        }
        dto = SupplierDto(**obj)

        self.assertEqual(obj, dict(obj))

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'name'))
        self.assertTrue(hasattr(dto, 'referenceNumber'))
        self.assertTrue(hasattr(dto, 'risk'))
        self.assertTrue(hasattr(dto, 'tier'))
        self.assertTrue(hasattr(dto, 'createdDate'))
        self.assertTrue(hasattr(dto, 'updatedDate'))
        self.assertTrue(hasattr(dto, 'events'))
        self.assertTrue(hasattr(dto, 'lastEvent'))

        self.assertEqual(1, dto.id)
        self.assertEqual('RedCompany', dto.name)
        self.assertEqual(None, dto.referenceNumber)
        self.assertEqual('https://example.com', dto.url)
        self.assertEqual('2020-10-28T11:06:58+0000', dto.createdDate)
        self.assertEqual('2020-10-29T13:16:12+0000', dto.updatedDate)
        self.assertEqual({
                'id': 2,
                'name': 'Tier A'
            }, dto.tier)
        self.assertEqual(2, dto.tier.id)
        self.assertEqual('Tier A', dto.tier.name)
        self.assertEqual({
            'id': 'aba57eb1-3efe-4867-a0b4-c8d52232ce3d',
            'date': '2020-12-13T10:10:00+0000',
            'type': 'Data breach',
            'description': 'Email addresses found in the data breach Foobar.'
        }, dto.lastEvent)
        self.assertEqual('aba57eb1-3efe-4867-a0b4-c8d52232ce3d', dto.lastEvent.id)
        self.assertEqual(2, dto.events.last7days)
        self.assertEqual(6, dto.events.last30days)
        self.assertEqual(120, dto.events.overall)
        self.assertEqual({
                'last7days': 2,
                'last30days': 6,
                'overall': 120
            }, dto.events)
