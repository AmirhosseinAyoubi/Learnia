# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""RabbitMQ consumer for the Processing Service.

Connects to RabbitMQ on startup, declares the processing queue, and blocks
on ``start_consuming()``.  Reconnects up to ``_MAX_RETRIES`` times with
linear back-off if the initial connection fails.
"""
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
    """Start the blocking RabbitMQ consumer with retry logic.

    Attempts to connect up to ``_MAX_RETRIES`` times.  Each failed attempt
    waits ``_RETRY_DELAY_SECONDS * attempt`` seconds before retrying.
    Runs in a background daemon thread started by ``main.py``.
    """
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            _connect_and_consume()
            return
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Consumer attempt %d/%d failed: %s", attempt, _MAX_RETRIES, exc)
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_DELAY_SECONDS * attempt)

    logger.error("RabbitMQ consumer could not start after %d attempts", _MAX_RETRIES)


def _connect_and_consume() -> None:
    """Open a RabbitMQ connection and begin consuming messages.

    Declares the queue as durable and uses ``prefetch_count=1`` so that
    only one message is delivered at a time per consumer.
    """
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


def _on_message(channel, method, properties, body) -> None:  # pylint: disable=unused-argument
    """Handle a single RabbitMQ message.

    Parses the JSON body, delegates to ``process_document``, and ACKs on
    success.  Any exception causes the message to be NACKed without requeue
    so it does not block the queue indefinitely.

    Args:
        channel: The pika channel object (used for ACK/NACK).
        method: Delivery metadata containing the delivery tag.
        properties: AMQP message properties (unused).
        body: Raw message bytes expected to be a UTF-8 JSON object with
            ``documentId``, ``fileUrl``, and ``fileType`` fields.
    """
    try:
        message = json.loads(body)
        document_id = message["documentId"]
        file_url = message["fileUrl"]
        file_type = message["fileType"]
        process_document(document_id, file_url, file_type)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Failed to handle message: %s", exc)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
