###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
import json
from functools import cached_property
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from threading import Thread
from urllib.parse import parse_qsl, urlparse

from everysk.config import settings
from everysk.core.compress import compress
from everysk.core.datetime import Date
from everysk.core.http import HttpSDKPOSTConnection, httpx
from everysk.core.unittests import TestCase, mock

from everysk.sdk.engines.market_data import MarketData, MarketDataPublic


class SilentHTTPRequestHandler(BaseHTTPRequestHandler):
    # https://realpython.com/python-http-server/

    def log_request(self, code = '-', size = '-'):
        # This method send all request logs to stdout, we just skip it
        pass

    @cached_property
    def url(self):
        return urlparse(self.path)

    @cached_property
    def query_data(self):
        return dict(parse_qsl(self.url.query))

    def get_response(self):
        return json.dumps(
            {
                "path": self.url.path,
                "query_data": self.query_data,
            }
        )

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(self.get_response().encode("utf-8"))



###############################################################################
#   Market Data Test Case Implementation
###############################################################################
class MarketDataTestCase(TestCase):

    def setUp(self) -> None:
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()
        return super().setUp()

    ###############################################################################
    #  Get Security Test Case Implementation
    ###############################################################################
    def test_get_security_is_called(self):
        market_data = MarketData(date=Date(2023, 7, 31))
        expected_content = compress({'class_name': 'MarketData', 'method_name': 'get_security', 'self_obj': market_data.to_dict(add_class_path=True), 'params': {'date': '123', 'ticker_list': ['test'], 'ticker_type': ['choice1', 'choice2'], 'projection': 'test_projection', 'nearest': True}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            market_data.get_security(date='123', ticker_list=['test'], ticker_type=['choice1', 'choice2'], projection='test_projection', nearest=True)

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    ###############################################################################
    #  Get Historical Test Case Implementation
    ###############################################################################
    def test_get_historical_is_called(self):
        market_data = MarketData(date=Date(2023, 7, 31))
        expected_content = compress({'class_name': 'MarketData', 'method_name': 'get_historical', 'self_obj': market_data.to_dict(add_class_path=True), 'params': {'date': '2023-08-14', 'start_date': '2022-05-14', 'end_date': '2024-07-17', 'ticker_list': ['test'], 'ticker_type': ['choice1', 'choice2'], 'projection': 'test_projection', 'nearest': True, 'real_time': True}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            market_data.get_historical(date='2023-08-14', start_date='2022-05-14', end_date='2024-07-17', ticker_list=['test'], ticker_type=['choice1', 'choice2'], projection='test_projection', nearest=True, real_time=True)

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    ###############################################################################
    #  Search Test Case Implementation
    ###############################################################################
    def test_search_is_called(self):
        market_data = MarketData(date=Date(2023, 7, 31))
        expected_content = compress({
            'class_name': 'MarketData',
            'method_name': 'search',
            'self_obj': market_data.to_dict(add_class_path=True),
            'params': {
                'conditions': [['asset', '=', 'test']],
                'fields': ['everysk_id', 'asset'],
                'order_by': '-everysk_id',
                'limit': 10,
                'date': '2023-08-14',
                'path': ''
            }
        }, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            market_data.search(
                conditions=[['asset', '=', 'test']],
                fields=['everysk_id', 'asset'],
                order_by='-everysk_id',
                limit=10,
                date='2023-08-14'
            )

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    ###############################################################################
    #  Get Currencies Test Case Implementation
    ###############################################################################
    def test_get_currencies_is_called(self):
        market_data = MarketData()
        expected_content = compress({
            'class_name': 'MarketData',
            'method_name': 'get_currencies',
            'self_obj': market_data.to_dict(add_class_path=True),
            'params': {}
        }, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            market_data.get_currencies()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

@mock.patch.dict('os.environ', {'MARKET_DATA_PUBLIC_URL': 'http://localhost:8080'})
class MarketDataPublicTestCase(TestCase):
    # pylint: disable=protected-access

    @classmethod
    def setUpClass(cls):
        cls.server_url = 'http://localhost:8080'
        cls.server = ThreadingHTTPServer(('localhost', 8080), SilentHTTPRequestHandler)
        cls.server_thread = Thread(target=cls.server.serve_forever)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()

    def setUp(self):
        self.market_data = MarketDataPublic()

    def test_defaults(self):
        self.assertEqual(self.market_data.cache_timeout, 60 * 60 * 24)
        self.assertEqual(self.market_data.http_timeout, 30)

    def test_get_server_url(self):
        self.assertEqual(
            self.market_data._get_server_url(),
            settings.MARKET_DATA_PUBLIC_URL
        )

    def test_get_response(self):
        params = {'limit': '1', 'test': 'value'}
        self.assertDictEqual(
            self.market_data._get_response(url=f'{self.server_url}/response', params=params),
            {'path': '/response', 'query_data': params}
        )

    def test_get_response_cache(self):
        self.assertDictEqual(
            self.market_data._get_response(url=f'{self.server_url}/response', params={'test': 'value'}),
            {'path': '/response', 'query_data': {'test': 'value'}}
        )

    def test_get_countries(self):
        self.assertDictEqual(
            self.market_data.get_countries(),
            {'path': '/countries', 'query_data': {'limit': '*', 'order_by': 'code__asc'}}
        )

    def test_get_cryptos(self):
        self.assertDictEqual(
            self.market_data.get_cryptos(),
            {'path': '/cryptos', 'query_data': {'limit': '*', 'order_by': 'code__asc'}}
        )

    def test_get_currencies(self):
        self.assertDictEqual(
            self.market_data.get_currencies(),
            {'path': '/currencies', 'query_data': {'limit': '*', 'order_by': 'code__asc'}}
        )

    def test_get_exchanges(self):
        self.assertDictEqual(
            self.market_data.get_exchanges(),
            {'path': '/exchanges', 'query_data': {'limit': '*', 'order_by': 'mic__asc'}}
        )

    def test_get_holidays(self):
        self.assertDictEqual(
            self.market_data.get_holidays(),
            {'path': '/holidays', 'query_data': {'limit': '*', 'order_by': 'date__asc'}}
        )
