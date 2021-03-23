import logging
import pulsar
import time
from fastapi import Depends, APIRouter

# from alfred.requests import PublishRequest, SubscribeRequest, UnsubscribeRequest

# consume should be on client side
from alfred.models import User
from alfred.db import get_nosql_db, MongoClient
from alfred.controllers import get_current_active_user
from fastapi.responses import StreamingResponse

# from alfred.config import MONGODB_DB_NAME

logger = logging.getLogger(__name__)
router = APIRouter()

client = pulsar.Client("pulsar://localhost:6650")


async def consumer_generator(consumer):
    while True:
        try:
            msg = consumer.receive(2000)
            yield "Received message '{}' id='{}'".format(msg.data(), msg.message_id())
            consumer.acknowledge(msg)
        except Exception:
            pass
        time.sleep(1)


@router.post("/subscribe/{topic}", tags=["Pulsar"], response_model=StreamingResponse)
async def subscribe_to_pulsar_topic(
    topic, current_user: User = Depends(get_current_active_user), db: MongoClient = Depends(get_nosql_db)
):
    """
    Subsribes to a pulsar topic
    """
    consumer = client.subscribe(topic, "shared")
    return StreamingResponse(consumer_generator(consumer))
