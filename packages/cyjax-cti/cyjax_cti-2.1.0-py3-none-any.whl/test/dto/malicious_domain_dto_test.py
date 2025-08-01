import unittest

from cyjax.resources.malicious_domain.dto import MaliciousDomainDto
from cyjax.resources.model_dto import ModelDto


class MaliciousDomainDtoTest(unittest.TestCase):

    def test_dto_instance(self):
        dto = MaliciousDomainDto()

        self.assertIsInstance(dto, dict)
        self.assertIsInstance(dto, ModelDto)

    def test_malicious_domain_dto_structure(self):
        obj = {
            "domains": [
                "autodiscover.coronavirusepicenter.com",
                "coronavirusepicenter.com",
                "cpanel.coronavirusepicenter.com",
                "cpcalendars.coronavirusepicenter.com",
                "cpcontacts.coronavirusepicenter.com",
                "mail.coronavirusepicenter.com",
                "webdisk.coronavirusepicenter.com",
                "webmail.coronavirusepicenter.com",
                "www.coronavirusepicenter.com"
            ],
            "matched_domains": [
                "autodiscover.coronavirusepicenter.com"
            ],
            "unmatched_domains": [
                "mail.coronavirusepicenter.com"
            ],
            "keyword": [
                "covid"
            ],
            "type": "ssl-certificate",
            "discovery_date": "2020-10-25T10:31:45+0100",
            "create_date": "",
            "expiration_timestamp": "2021-10-25T10:31:45+0100",
            "source": "Let's Encrypt 'Sapling 2023h1' log"
        }

        dto = MaliciousDomainDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'domains'))
        self.assertTrue(hasattr(dto, 'matched_domains'))
        self.assertTrue(hasattr(dto, 'unmatched_domains'))
        self.assertTrue(hasattr(dto, 'keyword'))
        self.assertTrue(hasattr(dto, 'type'))
        self.assertTrue(hasattr(dto, 'discovery_date'))
        self.assertTrue(hasattr(dto, 'create_date'))
        self.assertTrue(hasattr(dto, 'expiration_timestamp'))
        self.assertTrue(hasattr(dto, 'source'))

        self.assertEqual('ssl-certificate', dto.type)
        self.assertEqual('2020-10-25T10:31:45+0100', dto.discovery_date)
        self.assertEqual('', dto.create_date)
        self.assertEqual('2021-10-25T10:31:45+0100', dto.expiration_timestamp)
        self.assertEqual("Let's Encrypt 'Sapling 2023h1' log", dto.source)
        self.assertEqual(['covid'], dto.keyword)
        self.assertEqual(['mail.coronavirusepicenter.com'], dto.unmatched_domains)
        self.assertEqual(['autodiscover.coronavirusepicenter.com'], dto.matched_domains)
        self.assertEqual([
            "autodiscover.coronavirusepicenter.com",
            "coronavirusepicenter.com",
            "cpanel.coronavirusepicenter.com",
            "cpcalendars.coronavirusepicenter.com",
            "cpcontacts.coronavirusepicenter.com",
            "mail.coronavirusepicenter.com",
            "webdisk.coronavirusepicenter.com",
            "webmail.coronavirusepicenter.com",
            "www.coronavirusepicenter.com"
        ], dto.domains)
