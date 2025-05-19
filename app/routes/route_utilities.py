from flask import abort, make_response
from ..db import db
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging
import os


def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        response = {"message": f"{cls.__name__} {model_id} invalid"}
        abort(make_response(response , 400))

    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)
    
    if not model:
        response = {"message": f"{cls.__name__} {model_id} not found"}
        abort(make_response(response, 404))
    
    return model


client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
logger = logging.getLogger(__name__)

def chat_post_message(task):
    try:
        result = client.chat_postMessage(
            channel=os.environ.get('SLACK_CHANNEL_ID'),
            text=(f"Someone just completed the task {task.title}")
        )
        logger.info(result)
    except SlackApiError as e:
        logger.error(f"Error posting message: {e}")


def create_model(cls, model_data, response_key):
    try:
        new_model = cls.from_dict(model_data)

    except KeyError:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_model)
    db.session.commit()

    return {response_key: new_model.to_dict()}, 201