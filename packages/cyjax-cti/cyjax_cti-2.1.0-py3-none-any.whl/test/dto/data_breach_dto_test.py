import unittest

from cyjax.resources.data_breach.dto import DataBreachDto, DataBreachListDto, DataBreachMetadataDto, \
    IncidentReportMetadataDto, LeakedEmailDto, InvestigatorLeakedEmailDto
from cyjax.resources.model_dto import ModelDto


class DataBreachDtoTest(unittest.TestCase):

    def test_data_breach_dto_instance(self):
        dto = DataBreachDto()
        self.assertIsInstance(dto, ModelDto)

    def test_data_breach_list_dto_instance(self):
        dto = DataBreachListDto()
        self.assertIsInstance(dto, ModelDto)

    def test_incident_report_metadata_dto_instance(self):
        dto = IncidentReportMetadataDto()
        self.assertIsInstance(dto, ModelDto)

    def test_data_breach_metadata_dto_instance(self):
        dto = DataBreachMetadataDto()
        self.assertIsInstance(dto, ModelDto)

    def test_leaked_email_dto_instance(self):
        dto = LeakedEmailDto()
        self.assertIsInstance(dto, ModelDto)

    def test_investigator_leaked_email_dto_instance(self):
        dto = InvestigatorLeakedEmailDto()
        self.assertIsInstance(dto, ModelDto)

    def test_data_breach_dto_instance_schema(self):
        mocked_entry = {"id": 885,
                        "name": "Test-ABC123",
                        "content": "new content 4",
                        "incident_report": {
                            "id": 65303,
                            "title": "Report A1",
                            "url": "https://test.cyjax.com/api/cyjax/v2/report/incident/65303"
                        },
                        "data_classes": [
                            "Full names",
                            "IP addresses",
                            "Addresses"
                        ],
                        "discovered_at": "2023-03-17T11:37:52+0000"
                        }

        dto = DataBreachDto(**mocked_entry)

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'name'))
        self.assertTrue(hasattr(dto, 'content'))
        self.assertTrue(hasattr(dto, 'incident_report'))
        self.assertTrue(hasattr(dto, 'data_classes'))
        self.assertTrue(hasattr(dto, 'discovered_at'))

        self.assertEqual(885, dto.id)
        self.assertEqual('Test-ABC123', dto.name)
        self.assertEqual('new content 4', dto['content'])
        self.assertEqual(["Full names", "IP addresses", "Addresses"], dto.data_classes)
        self.assertEqual('2023-03-17T11:37:52+0000', dto['discovered_at'])
        self.assertEqual({"id": 65303,
                          "title": "Report A1",
                          "url": "https://test.cyjax.com/api/cyjax/v2/report/incident/65303"
                          }, dto.incident_report)
        ir_metadata = dto.incident_report
        self.assertIsInstance(ir_metadata, IncidentReportMetadataDto)
        self.assertEqual(65303, dto.incident_report.id)
        self.assertEqual('Report A1', dto.incident_report.get('title'))
        self.assertEqual('https://test.cyjax.com/api/cyjax/v2/report/incident/65303', dto.incident_report.url)

    def test_data_breach_list_dto_instance_schema(self):
        mocked_entry = {"id": 885,
                        "name": "Test-ABC123",
                        "data_classes": [
                            "Full names",
                            "IP addresses",
                            "Addresses"
                        ],
                        "discovered_at": "2023-03-17T11:37:52+0000"
                        }

        dto = DataBreachListDto(**mocked_entry)

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'name'))
        self.assertFalse(hasattr(dto, 'content'))
        self.assertFalse(hasattr(dto, 'incident_report'))
        self.assertTrue(hasattr(dto, 'data_classes'))
        self.assertTrue(hasattr(dto, 'discovered_at'))

        self.assertEqual(885, dto.id)
        self.assertEqual('Test-ABC123', dto.name)
        self.assertEqual(["Full names", "IP addresses", "Addresses"], dto.data_classes)
        self.assertEqual('2023-03-17T11:37:52+0000', dto.get('discovered_at'))

    def test_data_breach_metadata_schema(self):
        obj = {
            'id': 100,
            'name': 'Hello world',
            'url': 'https://test.cyjax.com/api/cyjax/v2/data-leak/breach/100'
        }
        dto = DataBreachMetadataDto(**obj)

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'name'))
        self.assertTrue(hasattr(dto, 'url'))

        self.assertEqual(100, dto.id)
        self.assertEqual('Hello world', dto.name)
        self.assertEqual('https://test.cyjax.com/api/cyjax/v2/data-leak/breach/100', dto['url'])

    def test_leaked_email_schema(self):
        obj = {
            'id': 'QEWtqoUB_vzuzQ6c3oBr',
            'email': 'john-doe@example.com',
            'source': 'Example Leak',
            'data_breach': {
                'id': 100,
                'name': 'Hello world',
                'url': 'https://test.cyjax.com/api/cyjax/v2/data-leak/breach/100'
            },
            'data_classes': [
                'Email addresses'
            ],
            'discovered_at': '2023-03-17T11:37:52+0000'
        }
        dto = LeakedEmailDto(**obj)

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'email'))
        self.assertTrue(hasattr(dto, 'source'))
        self.assertTrue(hasattr(dto, 'data_breach'))
        self.assertTrue(hasattr(dto, 'data_classes'))
        self.assertTrue(hasattr(dto, 'discovered_at'))

        self.assertEqual('QEWtqoUB_vzuzQ6c3oBr', dto.id)
        self.assertEqual('john-doe@example.com', dto.email)
        self.assertEqual('Example Leak', dto.source)
        self.assertEqual('2023-03-17T11:37:52+0000', dto.discovered_at)
        self.assertEqual(['Email addresses'], dto.data_classes)
        self.assertIsInstance(dto.data_breach, DataBreachMetadataDto)
        self.assertEqual(100, dto.data_breach.id)
        self.assertEqual('Hello world', dto.data_breach.name)
        self.assertEqual('https://test.cyjax.com/api/cyjax/v2/data-leak/breach/100', dto['data_breach']['url'])

    def test_investigator_leaked_email_schema(self):
        obj = {
            'email': 'john-doe@example.com',
            'domain': 'example.com',
            'full_name': 'John Doe',
            'country': 'Spain',
            'phone_number': '123456789',
            'data_breach': {
                'id': 100,
                'name': 'Hello world',
                'url': 'https://test.cyjax.com/api/cyjax/v2/data-leak/breach/100'
            },
            'discovered_at': '2023-03-17T11:37:52+0000'
        }
        dto = InvestigatorLeakedEmailDto(**obj)

        self.assertFalse(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'email'))
        self.assertTrue(hasattr(dto, 'data_breach'))
        self.assertTrue(hasattr(dto, 'discovered_at'))
        self.assertFalse(hasattr(dto, 'data_classes'))
        self.assertTrue(hasattr(dto, 'domain'))
        self.assertTrue(hasattr(dto, 'full_name'))
        self.assertTrue(hasattr(dto, 'username'))
        self.assertTrue(hasattr(dto, 'password'))
        self.assertTrue(hasattr(dto, 'address'))
        self.assertTrue(hasattr(dto, 'country'))
        self.assertTrue(hasattr(dto, 'ip_address'))
        self.assertTrue(hasattr(dto, 'date_of_birth'))
        self.assertTrue(hasattr(dto, 'gender'))
        self.assertTrue(hasattr(dto, 'phone_number'))

        self.assertEqual('john-doe@example.com', dto.email)
        self.assertEqual('example.com', dto.domain)
        self.assertEqual('2023-03-17T11:37:52+0000', dto.discovered_at)
        self.assertEqual('Spain', dto.country)
        self.assertEqual('John Doe', dto.full_name)
        self.assertEqual('123456789', dto.phone_number)
        self.assertIsNone(dto.username)
        self.assertIsNone(dto.password)
        self.assertIsNone(dto.address)
        self.assertIsNone(dto.ip_address)
        self.assertIsNone(dto.date_of_birth)
        self.assertIsNone(dto.gender)
        self.assertIsInstance(dto.data_breach, DataBreachMetadataDto)
        self.assertEqual(100, dto.data_breach.id)
        self.assertEqual('Hello world', dto.data_breach.name)
        self.assertEqual('https://test.cyjax.com/api/cyjax/v2/data-leak/breach/100', dto['data_breach']['url'])
