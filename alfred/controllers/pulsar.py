import logging
import time
import pulsar
from alfred.models import User

client = pulsar.Client("pulsar://localhost:6650")
logger = logging.getLogger(__name__)


class PulsarManager:
    def __init__(self):
        self.conn = client

    async def init_user_authorized_topics(self, current_user: User):
        """
        Subsribes the current_user to its preconfigured pulsar topics
        """
        topics = []
        for topic in current_user.authorized_pulsar_topics:
            consumer = self.conn.subscribe(topic, "shared")
            if consumer is not None:
                topics.append(topic)

        return {"initialized": topics}

    def publish_message(self, message, topic):
        producer = self.conn.create_producer(topic)
        producer.send(message.message)
        return {"topic": topic, "message": message.message, "status": "published"}

    async def consumer_generator(consumer):
        while True:
            msg = consumer.receive(2000)
            yield b"Received message '{}' id='{}'".format(msg.data(), msg.message_id())
            consumer.acknowledge(msg)
            time.sleep(1)
