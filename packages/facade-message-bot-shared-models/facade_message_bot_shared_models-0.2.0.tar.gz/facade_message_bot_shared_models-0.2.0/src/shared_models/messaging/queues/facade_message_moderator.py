from faststream.rabbit import RabbitQueue, QueueType
from faststream.rabbit.schemas.queue import QuorumQueueArgs


facade_message_moderator_queue = RabbitQueue(
    "moderator.facade_message",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
    arguments=QuorumQueueArgs(
        {
            "x-dead-letter-exchange": "dlx",
            "x-dead-letter-routing-key": "moderator.facade_message.dlx",
            "x-dead-letter-strategy": "at-least-once",
        }
    ),
)

facade_message_moderator_dlx_queue = RabbitQueue(
    "moderator.facade_message.dlx",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
)
