import abc
import json
from abc import ABC
from typing import Iterable, Any
from pickle import dumps, loads

from redis import Redis
from eric_sse import get_logger
from eric_sse.exception import NoMessagesException, RepositoryError
from eric_sse.message import MessageContract
from eric_sse.prefabs import SSEChannel
from eric_sse.queues import Queue
from eric_sse.persistence import (
    ConnectionRepositoryInterface, PersistableQueue,
    ChannelRepositoryInterface
)
from eric_sse.connection import Connection

logger = get_logger()

_PREFIX = 'eric-redis-queues'
_PREFIX_QUEUES = f'eric-redis-queues:q'
_PREFIX_LISTENERS = f'eric-redis-queues:l'
_PREFIX_CHANNELS = f'eric-redis-queues:c'

CONNECTION_REPOSITORY_DEFAULT = 'RedisConnectionsRepository'
CONNECTION_REPOSITORY_BLOCKING = 'RedisBlockingQueuesRepository'


class AbstractRedisQueue(PersistableQueue, ABC):

    def __init__(self, listener_id: str, host='127.0.0.1', port=6379, db=0):
        self.__id: str | None = None
        self._client: Redis | None = None

        self.__host: str | None = None
        self.__port: int | None = None
        self.__db: int | None = None
        self.__value_as_dict = {}

        self.setup_by_dict({
            'listener_id': listener_id,
            'host': host,
            'port': port,
            'db': db
        })

    @property
    def kv_key(self) -> str:
        return self.__id

    @property
    def kv_value_as_dict(self):
        return self.__value_as_dict

    def setup_by_dict(self, setup: dict):
        self.__id = setup['listener_id']
        self.__host = setup['host']
        self.__port = setup['port']
        self.__db = setup['db']
        self.__value_as_dict.update(setup)
        self._client = Redis(host=self.__host, port=self.__port, db=self.__db)

class RedisQueue(AbstractRedisQueue):


    def pop(self) -> Any | None:
        try:
            raw_value = self._client.lpop(f'{_PREFIX_QUEUES}:{self.kv_key}')
            if raw_value is None:
                raise NoMessagesException
            return loads(bytes(raw_value))

        except NoMessagesException:
            raise
        except Exception as e:
            raise RepositoryError(e)


    def push(self, msg: MessageContract) -> None:
        try:
            self._client.rpush(f'{_PREFIX_QUEUES}:{self.kv_key}', dumps(msg))
        except Exception as e:
            raise RepositoryError(e)

class BlockingRedisQueue(RedisQueue):
    """
    Implements a blocking queue.

    pop() behaviour relies on https://redis.io/docs/latest/commands/blpop/
    """

    def pop(self) -> Any | None:

        k, v = self._client.blpop([f'{_PREFIX_QUEUES}:{self.kv_key}'])
        return loads(bytes(v))

class AbstractRedisConnectionRepository(ConnectionRepositoryInterface, ABC):
    def __init__(self, host='127.0.0.1', port=6379, db=0):
        self._host: str = host
        self._port: int = port
        self._db: int = db
        self._client = Redis(host=host, port=port, db=db)

    @abc.abstractmethod
    def create_queue(self, listener_id: str) -> AbstractRedisQueue:
        ...

    def load_all(self) -> Iterable[Connection]:
        for redis_key in self._client.scan_iter(f"{_PREFIX_LISTENERS}:*"):
            key = redis_key.decode()
            try:
                listener = loads(self._client.get(key))
                queue = self.create_queue(listener_id=listener.id)
                yield Connection(listener=listener, queue=queue)
            except Exception as e:
                raise RepositoryError(e)

    def load(self, channel_id: str) -> Iterable[Connection]:
        for redis_key in self._client.scan_iter(f"{_PREFIX_LISTENERS}:{channel_id}:*"):
            key = redis_key.decode()
            try:
                listener = loads(self._client.get(key))
                queue = self.create_queue(listener_id=listener.id)
                yield Connection(listener=listener, queue=queue)
            except Exception as e:
                raise RepositoryError(e)

    def persist(self, channel_id:str,  connection: Connection) -> None:
        try:
            self._client.set(f'{_PREFIX_LISTENERS}:{channel_id}:{connection.listener.id}', dumps(connection.listener))
        except Exception as e:
            raise RepositoryError(e)

    def delete(self, channel_id: str, listener_id: str):
        """Deletes a listener given its channel id and listener id."""

        try:
            self._client.delete(f'{_PREFIX_LISTENERS}:{channel_id}:{listener_id}')
        except Exception as e:
            raise RepositoryError(e)
        try:
            key = f'{_PREFIX_QUEUES}:{listener_id}'
            self._client.delete(key)
        except Exception as e:
            raise RepositoryError(e)

class RedisConnectionsRepository(AbstractRedisConnectionRepository):

    def create_queue(self, listener_id: str) -> AbstractRedisQueue:
        return RedisQueue(listener_id= listener_id, host=self._host, port=self._port, db=self._db)

class RedisBlockingQueuesRepository(AbstractRedisConnectionRepository):

    def create_queue(self, listener_id: str) -> AbstractRedisQueue:
        return BlockingRedisQueue(listener_id= listener_id, host=self._host, port=self._port, db=self._db)


class RedisSSEChannelRepository(ChannelRepositoryInterface):


    def __init__(
            self, host='127.0.0.1', port=6379, db=0,
            connection_factory: str = CONNECTION_REPOSITORY_DEFAULT
    ):
        self.__host: str = host
        self.__port: int = port
        self.__db: int = db
        self.__client = Redis(host=host, port=port, db=db)


        self.__repositories_constructors = {
            CONNECTION_REPOSITORY_DEFAULT: RedisConnectionsRepository,
            CONNECTION_REPOSITORY_BLOCKING: RedisBlockingQueuesRepository,
        }

        self.__connection_factory = self.__create_repository(connection_factory)

    def __create_repository(self, class_name: str) -> ConnectionRepositoryInterface:
        try:
            constructor = self.__repositories_constructors[class_name]
        except KeyError as e:
            raise RepositoryError(f"Unknown repository class {class_name}") from e
        return constructor(host=self.__host, port=self.__port, db=self.__db)

    def load(self) -> Iterable[SSEChannel]:
        """Returns all channels from the repository."""
        try:
            for redis_key in self.__client.scan_iter(f"{_PREFIX_CHANNELS}:*"):
                key = redis_key.decode()
                try:
                    channel_construction_params: dict[str] = json.loads(self.__client.get(key))
                    connections_repository = self.__create_repository(channel_construction_params['connections_repository'])
                    channel_construction_params['connections_repository'] = connections_repository
                    channel = SSEChannel(**channel_construction_params)

                    for connection in connections_repository.load(channel.kv_key):
                        channel.register_connection(listener=connection.listener, queue=connection.queue)

                    yield channel
                except Exception as e:
                    logger.error(repr(e))

        except Exception as e:
            raise RepositoryError(e)

    def persist(self, persistable: SSEChannel):
        try:
            data_to_persist = persistable.kv_value_as_dict
            self.__client.set(f'{_PREFIX_CHANNELS}:{persistable.id}', json.dumps(data_to_persist))
        except Exception as e:
            raise RepositoryError(e)

    def delete(self, key: str):
        try:
            for listener_key in self.__client.scan_iter(f"{_PREFIX_LISTENERS}:{key}:*"):
                self.__connection_factory.delete(channel_id=key, listener_id=listener_key.decode().split(':')[3])

            self.__client.delete(f'{_PREFIX_CHANNELS}:{key}')
        except Exception as e:
            raise RepositoryError(e)

    def delete_listener(self, channel_id: str, listener_id: str) -> None:
        try:
            self.__client.delete(f'{_PREFIX_LISTENERS}:{channel_id}:{listener_id}')
        except Exception as e:
            raise RepositoryError(e)
