from flask import abort, make_response
from ..db import db
import logging
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        response = {"message": f"{cls.__name__} {model_id} invalid"}
        abort(make_response(response, 400))

    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)
    
    if not model:
        response = {"message": f"{cls.__name__} {model_id} not found"}
        abort(make_response(response, 404))
    
    return model


logger = logging.getLogger(__name__)


def chat_post_message(task):
    token = os.environ.get('SLACK_BOT_TOKEN')
    channel = os.environ.get('SLACK_CHANNEL_ID')

    try:
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },

            json={
                "channel": channel,
                "text": f"Someone just completed the task {task.title}"
            }
        )
        if response.status_code == 200 and response.json().get("ok"):
            logger.info("Slack message sent successfully.")
        else:
            logger.error(f"Slack API error: {response.json()}")
    except Exception as e:
        logger.error(f"Failed to send Slack message: {e}")


def create_model(cls, model_data, response_key):
    try:
        new_model = cls.from_dict(model_data)

    except KeyError:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(new_model)
    db.session.commit()

    return {response_key: new_model.to_dict()}, 201


