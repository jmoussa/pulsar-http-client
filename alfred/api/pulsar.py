import logging
from fastapi import Depends, APIRouter

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
pulsar_manager = PulsarManager()


@router.post("/init_subscribe", tags=["Pulsar"])
async def init_subscribe(
    current_user: User = Depends(get_current_active_user), db: MongoClient = Depends(get_nosql_db)
):
    """
    Subsribes the current_user to its preconfigured pulsar topics
    """
    response = pulsar_manager.init_user_authorized_topics(current_user)
    return JSONResponse(status_code=200, content=response)


@router.post("/send_pulsar_message/{topic}", tags=["Pulsar"])
async def publish_to_pulsar_topic(
    topic,
    message: PulsarMessage,
    current_user=Depends(get_current_active_user),
):
    if topic in current_user.authorized_pulsar_topics:
        response = pulsar_manager.publish_message(message.message, topic)
        return JSONResponse(status_code=200, content=response)
    else:
        return JSONResponse(status_code=403, content={"message": "User does not have rights to publish to this topic"})
