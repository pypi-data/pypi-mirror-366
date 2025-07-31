import json
from typing import Iterable, List
from pickle import dumps, loads

from redis import Redis
from eric_sse import get_logger
from eric_sse.exception import NoMessagesException, RepositoryError
from eric_sse.message import MessageContract
from eric_sse.prefabs import SSEChannel
from eric_sse.queue import Queue
from eric_sse.connection import Connection, ConnectionRepositoryInterface, ChannelRepositoryInterface, ChannelInterface, ObjectPersistenceMixin

logger = get_logger()

_PREFIX = 'eric-redis-queues'
_PREFIX_QUEUES = f'eric-redis-queues:q'
_PREFIX_LISTENERS = f'eric-redis-queues:l'
_PREFIX_CHANNELS = f'eric-redis-queues:c'

class RedisQueue(Queue, ObjectPersistenceMixin):

    def __init__(self, listener_id: str, host='127.0.0.1', port=6379, db=0):
        self.__id: str | None = None
        self.__client: Redis | None = None

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
    def id(self) -> str:
        return self.__id

    @property
    def value_as_dict(self):
        return self.__value_as_dict

    def setup_by_dict(self, setup: dict):
        self.__id = setup['listener_id']
        self.__host = setup['host']
        self.__port = setup['port']
        self.__db = setup['db']
        self.__value_as_dict.update(setup)
        self.__client = Redis(host=self.__host, port=self.__port, db=self.__db)

    def pop(self) -> MessageContract:

        if not self.__client.exists(f'{_PREFIX_QUEUES}:{self.id}'):
            raise NoMessagesException

        try:
            raw_value = self.__client.lpop(f'{_PREFIX_QUEUES}:{self.id}')
            return loads(raw_value)

        except Exception as e:
            raise RepositoryError(e)


    def push(self, msg: MessageContract) -> None:
        try:
            self.__client.rpush(f'{_PREFIX_QUEUES}:{self.id}', dumps(msg))
        except Exception as e:
            raise RepositoryError(e)

class RedisConnectionsRepository(ConnectionRepositoryInterface):
    def __init__(self, host='127.0.0.1', port=6379, db=0):
        self.__host: str = host
        self.__port: int = port
        self.__db: int = db
        self.__client = Redis(host=host, port=port, db=db)

    def create_queue(self, listener_id: str) -> Queue:
        return RedisQueue(listener_id= listener_id, host=self.__host, port=self.__port, db=self.__db)

    def load(self) -> Iterable[Connection]:
        for redis_key in self.__client.scan_iter(f"{_PREFIX_LISTENERS}:*"):
            key = redis_key.decode()
            try:
                listener = loads(self.__client.get(key))
                queue = self.create_queue(listener_id=listener.id)
                yield Connection(listener=listener, queue=queue)
            except Exception as e:
                raise RepositoryError(e)


    def persist(self, connection: Connection) -> None:
        try:
            self.__client.set(f'{_PREFIX_LISTENERS}:{connection.listener.id}', dumps(connection.listener))
        except Exception as e:
            raise RepositoryError(e)

    def delete(self, listener_id: str):
        try:
            self.__client.delete(f'{_PREFIX_LISTENERS}:{listener_id}')
        except Exception as e:
            raise RepositoryError(e)
        try:
            self.__client.delete(f'{_PREFIX_QUEUES}:{listener_id}')
        except Exception as e:
            raise RepositoryError(e)



class RedisChannelRepository(ChannelRepositoryInterface):
    def __init__(self, host='127.0.0.1', port=6379, db=0):
        self.__host: str = host
        self.__port: int = port
        self.__db: int = db
        self.__client = Redis(host=host, port=port, db=db)

    def load(self) -> Iterable[SSEChannel]:
        try:
            connections_repository = RedisConnectionsRepository(host=self.__host, port=self.__port, db=self.__db)
            for redis_key in self.__client.scan_iter(f"{_PREFIX_CHANNELS}:*"):
                key = redis_key.decode()
                try:
                    channel_construction_params: dict[str] = json.loads(self.__client.get(key))
                    channel = SSEChannel(**channel_construction_params, connections_repository=connections_repository)

                    for connection in connections_repository.load():
                        channel.register_connection(listener=connection.listener, queue=connection.queue)

                    yield channel
                except Exception as e:
                    logger.error(repr(e))

        except Exception as e:
            raise RepositoryError(e)

    def persist(self, channel: ObjectPersistenceMixin):
        try:
            self.__client.set(f'{_PREFIX_CHANNELS}:{channel.id}', json.dumps(channel.value_as_dict()))
        except Exception as e:
            raise RepositoryError(e)

    def delete(self, channel_id: str):
        try:
            self.__client.delete(f'{_PREFIX_CHANNELS}:{channel_id}')
        except Exception as e:
            raise RepositoryError(e)
