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
from utils.text import get_channels

YAML_FILE = "config.yaml"
help = read_yaml("config.yaml").get("help")


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
    - api_app_id : A[A-Z0-9]{10}
    - is_enterprise_install : true|false
    - response_url : [https://hooks.slack.com/commands/{team_id}/[0-9]{13}/[0-9a-zA-Z]{24}]()
    - trigger_id : [0-9]{13}.[0-9]{13}.[0-9a-z]{32}

    Returns:
        (iterable): values
    """
    command["context"] = command.pop("command")
    list(map(exec, (f"{k}='{v}'" for k, v in command.items() if k in values)))
    locals_ = locals()
    if "text" in locals_:
        text = html.unescape(text)  # '<@Uxxxxxxxxxx>': str
        channels = get_channels(text)  # ['Cxxxxxxxxxx', ...]: list
    return (locals_.get(k, None) for k in values)


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

    members = client.conversations_members(channel=channel_id).get("members")  # type: ignore [Uxxxxxxxxxx, ...]: list
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
    @echo will send a message on the channel instead of you. (anonymous message)
    """
    logger.info(pformat(body))

    channel_id, text, channels = get_values(command, ["channel_id", "text", "channels"])
    # [processing]
    # TODO:
    # [-] error handling : channel_not_found, is_archived
    # if the message is valid, send the message to the channel
    if text:
        ack()
        # send the message to the channel
        say(text=text)
        # send the message to the mentioned channels
        for channel in channels:
            say(
                text=f"이 채널이 <#{channel_id}>에서 멘션되었습니다.",
                attachments=blocks.attachments(
                    color="#d0d0d0",
                    blocks=[blocks.Section(text=blocks.mrkdwn(text=text))],
                ),
                channel=channel,
            )
    # if the message is invalid, send help message
    else:
        ack(text=help.get("echo"))


def send(
    body: Dict[str, Any],
    logger: logging.Logger,
    command: Dict[str, Any],
    ack: Ack,
    say: Say,
):
    """
    send a message to mentioned channels
    """
    logger.info(pformat(body))

    user_id, text, channels = get_values(command, ["user_id", "text", "channels"])
    # [processing]
    # TODO:
    # [-] error handling : channel_not_found, is_archived
    # [-] preview message
    # if any channel is mentioned, send the message to the channel
    if channels:
        ack(text=f"<#{'> <#'.join(channels)}>로 메시지를 보냈습니다.\n> {text}")
        # send the message to the mentioned channels
        for channel in channels:
            say(
                text=f"<@{user_id}>님이 보낸 메시지 입니다.",
                attachments=blocks.attachments(
                    color="#d0d0d0",
                    blocks=[blocks.Section(text=blocks.mrkdwn(text=text))],
                ),
                channel=channel,
            )
    # if no channel is mentioned, send help message
    else:
        ack(text=help.get("send"))


def shuffle(
    body: Dict[str, Any],
    logger: logging.Logger,
    client: slack_sdk.web.client.WebClient,
    command: Dict[str, Any],
    ack: Ack,
    say: Say,
):
    """
    shuffle the order of the members in the channel
    """
    logger.info(pformat(body))

    channel_id, user_id, text = get_values(command, ["channel_id", "user_id", "text"])
    members = get_members(client, channel_id)
    random.seed()
    random.shuffle(members)
    members = map(lambda i, user: f"{i + 1}. <@{user}>\n", *zip(*enumerate(members)))

    # [processing]
    ack()
    say(
        blocks=[
            blocks.Section(text=blocks.mrkdwn(text="".join(members))),
            blocks.Divider(),
            blocks.Context(
                elements=[
                    blocks.mrkdwn(
                        text=f"<@{user_id}>님이 `/shuffle {text if text else ''}`로 랜덤 셔플하였습니다."
                    )
                ]
            ),
        ]
    )


def choices(
    body: Dict[str, Any],
    logger: logging.Logger,
    client: slack_sdk.web.client.WebClient,
    command: Dict[str, Any],
    ack: Ack,
    say: Say,
):
    """
    choose a random member from the channel
    """
    logger.info(pformat(body))

    channel_id, user_id, text = get_values(command, ["channel_id", "user_id", "text"])
    members = get_members(client, channel_id)
    counter = Counter(members)  # Counter({'Uxxxxxxxxxx': 1, ...}): Counter
    random.seed()
    if text:
        if re.search(r"^help\s*", text):
            ack(text=help)
            return
        elif num := re.search(r"^[1-9]\d*", text):
            num = int(num.group())
        else:
            num = 1
    else:
        num = 1
    selected_members = random.choices(tuple(counter.keys()), weights=counter.values(), k=num)  # type: ignore
    selected_members = map(
        lambda i, user: f"{i + 1}. <@{user}>\n", *zip(*enumerate(selected_members))
    )

    # [processing]
    # if the command is valid, send the message to the channel
    ack()
    say(
        blocks=[
            blocks.Section(text=blocks.mrkdwn(text="".join(selected_members))),
            blocks.Divider(),
            blocks.Context(
                elements=[
                    blocks.mrkdwn(
                        text=f"<@{user_id}>님이 `/choices {text if text else ''}`로 랜덤 선택하였습니다."
                    )
                ]
            ),
        ]
    )
