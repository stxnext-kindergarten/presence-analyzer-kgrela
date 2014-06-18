# -*- coding: utf-8 -*-
"""Presence analyzer unit tests."""
import os.path
import json
import datetime
import unittest

from presence_analyzer import (
    main,
    views,
    utils,
    )

TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)

TEST_DATA_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.xml'
)

TEST_CACHED_DATA = os.path.join(
    os.path.dirname(__file__), '..', '..',
    'runtime', 'data', 'test_cache_data.csv'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """Views tests."""

    def setUp(self):
        """Before each test, set up a environment."""
        main.app.config.update({
            'DATA_CSV': TEST_DATA_CSV,
            'DATA_XML': TEST_DATA_XML,
            })
        self.client = main.app.test_client()

    def tearDown(self):
        """Get rid of unused objects after each test."""
        pass

    def test_mainpage(self):
        """Test main page redirect."""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """Test users listing."""
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertListEqual(data, [
            {
                u'avatar': u'https://intranet.stxnext.pl/api/images/users/151',
                u'name': u'Not F.',
                u'user_id': u'11'
            }, {
                u'avatar': u'https://intranet.stxnext.pl/api/images/users/165',
                u'name': u'Rando M.',
                u'user_id': u'10'
            }
        ])

    def test_users_view(self):
        """Test user view"""
        result = self.client.get('/api/v1/mean_time_weekday/11')
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, 'application/json')
        data = json.loads(result.data)
        self.assertIsInstance(data[0], list)
        self.assertListEqual(data, [
            [u'Mon', 24123],
            [u'Tue', 16564.0],
            [u'Wed', 25321.0],
            [u'Thu', 22984.0],
            [u'Fri', 6426.0],
            [u'Sat', 0],
            [u'Sun', 0]
        ])

    def test_mean_time_weekday_view(self):
        """Test view of mean time for user"""
        result = self.client.get('/api/v1/mean_time_weekday/11')
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, 'application/json')
        data = json.loads(result.data)
        self.assertIsInstance(data[0], list)
        self.assertListEqual(data, [
            [u'Mon', 24123.0],
            [u'Tue', 16564.0],
            [u'Wed', 25321.0],
            [u'Thu', 22984.0],
            [u'Fri', 6426.0],
            [u'Sat', 0],
            [u'Sun', 0]
        ])

    def test_presence_weekday_view(self):
        """Test view of weekday time for user"""
        result = self.client.get('/api/v1/presence_weekday/11')
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, 'application/json')
        data = json.loads(result.data)
        self.assertListEqual(data, [
            [u'Weekday', u'Presence (s)'],
            [u'Mon', 24123.0],
            [u'Tue', 16564.0],
            [u'Wed', 25321.0],
            [u'Thu', 45968.0],
            [u'Fri', 6426.0],
            [u'Sat', 0],
            [u'Sun', 0]
        ])

    def test_presence_start_end_view(self):
        """Test view of start-end time for user"""
        result = self.client.get('/api/v1/presence_start_end/11')
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, 'application/json')
        data = json.loads(result.data)
        self.assertListEqual(data, [
            [u'Mon', 33134.0, 57257.0],
            [u'Tue', 33590.0, 50154.0],
            [u'Wed', 33206.0, 58527.0],
            [u'Thu', 35602.0, 58586.0],
            [u'Fri', 47816.0, 54242.0],
            [u'Sat', 0, 0],
            [u'Sun', 0, 0]
        ])

        result = self.client.get('/api/v1/presence_start_end/10')
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, 'application/json')
        data = json.loads(result.data)
        self.assertListEqual(data, [
            [u'Mon', 0, 0],
            [u'Tue', 34745.0, 64792.0],
            [u'Wed', 33592.0, 58057.0],
            [u'Thu', 38926.0, 62631.0],
            [u'Fri', 0, 0],
            [u'Sat', 0, 0],
            [u'Sun', 0, 0]
        ])

    def test_template_render(self):
        """Test rendering templates"""
        data_list = [
            {
                'url': "/presence_weekday.html",
                "unique": "Presence by weekday"
            }, {
                'url': "/mean_time_weekday.html",
                "unique": "Presence mean time by weekday"
            }, {
                'url': "/presence_start_end.html",
                "unique": "Presence start-end weekday"
            }
        ]
        for data in data_list:
            result = self.client.get(data['url'])
            self.assertIsNotNone(result)
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.content_type, 'text/html; charset=utf-8')
            self.assertIn(data['unique'], result.data)

    def test_template_render_secon(self):
        """Second testing function simulating real tests
        Especially for you
        """
        wrong_data = [
            {'url': "/basic.html", "code": 404},
            {'url': "/not_existing.html", "code": 404}
        ]
        for data in wrong_data:
            result = self.client.get(data['url'])
            self.assertEqual(result.status_code, data['code'])


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """Utility functions tests."""

    def setUp(self):
        """Before each test, set up a environment."""
        main.app.config.update({
            'DATA_CSV': TEST_DATA_CSV,
            'DATA_XML': TEST_DATA_XML,
        })
        utils.CACHE_DATA = {}

    def tearDown(self):
        """Get rid of unused objects after each test."""
        pass

    def test_get_data(self):
        """Test parsing of CSV file."""
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_group_by_weekday(self):
        """Test groups entries by weekday"""
        data = utils.get_data()
        result = utils.group_by_weekday(data[10])
        self.assertEqual(len(result), 7)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result[2], list)
        self.assertDictEqual(result, {
            0: [],
            1: [utils.interval
                (data[10][datetime.date(2013, 9, 10)]['start'],
                 data[10][datetime.date(2013, 9, 10)]['end']
                 )
                ],
            2: [utils.interval
                (data[10][datetime.date(2013, 9, 11)]['start'],
                 data[10][datetime.date(2013, 9, 11)]['end']
                 )
                ],
            3: [utils.interval
                (data[10][datetime.date(2013, 9, 12)]['start'],
                 data[10][datetime.date(2013, 9, 12)]['end']
                 )
                ],
            4: [],
            5: [],
            6: [],
        })

        self.assertEqual(len(result[3]), 1)

    def test_group_by_start_end(self):
        """Test group by start-end"""
        data = utils.get_data()
        self.assertIsNotNone(data)
        result = utils.group_by_start_end(data[11])
        self.assertIsNotNone(result)
        self.assertIsInstance(data, dict)
        self.assertEqual(len(result), 7)
        self.assertDictEqual(result, {
            0: {'start': [33134], 'end': [57257]},
            1: {'start': [33590], 'end': [50154]},
            2: {'start': [33206], 'end': [58527]},
            3: {'start': [37116, 34088], 'end': [60085, 57087]},
            4: {'start': [47816], 'end': [54242]},
            5: {'start': [], 'end': []},
            6: {'start': [], 'end': []}
        })

        result = utils.group_by_start_end(data[10])
        self.assertIsNotNone(result)
        self.assertIsInstance(data, dict)
        self.assertEqual(len(result), 7)
        self.assertDictEqual(result, {
            0: {'start': [], 'end': []},
            1: {'start': [34745], 'end': [64792]},
            2: {'start': [33592], 'end': [58057]},
            3: {'start': [38926], 'end': [62631]},
            4: {'start': [], 'end': []},
            5: {'start': [], 'end': []},
            6: {'start': [], 'end': []}
        })

    def test_seconds_since_midnight(self):
        """Test calculated amount of seconds since midnight"""
        sample_date = datetime.time(10, 10, 10)
        self.assertEqual(utils.seconds_since_midnight(sample_date),
                         10*3600 + 10*60 + 10)

    def test_interval(self):
        """Test calculates inverval in seconds between two
        datetime.time objects.
        """
        sample_date_1 = datetime.time(10, 10, 10)
        sample_date_2 = datetime.time(12, 12, 12)
        self.assertEqual(utils.interval(sample_date_1, sample_date_2),
                         2*3600 + 2*60 + 2)

    def test_mean(self):
        """Test calculates arithmetic mean."""
        self.assertIsNotNone(utils.mean([]))
        self.assertIsInstance(utils.mean([1, 1.4, 5, 1.3]), float)
        self.assertEqual(utils.mean([1, 2, 3, 4]), 2.5)
        self.assertEqual(utils.mean([-1, -2, 3, 4]), 1)
        self.assertEqual(utils.mean([1.1, 1.2, 1.3, 1.4]), 1.25)
        self.assertEqual(utils.mean([]), 0)

    def test_get_users_data(self):
        """Test returned data from xml"""
        data = utils.get_users_data()
        self.assertDictEqual(data, {
            '10': {
                u'avatar': u'https://intranet.stxnext.pl/api/images/users/165',
                u'name': 'Rando M.',
            },
            '11': {
                u'avatar': u'https://intranet.stxnext.pl/api/images/users/151',
                u'name': 'Not F.',
            }
        })

    def test_cache(self):
        """ Test cache decorator"""
        data = [1, 2, 3, 4, 5]

        @utils.cache("decorated function", 600)
        def decorated_function():
            """Helper function for testing decorator"""
            return data

        for i in xrange(5):
            result = decorated_function()
            self.assertEqual(result, data)
            utils.get_data()
        self.assertIn("decorated function", utils.CACHE_DATA)

        utils.get_data()
        data = utils.CACHE_DATA['get_data']['result']
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

        main.app.config.update({'DATA_CSV': TEST_CACHED_DATA})

        data = utils.CACHE_DATA['get_data']['result']
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

        utils.CACHE_DATA = {}
        data = utils.get_data()
        self.assertEqual(data, {
            10: {
                datetime.date(2013, 9, 10): {
                    'end': datetime.time(17, 59, 52),
                    'start': datetime.time(9, 39, 5)
                }
            }
        })


def suite():
    """Default test suite."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__    ':
    unittest.main()
