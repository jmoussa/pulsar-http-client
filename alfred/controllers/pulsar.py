import logging
import time
import pulsar
from alfred.models import User

client = pulsar.Client("pulsar://localhost:6650")
logger = logging.getLogger(__name__)


class PulsarManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.conn = client
        self.consumers = {}
        self.producers = {}

    async def init_user_authorized_topics(self, current_user: User):
        """
        Subsribes the current_user to its preconfigured pulsar topics
        """
        topics = []
        for topic in current_user.authorized_pulsar_topics:
            self.consumers[topic] = self.conn.subscribe(topic, "shared")
            if self.consumers[topic] is not None:
                topics.append(topic)
        return {"initialized": topics}

    def publish_message(self, message, topic):
        self.producers[topic] = self.conn.create_producer(topic)
        if self.producers.get(topic, None):
            self.producers[topic].send(message.message)
            return {"topic": topic, "message": message.message, "status": "published"}
        else:
            return {"topic": topic, "message": "error creating producer", "status": "not published"}

    def subscribe(self, topic):
        self.consumers[topic] = self.conn.subscribe(topic, "shared")
        self.producers[topic] = self.conn.connect(topic)

    async def consumer_generator(self, topic):
        if self.consumers.get(topic, None):
            consumer = self.consumers[topic].subscribe(topic, "shared")
            while True:
                msg = consumer.receive(2000)
                yield b"Received message: '{}' id='{}'".format(msg.data(), msg.message_id())
                consumer.acknowledge(msg)
                time.sleep(1)
        else:
            raise Exception("No consumer found for topic")
