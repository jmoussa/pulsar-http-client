import logging
import pulsar
from alfred.models import User

client = pulsar.Client("pulsar://localhost:6650")
logger = logging.getLogger(__name__)


class PulsarManager:
    def __init__(self):
        self.conn = client

    async def init_user(self, current_user: User):
        """
        Subsribes the current_user to its preconfigured pulsar topics
        """
        topics = []
        for topic in current_user.authorized_pulsar_topics:
            consumer = self.conn.subscribe(topic, "shared")
            if consumer is not None:
                topics.append(topic)

        return {"initialized": topics}
