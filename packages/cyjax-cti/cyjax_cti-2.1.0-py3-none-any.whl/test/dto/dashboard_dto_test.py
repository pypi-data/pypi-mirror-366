import unittest

from cyjax.resources.dashboard.dto import CounterWidgetDto, DashboardDto, TableWidgetDto, MapWidgetDto, \
    MitreWidgetDto, MetricWidgetDto, WidgetDto, MitreTacticDto, MitreTechniqueDto, MapDataPointDto, MetricSeriesDto, \
    MetricPointDto

from cyjax.resources.model_dto import ModelDto


class DashboardDtoTest(unittest.TestCase):

    def test_dashboard_dto_instance(self):
        dto = DashboardDto()
        self.assertIsInstance(dto, ModelDto)

    def test_widget_dto_instance(self):
        dto = WidgetDto()
        self.assertIsInstance(dto, ModelDto)

    def test_counter_dto_instance(self):
        dto = CounterWidgetDto()
        self.assertIsInstance(dto, ModelDto)

    def test_table_dto_instance(self):
        dto = TableWidgetDto()
        self.assertIsInstance(dto, ModelDto)

    def test_map_dto_instance(self):
        dto = MapWidgetDto()
        self.assertIsInstance(dto, ModelDto)

    def test_mitre_dto_instance(self):
        dto = MitreWidgetDto()
        self.assertIsInstance(dto, ModelDto)

    def test_metric_dto_instance(self):
        dto = MetricWidgetDto()
        self.assertIsInstance(dto, ModelDto)

    def test_dashboard_dto_schema(self):
        obj = {
            'id': 1,
            'name': 'Ransomware victims',
            'description': 'Lorem ipsum',
            'type': 'personal'
        }

        dto = DashboardDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'name'))
        self.assertTrue(hasattr(dto, 'description'))
        self.assertTrue(hasattr(dto, 'type'))

        self.assertEqual(1, dto.id)
        self.assertEqual('Ransomware victims', dto.get('name'))
        self.assertEqual('Lorem ipsum', dto.description)
        self.assertEqual('personal', dto.type)

    def test_widget_dto_schema(self):
        obj = {
            'id': 1,
            'title': 'Example Widget',
            'url': 'https://api.cymon.co/v2/dashboard/widget/metric/789',
            'type': 'data'
        }

        dto = WidgetDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'id'))
        self.assertTrue(hasattr(dto, 'title'))
        self.assertTrue(hasattr(dto, 'url'))
        self.assertTrue(hasattr(dto, 'type'))

        self.assertEqual(1, dto.id)
        self.assertEqual('Example Widget', dto.get('title'))
        self.assertEqual('https://api.cymon.co/v2/dashboard/widget/metric/789', dto.url)
        self.assertEqual('data', dto.type)

    def test_counter_dto_schema(self):
        obj = {
            'title': 'Example Widget',
            'count': 423
        }

        dto = CounterWidgetDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'title'))
        self.assertTrue(hasattr(dto, 'count'))

        self.assertEqual('Example Widget', dto.get('title'))
        self.assertEqual(423, dto.count)

    def test_table_dto_schema(self):
        obj = {
            'title': 'Example Widget',
            'data': [
                {'id': 1, 'name': 'John', 'age': 50},
                {'id': 2, 'name': 'Barry', 'age': 32}
            ]
        }

        dto = TableWidgetDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'title'))
        self.assertTrue(hasattr(dto, 'data'))

        self.assertEqual('Example Widget', dto.get('title'))
        self.assertIsInstance(dto.data, list)
        self.assertIsInstance(dto.data[0], dict)
        self.assertEqual({'id': 1, 'name': 'John', 'age': 50}, dto.data[0])

    def test_map_dto_schema(self):
        obj = {
            "title": "Geopolitical alerts map",
            "data": [
                {
                    "code": "US",
                    "color": "#d8854f",
                    "value": 24
                },
                {
                    "code": "IQ",
                    "color": "#d8854f",
                    "value": 11
                },
                {
                    "code": "IN",
                    "color": "#d8854f",
                    "value": 9
                },
                {
                    "code": "AU",
                    "color": "#d8854f",
                    "value": 7
                },
                {
                    "code": "CN",
                    "color": "#d8854f",
                    "value": 7
                }
            ]
        }

        dto = MapWidgetDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'title'))
        self.assertTrue(hasattr(dto, 'data'))

        self.assertEqual('Geopolitical alerts map', dto.get('title'))
        self.assertIsInstance(dto.data, list)
        self.assertIsInstance(dto.data[0], MapDataPointDto)
        self.assertEqual({"code": "AU", "color": "#d8854f", "value": 7}, dto.data[3])
        self.assertEqual(24, dto.data[0].value)
        self.assertEqual(None, dto.data[0].url)
        self.assertEqual(None, dto.data[0].label)

    def test_mitre_dto_schema(self):
        obj = {
            "title": "Incident reports",
            "tactics": [
                {
                    "name": "Reconnaissance",
                    "techniques": [
                        {
                            "externalId": "T1595",
                            "key": "433",
                            "label": "Active Scanning",
                            "value": 35
                        }
                    ]
                }
            ]
        }

        dto = MitreWidgetDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'title'))
        self.assertTrue(hasattr(dto, 'tactics'))

        self.assertEqual('Incident reports', dto.get('title'))
        self.assertIsInstance(dto.tactics, list)
        self.assertIsInstance(dto.tactics[0], MitreTacticDto)
        self.assertIsInstance(dto.tactics[0].techniques, list)
        self.assertIsInstance(dto.tactics[0].techniques[0], MitreTechniqueDto)
        self.assertEqual('Reconnaissance', dto.tactics[0].name)
        self.assertEqual('T1595', dto.tactics[0].techniques[0].externalId)
        self.assertEqual('433', dto.tactics[0].techniques[0].key)
        self.assertEqual('Active Scanning', dto.tactics[0].techniques[0].label)
        self.assertEqual(35, dto.tactics[0].techniques[0].value)

    def test_metric_dto_schema(self):
        obj = {
            "title": "Incident reports",
            "description": "In last year",
            "xAxis": "Date",
            "yAxis": "Number of events",
            "series": [
                {
                    "id": "incident-report",
                    "name": "Lockbit",
                    "points": [
                        {
                            "key": "1651363200000",
                            "label": "May 2022",
                            "value": 0
                        }
                    ]
                }
            ]
        }

        dto = MetricWidgetDto(**obj)

        self.assertEqual(obj, dict(dto))

        self.assertTrue(hasattr(dto, 'title'))
        self.assertTrue(hasattr(dto, 'description'))
        self.assertTrue(hasattr(dto, 'xAxis'))
        self.assertTrue(hasattr(dto, 'yAxis'))
        self.assertTrue(hasattr(dto, 'series'))

        self.assertEqual('Incident reports', dto.get('title'))
        self.assertEqual('In last year', dto.description)
        self.assertEqual('Date', dto.xAxis)
        self.assertEqual('Number of events', dto.yAxis)

        self.assertIsInstance(dto.series, list)
        self.assertIsInstance(dto.series[0], MetricSeriesDto)

        self.assertEqual('incident-report', dto.series[0].id)
        self.assertEqual('Lockbit', dto.series[0].name)
        self.assertIsInstance(dto.series[0].points, list)
        self.assertIsInstance(dto.series[0].points[0], MetricPointDto)

        self.assertEqual('1651363200000', dto.series[0].points[0].key)
        self.assertEqual('May 2022', dto.series[0].points[0].label)
        self.assertEqual(0, dto.series[0].points[0].value)
