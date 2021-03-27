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
from fastapi.responses import JSONResponse

# from alfred.config import MONGODB_DB_NAME

logger = logging.getLogger(__name__)
router = APIRouter()

client = pulsar.Client("pulsar://localhost:6650")


# TODO: Need to Refactor the consume functionality to work in a websocket
async def consumer_generator(consumer):
    while True:
        msg = consumer.receive(2000)
        yield b"Received message '{}' id='{}'".format(msg.data(), msg.message_id())
        consumer.acknowledge(msg)
        time.sleep(1)


@router.post("/subscribe/{topic}", tags=["Pulsar"])
async def subscribe_to_pulsar_topic(
    topic, current_user: User = Depends(get_current_active_user), db: MongoClient = Depends(get_nosql_db)
):
    """
    Subsribes to a pulsar topic
    """
    client.subscribe(topic, "shared")
    return JSONResponse(status_code=200, content={"topic": topic})


@router.post("/send_pulsar_message/{topic}", tags=["Pulsar"])
async def publish_to_pulsar_topic(
    topic,
    message: PulsarMessage,
    # current_user=Depends(get_current_active_user),
    # db: MongoClient = Depends(get_nosql_db),
):

    producer = client.create_producer(topic)
    producer.send(message.message.encode("utf-8"))
    return JSONResponse(status_code=200, content={"topic": topic, "message": message.message})
