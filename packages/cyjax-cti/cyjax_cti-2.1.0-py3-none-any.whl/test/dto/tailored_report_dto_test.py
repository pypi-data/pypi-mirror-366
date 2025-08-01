import unittest

from cyjax.resources.tailored_report.dto import TailoredReportDto
from cyjax.resources.model_dto import ModelDto


class TailoredReportDtoDtoTest(unittest.TestCase):

    def test_tailored_report_dto_instance(self):
        dto = TailoredReportDto()

        self.assertIsInstance(dto, dict)
        self.assertIsInstance(dto, ModelDto)

    def test_tailored_report_dto_structure(self):
        obj = {
            "id": 123456,
            "title": "Example my report title",
            "content": "<p>Lorem ipsum dolor sit amet, constur lus pretium. Mattis pellentesque id nibh...</p>",
            "severity": "low",
            "source_evaluation": "mostly-reliable",
            "impact": "some-impact",
            "last_update": "2020-10-27T10:54:23+0000"
        }

        dto = TailoredReportDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'title'))
        self.assertTrue(hasattr(dto, 'content'))
        self.assertTrue(hasattr(dto, 'severity'))
        self.assertTrue(hasattr(dto, 'source_evaluation'))
        self.assertTrue(hasattr(dto, 'impact'))
        self.assertTrue(hasattr(dto, 'last_update'))

        self.assertEqual(123456, dto.id)
        self.assertEqual('Example my report title', dto.title)
        self.assertEqual('low', dto.severity)
        self.assertEqual('mostly-reliable', dto.source_evaluation)
        self.assertEqual('some-impact', dto.impact)
        self.assertEqual('2020-10-27T10:54:23+0000', dto.last_update)
        self.assertEqual('<p>Lorem ipsum dolor sit amet, constur lus pretium. Mattis pellentesque id nibh...</p>',
                         dto.content)
