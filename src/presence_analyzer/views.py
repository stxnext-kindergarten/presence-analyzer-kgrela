# -*- coding: utf-8 -*-
"""Defines views."""

import calendar
from flask import (
    url_for,
    redirect,
)
from flask.ext.mako import render_template
from mako.exceptions import TopLevelLookupException

from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify,
    get_data,
    mean,
    group_by_weekday,
    group_by_start_end,
    get_users_data,
)

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103

TEMPLATE_LIST = (
    'presence_weekday.html',
    'mean_time_weekday.html',
    'presence_start_end.html'
)


@app.route('/')
def mainpage():
    """Redirects to front page."""
    return redirect(
        url_for('template_render', template_name="presence_weekday.html")
        )


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """Users listing for dropdown."""
    data = get_users_data()
    result = [
        {
            'user_id': user,
            'name': user_data['name'],
            'avatar': user_data['avatar']
        }
        for user, user_data in data.iteritems()
    ]

    return result


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """Returns mean presence time of given user grouped by weekday."""
    data = get_data()
    if user_id not in data:
        log.debug('User {0} not found!'.format(user_id))
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """Returns total presence time of given user grouped by weekday."""
    data = get_data()
    if user_id not in data:
        log.debug('User {0} not found!'.format(user_id))
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()
              ]
    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """Returns mean start and end time of given user"""
    data = get_data()
    if user_id not in data:
        log.debug('User {0} not found!'.format(user_id))
        return []

    weekdays = group_by_start_end(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(times['start']), mean(times['end']))
        for weekday, times in weekdays.items()
        ]
    return result


@app.route('/<template_name>', methods=['GET'])
def template_render(template_name):
    """Create HTML document from template"""
    try:
        if template_name in TEMPLATE_LIST:
            return render_template(template_name)
        else:
            raise TopLevelLookupException
    except TopLevelLookupException:
        return "404", 404
