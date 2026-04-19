import json
import logging
import time
import pika
from ..config import settings
from ..services import process_document

logger = logging.getLogger(__name__)

_MAX_RETRIES = 5
_RETRY_DELAY_SECONDS = 5


def start_consumer() -> None:
    """Start blocking RabbitMQ consumer. Runs in a background daemon thread."""
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            _connect_and_consume()
            return
        except Exception as e:
            logger.error("Consumer attempt %d/%d failed: %s", attempt, _MAX_RETRIES, e)
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_DELAY_SECONDS * attempt)

    logger.error("RabbitMQ consumer could not start after %d attempts", _MAX_RETRIES)


def _connect_and_consume() -> None:
    credentials = pika.PlainCredentials(settings.rabbitmq_user, settings.rabbitmq_password)
    params = pika.ConnectionParameters(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300,
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.rabbitmq_queue, on_message_callback=_on_message)
    logger.info("RabbitMQ consumer listening on queue: %s", settings.rabbitmq_queue)
    channel.start_consuming()


def _on_message(channel, method, properties, body) -> None:
    try:
        message = json.loads(body)
        document_id = message["documentId"]
        file_url = message["fileUrl"]
        file_type = message["fileType"]
        process_document(document_id, file_url, file_type)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error("Failed to handle message: %s", e)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
