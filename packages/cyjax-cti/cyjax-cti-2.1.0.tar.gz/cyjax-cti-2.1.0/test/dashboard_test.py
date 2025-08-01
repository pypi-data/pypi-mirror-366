from unittest.mock import MagicMock

import responses

import cyjax
from cyjax import Dashboard
from cyjax.resources.dashboard.dto import CounterWidgetDto, DashboardDto, TableWidgetDto, MapWidgetDto, \
    MitreWidgetDto, MetricWidgetDto, WidgetDto, MitreTacticDto, MitreTechniqueDto, MapDataPointDto
from cyjax.resources.resource import Resource
from cyjax.api_client import ApiClient


class TestDashboard:

    def test_instance(self):
        resource = Dashboard('123', 'test')
        assert isinstance(resource, Resource)
        assert isinstance(resource._api_client, ApiClient)
        assert '123' == resource._api_client.get_api_key()
        assert 'test' == resource._api_client.get_api_url()

    def test_list_without_parameters(self, mocker):
        resource = Dashboard()
        resource._api_client = MagicMock()
        spy_method_get_list = mocker.spy(resource, '_get_list')

        resource.list()
        spy_method_get_list.assert_called_once_with(endpoint='/dashboard',
                                                    params={},
                                                    dto=DashboardDto)

    def test_list_with_parameters(self, mocker):
        resource = Dashboard()
        resource._api_client = MagicMock()
        spy_method_get_list = mocker.spy(resource, '_get_list')

        resource.list(type='test type')
        spy_method_get_list.assert_called_once_with(endpoint='/dashboard',
                                                    params={
                                                        'type': 'test type'},
                                                    dto=DashboardDto)

    def test_list_dashboard_widgets(self, mocker):
        resource = Dashboard()
        resource._api_client = MagicMock()
        spy_method_get_list = mocker.spy(resource, '_get_list')

        resource.list_widgets(dashboard_id=1234)
        spy_method_get_list.assert_called_once_with(endpoint='/dashboard/1234/widget',
                                                    dto=WidgetDto)

    def test_get_table_widget(self, mocker):
        resource = Dashboard()
        resource._api_client = MagicMock()
        spy_method_get_widget = mocker.spy(resource, '_get_widget')

        resource.get_table_widget(widget_id=1234)
        spy_method_get_widget.assert_called_once_with(endpoint='/dashboard/widget/table/1234',
                                                      params={},
                                                      dto=TableWidgetDto)

    def test_get_table_widget_with_page_param(self, mocker):
        resource = Dashboard()
        resource._api_client = MagicMock()
        spy_method_get_widget = mocker.spy(resource, '_get_widget')

        resource.get_table_widget(widget_id=1234, page=1)
        spy_method_get_widget.assert_called_once_with(endpoint='/dashboard/widget/table/1234',
                                                      params={'page': 1},
                                                      dto=TableWidgetDto)

    def test_get_table_widget_with_per_page_param(self, mocker):
        resource = Dashboard()
        resource._api_client = MagicMock()
        spy_method_get_widget = mocker.spy(resource, '_get_widget')

        resource.get_table_widget(widget_id=1234, per_page=1)
        spy_method_get_widget.assert_called_once_with(endpoint='/dashboard/widget/table/1234',
                                                      params={'per-page': 1},
                                                      dto=TableWidgetDto)

    def test_get_table_widget_with_all_params(self, mocker):
        resource = Dashboard()
        resource._api_client = MagicMock()
        spy_method_get_widget = mocker.spy(resource, '_get_widget')

        resource.get_table_widget(widget_id=1234, per_page=10, page=1)
        spy_method_get_widget.assert_called_once_with(endpoint='/dashboard/widget/table/1234',
                                                      params={'per-page': 10,
                                                              'page': 1},
                                                      dto=TableWidgetDto)

    def test_mitre_table_widget(self, mocker):
        resource = Dashboard()
        resource._api_client = MagicMock()
        spy_method_get_widget = mocker.spy(resource, '_get_widget')

        resource.get_mitre_widget(widget_id=1234)
        spy_method_get_widget.assert_called_once_with(endpoint='/dashboard/widget/mitre/1234',
                                                      dto=MitreWidgetDto,
                                                      params={'format': 'json'})

    def test_metric_table_widget(self, mocker):
        resource = Dashboard()
        resource._api_client = MagicMock()
        spy_method_get_widget = mocker.spy(resource, '_get_widget')

        resource.get_metric_widget(widget_id=1234)
        spy_method_get_widget.assert_called_once_with(endpoint='/dashboard/widget/metric/1234',
                                                      dto=MetricWidgetDto,
                                                      params={'format': 'json'})

    def test_map_table_widget(self, mocker):
        resource = Dashboard()
        resource._api_client = MagicMock()
        spy_method_get_widget = mocker.spy(resource, '_get_widget')

        resource.get_map_widget(widget_id=1234)
        spy_method_get_widget.assert_called_once_with(endpoint='/dashboard/widget/map/1234',
                                                      dto=MapWidgetDto,
                                                      params={'format': 'json'})

    def test_counter_table_widget(self, mocker):
        resource = Dashboard()
        resource._api_client = MagicMock()
        spy_method_get_widget = mocker.spy(resource, '_get_widget')

        resource.get_counter_widget(widget_id=1234)
        spy_method_get_widget.assert_called_once_with(endpoint='/dashboard/widget/counter/1234',
                                                      dto=CounterWidgetDto,
                                                      params={'format': 'json'})

    @responses.activate
    def test_list_response(self):
        resource = Dashboard(api_key='test')

        mocked_entries = [
            {
                'id': 100,
                'title': 'Ransomware victims',
                'description': 'The dashboard shows ransowmare victims by sectors and country.',
                'type': 'personal',
            },
            {
                'id': 104,
                'title': 'Incident reports',
                'description': 'The dashboard from library.',
                'type': 'library',
            }
        ]
        responses.add(responses.GET, resource._api_client.get_api_url() + '/dashboard',
                      json=mocked_entries,
                      status=200)

        response = resource.list()

        assert isinstance(response, list) is True
        assert isinstance(response[0], DashboardDto) is True
        assert isinstance(response[1], DashboardDto) is True

    @responses.activate
    def test_list_widgets_response(self):
        resource = Dashboard(api_key='test')

        mocked_entries = [
            {
                'id': 100,
                'title': 'Widget A',
                'rul': 'https://api.cymon.co/v2/dashboard/widget/metric/100',
                'type': 'data',
            },
            {
                'id': 101,
                'title': 'Widget B',
                'rul': 'https://api.cymon.co/v2/dashboard/widget/metric/101',
                'type': 'data',
            }
        ]
        responses.add(responses.GET, resource._api_client.get_api_url() + '/dashboard/4/widget',
                      json=mocked_entries,
                      status=200)

        response = resource.list_widgets(4)

        assert isinstance(response, list) is True
        assert isinstance(response[0], WidgetDto) is True
        assert isinstance(response[1], WidgetDto) is True

    @responses.activate
    def test_table_widget_response(self):
        resource = Dashboard(api_key='test')

        obj = {
            'title': 'Example Widget',
            'data': [
                {'id': 1, 'name': 'John', 'age': 50},
                {'id': 2, 'name': 'Barry', 'age': 32}
            ]
        }

        responses.add(responses.GET, resource._api_client.get_api_url() + '/dashboard/widget/table/5',
                      json=obj,
                      status=200)

        response = resource.get_table_widget(5)

        assert isinstance(response, TableWidgetDto) is True
        assert 'Example Widget' == response.title
        assert isinstance(response.data[0], dict)
        assert 1 == response.data[0].get('id')

    @responses.activate
    def test_mitre_widget_response(self):
        resource = Dashboard(api_key='test')

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

        responses.add(responses.GET, resource._api_client.get_api_url() + '/dashboard/widget/mitre/5',
                      json=obj,
                      status=200)

        response = resource.get_mitre_widget(5)

        assert isinstance(response, MitreWidgetDto) is True
        assert 'Incident reports' == response.title
        assert isinstance(response.tactics, list)
        assert isinstance(response.tactics[0], MitreTacticDto)
        assert isinstance(response.tactics[0].techniques, list)
        assert isinstance(response.tactics[0].techniques[0], MitreTechniqueDto)
        assert 'T1595' == response.tactics[0].techniques[0].externalId

    @responses.activate
    def test_map_widget_response(self):
        resource = Dashboard(api_key='test')

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

        responses.add(responses.GET, resource._api_client.get_api_url() + '/dashboard/widget/map/5',
                      json=obj,
                      status=200)

        response = resource.get_map_widget(5)

        assert isinstance(response, MapWidgetDto) is True
        assert 'Geopolitical alerts map' == response.title
        assert isinstance(response.data, list)
        assert isinstance(response.data[0], MapDataPointDto)
        assert 'CN' == response.data[4].code
        assert '#d8854f' == response.data[4].color
        assert 7 == response.data[4].value
        assert response.data[4].url is None
        assert response.data[4].label is None

    @responses.activate
    def test_counter_widget_response(self):
        resource = Dashboard(api_key='test')

        obj = {
            'title': 'Example Widget',
            'count': 423
        }

        responses.add(responses.GET, resource._api_client.get_api_url() + '/dashboard/widget/counter/5',
                      json=obj,
                      status=200)

        response = resource.get_counter_widget(5)

        assert isinstance(response, CounterWidgetDto) is True
        assert 'Example Widget' == response.title
        assert 423 == response.count

    @responses.activate
    def test_get_counter_widget_data_from_dto(self):
        cyjax.api_key = 'test'
        resource = Dashboard(api_key='test')

        obj = {
            'title': 'Example Widget',
            'count': 423
        }

        responses.add(responses.GET, resource._api_client.get_api_url() + '/dashboard/widget/counter/5012',
                      json=obj,
                      status=200)

        dto = WidgetDto(**{'id': 5012,
                           'title': 'Reports in the last 30 days',
                           'type': 'counter',
                           'url': 'https://api.cymon.co/v2/dashboard/widget/counter/5012'})

        response = dto.get_data()

        assert isinstance(response, CounterWidgetDto) is True
        assert 'Example Widget' == response.title
        assert 423 == response.count

        cyjax.api_key = None
