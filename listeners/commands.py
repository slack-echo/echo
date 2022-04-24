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
from utils.text import get_channels, get_emojis, get_urls, get_users

YAML_FILE = "https://api.github.com/repos/skkuinit/echo/contents/config.yaml"


def get_values(command: Dict[str, Any], values: Iterable[str]) -> Iterable[str]:
    """
    get values from the command

    Args:
        command (dict): payload of the app.command
        values (iterable): values to get from the command
    value (str):
    - api_app_id : A[A-Z0-9]{10}
    - channel_id : [C|G]A-Z0-9]{10}
    - channel_name : #{channel_name}
    - command(context) : /{command}
    - is_enterprise_install : true|false
    - response_url : https://hooks.slack.com/commands/{team_id}/[0-9]{13}/[0-9a-zA-Z]{24}
    - team_domain : {team_domain}.slack.com
    - team_id : T[A-Z0-9]{10}
    - text : {text} (if text is not empty)
        - channels : [C|G]A-Z0-9]{10}
        - emojis : :emoji:
        - urls : <https?://[^\s]+>
        - users : U[A-Z0-9]{10}
    - token : [0-9a-zA-Z]{24}
    - trigger_id : [0-9]{13}.[0-9]{13}.[0-9a-z]{32}
    - user_id : U[A-Z0-9]{10}
    - user_name : {user_name}@{email_domain}

    Returns:
        (iterable): values
    """
    command.update(context=command.pop("command"))
    command.update(text=html.unescape(text := command.pop("text", "")))
    filtered_dict = {k: v for k, v in command.items() if k in values}

    if "channels" in values:
        filtered_dict.update(channels=get_channels(text))
    if "users" in values:
        filtered_dict.update(users=get_users(text))
    if "emojis" in values:
        filtered_dict.update(emojis=get_emojis(text))
    if "urls" in values:
        filtered_dict.update(urls=get_urls(text))
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

    members = client.conversations_members(channel=channel_id).get("members")
    members = list(set(members) - set(SLACK_BOT_USER_ID))
    return members


def get_help_message(context: str) -> str:
    """
    get help message for the yaml file
    """
    help_msg = read_yaml(YAML_FILE).get("help")
    return help_msg.get(context)


def echo(
    body: Dict[str, Any],
    logger: logging.Logger,
    command: Dict[str, Any],
    ack: Ack,
    say: Say,
):
    """
    `/echo` : @echo will send a message on the channel instead of you. (anonymous message)
    `/anonymous` : send a message on the channel as "익명" with an anonymous profile image. (anonymous message)
    `/disguise` : send a message on the channel in disguise as you wish. (anonymous message)
    """
    logger.info(pformat(body))

    channel_id, text, context = get_values(command, ["channel_id", "text", "context"])

    # if the message is valid, send the message to the channel
    # else the message is invalid, send help message
    if context.startswith("/echo"):
        if text:
            ack()
            say(text=text)
        else:
            ack(text=get_help_message("echo"))
            return
    elif context.startswith("/anonymous"):
        if text:
            ack()
            say(text=text, username="익명", icon_emoji=":bust_in_silhouette:")
        else:
            ack(text=get_help_message("anonymous"))
            return
    elif context.startswith("/disguise"):
        if text:
            # get url for profile image
            url, *_ = get_urls(text) or ("",)
            text = re.sub(re.escape(url) + "\s+", "", text) if url else text
            url = url.strip("<>")

            # get emoji for profile image
            emoji, *_ = (None,) if url else (get_emojis(text) or (":bust_in_silhouette:",))  # type: ignore
            text = re.sub(emoji + "\s+", "", text, 1) if emoji else text

            # get username for profile
            username, *_ = text.split()
            text = re.sub(username + "\s+", "", text, 1)

            kwagrs = {"username": username, "icon_emoji": emoji, "icon_url": url}
            ack()
            say(text=text, **kwagrs)
        else:
            ack(text=get_help_message("disguise"))
            return

    channels = get_channels(text)
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
                ack(text=f"메시지를 보낸 후 <#{channel}>로 멘션 알림에 실패하였습니다. 채널에 앱이 존재하지 않습니다.")
            elif error == "is_archived":
                ack(text=f"메시지를 보낸 후 <#{channel}>로 멘션 알림에 실패하였습니다. 채널이 보관되어 있습니다.")


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
    # else no channel is mentioned, send help message
    if channels:
        ack(text=f"<#{'> <#'.join(channels)}>로 메시지를 보냅니다.\n> {text}")
    else:
        ack(text=get_help_message("send"))

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
                ack(text=f"<#{channel}>로 메시지 보내기를 실패하였습니다. 채널에 앱이 존재하지 않습니다.")
            elif error == "is_archived":
                ack(text=f"<#{channel}>로 메시지 보내기를 실패하였습니다. 채널이 보관되어 있습니다.")


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
        ack(text=get_help_message("choices"))
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

    channel_name, user_id, user_name, users, context = get_values(command, ["channel_name", "user_id", "user_name", "users", "context"])  # type: ignore

    # get the meeting link
    if users:
        code = user_name.replace(".", "-")
    else:
        *_, code = channel_name.split("_")
        code = re.sub("[^a-z0-9-]+", "", code)

    link = (
        "https://accounts.google.com/AccountChooser"
        + "?hd=g.skku.edu"
        + f"&continue=https://g.co/meet/{code}"
        + "&flowName=GlifWebSignIn"
        + "&flowEntry=AccountChooser"
    )
    block = [
        blocks.Section(text=blocks.mrkdwn(text=f"> *<{link}|Google Meet 참여하기>*")),
        blocks.Divider(),
        blocks.Context(
            elements=[blocks.mrkdwn(text=f"<@{user_id}>님이 `{context}`를 실행하였습니다.")]
        ),
    ]

    # send the message
    ack()
    for user in users:
        say(username="Google Meet", icon_emoji=":meet:", blocks=block, channel=user)
    else:
        say(username="Google Meet", icon_emoji=":meet:", blocks=block)
