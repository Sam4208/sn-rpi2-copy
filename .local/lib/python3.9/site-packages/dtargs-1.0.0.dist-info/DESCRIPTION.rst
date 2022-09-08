.. image:: https://travis-ci.org/petedmarsh/dtargs.png?branch=master
    :target: https://travis-ci.org/petedmarsh/dtargs

Introduction
------------

dtargs is a small module that makes accepting date/time arguments with Argparse easier.

Examples
--------

A date argument ::

    import argparse
    import dtargs

    parser = argparse.ArgumentParser()
    parser.add_argument('start', type=dtargs.DateType()) # defaults to %Y-%m-%d
    parser.add_argument('end', type=dtargs.DateType('%d/%m/%Y'))

A date/time argument ::

    import argparse
    import dtargs

    parser = argparse.ArgumentParser()
    parser.add_argument('start', type=dtargs.DateTimeType()) # defaults to %Y-%m-%dT%H:%M:%SZ
    parser.add_argument('end', type=dtargs.DateTimeType('%H:%M:%S_%Y-%m-%d', tz=None)

Timezones
---------

The DateTimeType accepts a tz parameter, which is handled thusly ::

    import dtargs

    dtargs.DateTimeType()('2015-01-02T12:34:56Z')
    >>> datetime.datetime(2015, 1, 2, 12, 34, 56, tzinfo=<UTC>)

    dtargs.DateTimeType(tz=None)('2015-01-02T12:34:56Z')
    >> datetime.datetime(2015, 1, 2, 12, 34, 56, tzinfo=None)

    dtargs.DateTimeType('%Y-%m-%dT%H:%M:%S%z', tz=None)('2015-01-02T12:34:56+0100')
    >> datetime.datetime(2015, 1, 2, 12, 34, 56, tzinfo=datetime.timezone(datetime.timedelta(0, 3600))

    dtargs.DateTimeType('%Y-%m-%dT%H:%M:%S%z', tz=pytz.utc)('2015-01-02T12:34:56+0500')
    >> datetime.datetime(2015, 1, 2, 7, 34, 56, tzinfo=<UTC>)

Testing
-------

Install dependencies ::

    $ pip install -r dev-requirements.txt

To run tests ::

   $ py.test


