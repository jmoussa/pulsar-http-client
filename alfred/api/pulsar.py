import logging
import pulsar
import time
from fastapi import Depends, APIRouter

# from alfred.requests import PublishRequest, SubscribeRequest, UnsubscribeRequest

# consume should be on client side
from alfred.models import User
from alfred.db import get_nosql_db, MongoClient
from alfred.controllers import get_current_active_user
from alfred.requests import PulsarMessage
from fastapi.responses import StreamingResponse, JSONResponse

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


@router.post("/add_topic/{topic}", tags=["Pulsar"], response_model=JSONResponse)
async def add_topic_to_pulsar(
    topic, current_user=Depends(get_current_active_user), db: MongoClient = Depends(get_nosql_db)
):
    """
    Adds a topic to pulsar
    """
    producer = client.create_producer(topic)
    return JSONResponse(status_code=200, content={"topic": topic, "producer": producer})


@router.post("/send_pulsar_message/{topic}", tags=["Pulsar"], response_model=JSONResponse)
async def publish_to_pulsar_topic(
    topic,
    message: PulsarMessage,
    current_user=Depends(get_current_active_user),
    db: MongoClient = Depends(get_nosql_db),
):

    producer = client.create_producer(topic)
    producer.send(message.encode("utf-8"))
    return JSONResponse(status_code=200, content={"topic": topic, "message": {**message.message}})
