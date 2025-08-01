import unittest

from cyjax.resources.tweet.dto import TweetDto
from cyjax.resources.model_dto import ModelDto


class TweetDtoTest(unittest.TestCase):

    def test_tweet_dto_instance(self):
        dto = TweetDto()

        self.assertIsInstance(dto, dict)
        self.assertIsInstance(dto, ModelDto)

    def test_tweet_dto_structure(self):
        obj = {
            'id': '4BU4B3sBOwKq8pfUK62q',
            'tweet_id': '1461348555919028225',
            'tweet': 'Honeywell Experion PKS vulnerabilities – What are they? How do they affect your business?',
            'author': '@Cyjax_Ltd',
            'link': 'https://twitter.com/Cyjax_Ltd/status/1461348555919028225',
            'timestamp': '2021-11-18T15:00:00+01:00'
        }
        dto = TweetDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'tweet_id'))
        self.assertTrue(hasattr(dto, 'tweet'))
        self.assertTrue(hasattr(dto, 'author'))
        self.assertTrue(hasattr(dto, 'link'))
        self.assertTrue(hasattr(dto, 'timestamp'))

        self.assertEqual('4BU4B3sBOwKq8pfUK62q', dto.id)
        self.assertEqual('1461348555919028225', dto.tweet_id)
        self.assertEqual('Honeywell Experion PKS vulnerabilities – What are they? How do they affect your business?',
                         dto.tweet)
        self.assertEqual('https://twitter.com/Cyjax_Ltd/status/1461348555919028225', dto.link)
        self.assertEqual('2021-11-18T15:00:00+01:00', dto.timestamp)
