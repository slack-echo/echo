import logging
import os

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

import auth
import listeners


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

    # On multiple workspaces
    # process_before_response must be True when running on FaaS
    app = App(
        process_before_response=True,
        authorize=auth.authorize,
        request_verification_enabled=False,
    )
    app.middleware(auth.verify)
    """
    # On single workspace
    app =App(
        process_before_response=True,
        token=os.environ.get("SLACK_BOT_TOKEN"),
        signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
    )
    """
    listeners.listen(app)

    # Flask adapter
    handler = SlackRequestHandler(app)
    return handler.handle(request)


if os.environ.get("ENV") == "dev":
    print("Development mode")
    logging.basicConfig(level=logging.DEBUG)
    auth.SECRET_PATH = "auth/.env.yaml"
    listeners.commands.YAML_FILE = "config.yaml"

    app = App(authorize=auth.authorize, request_verification_enabled=False)
    app.middleware(auth.verify)
    listeners.listen(app)

    app.start(port=int(os.environ.get("PORT", 3000)))
