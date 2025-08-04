Redis support for eric-sse

Example of usage:

    from eric_sse.prefabs import SSEChannel
    from eric_redis_queues import RedisConnectionsRepository
    
    c = SSEChannel(connections_repository=RedisConnectionsRepository())

Documentation: https://laxertu.github.io/eric-redis-queues/
