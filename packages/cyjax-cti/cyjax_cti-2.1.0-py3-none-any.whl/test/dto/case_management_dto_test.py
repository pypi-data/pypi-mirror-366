import unittest

from cyjax.resources.case_management.dto import CaseActivityDto, CaseDto, CaseListDto, CaseEvidenceDto
from cyjax.resources.model_dto import ModelDto


class DataBreachDtoTest(unittest.TestCase):

    def test_case_management_list_dto_instance(self):
        dto = CaseListDto()
        self.assertIsInstance(dto, ModelDto)

    def test_case_management_dto_instance(self):
        dto = CaseDto()
        self.assertIsInstance(dto, ModelDto)
        self.assertIsInstance(dto, CaseListDto)

    def test_case_activity_dto_instance(self):
        dto = CaseActivityDto()
        self.assertIsInstance(dto, ModelDto)

    def test_case_dto_schema(self):
        obj = {
            'id': 123456,
            'title': 'Example case',
            'referenceNumber': 'ABC-123',
            'status': 'Open',
            'priority': 'Low',
            'isConfidential': True,
            'createdDate': '2022-10-27T11:16:45+0000',
            'updatedDate': '2022-10-27T11:16:45+0000',
            'description': 'Lorem ipsum...',
            'createdBy': 'john-doe@example.com',
            'assignees': [
                'john-doe@example.com',
                'carol-red@example.com'
            ],
            'activitiesUrl': 'https://api.cymon.co/v2/case/1000/activity',
            'evidences': [
                {
                    'author': 'john-doe@example.com',
                    'createdDate': '2022-10-27T11:16:45+0000',
                    'note': 'Lorem ipsum',
                    'files': [
                        {
                            'name': 'Evidence-1.jpg',
                            'url': 'https://api.cymon.co/v2/case/1000/file/2000'
                        }
                    ]
                }
            ],
        }

        dto = CaseDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'title'))
        self.assertTrue(hasattr(dto, 'referenceNumber'))
        self.assertTrue(hasattr(dto, 'status'))
        self.assertTrue(hasattr(dto, 'priority'))
        self.assertTrue(hasattr(dto, 'isConfidential'))
        self.assertTrue(hasattr(dto, 'createdDate'))
        self.assertTrue(hasattr(dto, 'updatedDate'))
        self.assertTrue(hasattr(dto, 'evidences'))
        self.assertTrue(hasattr(dto, 'activitiesUrl'))
        self.assertTrue(hasattr(dto, 'assignees'))
        self.assertTrue(hasattr(dto, 'createdBy'))
        self.assertTrue(hasattr(dto, 'description'))

        self.assertEqual(123456, dto.id)
        self.assertEqual('Example case', dto.title)
        self.assertEqual('ABC-123', dto.referenceNumber)
        self.assertEqual('Open', dto.status)
        self.assertEqual('Low', dto.priority)
        self.assertEqual(True, dto.isConfidential)
        self.assertEqual('2022-10-27T11:16:45+0000', dto.createdDate)
        self.assertEqual('2022-10-27T11:16:45+0000', dto.updatedDate)
        self.assertEqual('john-doe@example.com', dto.createdBy)
        self.assertEqual('Lorem ipsum...', dto.description)
        self.assertEqual('https://api.cymon.co/v2/case/1000/activity', dto.activitiesUrl)

        assignees = dto.assignees
        self.assertIsInstance(assignees, list)
        self.assertEqual([
            'john-doe@example.com',
            'carol-red@example.com'
        ], assignees)

        evidences = dto.evidences
        self.assertIsInstance(evidences, list)
        self.assertIsInstance(evidences[0], CaseEvidenceDto)
        self.assertEqual('john-doe@example.com', evidences[0].author)
        self.assertEqual(
            [
                {
                    'author': 'john-doe@example.com',
                    'createdDate': '2022-10-27T11:16:45+0000',
                    'note': 'Lorem ipsum',
                    'files': [
                        {
                            'name': 'Evidence-1.jpg',
                            'url': 'https://api.cymon.co/v2/case/1000/file/2000'
                        }
                    ]
                }
            ],
            evidences)

    def test_case_list_dto_schema(self):
        obj = {
            'id': 123456,
            'title': 'Example case',
            'referenceNumber': 'ABC-123',
            'status': 'Open',
            'priority': 'Low',
            'isConfidential': True,
            'createdDate': '2022-10-27T11:16:45+0000',
            'updatedDate': '2022-10-27T11:16:45+0000'
        }

        dto = CaseListDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'title'))
        self.assertTrue(hasattr(dto, 'referenceNumber'))
        self.assertTrue(hasattr(dto, 'status'))
        self.assertTrue(hasattr(dto, 'priority'))
        self.assertTrue(hasattr(dto, 'isConfidential'))
        self.assertTrue(hasattr(dto, 'createdDate'))
        self.assertTrue(hasattr(dto, 'updatedDate'))

        self.assertEqual(123456, dto.id)
        self.assertEqual('Example case', dto.title)
        self.assertEqual('ABC-123', dto.referenceNumber)
        self.assertEqual('Open', dto.status)
        self.assertEqual('Low', dto.priority)
        self.assertEqual(True, dto.isConfidential)
        self.assertEqual('2022-10-27T11:16:45+0000', dto.createdDate)
        self.assertEqual('2022-10-27T11:16:45+0000', dto.updatedDate)

    def test_case_activity_dto_schema(self):
        obj = {
            'description': 'Added a new comment',
            'comment': 'Lorem ipsum...',
            'createdBy': 'john-doe@example.com',
            'createdDate': '2022-10-27T11:16:45+0000'
        }

        dto = CaseActivityDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'description'))
        self.assertTrue(hasattr(dto, 'comment'))
        self.assertTrue(hasattr(dto, 'createdBy'))
        self.assertTrue(hasattr(dto, 'createdDate'))

        self.assertEqual('Added a new comment', dto.description)
        self.assertEqual('Lorem ipsum...', dto.comment)
        self.assertEqual('john-doe@example.com', dto.createdBy)
        self.assertEqual('2022-10-27T11:16:45+0000', dto.createdDate)
