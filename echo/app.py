import json
import os

import flask

import main

app = flask.Flask(__name__)
file = open("config.json")
secret = json.load(file)
oauth_token = secret.get("OAUTH_TOKEN")


@app.route("/echo", methods=["GET", "POST"])
def echo():
    return main.respond(flask.request)


def get_channel_history(channel):
    url = "https://slack.com/api/conversations.history"
    data = {"channel": channel}
    headers = {"Authorization": "Bearer " + oauth_token}
    resp = requests.get(url, data=data, headers=headers)
    print(resp)
    return resp.json()


def delete_message(channel, message_id):
    url = "https://slack.com/api/chat.delete"
    data = {"channel": channel, "ts": message_id}
    headers = {"Authorization": "Bearer " + oauth_token}
    resp = requests.post(url, data=data, headers=headers)
    print(resp)
    return make_response("Delete", 200)


if __name__ == "__main__":
    app.run("0.0.0.0", port=8080)
