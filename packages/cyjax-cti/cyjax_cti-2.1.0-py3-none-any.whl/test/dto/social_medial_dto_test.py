import unittest

from cyjax.resources.social_media import SocialMediaDto
from cyjax.resources.model_dto import ModelDto


class SocialMediaDtoTest(unittest.TestCase):

    def test_dto_instance(self):
        dto = SocialMediaDto()

        self.assertIsInstance(dto, dict)
        self.assertIsInstance(dto, ModelDto)

    def test_dto_schema(self):
        obj = {
            "id": "KhcL2YkBosMNOyi6NkjP",
            "source": "instagram",
            "username": "@Taylor_42341",
            "content": "<p>Lorem ipsum...</p>",
            "priority": "high",
            "tags": [
                "BANK",
                "fraud",
                "UK",
                "Europe",
            ],
            "source_timestamp": "2023-08-09T06:44:42+0000",
            "timestamp": "2023-08-09T06:44:42+0000",
            "image": "https://api.cymon.co/v2/social-media/KhcL2YkBosMNOyi6NkjP/image"
        }

        dto = SocialMediaDto(**obj)

        self.assertEqual('KhcL2YkBosMNOyi6NkjP', dto.id)
        self.assertEqual('instagram', dto.get('source'))
        self.assertEqual('@Taylor_42341', dto['username'])
        self.assertEqual('<p>Lorem ipsum...</p>', dto.content)
        self.assertEqual('high', dto.priority)
        self.assertEqual([
                "BANK",
                "fraud",
                "UK",
                "Europe",
            ], dto.tags)
        self.assertEqual('2023-08-09T06:44:42+0000', dto.source_timestamp)
        self.assertEqual('2023-08-09T06:44:42+0000', dto.timestamp)
        self.assertEqual('https://api.cymon.co/v2/social-media/KhcL2YkBosMNOyi6NkjP/image', dto.image)
        self.assertEqual(obj, dict(dto))
