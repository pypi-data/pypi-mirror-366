from datetime import datetime, timedelta

from .exceptions import InvalidDateFormatException

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


class DateHelper(object):

    @staticmethod
    def parse_date(date):
        """
        Parse the date to string based on the parameter type.
        :param date: The date.
        :type date: datetime, timedelta, str
        :return: The date as string in ISO8601 format.
        :rtype: str
        :raises InvalidDateFormatException: Whether the date cannot be parsed.
        """
        if isinstance(date, timedelta):
            date = datetime.now().astimezone() - date
            date = date.replace(microsecond=0).isoformat()
        elif isinstance(date, datetime):
            if not date.tzinfo:
                date = date.astimezone()

            date = date.replace(microsecond=0).isoformat()

        elif isinstance(date, str):
            # try to parse string to datetime object
            date_object = None

            # Python 3.7>= compatible
            try:
                date_object = datetime.fromisoformat(date)
            except Exception:
                pass

            # Python 3.6 compatible
            if date_object is None:
                try:
                    if '+' in date:
                        parts = date.split('+')
                        date = "{}+{}".format(parts[0], parts[1].replace(':', ''))

                    date_object = datetime.strptime(date, DATE_FORMAT)
                except Exception:
                    pass

            if date_object is None:
                raise InvalidDateFormatException("Incorrect date format, should be %s" % DATE_FORMAT)
            else:
                date = date_object.replace(microsecond=0).isoformat()
        else:
            raise InvalidDateFormatException("Please provide a datetime, timedelta or str object")

        return date

    @staticmethod
    def build_date_params(since=None, until=None):
        date_params = {}

        if since:
            try:
                date_params.update({'since': DateHelper.parse_date(since)})
            except InvalidDateFormatException as e:
                raise InvalidDateFormatException("since: %s" % e)

        if until:
            try:
                date_params.update({'until': DateHelper.parse_date(until)})
            except InvalidDateFormatException as e:
                raise InvalidDateFormatException("until: %s" % e)

        return date_params
