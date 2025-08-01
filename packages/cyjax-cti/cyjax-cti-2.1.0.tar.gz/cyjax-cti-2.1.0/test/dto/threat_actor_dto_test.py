import unittest

from cyjax.resources.threat_actor.dto import ThreatActorDto
from cyjax.resources.model_dto import ModelDto


class TailoredReportDtoDtoTest(unittest.TestCase):

    def test_threat_actor_dto_instance(self):
        dto = ThreatActorDto()

        self.assertIsInstance(dto, dict)
        self.assertIsInstance(dto, ModelDto)

    def test_threat_actor_dto_structure(self):
        obj = {
            'id': '1GoxxHsBJHuZwz72-jG2',
            'name': 'APT-C-37',
            'aliases': [
                'PaiPaiBear'
            ],
            'description': 'APT-C-37 is believed to be an Syrian cyberespionage group.',
            'notes': '',
            'techniques': [
                'Bash History',
                'Command and Scripting Interpreter'
            ],
            'software': [
                'Emotet'
            ],
            'last_update': '2020-10-27T10:54:23+0000'
        }

        dto = ThreatActorDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'name'))
        self.assertTrue(hasattr(dto, 'aliases'))
        self.assertTrue(hasattr(dto, 'description'))
        self.assertTrue(hasattr(dto, 'notes'))
        self.assertTrue(hasattr(dto, 'techniques'))
        self.assertTrue(hasattr(dto, 'software'))
        self.assertTrue(hasattr(dto, 'last_update'))

        self.assertEqual('1GoxxHsBJHuZwz72-jG2', dto.id)
        self.assertEqual('APT-C-37', dto.name)
        self.assertEqual(['PaiPaiBear'], dto.aliases)
        self.assertEqual('APT-C-37 is believed to be an Syrian cyberespionage group.', dto.description)
        self.assertEqual('', dto.notes)
        self.assertEqual(['Bash History', 'Command and Scripting Interpreter'], dto.techniques)
        self.assertEqual(['Emotet'], dto.software)
        self.assertEqual('2020-10-27T10:54:23+0000', dto.last_update)
