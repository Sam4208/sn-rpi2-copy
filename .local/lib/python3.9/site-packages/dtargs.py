# -*- coding: utf-8 -*-

import argparse
import pytz
from datetime import datetime


class DateType(object):
    """Factory for creating datetime.date object types

    Instances of DateType are typically passed as type= arguments to the
    ArgumentParser add_argument() method.

    :param date_format: A date format string that datetime.strptime accepts
                        (default '%Y-%m-%d')
    :type date_format: str
    """

    def __init__(self, date_format='%Y-%m-%d'):
        self.date_format = date_format

    def __call__(self, string):
        try:
            return datetime.strptime(string, self.date_format).date()
        except (TypeError, ValueError) as e:
            raise argparse.ArgumentTypeError('could not parse "%s" as "%s"'
                                             % (string, self.date_format))

    def __repr__(self):
        return '%s(date_format="%s")' % (type(self).__name__, self.date_format)


class DateTimeType(object):
    """Factory for creating datetime.datetime object types

    Instances of DateTimeType are typically passed as type= arguments to the
    ArgumentParser add_argument() method.

    The tz parameter is handled thusly:

        1. If date_time_format does not include timezone directives and tz is
           None then a naive datetime instance will be returned (i.e.
           tzinfo=None)
        2. If date_time_format does include timezone directives and ts is None
           then a timezone-aware datetime instance will be returned with
           whatever tzinfo is set by strptime (i.e. tzinfo=datetime.timezone)
        3. If date_time_format does not include timezone directives and tz is
           not None then a timezone-aware datetime instance will be returned
           with tzinfo set to tz
        4. If date_time_format does include timezone directives and ts is not
           None then the datetime instance from strptime will be converted into
           the tz timezone

    :param date_time_format: A date/time format string that datetime.strptime
                             accepts (default '%Y-%m-%dT%H:%M:%SZ')
    :type date_time_format: str
    :param tz: The timezone to apply to the date/time, may be None in which
               case a naive datetime.datetime instance is returned (default
               pytz.utc)
    :type tz: datetime.timezone
    """

    def __init__(self, date_time_format='%Y-%m-%dT%H:%M:%SZ', tz=pytz.utc):
        self.date_time_format = date_time_format
        self.tz = tz

    def __call__(self, string):
        try:
            date_time = datetime.strptime(string, self.date_time_format)
            if self.tz:
                if date_time.tzinfo:
                    date_time = date_time.astimezone(self.tz)
                else:
                    date_time = date_time.replace(tzinfo=self.tz)
            return date_time
        except (TypeError, ValueError) as e:
            raise  argparse.ArgumentTypeError('could not parse "%s" as "%s"'
                % (string, self.date_time_format))

    def __repr__(self):
        return '%s(date_time_format="%s", tz=%s)' % (type(self).__name__,
                                                      self.date_time_format,
                                                      repr(self.tz))
