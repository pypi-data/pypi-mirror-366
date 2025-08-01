from typing import Optional, List, Union

import cyjax
from cyjax.resources.model_dto import ModelDto


class DashboardDto(ModelDto):

    @property
    def id(self) -> int:
        """
        The model identifier.
        :rtype int:
        """
        return self.get('id')

    @property
    def name(self) -> str:
        """
        The dashboard name.
        :rtype str:
        """
        return self.get('name')

    @property
    def description(self) -> str:
        """
        The dashboard description.
        :rtype str:
        """
        return self.get('description')

    @property
    def type(self) -> str:
        """
        The dashboard type.
        :rtype str:
        """
        return self.get('type')

    def __repr__(self):
        return '<DashboardDto id={}>'.format(self.id)


class TableWidgetDto(ModelDto):

    @property
    def title(self) -> str:
        """
        The dashboard widget title.
        :rtype str:
        """
        return self.get('title')

    @property
    def data(self) -> list:
        """
        The list of data. The object type depends on the selected data store.
        :rtype list:
        """
        return self.get('data')

    def __repr__(self):
        return '<TableWidgetDto title={}>'.format(self.title)


class MitreTechniqueDto(ModelDto):

    @property
    def key(self) -> str:
        """
        The technique ID.
        :rtype str:
        """
        return self.get('key')

    @property
    def externalId(self) -> str:
        """
        The external ID.
        :rtype str:
        """
        return self.get('externalId')

    @property
    def label(self) -> str:
        """
        The technique label.
        :rtype str:
        """
        return self.get('label')

    @property
    def value(self) -> int:
        """
        The technique value.
        :rtype int:
        """
        return self.get('value')

    def __repr__(self):
        return '<MitreTechniqueDto id={}>'.format(self.externalId)


class MitreTacticDto(ModelDto):

    @property
    def name(self) -> str:
        """
        The tactic name.
        :rtype str:
        """
        return self.get('name')

    @property
    def techniques(self) -> List[MitreTechniqueDto]:
        """
        The list of techniques.
        :rtype List[MitreTechniqueDto]:
        """
        return self._prop_list_to_dto('techniques', MitreTechniqueDto)

    def __repr__(self):
        return '<MitreTacticDto name={}>'.format(self.name)


class MitreWidgetDto(ModelDto):

    @property
    def title(self) -> str:
        """
        The dashboard widget title.
        :rtype str:
        """
        return self.get('title')

    @property
    def tactics(self) -> List[MitreTacticDto]:
        """
        The list of tactics.
        :rtype List[MitreTacticDto]:
        """
        return self._prop_list_to_dto('tactics', MitreTacticDto)

    def __repr__(self):
        return '<MitreWidgetDto title={}>'.format(self.title)


class MetricPointDto(ModelDto):

    @property
    def key(self) -> str:
        """
        The key.
        :rtype str:
        """
        return self.get('key')

    @property
    def label(self) -> str:
        """
        The label.
        :rtype str:
        """
        return self.get('label')

    @property
    def value(self) -> str:
        """
        The value.
        :rtype str:
        """
        return self.get('value')

    def __repr__(self):
        return '<MetricPointDto key={}>'.format(self.key)


class MetricSeriesDto(ModelDto):

    @property
    def id(self) -> str:
        """
        The data store ID.
        :rtype str:
        """
        return self.get('id')

    @property
    def name(self) -> str:
        """
        The series name.
        :rtype str:
        """
        return self.get('name')

    @property
    def points(self) -> List[MetricPointDto]:
        """
        The list of data points for the series.
        :rtype List[MetricSeriesDto]:
        """
        return self._prop_list_to_dto('points', MetricPointDto)

    def __repr__(self):
        return '<MetricSeriesDto id={}>'.format(self.id)


class MetricWidgetDto(ModelDto):

    @property
    def title(self) -> str:
        """
        The dashboard widget title.
        :rtype str:
        """
        return self.get('title')

    @property
    def description(self) -> str:
        """
        The dashboard widget description.
        :rtype str:
        """
        return self.get('description')

    @property
    def xAxis(self) -> str:
        """
        The widget xAxis name.
        :rtype str:
        """
        return self.get('xAxis')

    @property
    def yAxis(self) -> str:
        """
        The widget yAxis name.
        :rtype str:
        """
        return self.get('yAxis')

    @property
    def series(self) -> List[MetricSeriesDto]:
        """
        The list of series.
        :rtype List[MetricSeriesDto]:
        """
        return self._prop_list_to_dto('series', MetricSeriesDto)

    def __repr__(self):
        return '<MetricWidgetDto title={}>'.format(self.title)


class MapDataPointDto(ModelDto):

    @property
    def code(self) -> str:
        """
        The country code.
        :rtype str:
        """
        return self.get('code')

    @property
    def color(self) -> str:
        """
        The color code.
        :rtype str:
        """
        return self.get('color')

    @property
    def value(self) -> int:
        """
        The value.
        :rtype str:
        """
        return self.get('value')

    @property
    def label(self) -> Optional[str]:
        """
        The data point label.
        :rtype Optional[str]:
        """
        return self.get('label')

    @property
    def url(self) -> Optional[str]:
        """
        The URL for the data point.
        :rtype Optional[str]:
        """
        return self.get('url')

    def __repr__(self):
        return '<MapDataPointDto code={}>'.format(self.code)


class MapWidgetDto(ModelDto):

    @property
    def title(self) -> str:
        """
        The dashboard widget title.
        :rtype str:
        """
        return self.get('title')

    @property
    def data(self) -> List[MapDataPointDto]:
        """
        The list of data points.
        :rtype List[MapDataPointDto]:
        """
        return self._prop_list_to_dto('data', MapDataPointDto)

    def __repr__(self):
        return '<MapWidgetDto title={}>'.format(self.title)


class CounterWidgetDto(ModelDto):

    @property
    def title(self) -> str:
        """
        The dashboard widget title.
        :rtype str:
        """
        return self.get('title')

    @property
    def count(self) -> int:
        """
        The value of the counter.
        :rtype int:
        """
        return self.get('count')

    def __repr__(self):
        return '<CounterWidgetDto title={}>'.format(self.title)


class WidgetDto(ModelDto):

    @property
    def id(self) -> int:
        """
        The model identifier.
        :rtype int:
        """
        return self.get('id')

    @property
    def title(self) -> str:
        """
        The dashboard widget title.
        :rtype str:
        """
        return self.get('title')

    @property
    def url(self) -> str:
        """
        The dashboard widget url.
        :rtype str:
        """
        return self.get('url')

    @property
    def type(self) -> str:
        """
        The dashboard widget type.
        :rtype str:
        """
        return self.get('type')

    def get_data(self) -> Union[TableWidgetDto, CounterWidgetDto, MapWidgetDto, MitreWidgetDto, MetricWidgetDto]:
        """
        Gets the widget data from API

        :return: The widget response as DTO.
        :rtype Union[TableWidgetDto, CounterWidgetDto, MapWidgetDto, MitreWidgetDto, MetricWidgetDto]:
        """
        widget_id = self.id
        widget_type = self.type
        resource = cyjax.Dashboard()

        if widget_type == 'table':
            return resource.get_table_widget(widget_id)
        elif widget_type == 'counter':
            return resource.get_counter_widget(widget_id)
        elif widget_type == 'map':
            return resource.get_map_widget(widget_id)
        elif widget_type == 'metric':
            return resource.get_metric_widget(widget_id)
        elif widget_type == 'mitre':
            return resource.get_mitre_widget(widget_id)

    def __repr__(self):
        return '<WidgetDto id={}>'.format(self.id)
