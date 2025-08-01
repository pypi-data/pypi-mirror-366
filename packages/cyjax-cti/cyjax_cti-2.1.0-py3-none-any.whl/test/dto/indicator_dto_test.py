import unittest

from cyjax.resources.indicator_of_compromise.dto import IndicatorDto, EnrichmentDto, AsnDto, GeoIpDto, SightingDto
from cyjax.resources.model_dto import ModelDto


class IndicatorDtoTest(unittest.TestCase):

    def test_dto_instance(self):
        dto = IndicatorDto()

        self.assertIsInstance(dto, dict)
        self.assertIsInstance(dto, ModelDto)

    def test_indicator_dto_structure(self):
        obj = {
            'uuid': 'w86e9b2d-214b-42d0-sd01-c296972d05b4',
            'value': '23873bf2670cf64c2440058130548d4e4da412dd',
            'type': 'FileHash-SHA1',
            'industry_type': [
                'Financial'
            ],
            'handling_condition': 'GREEN',
            'ttp': [
                'Malicious File'
            ],
            'description': 'WellMess malware analysis report',
            'source': 'https://api.cymon.co/v2/report/incident/1000000',
            'discovered_at': '2022-10-13T09:25:36+0000',
        }

        dto = IndicatorDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'uuid'))
        self.assertTrue(hasattr(dto, 'type'))
        self.assertTrue(hasattr(dto, 'industry_type'))
        self.assertTrue(hasattr(dto, 'handling_condition'))
        self.assertTrue(hasattr(dto, 'ttp'))
        self.assertTrue(hasattr(dto, 'value'))
        self.assertTrue(hasattr(dto, 'description'))
        self.assertTrue(hasattr(dto, 'source'))
        self.assertTrue(hasattr(dto, 'discovered_at'))
        self.assertTrue(hasattr(dto, 'get_incident_report'))

        self.assertEqual('w86e9b2d-214b-42d0-sd01-c296972d05b4', dto.uuid)
        self.assertEqual('FileHash-SHA1', dto.type)
        self.assertEqual(['Financial'], dto.industry_type)
        self.assertEqual('GREEN', dto.handling_condition)
        self.assertEqual('WellMess malware analysis report', dto.description)
        self.assertEqual('https://api.cymon.co/v2/report/incident/1000000', dto.source)
        self.assertEqual('2022-10-13T09:25:36+0000', dto.discovered_at)
        self.assertEqual(['Malicious File'], dto.ttp)
        self.assertEqual('23873bf2670cf64c2440058130548d4e4da412dd', dto.value)

    def test_enrichment_dto_structure(self):
        obj = {
            "type": "IPv4",
            "last_seen_timestamp": "2022-10-13T04:32:16Z",
            "geoip": {
                "ip_address": "185.129.62.62",
                "city": "Buenos Aires",
                "country_name": "Argentina",
                "country_code": "AR"
            },
            "asn": {
                "organization": "Telecom Argentina S.A",
                "number": "10318"
            },
            "sightings": [
                {
                    "count": 421,
                    "last_seen_timestamp": "2022-10-13T04:32:16Z",
                    "description": "Blacklisted IP",
                    "source": "Talos (Cisco)"
                },
                {
                    "count": 1,
                    "last_seen_timestamp": "2022-10-15T10:52:00Z",
                    "description": "Ransom Cartel ransomware possibly connected with REvil",
                    "source": "Cyjax"
                },
                {
                    "count": 4,
                    "last_seen_timestamp": "2020-08-28T18:08:00Z",
                    "description": "STIX package",
                    "source": "DHS AIS"
                }
            ]
        }

        dto = EnrichmentDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'type'))
        self.assertTrue(hasattr(dto, 'last_seen_timestamp'))
        self.assertTrue(hasattr(dto, 'geoip'))
        self.assertTrue(hasattr(dto, 'asn'))
        self.assertTrue(hasattr(dto, 'sightings'))

        self.assertEqual('IPv4', dto.type)
        self.assertEqual('2022-10-13T04:32:16Z', dto.last_seen_timestamp)

        geoip = dto.geoip
        self.assertIsInstance(geoip, GeoIpDto)
        self.assertEqual('AR', geoip.country_code)
        self.assertEqual('Argentina', geoip.country_name)
        self.assertEqual('185.129.62.62', geoip.ip_address)
        self.assertEqual('Buenos Aires', geoip.city)

        asn = dto.asn
        self.assertIsInstance(asn, AsnDto)
        self.assertEqual('10318', asn.number)
        self.assertEqual('Telecom Argentina S.A', asn.organization)

        sightings = dto.sightings
        self.assertIsInstance(sightings, list)
        self.assertEqual(3, len(sightings))
        self.assertIsInstance(sightings[0], SightingDto)
        self.assertIsInstance(sightings[1], SightingDto)
        self.assertIsInstance(sightings[2], SightingDto)

        self.assertEqual(421, sightings[0].count)
        self.assertEqual('Talos (Cisco)', sightings[0].source)
        self.assertEqual('Blacklisted IP', sightings[0].description)
        self.assertEqual('2022-10-13T04:32:16Z', sightings[0].last_seen_timestamp)

    def test_enrichment_dto_structure_without_data(self):
        obj = {
            "type": "IPv4",
            "last_seen_timestamp": "2022-10-13T04:32:16Z",
            "sightings": [
                {
                    "count": 421,
                    "last_seen_timestamp": "2022-10-13T04:32:16Z",
                    "description": "Blacklisted IP",
                    "source": "Talos (Cisco)"
                }
            ]
        }

        dto = EnrichmentDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'type'))
        self.assertTrue(hasattr(dto, 'last_seen_timestamp'))
        self.assertTrue(hasattr(dto, 'geoip'))
        self.assertTrue(hasattr(dto, 'asn'))
        self.assertTrue(hasattr(dto, 'sightings'))
        self.assertEqual('IPv4', dto.type)
        self.assertEqual('2022-10-13T04:32:16Z', dto.last_seen_timestamp)
        self.assertIsNone(dto.geoip)
        self.assertIsNone(dto.asn)

        sightings = dto.sightings
        self.assertIsInstance(sightings, list)
        self.assertEqual(1, len(sightings))
        self.assertIsInstance(sightings[0], SightingDto)
