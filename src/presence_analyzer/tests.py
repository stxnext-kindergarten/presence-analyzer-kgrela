# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_users_view(self):
        """Test user view"""
        result = self.client.get('/api/v1/mean_time_weekday/11')
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 200)
        data = json.loads(result.data)
        self.assertIsInstance(data[0], list)
        self.assertListEqual(data,
                             [[u'Mon', 24123],
                              [u'Tue', 16564.0],
                              [u'Wed', 25321.0],
                              [u'Thu', 22984.0],
                              [u'Fri', 6426.0],
                              [u'Sat', 0],
                              [u'Sun', 0]
                              ]
                             )

    def test_mean_time_weekday_view(self):
        """Test view of mean time for user"""
        result = self.client.get('/api/v1/mean_time_weekday/11')
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 200)
        data = json.loads(result.data)
        self.assertIsInstance(data[0], list)
        self.assertListEqual(data,
                             [[u'Mon', 24123.0],
                              [u'Tue', 16564.0],
                              [u'Wed', 25321.0],
                              [u'Thu', 22984.0],
                              [u'Fri', 6426.0],
                              [u'Sat', 0],
                              [u'Sun', 0]
                              ],
                             )

    def test_presence_weekday_view(self):
        """Test pesence """
        result = self.client.get('/api/v1/presence_weekday/11')
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, 'application/json')
        data = json.loads(result.data)
        self.assertListEqual(data,
                             [[u'Weekday', u'Presence (s)'],
                              [u'Mon', 24123.0],
                              [u'Tue', 16564.0],
                              [u'Wed', 25321.0],
                              [u'Thu', 45968.0],
                              [u'Fri', 6426.0],
                              [u'Sat', 0],
                              [u'Sun', 0]
                              ],
                             )


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
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
        self.assertEqual(result[1][0],
                         utils.interval(data[10][datetime.date(2013, 9, 10)]
                                        ['start'],
                                        data[10][datetime.date(2013, 9, 10)]
                                        ['end']))
        self.assertEqual(len(result[3]), 1)

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


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
