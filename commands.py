import json
from pprint import pformat

from utils.loader import read_yaml
from utils.text import is_channel_mentioned, parse_random_command, text_replace
from utils.random import shuffle, select, choices


def echo(body, logger, command, ack, say):
    logger.info(pformat(body))

    # [from request]
    channel_id = command.get("channel_id")
    text = command.get("text")

    # [preprocessing]
    text = text_replace(text)
    mentioned_channels = is_channel_mentioned(text)

    template = read_yaml("templates/echo.yaml")
    pretext = template["text"]["pretext"].format(channel_id=channel_id)
    attachments = template["attachments"].format(text)
    help = template["text"]["help"]

    # [processing]
    if text:
        ack()
        say(text=text)
        for channel in mentioned_channels:
            # TODO:
            # [-] error handling : channel_not_found, is_archived
            say(text=pretext, attachments=json.loads(attachments), channel=channel)
    else:
        ack(text=help)


def send(body, logger, command, ack, say):
    logger.info(pformat(body))

    # [from request]
    user_id = command.get("user_id")
    text = command.get("text")

    # [preprocessing]
    text = text_replace(text)
    mentioned_channels = is_channel_mentioned(text)

    template = read_yaml("templates/send.yaml")
    send = template["text"]["send"].format(
        channel="> <#".join(mentioned_channels), text=text
    )
    receive = template["text"]["receive"].format(user_id=user_id)
    attachments = template["attachments"].format(text)
    help = template["text"]["help"]

    # [processing]
    if mentioned_channels:
        ack(text=send)
        for channel in mentioned_channels:
            # TODO:
            # [-] error handling : channel_not_found, is_archived
            say(text=receive, attachments=json.loads(attachments), channel=channel)
    else:
        ack(text=help)


def random(body, logger, client, command, ack, say):
    logger.info(pformat(body))

    # [from request]
    channel_id = command.get("channel_id")
    user_id = command.get("user_id")
    text = command.get("text")

    # [preprocessing]
    num_to_select, *options = parse_random_command(text)
    members = client.conversations_members(channel=channel_id).get("members")
    shuffle(members, options)
    selectable = len(set(members))

    template = read_yaml("templates/random.yaml")
    blocks = template["blocks"]
    context = template["text"]["context"].format(
        user_id=user_id, text=text if text else ""
    )
    selected = template["text"]["selected"]
    selected_list = lambda i, user: selected.format(num=i + 1, user=user)
    help = template["text"]["help"].format(user_id=user_id)

    # [processing]
    if selectable and num_to_select:
        ack()
        selected_members = select(members, num_to_select)
        selected_member_list = "\n".join(
            map(selected_list, *zip(*enumerate(selected_members)))
        )
        say(blocks=json.loads(blocks.format(selected_member_list, context)))
    else:
        ack(text=help)
