import azure.functions as func
import logging

import os
from slack_bolt import App
from utils.handler import SlackRequestHandler

import auth
import listeners

app = func.FunctionApp()

# Learn more at aka.ms/pythonprogrammingmodel

# Get started by running the following code to create a function using a HTTP trigger.


@app.function_name(name="EchoBot")
@app.route(route="slack/events", auth_level=func.AuthLevel.ANONYMOUS)
def echo_bot(req: func.HttpRequest):
    logging.basicConfig(level=logging.DEBUG)
    auth.SECRET_PATH = "auth/.env.yaml"
    listeners.commands.YAML_FILE = "config.yaml"

    # On multiple workspaces
    # process_before_response must be True when running on FaaS
    # slack_app = App(authorize=auth.authorize, request_verification_enabled=False)
    # slack_app.middleware(auth.verify)

    # On single workspace
    slack_app = App(
        process_before_response=True,
        token=os.environ.get("SLACK_BOT_TOKEN"),
        signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    )

    listeners.listen(slack_app)

    # Flask adapter
    handler = SlackRequestHandler(slack_app)
    return handler.handle(req)
