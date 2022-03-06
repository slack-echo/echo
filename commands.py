import json
import logging
import random
import re
from collections import Counter
from pprint import pformat
from typing import Any, Dict

import slack_sdk
from slack_bolt import Ack, Say

from utils.loader import read_yaml
from utils.text import get_mentioned_channels, text_replace


def echo(
    body: Dict[str, Any],
    logger: logging.Logger,
    command: Dict[str, Any],
    ack: Ack,
    say: Say,
):
    """
    @echo will send a message on the channel instead of you. (anonymous message)

    Args:
        body: the body of the request
        logger: the logger
        command: the command
        ack: the ack function
        say: the say function

    Returns:
        None
    """
    logger.info(pformat(body))

    # [from request]
    # get channel id and text from the command
    channel_id = command.get("channel_id")  # Cxxxxxxxxx: str
    text = command.get("text")  # 'text &lt;@Uxxxxxxxxxx|&gt;': str

    # [preprocessing]
    # replace &lt; and |&gt; with < and > respectively
    text = text_replace(text)  # 'text <@Uxxxxxxxxxx>': str
    # get mentioned channels from the text
    mentioned_channels = get_mentioned_channels(text)  # ['Cxxxxxxxxxx', ...]: list

    # build the message to send
    template = read_yaml("templates/echo.yaml")  # dict from yaml
    pretext = template["text"]["pretext"].format(channel_id=channel_id)  # formatted str
    attachments = template["attachments"].format(text)  # formatted json
    help = template["text"]["help"]  # str

    # [processing]
    # TODO:
    # [-] error handling : channel_not_found, is_archived
    # if the message is valid, send the message to the channel
    if text:
        ack()
        # send the message to the channel
        say(text=text)
        # send the message to the mentioned channels
        for channel in mentioned_channels:
            say(text=pretext, attachments=json.loads(attachments), channel=channel)
    # if the message is invalid, send help message
    else:
        ack(text=help)


def send(
    body: Dict[str, Any],
    logger: logging.Logger,
    command: Dict[str, Any],
    ack: Ack,
    say: Say,
):
    """
    send a message to mentioned channels

    Args:
        body: the body of the request
        logger: the logger
        command: the command
        ack: the ack function
        say: the say function

    Returns:
        None
    """
    logger.info(pformat(body))

    # [from request]
    # get user id and text from the command
    user_id = command.get("user_id")  # Uxxxxxxxxxx: str
    text = command.get("text")  # 'text &lt;@Uxxxxxxxxxx|&gt;': str

    # [preprocessing]
    # replace &lt; and |&gt; with < and > respectively
    text = text_replace(text)  # 'text <@Uxxxxxxxxxx>': str
    # get mentioned channels from the text
    mentioned_channels = get_mentioned_channels(text)  # ['Cxxxxxxxxxx', ...]: list

    # build the message to send
    template = read_yaml("templates/send.yaml")  # dict from yaml
    send = template["text"]["send"].format(channel="> <#".join(mentioned_channels), text=text)  # type: ignore # formatted str
    receive = template["text"]["receive"].format(user_id=user_id)  # formatted str
    attachments = template["attachments"].format(text)  # formatted json
    help = template["text"]["help"]  # str

    # [processing]
    # TODO:
    # [-] error handling : channel_not_found, is_archived
    # [-] preview message
    # if any channel is mentioned, send the message to the channel
    if mentioned_channels:
        ack(text=send)
        # send the message to the mentioned channels
        for channel in mentioned_channels:
            say(text=receive, attachments=json.loads(attachments), channel=channel)
    # if no channel is mentioned, send help message
    else:
        ack(text=help)


def shuffle(
    body: Dict[str, Any],
    logger: logging.Logger,
    client: slack_sdk.web.client.WebClient,
    command: Dict[str, Any],
    ack: Ack,
    say: Say,
):
    """

    Args:
        body: the body of the request
        logger: the logger
        client: the client
        command: the command
        ack: the ack function
        say: the say function

    Returns:
        None
    """
    logger.info(pformat(body))

    # [from request]
    # get channel id, user id and text from the command
    channel_id = command.get("channel_id")  # Cxxxxxxxxx: str
    user_id = command.get("user_id")  # Uxxxxxxxxxx: str
    text = command.get("text")  # 'text &lt;@Uxxxxxxxxxx|&gt;': str

    # [preprocessing]
    members = client.conversations_members(channel=channel_id).get("members")  # type: ignore [Uxxxxxxxxxx, ...]: list
    # members.remove("U02EE3TDD5J")
    random.seed()
    random.shuffle(members)

    # build the message to send
    template = read_yaml("templates/shuffle.yaml")
    blocks = template["blocks"]
    context = template["text"]["context"].format(user_id=user_id, text=text if text else "")  # type: ignore
    numbered_user_list = lambda i, user: template["text"]["numbered-user"].format(num=i + 1, user=user)  # type: ignore

    # [processing]
    ack()
    shuffled_member_list = "".join(map(numbered_user_list, *zip(*enumerate(members))))  # type: ignore
    say(blocks=json.loads(blocks.format(shuffled_member_list, context)))


def choices(
    body: Dict[str, Any],
    logger: logging.Logger,
    client: slack_sdk.web.client.WebClient,
    command: Dict[str, Any],
    ack: Ack,
    say: Say,
):
    """

    Args:
        body: the body of the request
        logger: the logger
        client: the client
        command: the command
        ack: the ack function
        say: the say function

    Returns:
        None
    """
    logger.info(pformat(body))

    # [from request]
    # get channel id, user id and text from the command
    channel_id = command.get("channel_id")  # Cxxxxxxxxx: str
    user_id = command.get("user_id")  # Uxxxxxxxxxx: str
    text = command.get("text")  # 'text &lt;@Uxxxxxxxxxx|&gt;': str

    # [preprocessing]
    members = client.conversations_members(channel=channel_id).get("members")  # type: ignore [Uxxxxxxxxxx, ...]: list
    # members.remove("U02EE3TDD5J")
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

    # build the message to send
    template = read_yaml("templates/choices.yaml")
    blocks = template["blocks"]
    context = template["text"]["context"].format(user_id=user_id, text=text if text else "")  # type: ignore
    numbered_user_list = lambda i, user: template["text"]["numbered-user"].format(num=i + 1, user=user)  # type: ignore
    help = template["text"]["help"].format(user_id=user_id)

    # [processing]
    # if the command is valid, send the message to the channel
    ack()
    selected_member_list = "".join(map(numbered_user_list, *zip(*enumerate(selected_members))))  # type: ignore
    say(blocks=json.loads(blocks.format(selected_member_list, context)))
