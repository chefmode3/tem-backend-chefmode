from __future__ import annotations

import logging
import os

from flask import g
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from app.models import SubscriptionMembership


logging.basicConfig(level=logging.INFO)


def send_slack_message(message: str):
    try:
        slack_token = os.environ['SLACK_BOT_TOKEN']
        client = WebClient(token=slack_token)
        # logging.info("response")
        channel: str = os.environ['SLACK_CHANNEL']
        client.chat_postMessage(
            channel=channel,
            text=message
        )

        # logging.info("response")

    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        logging.error(e.response['error'])
        assert e.response['error']  # str like 'invalid_auth', 'channel_not_found'


def send_slack_notification_recipe(recipe_source_link: str, head_message: str = 'New recipe generated', recipe_chefmode_url: str = None, user_id = None):
    get_user_type = 'free'
    if user_id:
        subscription = SubscriptionMembership.query.filter_by(user_id=user_id).first()
        if subscription:
            get_user_type = 'premium'

    send_slack_message(
        message=f"{head_message} \n Original source: {recipe_source_link},\n Chefmode source: {recipe_chefmode_url},\n User subscription status: {get_user_type},  "
    )
    logging.info('response')
