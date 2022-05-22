import logging
import os

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

import listeners
from authorize import authorize, verify


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
    logging.basicConfig(level=logging.INFO)

    # process_before_response must be True when running on FaaS
    app = App(
        process_before_response=True,
        authorize=authorize,
        request_verification_enabled=False,
    )
    listeners.listen(app)
    app.middleware(verify)

    # Flask adapter
    handler = SlackRequestHandler(app)
    return handler.handle(request)


if os.environ.get("ENV") == "dev":
    print("Development mode")
    logging.basicConfig(level=logging.DEBUG)

    app = App(authorize=authorize, request_verification_enabled=False)
    app.middleware(verify)
    listeners.listen(app)

    app.start(port=int(os.environ.get("PORT", 3000)))
