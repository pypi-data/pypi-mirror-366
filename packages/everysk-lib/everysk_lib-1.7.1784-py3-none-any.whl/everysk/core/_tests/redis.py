###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# pylint: disable=protected-access
from concurrent.futures import ThreadPoolExecutor
from os import environ
from time import sleep
from uuid import uuid4
from redis import exceptions, client # pylint: disable=import-self

from everysk.config import settings, SettingsManager
from everysk.core import redis as redis_module
from everysk.core.redis import (
    RedisCache, RedisCacheCompressed, RedisChannel, RedisClient,
    RedisEmptyListError, RedisList, RedisLock, cache
)
from everysk.core.unittests import TestCase, mock


@cache(timeout=1)
def sum(a: int, b: int = 0) -> int: # pylint: disable=redefined-builtin
    return a + b


class CacheDecoratorTestCase(TestCase):

    def setUp(self) -> None:
        self.obj = RedisCache()
        self.obj.flush_all()

    def test_timeout_value_not_int(self):
        with self.assertRaises(ValueError) as context:
            cache(timeout='1')

        self.assertEqual(str(context.exception), 'Timeout must be an integer greater than 0.')

    def test_timeout_value_zero(self):
        with self.assertRaises(ValueError) as context:
            cache(timeout=0)

        self.assertEqual(str(context.exception), 'Timeout must be an integer greater than 0.')

    def test_timeout_value_negative(self):
        with self.assertRaises(ValueError) as context:
            cache(timeout=-1)

        self.assertEqual(str(context.exception), 'Timeout must be an integer greater than 0.')

    def test_cache_decorator(self):
        self.assertEqual(sum(1, 1), 2)
        self.assertEqual(sum(1, 1), 2)
        self.assertListEqual(
            self.obj.connection.keys(),
            [b'sum:e718fe8edf8a7c2917cd7444286b7048042a74abf5208f1d70933c08dbd6b7e9']
        )
        self.assertDictEqual(sum.info, {'hits': 1, 'misses': 1})
        sleep(1.1)
        self.assertEqual(sum(1, 1), 2)
        self.assertDictEqual(sum.info, {'hits': 1, 'misses': 2})
        self.assertEqual(sum(a=1, b=1), 2)
        self.assertDictEqual(sum.info, {'hits': 1, 'misses': 3})
        self.assertEqual(sum(1), 1)
        self.assertDictEqual(sum.info, {'hits': 1, 'misses': 4})

    def test_cache_decorator_clear(self):
        self.obj.set('key', 1)
        self.assertEqual(sum(1, 1), 2)
        self.assertEqual(sum(1, 2), 3)
        self.assertEqual(sum(1, 3), 4)
        self.assertListEqual(
            sorted(self.obj.connection.keys()),
            [
                b'2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683',
                b'sum:3a316d6d3226f84c1e46e4447fa8d5fd800bff4a1bc6498152523cd4a602b69b',
                b'sum:4e3970018fa500922ce5c087f84c734d7b47b0651da2f2e17226801885838032',
                b'sum:e718fe8edf8a7c2917cd7444286b7048042a74abf5208f1d70933c08dbd6b7e9',
            ]
        )
        sum.clear()
        self.assertListEqual(self.obj.connection.keys(), [b'2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683'])


class RedisClientTestCase(TestCase):

    def setUp(self) -> None:
        RedisClient._connection = {}

    @mock.patch.object(redis_module, 'log')
    def test_environ(self, log: mock.MagicMock):
        environ['REDIS_HOST'] = '0.1.0.1'
        environ['REDIS_PORT'] = '1234'
        redis = RedisClient()
        self.assertEqual(redis.host, environ['REDIS_HOST'])
        self.assertEqual(redis.port, int(environ['REDIS_PORT']))
        del environ['REDIS_HOST']
        del environ['REDIS_PORT']
        log.debug.assert_called_once_with('Connecting on Redis(%s:%s).....', redis.host, redis.port)

    @mock.patch.object(redis_module, 'log')
    def test_connection_property(self, log: mock.MagicMock):
        redis = RedisClient()
        self.assertEqual(redis.connection, redis._connection[redis._connection_key()])
        self.assertEqual(redis.connection, RedisClient._connection[redis._connection_key()])
        log.debug.assert_called_once()

    @mock.patch.object(redis_module, 'log')
    def test_hash_key(self, log: mock.MagicMock):
        redis = RedisClient()
        self.assertEqual(
            redis.get_hash_key('a'),
            'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'
        )
        # Check again to guarantee the same hash
        self.assertEqual(
            redis.get_hash_key('a'),
            'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'
        )
        log.debug.assert_called_once()

    @mock.patch.object(redis_module, 'log')
    def test_connect(self, log: mock.MagicMock):
        redis = RedisClient()
        log.debug.assert_called_once()
        RedisClient._connection = {}
        self.assertIsNone(RedisClient._connection.get(redis._connection_key(), None))
        redis._connect()
        self.assertIsNotNone(RedisClient._connection[redis._connection_key()])

    @mock.patch.object(RedisClient, '_connect')
    def test_connection_error_connection(self, _connect: mock.MagicMock):
        obj = RedisClient()
        redis_mock = mock.MagicMock(spec=redis_module.Redis)
        redis_mock.ping.side_effect = exceptions.ConnectionError
        with mock.patch.object(RedisClient, '_connection', {obj._connection_key(): redis_mock}) as _connection:
            connection = obj.connection # pylint: disable=unused-variable
        _connection[obj._connection_key()].ping.assert_called_once_with()
        _connect.assert_has_calls((mock.call(), mock.call()))

    @mock.patch.object(redis_module.log, 'debug', mock.MagicMock)
    def test_flush_all(self):
        cli = RedisClient()
        # Generate a random key to test
        key = uuid4().hex
        with SettingsManager(settings):
            settings.REDIS_SHOW_LOGS = True
            cli.connection.set(key, 'Flush-test')
            with mock.patch.object(redis_module.log, 'info') as debug:
                cli.flush_all()
            debug.assert_called_once_with('Redis flushed all keys.')
            self.assertIsNone(cli.connection.get(key))

            cli.connection.set(key, 'Flush-test')
            with mock.patch.object(redis_module.log, 'error') as debug:
                redis_mock = mock.MagicMock(spec=redis_module.Redis)
                redis_mock.flushall.return_value = 0
                with mock.patch.object(RedisClient, '_connection', {cli._connection_key(): redis_mock}) as _connect:
                    cli.flush_all()
            debug.assert_called_once_with('Redis flush all keys failed.')
            self.assertEqual(cli.connection.get(key), b'Flush-test')

    @mock.patch.object(redis_module.log, 'debug', mock.MagicMock)
    def test_build_prefix(self):
        cli = RedisClient(prefix='test')
        self.assertEqual(cli._build_prefix(), cli.prefix)
        self.assertEqual(cli._build_prefix('prefix'), 'prefix')

        with SettingsManager(settings):
            settings.REDIS_NAMESPACE = 'namespace'
            self.assertEqual(cli._build_prefix('prefix'), 'namespace:prefix')
            self.assertEqual(cli._build_prefix(), f'namespace:{cli.prefix}')
            settings.REDIS_NAMESPACE = None
            self.assertEqual(cli._build_prefix('prefix'), 'prefix')
            self.assertEqual(cli._build_prefix(), cli.prefix)

    @mock.patch.object(redis_module.log, 'debug', mock.MagicMock)
    def test_get_hash_key(self):
        cli = RedisClient()
        self.assertEqual(
            cli.get_hash_key('a'),
            'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'
        )
        # Check again to guarantee the same hash
        self.assertEqual(
            cli.get_hash_key('a'),
            'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'
        )
        self.assertRaisesRegex(
            ValueError,
            'Key cannot be None.',
            cli.get_hash_key,
            None
        )

@mock.patch.object(redis_module, 'log', mock.MagicMock())
class RedisCacheTestCase(TestCase):

    def setUp(self) -> None:
        RedisClient._connection = {}

    def tearDown(self):
        # Clean up the Redis cache after each test
        obj = RedisCache()
        obj.flush_all()

    def test_get_hash_key(self):
        obj = RedisCache()
        hash_key = '2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683'
        self.assertEqual(obj.get_hash_key('key'), hash_key)
        # Must always be the same value
        self.assertEqual(obj.get_hash_key('key'), hash_key)

    def test_get_set_delete(self):
        obj = RedisCache()
        obj.delete('key')
        self.assertIsNone(obj.get('key'))
        obj.set('key', 'My value.')
        self.assertEqual(obj.get('key'), b'My value.')
        obj.set('key', 1)
        self.assertEqual(obj.get('key'), b'1')
        obj.set('key', b'1.1')
        self.assertEqual(obj.get('key'), b'1.1')
        obj.delete('key')
        self.assertIsNone(obj.get('key'))

    def test_set_error(self):
        obj = RedisCache()
        self.assertRaises(exceptions.DataError, obj.set, 'key', ())
        self.assertRaises(exceptions.DataError, obj.set, 'key', [])
        self.assertRaises(exceptions.DataError, obj.set, 'key', {})
        self.assertRaises(exceptions.DataError, obj.set, 'key', obj)

    def test_prefix(self):
        key = b'prefix:2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683'
        obj = RedisCache(prefix='prefix')
        self.assertNotIn(key, obj.connection.keys())
        obj.set('key', 1)
        self.assertIn(key, obj.connection.keys())
        obj.delete('key')
        self.assertNotIn(key, obj.connection.keys())

    def test_delete_prefix(self):
        keys = [
            b'other:2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683',
            b'prefix:cd42404d52ad55ccfa9aca4adc828aa5800ad9d385a0671fbcbf724118320619',
            b'prefix:2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683',
        ]
        # Create a key with another prefix
        obj = RedisCache(prefix='other')
        obj.flush_all()
        obj.set('key', 1)

        obj = RedisCache(prefix='prefix')
        obj.set('key', 1)
        obj.set('value', 1)
        self.assertListEqual(sorted(obj.connection.keys()), sorted(keys))

        # Delete the key with other
        obj.delete_prefix(prefix='other')
        self.assertListEqual(sorted(obj.connection.keys()), sorted(keys[1:]))

        # Delete keys with prefix
        obj.delete_prefix()
        self.assertListEqual(obj.connection.keys(), [])

    def test_get_multi(self):
        obj = RedisCache()
        obj.set_multi({
            'key1': 1,
            'key2': 2,
            'key3': 3,
        })
        self.assertDictEqual(
            obj.get_multi(['key1', 'key2', 'key3']),
            {'key1': b'1', 'key2': b'2', 'key3': b'3'}
        )
        self.assertDictEqual(
            obj.get_multi(['key1', 'key2']),
            {'key1': b'1', 'key2': b'2'}
        )
        self.assertDictEqual(
            obj.get_multi(['key4']),
            {'key4': None}
        )

    def test_set_multi_error(self):
        obj = RedisCache()
        data = {
            'key1': 1,
            'key2': 2,
            'key3': 3,
        }
        redis_mock = mock.MagicMock(spec=redis_module.Redis)
        redis_mock.pipeline.return_value.execute.return_value = [True, True, False]
        with mock.patch.object(RedisClient, '_connection', {obj._connection_key(): redis_mock}) as _connection:
            with mock.patch.object(redis_module.log, 'error') as error:
                obj.set_multi(data)
            error.assert_called_once_with('Error RedisCache set_multi', extra={
                'labels': {
                    'REDIS_NAMESPACE': settings.REDIS_NAMESPACE,
                    'data': data,
                    'time': obj.timeout_default
            }})

    def test_delete_multi(self):
        obj = RedisCache()
        obj.set_multi({
            'key1': 1,
            'key2': 2,
            'key3': 3,
        })
        self.assertDictEqual(
            obj.get_multi(['key1', 'key2', 'key3']),
            {'key1': b'1', 'key2': b'2', 'key3': b'3'}
        )
        self.assertTrue(obj.delete_multi(['key1', 'key2']))
        self.assertDictEqual(
            obj.get_multi(['key1', 'key2']),
            {'key1': None, 'key2': None}
        )
        self.assertDictEqual(
            obj.get_multi(['key3']),
            {'key3': b'3'}
        )
        self.assertFalse(obj.delete_multi([]))
        self.assertTrue(obj.delete_multi('key3'))
        self.assertFalse(obj.delete_multi(['key3']))

    def test_incr(self):
        obj = RedisCache()
        self.assertEqual(obj.incr('key', initial_value=0), 1)
        self.assertEqual(obj.incr('key', initial_value=0), 2)
        self.assertEqual(obj.incr('key', delta=2, initial_value=0), 4)
        self.assertEqual(obj.incr('key', delta=2, initial_value=0), 6)
        self.assertEqual(obj.get('key'), b'6')

        self.assertRaisesRegex(
            ValueError,
            'Initial value must be set.',
            obj.incr,
            'key',
        )

        redis_mock = mock.MagicMock(spec=redis_module.Redis)
        redis_mock.pipeline.return_value.execute.return_value = [None, None]
        with mock.patch.object(RedisClient, '_connection', {obj._connection_key(): redis_mock}) as _connection:
            with mock.patch.object(redis_module.log, 'error') as error:
                obj.incr('key', initial_value=0)
        error.assert_called_once_with('Error RedisCache incr', extra={
            'labels': {
                'REDIS_NAMESPACE': settings.REDIS_NAMESPACE,
                'key': 'key',
                'delta': 1,
                'initial_value': 0,
            }
        })

    def test_decr(self):
        obj = RedisCache()
        self.assertEqual(obj.decr('key_1', initial_value=0), 0)
        self.assertEqual(obj.decr('key', initial_value=5), 4)
        self.assertEqual(obj.decr('key', delta=2, initial_value=0), 2)
        self.assertEqual(obj.decr('key', delta=2, initial_value=0), 0)
        self.assertEqual(obj.get('key'), b'0')

        self.assertRaisesRegex(
            ValueError,
            'Initial value must be set.',
            obj.decr,
            'key',
        )

        redis_mock = mock.MagicMock(spec=redis_module.Redis)
        redis_mock.pipeline.return_value.__enter__.return_value.get.return_value = 5
        redis_mock.pipeline.return_value.__enter__.return_value.execute.side_effect = (exceptions.WatchError, [4])
        with mock.patch.object(RedisClient, '_connection', {obj._connection_key(): redis_mock}) as _connection:
            ret = obj.decr('key', initial_value=0)

        self.assertEqual(ret, 4)

    def test_rpush(self):
        obj = RedisCache()
        self.assertEqual(obj.rpush('key', 1), True)
        self.assertEqual(obj.rpush('key', 2, 3), True)
        self.assertListEqual(obj.lrange('key', 0, -1), [b'1', b'2', b'3'])

        redis_mock = mock.MagicMock(spec=redis_module.Redis)
        redis_mock.pipeline.return_value.__enter__.return_value.execute.return_value = (4)
        with mock.patch.object(RedisClient, '_connection', {obj._connection_key(): redis_mock}) as _connection:
            obj.rpush('key', 2, timeout=1)
        _connection[obj._connection_key()].pipeline.return_value.__enter__.return_value.expire.assert_called_once_with(obj.get_hash_key('key'), 1)

    def test_hset(self):
        obj = RedisCache()
        self.assertEqual(obj.hset('key', 'field_1', 1), True)
        self.assertEqual(obj.hset('key', 'field_2', 2), True)
        self.assertEqual(obj.hset('key', 'field_3', 3), True)
        self.assertEqual(obj.hgetall('key'), {b'field_1': b'1', b'field_2': b'2', b'field_3': b'3'})
        self.assertEqual(obj.hset('key', 'field_1', 'test'), True)
        self.assertEqual(obj.hgetall('key'), {b'field_1': b'test', b'field_2': b'2', b'field_3': b'3'})

        redis_mock = mock.MagicMock(spec=redis_module.Redis)
        redis_mock.pipeline.return_value.__enter__.return_value.execute.return_value = (4)
        with mock.patch.object(RedisClient, '_connection', {obj._connection_key(): redis_mock}) as _connection:
            obj.hset('key', 'field', 2, timeout=1)
        _connection[obj._connection_key()].pipeline.return_value.__enter__.return_value.expire.assert_called_once_with(obj.get_hash_key('key'), 1)

class RedisCacheGetSetTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        RedisClient._connection = {}
        with mock.patch.object(redis_module.log, 'debug') as debug:
            cls.cache = RedisCache()
            debug.assert_called_once_with('Connecting on Redis(%s:%s).....', cls.cache.host, cls.cache.port)

        cls.key = 'redis-get-set-test-case'

    def setUp(self) -> None:
        self.cache.delete(self.key)
        self.mock = mock.MagicMock()

    def func(self, **kwargs):
        sleep(0.1)
        self.mock(**kwargs)
        return f'return: {kwargs}'

    def test_redis_get_set(self):
        obj01 = RedisCache()
        obj02 = RedisCache()
        with ThreadPoolExecutor() as executor:
            task01 = executor.submit(obj01.get_set, key=self.key, func=self.func, keyword='value01')
            sleep(0.05) # This is just to guarantee that value1 will always be called first
            task02 = executor.submit(obj02.get_set, key=self.key, func=self.func, keyword='value02')
            self.assertEqual(task01.result(), task02.result())
        self.mock.assert_called_once_with(keyword='value01')

    @mock.patch.object(redis_module.log, 'error')
    def test_get_set_func_error_both_exit(self, error: mock.MagicMock):
        """
        This test is to check if the error is raised when multiple threads
        are trying to access the same key and the function raises an error.
        The first thread will raise the error and the second thread will
        return None.
        """
        self.mock.side_effect = AttributeError
        obj01 = RedisCache()
        obj02 = RedisCache()
        with ThreadPoolExecutor() as executor:
            task01 = executor.submit(obj01.get_set, key=self.key, func=self.func, keyword='value01')
            sleep(0.05) # This is just to guarantee that value1 will always be called first
            task02 = executor.submit(obj02.get_set, key=self.key, func=self.func, keyword='value02')
            self.assertIsNone(task01.result())
            self.assertIsNone(task02.result())

        self.mock.assert_called_once_with(keyword='value01')
        error.assert_called_once()

    @mock.patch.object(redis_module.log, 'error')
    def test_get_set_func_error(self, error: mock.MagicMock):
        self.mock.side_effect = AttributeError
        result = RedisCache().get_set(key=self.key, func=self.func)
        self.assertIsNone(result)
        self.mock.assert_called_once_with()
        error.assert_called_once()


@mock.patch.object(redis_module, 'log', mock.MagicMock())
class RedisCacheCompressedTestCase(TestCase):

    def setUp(self) -> None:
        RedisClient._connection = {}

    def test_get_hash_key(self):
        obj = RedisCacheCompressed()
        hash_key = '2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683'
        self.assertEqual(obj.get_hash_key('key'), hash_key)
        # Must always be the same value
        self.assertEqual(obj.get_hash_key('key'), hash_key)

    def test_get_set_delete(self):
        obj = RedisCacheCompressed()
        self.assertIsNone(obj.get('key'))
        lst = [1, 'test', 1.1, {'key': 'value'}]
        obj.set('key', lst)
        self.assertListEqual(obj.get('key'), lst)
        dct = {'lst': [1, 't'], 'dct': {'key': 'value'}, 'key': 1}
        obj.set('key', dct)
        self.assertDictEqual(obj.get('key'), dct)
        obj.delete('key')
        self.assertIsNone(obj.get('key'))


@mock.patch.object(redis_module, 'log', mock.MagicMock())
class RedisListTestCase(TestCase):

    def setUp(self) -> None:
        RedisClient._connection = {}
        self.name = 'redis-list-test-case'

    def test_push_pop(self):
        lst = RedisList(name=self.name)
        lst.clear() # Clear all elements
        self.assertRaises(RedisEmptyListError, lst.pop)
        obj = {'lst': [1, 1.1, 'test', True]}
        lst.push(obj)
        self.assertEqual(lst.pop(), obj)

    def test_bpop_timeout(self):
        lst = RedisList(name=self.name)
        lst.clear() # Clear all elements
        self.assertRaises(RedisEmptyListError, lst.bpop, 0.5)

    def test_bpop(self):
        lst = RedisList(name=self.name)
        lst.clear() # Clear all elements
        obj = {'lst': [1, 1.1, 'test', True]}
        lst.push(obj)
        self.assertTupleEqual(lst.bpop(0.5), (self.name, obj))

    def test_clear(self):
        lst = RedisList(name=self.name)
        lst.clear() # Clear all elements
        self.assertRaises(RedisEmptyListError, lst.pop)
        obj = {'lst': [1, 1.1, 'test', True]}
        lst.push(obj)
        lst.clear()
        self.assertRaises(RedisEmptyListError, lst.pop)


@mock.patch.object(redis_module, 'log', mock.MagicMock())
@mock.patch.object(RedisChannel, '_channel', spec=client.PubSub)
class RedisChannelTestCase(TestCase):

    def setUp(self) -> None:
        self.name = 'tests'
        RedisClient._connection = {}

    def test_send(self, _channel: mock.MagicMock):
        channel = RedisChannel(name=self.name)
        redis_mock = mock.MagicMock(spec=redis_module.Redis)
        with mock.patch.object(RedisClient, '_connection', {channel._connection_key(): redis_mock}) as _connection:
            channel.send('Hi')
        _connection[channel._connection_key()].publish.assert_called_once_with(channel.name, 'Hi')
        _channel.assert_not_called()

    def test_channel(self, _channel: mock.MagicMock):
        channel = RedisChannel(name=self.name)
        redis_mock = mock.MagicMock(spec=redis_module.Redis)
        redis_mock.pubsub.return_value = _channel
        with mock.patch.object(RedisClient, '_connection', {channel._connection_key(): redis_mock}) as _connection:
            channel._channel = None
            channel.channel # Call the property - pylint: disable=pointless-statement
        _connection[channel._connection_key()].pubsub.assert_called_once_with()
        _channel.subscribe.assert_called_once_with(channel.name)

    def test_parse_message(self, _channel: mock.MagicMock):
        channel = RedisChannel(name=self.name)
        message = {'channel': self.name.encode('utf-8'), 'data': b'data'}
        self.assertTupleEqual(channel.parse_message(message), (self.name, 'data'))
        _channel.assert_not_called()

    def test_consume_process_message(self, _channel: mock.MagicMock):
        channel = RedisChannel(name=self.name)
        message = {'channel': self.name.encode('utf-8'), 'data': b'data'}
        _channel.listen.return_value = [message]
        channel.process_message = mock.MagicMock()
        channel.consume()
        channel.process_message.assert_called_once_with('data')

    def test_process(self, _channel: mock.MagicMock):
        channel = RedisChannel(name=self.name)
        self.assertIsNone(channel.process_message('data'))
        _channel.assert_not_called()

    def test_consume_callback(self, _channel: mock.MagicMock):
        channel = RedisChannel(name=self.name)
        message = {'channel': self.name.encode('utf-8'), 'data': b'data'}
        _channel.listen.return_value = [message]
        callback = mock.MagicMock()
        channel.consume(callback)
        callback.assert_called_once_with('data')

    def test_consume_break(self, _channel: mock.MagicMock):
        channel = RedisChannel(name=self.name)
        message = {'channel': self.name.encode('utf-8'), 'data': b'data'}
        exit_message = {'channel': self.name.encode('utf-8'), 'data': RedisChannel.exit_message}
        _channel.listen.return_value = [exit_message, message]
        callback = mock.MagicMock()
        channel.consume(callback)
        callback.assert_not_called()


@mock.patch.object(redis_module, 'log', mock.MagicMock())
class RedisLockTestCase(TestCase):

    def setUp(self) -> None:
        self.name = 'tests'
        RedisClient._connection = {}

    def tearDown(self) -> None:
        RedisLock(name=self.name).release(force=True)

    def test_acquire(self):
        lock01 = RedisLock(name=self.name)
        lock02 = RedisLock(name=self.name)
        self.assertTrue(lock01.acquire(blocking=False))
        self.assertFalse(lock02.acquire(blocking=False))
        self.assertIsNone(lock01.release())
        self.assertIsNone(lock01.token)

        self.assertTrue(lock01.acquire(token='test', blocking=False))
        self.assertEqual(lock01.token, 'test')

    @mock.patch('everysk.core.redis.RedisLock._get_lock', spec=redis_module.Redis.lock)
    def test_acquire_blocking(self, lock: mock.MagicMock):
        lock01 = RedisLock(name=self.name)
        lock01.acquire(blocking_timeout=1.0)
        lock.return_value.acquire.assert_called_once_with(token=lock01._encode_token(), blocking=None, blocking_timeout=1.0)

    def test_timeout(self):
        lock01 = RedisLock(name=self.name, timeout=1)
        lock02 = RedisLock(name=self.name, timeout=1)
        self.assertTrue(lock01.acquire(blocking=False))
        self.assertFalse(lock02.acquire(blocking=False))
        sleep(1.5) # With 1 second the test breaks sometimes
        self.assertTrue(lock02.acquire(blocking=False))

    def test_owned(self):
        lock01 = RedisLock(name=self.name)
        lock02 = RedisLock(name=self.name)
        lock01.acquire(blocking=False)
        lock02.acquire(blocking=False)
        self.assertTrue(lock01.owned())
        self.assertFalse(lock02.owned())

    def test_release(self):
        lock01 = RedisLock(name=self.name)
        lock02 = RedisLock(name=self.name)
        lock01.acquire(blocking=False)
        lock02.acquire(blocking=False)
        self.assertRaisesRegex(
            exceptions.LockError,
            'Cannot release an unlocked lock',
            lock02.release
        )
        self.assertFalse(lock02.acquire(blocking=False))
        self.assertIsNone(lock01.release())
        self.assertTrue(lock02.acquire(blocking=False))

    def test_release_force(self):
        lock01 = RedisLock(name=self.name)
        lock02 = RedisLock(name=self.name)
        lock01.acquire(blocking=False)
        lock02.acquire(blocking=False)
        self.assertIsNone(lock02.release(force=True))
        self.assertTrue(lock02.acquire(blocking=False))
        self.assertRaisesRegex(
            exceptions.LockError,
            'Cannot release a lock that\'s no longer owned',
            lock01.release
        )
        self.assertFalse(lock01.acquire(blocking=False))

    def test_encode_token(self):
        lock = RedisLock(name=self.name)
        self.assertEqual(lock._encode_token('token'), b'redis-lock:3c469e9d6c5875d37a43f353d4f88e61fcf812c66eee3457465a40b0da4153e0')
        self.assertRaisesRegex(
            exceptions.LockError,
            'Cannot encode an empty token',
            lock._encode_token,
        )

    def test_do_release(self):
        lock01 = RedisLock(name=self.name)
        lock02 = RedisLock(name=self.name)
        self.assertTrue(lock01.acquire(token='test', blocking=False))
        self.assertIsNone(lock02.do_release(expected_token='test'))
        self.assertTrue(lock02.acquire(token='test', blocking=False))
        self.assertRaisesRegex(
            exceptions.LockError,
            'Cannot release an unlocked lock',
            lock01.do_release,
            expected_token=None
        )
        lock02.name = 'test2'
        self.assertIsNone(lock02.do_release(expected_token='token_2'))

    def test_get_lock_info(self):
        lock = RedisLock(name=self.name)
        self.assertEqual(lock.get_lock_info(), {
            'locked': False,
            'name': lock.name
        })
        self.assertTrue(lock.acquire(blocking=False))
        self.assertEqual(lock.get_lock_info(), {
            'locked': True,
            'name': lock.name
        })
