# https://cloud.google.com/functions/docs/first-python

import logging
import os

logging.basicConfig(level=logging.DEBUG)

from slack_bolt import App

import listeners

# process_before_response must be True when running on FaaS
app = App(
    process_before_response=True,
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)

listeners.listen(app)

# Flask adapter
from slack_bolt.adapter.flask import SlackRequestHandler

handler = SlackRequestHandler(app)

# Cloud Function
def echo_bot(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    return handler.handle(request)


if os.environ.get("ENV") == "dev":
    app.start(port=int(os.environ.get("PORT", 3000)))
