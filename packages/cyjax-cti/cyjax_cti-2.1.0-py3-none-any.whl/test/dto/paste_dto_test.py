import unittest

from cyjax.resources.paste.dto import PasteDto
from cyjax.resources.model_dto import ModelDto


class PasteDtoTest(unittest.TestCase):

    def test_paste_dto_instance(self):
        dto = PasteDto()

        self.assertIsInstance(dto, dict)
        self.assertIsInstance(dto, ModelDto)

    def test_paste_dto_structure(self):
        obj = {
            "id": "126ec717874595c3bc02e3eac24ceab861013e8b",
            "paste_id": "cRK1nFrw",
            "title": "https://pastebin.com/cRK1nFrw",
            "url": "https://pastebin.com/cRK1nFrw",
            "content": "pi@raspi2:~ $ sudo ./czadsb-install.sh />",
            "discovered_at": "2020-10-28T11:06:58+0000"
        }
        dto = PasteDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'paste_id'))
        self.assertTrue(hasattr(dto, 'title'))
        self.assertTrue(hasattr(dto, 'url'))
        self.assertTrue(hasattr(dto, 'content'))
        self.assertTrue(hasattr(dto, 'discovered_at'))

        self.assertEqual('126ec717874595c3bc02e3eac24ceab861013e8b', dto.id)
        self.assertEqual('cRK1nFrw', dto.paste_id)
        self.assertEqual('https://pastebin.com/cRK1nFrw', dto.title)
        self.assertEqual('https://pastebin.com/cRK1nFrw', dto.url)
        self.assertEqual('pi@raspi2:~ $ sudo ./czadsb-install.sh />', dto.content)
        self.assertEqual('2020-10-28T11:06:58+0000', dto.discovered_at)
