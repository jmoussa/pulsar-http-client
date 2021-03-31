import logging
from fastapi import Depends, APIRouter, WebSocket

# from alfred.requests import PublishRequest, SubscribeRequest, UnsubscribeRequest

from alfred.models import User
from alfred.db import get_nosql_db, MongoClient
from alfred.controllers import get_current_active_user
from alfred.controllers.pulsar import PulsarManager
from alfred.requests import PulsarMessage
from fastapi.responses import JSONResponse

# from alfred.config import MONGODB_DB_NAME

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/init_subscribe", tags=["Pulsar"])
async def initialize_user_subscriptions(current_user: User = Depends(get_current_active_user)):
    """
    Subsribes the current_user to its preconfigured pulsar topics
    """
    pulsar_manager = PulsarManager(current_user["_id"])
    response = pulsar_manager.init_user_authorized_topics(current_user)
    return JSONResponse(status_code=200, content=response)


@router.put("/subscribe/{topic}", tags=["Pulsar"])
async def subscribe_to_topic(topic: str, current_user: User = Depends(get_current_active_user)):
    """
    Subscribe to a topic (generates producer and consumer object for user's PulsarManager)
    """
    try:
        pulsar_manager = PulsarManager(current_user["_id"])
        pulsar_manager.subscribe(topic)
        return JSONResponse(status_code=200, content={"status": "success"})
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return JSONResponse(status_code=500, content={"status": "failed", "message": message})


@router.websocket("/feed/{topic}")
async def topic_feed(
    websocket: WebSocket,
    topic: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Websocket that sends messages from a subscribed topic
    """
    pulsar_manager = PulsarManager(current_user["_id"])
    await websocket.accept()
    try:
        while True:
            for response in pulsar_manager.consumer_generator(topic):
                await websocket.send_text(response)
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        logger.error(message)
        # remove user
        logger.warning(f"Disconnecting {topic} Websocket")
        await websocket.close()


@router.post("/send_pulsar_message/{topic}", tags=["Pulsar"])
async def publish_to_pulsar_topic(
    topic,
    message: PulsarMessage,
    current_user=Depends(get_current_active_user),
):
    pulsar_manager = PulsarManager(current_user["_id"])
    if topic in current_user.authorized_pulsar_topics:
        response = pulsar_manager.publish_message(message.message, topic)
        return JSONResponse(status_code=200, content=response)
    else:
        return JSONResponse(status_code=403, content={"message": "User does not have rights to publish to this topic"})
