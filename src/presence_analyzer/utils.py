# -*- coding: utf-8 -*-
"""Helper functions used in views."""

import csv
from json import dumps
from functools import wraps
from datetime import (
    datetime,
    timedelta,
)
import thread

from flask import Response
from lxml import etree

from presence_analyzer.main import app

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103

CACHE_DATA = {}


def jsonify(function):
    """Creates a response with the JSON representation of wrapped
    function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """Helper function for jsonify fucntion"""
        return Response(dumps(function(*args, **kwargs)),
                        mimetype='application/json')
    return inner


def locker(function):
    """Lock given function."""
    function.__lock__ = thread.allocate_lock()

    @wraps(function)
    def locker_handler(*args, **kwds):
        """Wait if function is locked."""
        with function.__lock__:
            result = function(*args, **kwds)
            return result
    return locker_handler


def cache(name, time):
    """Store result of funtion for given time."""
    def cache_function(function):
        """Get function for cache handler"""
        @wraps(function)
        def cache_handler(*args, **kwds):
            """Return value from cache. If value doesn't exist load it."""
            if name not in CACHE_DATA.keys() or\
                    CACHE_DATA[name]['time'] < datetime.now():
                CACHE_DATA[name] = {
                    'result': function(*args, **kwds),
                    'time': datetime.now() + timedelta(seconds=time)
                }
            return CACHE_DATA[name]['result']
        return cache_handler
    return cache_function


@locker
@cache("get_data", 600)
def get_data():
    """Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def group_by_weekday(items):
    """Groups presence entries by weekday"""
    result = {i: [] for i in range(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def group_by_start_end(items):
    """Groups presence entries by"""
    result = {i: {'start': [], 'end': []} for i in range(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()]['start'].append(seconds_since_midnight(start))
        result[date.weekday()]['end'].append(seconds_since_midnight(end))
    return result


def seconds_since_midnight(time):
    """Calculates amount of seconds since midnight."""
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """Calculates inverval in seconds between two datetime.time
    objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """Calculates arithmetic mean. Returns zero for empty lists."""
    return float(sum(items)) / len(items) if len(items) > 0 else 0


def get_users_data():
    """Returns users data. Their id, name and avatar address."""
    with open(app.config['DATA_XML'], 'r') as xmlfile:
        data = etree.parse(xmlfile)
    root = data.getroot()
    config = root[0]
    server = {
        u'protocol': unicode(config.findtext(u'protocol')),
        u'host': unicode(config.findtext('host'))
    }
    address = '{0}://{1}'.format(server['protocol'], server[u'host'])
    return {
        user.get('id'): {
            u'name': user.findtext(u'name'),
            u'avatar': '{0}{1}'.format(address, user.findtext(u'avatar'))
        }
        for user in root[1]
    }


def update_xml():
    """Update the server"""
    from urllib import urlretrieve

    return urlretrieve(
        app.config['DATA_SERVER_ADDRESS'],
        app.config['DATA_XML']
    )
