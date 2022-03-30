import html
import logging
import random
import re
from collections import Counter
from pprint import pformat
from typing import Any, Dict, Iterable

import slack_sdk
from slack_bolt import Ack, Say

from utils import blocks
from utils.loader import read_yaml
from utils.text import get_channels, get_users

YAML_FILE = "https://api.github.com/repos/skkuinit/echo/contents/config.yaml"


def get_values(command: Dict[str, Any], values: Iterable[str]) -> Iterable[str]:
    """
    get values from the command

    Args:
        command (dict): payload of the app.command
        values (iterable): values to get from the command
    value (str):
    - token : [0-9a-zA-Z]{24}
    - team_id : T[A-Z0-9]{10}
    - team_domain : {team_domain}.slack.com
    - channel_id : [C|G]A-Z0-9]{10}
    - channel_name : #{channel_name}
    - user_id : U[A-Z0-9]{10}
    - user_name : {user_name}@{email_domain}
    - context : /{command}
    - text : {text} (if text is not empty)
        - channels : [C|G]A-Z0-9]{10}
        - users : U[A-Z0-9]{10}
    - api_app_id : A[A-Z0-9]{10}
    - is_enterprise_install : true|false
    - response_url : [https://hooks.slack.com/commands/{team_id}/[0-9]{13}/[0-9a-zA-Z]{24}]()
    - trigger_id : [0-9]{13}.[0-9]{13}.[0-9a-z]{32}

    Returns:
        (iterable): values
    """
    command.update(context=command.pop("command"))
    command.update(
        text=html.unescape(text := command.pop("text", ""))
    )  # '<@Uxxxxxxxxxx>': str
    filtered_dict = {k: v for k, v in command.items() if k in values}

    if "channels" in values:
        filtered_dict.update(channels=get_channels(text))  # ['Cxxxxxxxxxx', ...]: list
    if "users" in values:
        filtered_dict.update(users=get_users(text))  # ['Uxxxxxxxxxx', ...]: list
    if "context" in filtered_dict and text:
        filtered_dict.update(context=filtered_dict.pop("context") + " " + text)

    return (filtered_dict.get(k, "") for k in values)


def get_members(client: slack_sdk.web.client.WebClient, channel_id: str) -> list:
    """
    get members of the channel

    Args:
        client (slack_sdk.web.client.WebClient): client of slack api
        channel_id (str): channel id to get members

    Returns:
        (list): members of the channel
    """
    SLACK_BOT_USER_ID = read_yaml(YAML_FILE).get("SLACK_BOT_USER_ID")

    members = client.conversations_members(channel=channel_id).get("members")  # type: ignore ['Uxxxxxxxxxx', ...]: list
    members = list(set(members) - set(SLACK_BOT_USER_ID))
    return members


def echo(
    body: Dict[str, Any],
    logger: logging.Logger,
    command: Dict[str, Any],
    ack: Ack,
    say: Say,
):
    """
    `/echo` : @echo will send a message on the channel instead of you. (anonymous message)
    """
    logger.info(pformat(body))

    channel_id, text, channels = get_values(command, ["channel_id", "text", "channels"])

    # if the message is valid, send the message to the channel
    if text:
        ack()
        say(text=text)

        # mention the channel in the message
        for channel in channels:
            try:
                say(
                    text=f"이 채널이 <#{channel_id}>에서 멘션되었습니다.",
                    attachments=blocks.attachments(
                        color="#d0d0d0",
                        blocks=[blocks.Section(text=blocks.mrkdwn(text=text))],
                    ).to_dict(),
                    channel=channel,
                )
            except slack_sdk.errors.SlackApiError as e:
                error = e.response["error"]
                logger.error(error)
                if error == "channel_not_found":
                    ack(text=f"메시지를 보낸 후 <#{channel}>로 멘션 알림에 실패하였습니다. 채널에 앱이 존재하지 않습니다.")  # type: ignore
                elif error == "is_archived":
                    ack(text=f"메시지를 보낸 후 <#{channel}>로 멘션 알림에 실패하였습니다. 채널이 보관되어 있습니다.")

    # if the message is invalid, send help message
    else:
        HELP = read_yaml(YAML_FILE).get("help")
        ack(text=HELP.get("echo"))


def send(
    body: Dict[str, Any],
    logger: logging.Logger,
    command: Dict[str, Any],
    ack: Ack,
    say: Say,
):
    """
    `/send` : send a message to mentioned channels
    """
    logger.info(pformat(body))

    user_id, text, channels = get_values(command, ["user_id", "text", "channels"])

    # TODO:
    # [-] preview message
    # if any channel is mentioned, send the message to the channel
    if channels:
        ack(text=f"<#{'> <#'.join(channels)}>로 메시지를 보냅니다.\n> {text}")

        # send the message to the channels in the message
        for channel in channels:
            try:
                say(
                    text=f"<@{user_id}>님이 보낸 메시지 입니다.",
                    attachments=blocks.attachments(
                        color="#d0d0d0",
                        blocks=[blocks.Section(text=blocks.mrkdwn(text=text))],
                    ).to_dict(),
                    channel=channel,
                )
            except slack_sdk.errors.SlackApiError as e:
                error = e.response["error"]
                logger.error(error)
                if error == "channel_not_found":
                    ack(text=f"<#{channel}>로 메시지 보내기를 실패하였습니다. 채널에 앱이 존재하지 않습니다.")  # type: ignore
                elif error == "is_archived":
                    ack(text=f"<#{channel}>로 메시지 보내기를 실패하였습니다. 채널이 보관되어 있습니다.")

    # if no channel is mentioned, send help message
    else:
        HELP = read_yaml(YAML_FILE).get("help")
        ack(text=HELP.get("send"))


def rand(
    body: Dict[str, Any],
    logger: logging.Logger,
    client: slack_sdk.web.client.WebClient,
    command: Dict[str, Any],
    ack: Ack,
    say: Say,
):
    """
    `/shuffle` : shuffle the members of the channel
    `/choices` : choose a random member of the channel
    """
    logger.info(pformat(body))

    channel_id, user_id, text, context = get_values(command, ["channel_id", "user_id", "text", "context"])  # type: ignore
    members = get_members(client, channel_id)

    random.seed()

    # handle the context
    if context.startswith("/shuffle") or context.startswith("/choices all"):
        random.shuffle(members)
    elif context.startswith("/choices help"):
        HELP = read_yaml(YAML_FILE).get("help")
        ack(text=HELP.get("choices"))
        return
    elif context.startswith("/choices"):
        # get the number to choose
        if text and (num := re.search(r"^[1-9]\d*", text)):
            num = int(num.group())
        else:
            num = 1
        counter = Counter(members)  # Counter({'Uxxxxxxxxxx': 1, ...}): Counter
        members = random.choices(tuple(counter.keys()), weights=counter.values(), k=num)

    # build the message to send
    members = map(lambda i, user: f"{i + 1}. <@{user}>\n", *zip(*enumerate(members)))

    # send the message
    ack()
    say(
        blocks=[
            blocks.Section(text=blocks.mrkdwn(text="".join(members))),
            blocks.Divider(),
            blocks.Context(
                elements=[blocks.mrkdwn(text=f"<@{user_id}>님이 `{context}`를 실행하였습니다.")]
            ),
        ]
    )


def meet(
    body: Dict[str, Any],
    logger: logging.Logger,
    command: Dict[str, Any],
    ack: Ack,
    say: Say,
):
    """
    `/meet` : create a link for google meet
    """
    logger.info(pformat(body))

    channel_name, user_id, context = get_values(command, ["channel_name", "user_id", "context"])  # type: ignore

    # get the meeting link
    *_, code = channel_name.split("_")
    code = re.sub("[^a-z0-9-]+", "", code)
    link = (
        "https://accounts.google.com/AccountChooser"
        + "?hd=g.skku.edu"
        + f"&continue=https://g.co/meet/{code}"
        + "&flowName=GlifWebSignIn"
        + "&flowEntry=AccountChooser"
    )

    # send the message
    ack()
    say(
        blocks=[
            blocks.Section(text=blocks.mrkdwn(text=f"> *<{link}|Google Meet 참여하기>*")),
            blocks.Divider(),
            blocks.Context(
                elements=[blocks.mrkdwn(text=f"<@{user_id}>님이 `{context}`를 실행하였습니다.")]
            ),
        ]
    )
