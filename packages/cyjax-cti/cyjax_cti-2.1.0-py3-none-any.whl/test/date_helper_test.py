import datetime
from datetime import timedelta
from unittest.mock import patch, Mock

import pytest
import pytz

from cyjax.exceptions import InvalidDateFormatException
from cyjax.helpers import DateHelper


class TestDateHelper:

    fake_date = Mock(wraps=datetime.datetime)
    fake_date.now.return_value.astimezone.return_value = datetime.datetime(2020, 5, 2, 12, 0, 0, tzinfo=pytz.UTC)

    @patch('cyjax.helpers.datetime', fake_date)
    def test_parse_date_with_timedelta(self):
        parsed_date = DateHelper.parse_date(timedelta(hours=2))
        assert parsed_date == '2020-05-02T10:00:00+00:00'

    def test_parse_date_with_datetime_without_timezone(self):
        parsed_date = DateHelper.parse_date(datetime.datetime(2020, 5, 2, 10, 0, 0))
        assert parsed_date == datetime.datetime(2020, 5, 2, 10, 0, 0).astimezone().isoformat()

    def test_parse_date_with_datetime_with_timezone(self):
        parsed_date = DateHelper.parse_date(datetime.datetime(2020, 5, 2, 10, 0, 0, tzinfo=pytz.UTC))
        assert parsed_date == '2020-05-02T10:00:00+00:00'

    def test_parse_date_from_strings(self):
        parsed_date = DateHelper.parse_date('2020-12-09T11:25:24+00:00')
        assert parsed_date == '2020-12-09T11:25:24+00:00'

        parsed_date = DateHelper.parse_date('2020-12-09T11:25:24+02:00')
        assert parsed_date == '2020-12-09T11:25:24+02:00'

        parsed_date = DateHelper.parse_date('2020-12-09T11:25:24+0000')
        assert parsed_date == '2020-12-09T11:25:24+00:00'

        parsed_date = DateHelper.parse_date('2020-05-02T10:00:00+00:00')
        assert parsed_date == '2020-05-02T10:00:00+00:00'

    def test_parse_date_with_wrong_date(self):
        with pytest.raises(InvalidDateFormatException) as exception:
            DateHelper.parse_date('2020-20')

        assert 'Incorrect date format, should be %Y-%m-%dT%H:%M:%S%z' == str(exception.value)

        with pytest.raises(InvalidDateFormatException) as exception:
            DateHelper.parse_date(12)

        assert 'Please provide a datetime, timedelta or str object' == str(exception.value)

        with pytest.raises(InvalidDateFormatException) as exception:
            DateHelper.parse_date('something')

        assert 'Incorrect date format, should be %Y-%m-%dT%H:%M:%S%z' == str(exception.value)

        with pytest.raises(InvalidDateFormatException) as exception:
            DateHelper.parse_date({'date': '2020-05-02T10:00:00+00:00'})

        assert 'Please provide a datetime, timedelta or str object' == str(exception.value)

        with pytest.raises(InvalidDateFormatException) as exception:
            DateHelper.parse_date(['2020-05-02T10:00:00+00:00'])

        assert 'Please provide a datetime, timedelta or str object' == str(exception.value)
