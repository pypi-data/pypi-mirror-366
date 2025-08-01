from typing import Optional, List, Type

from cyjax.resources.resource import Resource
from cyjax.resources.model_dto import ModelDto
from .dto import CounterWidgetDto, DashboardDto, TableWidgetDto, MapWidgetDto, MitreWidgetDto, MetricWidgetDto, \
    WidgetDto


class Dashboard(Resource):

    def list(self, type: Optional[str] = None) -> List[DashboardDto]:
        """
        Lists all dashboards.

        :param type: The dashboard type.
        :type type: Optional[str]

        :return: The list of dashboards.
        :rtype List[DashboardDto]:
        """
        params = {}
        if type:
            params.update({'type': type})

        return self._get_list(endpoint='/dashboard',
                              params=params,
                              dto=DashboardDto)

    def list_widgets(self, dashboard_id: int) -> List[WidgetDto]:
        """
        List all widgets for a given dashboard

        :param dashboard_id: The dashboard ID.
        :type dashboard_id: int

        :return: The list of dashboard widgets.
        :rtype List[WidgetDto]:
        """

        return self._get_list(endpoint='/dashboard/{}/widget'.format(
            dashboard_id),
            dto=WidgetDto)

    def get_table_widget(self, widget_id: int, page: Optional[int] = None,
                         per_page: Optional[int] = None):
        """
        Gets a table widget

        :param widget_id: The dashboard widget ID.
        :type widget_id: int

        :return: The list of dashboard widgets.
        :rtype List[WidgetDto]:
        """
        params = {}
        if page:
            params.update({"page": page})
        if per_page:
            params.update({"per-page": per_page})

        return self._get_widget(
            endpoint='/dashboard/widget/table/{}'.format(widget_id),
            params=params,
            dto=TableWidgetDto
        )

    def get_mitre_widget(self, widget_id: int):
        """
        Gets a MITRE ATT&CK map widget

        :param widget_id: The dashboard widget ID.
        :type widget_id: int

        :return: MitreWidgetDto
        """
        return self._get_widget(
            endpoint='/dashboard/widget/mitre/{}'.format(widget_id),
            dto=MitreWidgetDto,
            params={'format': 'json'}
        )

    def get_metric_widget(self, widget_id: int):
        """
        Gets a metric widget

        :param widget_id: The dashboard widget ID.
        :type widget_id: int

        :return: MetricWidgetDto
        """
        return self._get_widget(
            endpoint='/dashboard/widget/metric/{}'.format(widget_id),
            dto=MetricWidgetDto,
            params={'format': 'json'}
        )

    def get_map_widget(self, widget_id: int):
        """
        Gets a metric widget

        :param widget_id: The dashboard widget ID.
        :type widget_id: int

        :return: MetricWidgetDto
        """
        return self._get_widget(
            endpoint='/dashboard/widget/map/{}'.format(widget_id),
            dto=MapWidgetDto,
            params={'format': 'json'}
        )

    def get_counter_widget(self, widget_id: int):
        """
        Gets a counter widget

        :param widget_id: The dashboard widget ID.
        :type widget_id: int

        :return: MetricWidgetDto
        """
        return self._get_widget(
            endpoint='/dashboard/widget/counter/{}'.format(widget_id),
            dto=CounterWidgetDto,
            params={'format': 'json'}
        )

    def _get_widget(self, endpoint: str, dto: Type[ModelDto], params=None) -> ModelDto:
        """
        Get the widget from the API endpoint

        :param endpoint: The endpoint.
        :type endpoint: str

        :param dto: The DTO class to apply to the response.
        :type dto: Type[ModelDto]

        :param params: The list of tuples or bytes to send in the query string for the request
        :type params:  Dictionary, optional

        :return: :class:`ModelDto <ModelDto>` object
        :rtype: ModelDto
        """
        response = self._api_client.send(method='get',
                                         endpoint=self._trim_endpoint(
                                             endpoint),
                                         params=params)
        obj = response.json()
        return dto(**obj)
