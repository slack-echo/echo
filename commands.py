import html
import logging
import random
import re
from collections import Counter
from pprint import pformat
from typing import Any, Dict

import slack_sdk
from slack_bolt import Ack, Say

from utils import blocks
from utils.loader import read_yaml
from utils.text import get_channels

SLACK_BOT_USER_ID = read_yaml("config.yaml").get("SLACK_BOT_USER_ID")
help = read_yaml("config.yaml").get("help")


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

    channel_id = command.get("channel_id")  # Cxxxxxxxxx: str
    text = command.get("text")  # 'text &lt;@Uxxxxxxxxxx|&gt;': str
    text = html.unescape(text)  # 'text <@Uxxxxxxxxxx>': str
    channels = get_channels(text)  # ['Cxxxxxxxxxx', ...]: list

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

    user_id = command.get("user_id")  # Uxxxxxxxxxx: str
    text = command.get("text")  # 'text &lt;@Uxxxxxxxxxx|&gt;': str
    text = html.unescape(text)  # 'text <@Uxxxxxxxxxx>': str
    channels = get_channels(text)  # ['Cxxxxxxxxxx', ...]: list

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

    channel_id = command.get("channel_id")  # Cxxxxxxxxx: str
    user_id = command.get("user_id")  # Uxxxxxxxxxx: str
    text = command.get("text")  # 'text &lt;@Uxxxxxxxxxx|&gt;': str
    text = html.unescape(text)  # 'text <@Uxxxxxxxxxx>': str

    # [preprocessing]
    members = client.conversations_members(channel=channel_id).get("members")  # type: ignore [Uxxxxxxxxxx, ...]: list
    members = list(set(members) - set(SLACK_BOT_USER_ID))
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

    channel_id = command.get("channel_id")  # Cxxxxxxxxx: str
    user_id = command.get("user_id")  # Uxxxxxxxxxx: str
    text = command.get("text")  # 'text &lt;@Uxxxxxxxxxx|&gt;': str
    text = html.unescape(text)  # 'text <@Uxxxxxxxxxx>': str

    # [preprocessing]
    members = client.conversations_members(channel=channel_id).get("members")  # type: ignore [Uxxxxxxxxxx, ...]: list
    members = list(set(members) - set(SLACK_BOT_USER_ID))
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
