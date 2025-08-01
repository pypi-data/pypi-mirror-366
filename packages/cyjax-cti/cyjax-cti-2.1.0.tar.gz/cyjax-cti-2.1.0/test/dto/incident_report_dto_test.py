import unittest

from cyjax.resources.incident_report.dto import IncidentReportDto, ReportIndicatorDto
from cyjax.resources.model_dto import ModelDto


class IncidentReportDtoTest(unittest.TestCase):

    def test_report_dto_instance(self):
        dto = IncidentReportDto()

        self.assertIsInstance(dto, dict)
        self.assertIsInstance(dto, ModelDto)

    def test_report_indicator_dto_instance(self):
        dto = ReportIndicatorDto()

        self.assertIsInstance(dto, dict)
        self.assertIsInstance(dto, ModelDto)

    def test_report_indicator_dto(self):
        obj = {
            'uuid': 'w86e9b2d-214b-42d0-sd01-c296972d05b4',
            'type': 'file',
            'industry_type': [
                'Unknown'
            ],
            'handling_condition': 'GREEN',
            'ttp': [
                'IcedID'
            ],
            'value': {
                'hashes': {
                    'MD5': '253e2e994b93805qdefea9e128e7ca3i'
                }
            },
            'description': 'IcedID samples',
            'source': 'https://api.cymon.co/v2/report/incident/1000000',
            'discovered_at': '2022-10-13T09:25:36+0000',
        }

        dto = ReportIndicatorDto(**obj)

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

        self.assertEqual('w86e9b2d-214b-42d0-sd01-c296972d05b4', dto.uuid)
        self.assertEqual('file', dto.type)
        self.assertEqual(['Unknown'], dto.industry_type)
        self.assertEqual('GREEN', dto.handling_condition)
        self.assertEqual('IcedID samples', dto.description)
        self.assertEqual('https://api.cymon.co/v2/report/incident/1000000', dto.source)
        self.assertEqual('2022-10-13T09:25:36+0000', dto.discovered_at)
        self.assertEqual(['IcedID'], dto.ttp)
        self.assertEqual({
                'hashes': {
                    'MD5': '253e2e994b93805qdefea9e128e7ca3i'
                }
            }, dto.value)

    def test_report_dto(self):
        obj = {
            'id': 69077,
            'title': 'WellMess malware analysis report',
            'source': 'https://example.com',
            'content': 'Lorem ipsum...',
            'severity': 'high',
            'source_evaluation': 'always-reliable',
            'impacts': {
                'government': 'some-impact',
                'infrastructure': 'some-impact',
                'healthcare': 'some-impact',
                'pharmaceutical': 'some-impact',
                'it': 'some-impact',
                'politics': 'some-impact',
                'media': 'some-impact',
                'others': 'minimal-impact',
                'ngo': 'some-impact',
                'education': 'some-impact'
            },
            'tags': [
                '@APT29',
                'Americas',
                'GOST',
                'Go Simple Tunnel',
                'GitHub'
            ],
            'countries': [
                'United Kingdom',
                'Russian Federation',
                'United States',
                'Canada'
            ],
            'techniques': [
                'Malicious File',
                'Process Injection'
            ],
            'technique_ids': [
                'T1003.008',
                'T1540'
            ],
            'software': [
                'Agent.btz'
            ],
            'software_ids': [
                'S0154'
            ],
            'ioc': [
                {
                    'uuid': 'w86e9b2d-214b-42d0-sd01-c296972d05b4',
                    'type': 'file',
                    'industry_type': [
                        'Unknown'
                    ],
                    'handling_condition': 'GREEN',
                    'ttp': [
                        'IcedID'
                    ],
                    'value': {
                        'hashes': {
                            'MD5': '253e2e994b93805qdefea9e128e7ca3i'
                        }
                    },
                    'description': 'IcedID samples',
                    'source': 'https://api.cymon.co/v2/report/incident/1000000',
                    'discovered_at': '2022-10-13T09:25:36+0000',
                }
            ],
            'ioc_count': 1,
            'last_update': '2020-10-27T10:57:52+0000'
        }

        dto = IncidentReportDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'title'))
        self.assertTrue(hasattr(dto, 'source'))
        self.assertTrue(hasattr(dto, 'content'))
        self.assertTrue(hasattr(dto, 'severity'))
        self.assertTrue(hasattr(dto, 'source_evaluation'))
        self.assertTrue(hasattr(dto, 'impacts'))
        self.assertTrue(hasattr(dto, 'tags'))
        self.assertTrue(hasattr(dto, 'countries'))
        self.assertTrue(hasattr(dto, 'techniques'))
        self.assertTrue(hasattr(dto, 'technique_ids'))
        self.assertTrue(hasattr(dto, 'software'))
        self.assertTrue(hasattr(dto, 'software_ids'))
        self.assertTrue(hasattr(dto, 'ioc'))
        self.assertTrue(hasattr(dto, 'ioc_count'))
        self.assertTrue(hasattr(dto, 'last_update'))

        self.assertEqual(69077, dto.id)
        self.assertEqual('WellMess malware analysis report', dto.title)
        self.assertEqual('https://example.com', dto.source)
        self.assertEqual('Lorem ipsum...', dto.content)
        self.assertEqual('high', dto.severity)
        self.assertEqual('always-reliable', dto.source_evaluation)
        self.assertEqual({'government': 'some-impact',
                          'infrastructure': 'some-impact',
                          'healthcare': 'some-impact',
                          'pharmaceutical': 'some-impact',
                          'it': 'some-impact',
                          'politics': 'some-impact',
                          'media': 'some-impact',
                          'others': 'minimal-impact',
                          'ngo': 'some-impact',
                          'education': 'some-impact'}, dto.impacts)
        self.assertEqual([
            '@APT29',
            'Americas',
            'GOST',
            'Go Simple Tunnel',
            'GitHub'
        ], dto.tags)
        self.assertEqual([
            'United Kingdom',
            'Russian Federation',
            'United States',
            'Canada'
        ], dto.countries)
        self.assertEqual(['Malicious File', 'Process Injection'], dto.techniques)
        self.assertEqual(['T1003.008', 'T1540'], dto.technique_ids)
        self.assertEqual(['Agent.btz'], dto.software)
        self.assertEqual(['S0154'], dto.software_ids)
        self.assertEqual(1, dto.ioc_count)
        self.assertEqual('2020-10-27T10:57:52+0000', dto.last_update)

        iocs = dto.ioc
        self.assertIsInstance(iocs, list)
        self.assertEqual(1, len(iocs))
        self.assertIsInstance(iocs[0], ReportIndicatorDto)
