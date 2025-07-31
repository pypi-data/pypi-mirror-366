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
from everysk.config import settings
from everysk.core.http import httpx
from everysk.core.compress import compress
from everysk.core.exceptions import InvalidArgumentError
from everysk.core.unittests import TestCase, mock
from everysk.sdk.base import HttpSDKPOSTConnection
from everysk.sdk.engines.lock import UserLock

###############################################################################
#   Get Method Test Case Implementation
###############################################################################
class UserLockTestCase(TestCase):

    def setUp(self):
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()

    def test_initialization(self):
        user_lock = UserLock(name='test_lock')
        self.assertIsInstance(user_lock, UserLock)
        self.assertEqual(user_lock.name, 'test_lock')
        self.assertEqual(user_lock.timeout, settings.USER_CACHE_LOCK_EXPIRATION_TIME)
        self.assertTrue(user_lock.blocking)
        self.assertIsNone(user_lock.token)

        user_lock = UserLock(name='test_lock')
        user_lock.name = 'test_lock_1'
        user_lock.timeout = 20.0
        user_lock.blocking = False
        user_lock.token = 'test_token'
        self.assertEqual(user_lock.name, 'test_lock_1')
        self.assertEqual(user_lock.timeout, 20.0)
        self.assertFalse(user_lock.blocking)
        self.assertEqual(user_lock.token, 'test_token')

        user_lock = UserLock(name='test_lock', timeout=15.0, blocking=False, token='test_token')
        self.assertEqual(user_lock.name, 'test_lock')
        self.assertEqual(user_lock.timeout, 15.0)
        self.assertFalse(user_lock.blocking)
        self.assertEqual(user_lock.token, 'test_token')

    def test_acquire(self):
        test_name = 'port_xyz'
        user_cache_lock: UserLock = UserLock(name=test_name)
        with mock.patch('httpx.Client.post') as mock_get_response:
            mock_get_response.return_value.content = 'true'
            mock_get_response.return_value.status_code = 200
            ret = user_cache_lock.acquire()

        self.assertTrue(ret)
        mock_get_response.assert_called_once_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=compress({'class_name': 'UserLock', 'method_name': 'acquire', 'self_obj': user_cache_lock.to_dict(add_class_path=True), 'params': {'token': None, 'blocking': None, 'blocking_timeout': None}}, protocol='gzip', serialize='json')
        )

        test_name = 'port_xyz'
        test_token = 'test_token'
        user_cache_lock: UserLock = UserLock(name=test_name)
        with mock.patch('httpx.Client.post') as mock_get_response:

            mock_get_response.return_value.content = 'true'
            mock_get_response.return_value.status_code = 200
            ret = user_cache_lock.acquire(token=test_token)

        self.assertTrue(ret)
        mock_get_response.assert_called_once_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=compress({'class_name': 'UserLock', 'method_name': 'acquire', 'self_obj': user_cache_lock.to_dict(add_class_path=True), 'params': {'token':test_token, 'blocking': None, 'blocking_timeout': None}}, protocol='gzip', serialize='json')
        )

    def test_release(self):
        test_name = 'port_xyz'

        user_cache_lock: UserLock = UserLock(name=test_name)
        self.assertRaisesRegex(
            InvalidArgumentError,
            'Cannot release an unlocked lock',
            user_cache_lock.release
        )

        user_cache_lock.token = 'test_token'
        with mock.patch('httpx.Client.post') as mock_get_response:
            mock_get_response.return_value.content = 'null'
            mock_get_response.return_value.status_code = 200
            ret = user_cache_lock.release()

        self.assertIsNone(ret)
        mock_get_response.assert_called_once_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=compress({'class_name': 'UserLock', 'method_name': 'release', 'self_obj': user_cache_lock.to_dict(add_class_path=True), 'params': {'force': False}}, protocol='gzip', serialize='json')
        )

    def test_do_release(self):
        test_name = 'port_xyz'
        expected_token = 'test_token'
        user_cache_lock: UserLock = UserLock(name=test_name)

        self.assertRaisesRegex(
            InvalidArgumentError,
            'Cannot release an unlocked lock',
            user_cache_lock.do_release,
            expected_token=None,
        )

        with mock.patch('httpx.Client.post') as mock_get_response:
            mock_get_response.return_value.content = 'null'
            mock_get_response.return_value.status_code = 200
            ret = user_cache_lock.do_release(expected_token=expected_token)

        self.assertIsNone(ret)
        mock_get_response.assert_called_once_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=compress({'class_name': 'UserLock', 'method_name': 'do_release', 'self_obj': user_cache_lock.to_dict(add_class_path=True), 'params': {'expected_token': expected_token}}, protocol='gzip', serialize='json')
        )

    def test_get_lock_info(self):
        test_name = 'port_xyz'
        user_cache_lock: UserLock = UserLock(name=test_name)
        with mock.patch('httpx.Client.post') as mock_get_response:
            mock_get_response.return_value.content = '{"locked": true, "name": "port_xyz"}'
            mock_get_response.return_value.status_code = 200
            ret = user_cache_lock.get_lock_info()

        self.assertIsInstance(ret, dict)
        self.assertDictEqual(ret, {'locked': True, 'name': test_name})
        mock_get_response.assert_called_once_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=compress({'class_name': 'UserLock', 'method_name': 'get_lock_info', 'self_obj': user_cache_lock.to_dict(add_class_path=True), 'params': {}}, protocol='gzip', serialize='json')
        )
