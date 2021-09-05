# [START functions_slack_setup]
import os

import requests
from flask import Flask, make_response, request


def respond(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """
    req = request.get_json()
    if "challenge" in req:
        resp = req.get("challenge")
        headers = {"content_type": "application/json"}
        return resp, 200, headers
    if "event" in req:
        event = req.get("event")
        isbot = event.get("bot_id")
        if not isbot:
            return event_handler(event)
    headers = {"X-Slack-No-Retry": 1}
    return "No Event", 404, headers


def event_handler(event):
    event_type = event.get("type")
    channel = event.get("channel")
    text = event.get("text")
    if event_type == "app_mention":
        return send_message(channel, text)
    elif event_type == "message":
        if "subtype" in event:
            event_subtype = event.get("subtype")
            if event_subtype == "message_deleted":
                return no_event_handler(event_type)
            elif event_subtype == "message_changed":
                return no_event_handler(event_type)
            elif event_subtype == "thread_broadcast":
                return send_message(channel, text)
        return send_message(channel, text)
    return no_event_handler(event_type)


def no_event_handler(event_type):
    error = "Cannot find event handler " + event_type
    headers = {"X-Slack-No-Retry": 1}
    return error, 200, headers


def send_message(channel, text):
    url = "https://slack.com/api/chat.postMessage"
    data = {"channel": channel, "text": text}
    headers = {"Authorization": "Bearer " + oauth_token}
    resp = requests.post(url, data=data, headers=headers)
    print(resp)
    return "Send", 200
