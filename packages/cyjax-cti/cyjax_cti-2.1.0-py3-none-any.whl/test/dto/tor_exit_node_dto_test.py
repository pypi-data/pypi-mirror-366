import unittest

from cyjax.resources.tor_exit_node.dto import TorExitNodeDto
from cyjax.resources.model_dto import ModelDto


class TailoredReportDtoDtoTest(unittest.TestCase):

    def test_tor_exit_node_dto_instance(self):
        dto = TorExitNodeDto()

        self.assertIsInstance(dto, dict)
        self.assertIsInstance(dto, ModelDto)

    def test_tor_exit_node_dto_schema(self):
        obj = {
            'id': '915ff901bd4f9310c8055ec157ac6d6fba52a5855ead80c966bdcaab0c298ea0',
            'ip': '97.103.2.110',
            'discovered_at': '2020-10-28T11:01:01+0000'
        }
        dto = TorExitNodeDto(**obj)

        self.assertIsInstance(dto, dict)
        self.assertIsInstance(dto, ModelDto)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'ip'))
        self.assertTrue(hasattr(dto, 'discovered_at'))

        self.assertEqual('915ff901bd4f9310c8055ec157ac6d6fba52a5855ead80c966bdcaab0c298ea0', dto.id)
        self.assertEqual('97.103.2.110', dto.ip)
        self.assertEqual('2020-10-28T11:01:01+0000', dto.discovered_at)
