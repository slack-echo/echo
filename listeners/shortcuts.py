import logging
from typing import Any, Dict, Iterable

import slack_sdk
import utils.models as m
from slack_bolt import Ack


def get_values(shortcut: Dict[str, Any], values: Iterable[Any]) -> Any:
    """
    get values from the shortcut

    Args:
        shortcut (dict): payload of the app.shortcut
        values (iterable): values to get from the shortcut
    value:
    - action_ts (str): [0-9]{10}.[0-9]{6}
    - callback_id (str): {callback_id}
    - channel (dict):
        - id (str): [C|G]A-Z0-9]{10}
        - name (str): #{channel_name}
    - enterprise : None
    - is_enterprise_install (bool): True|False
    - message (dict):
        - bot_id (str): B[A-Z0-9]{10}
        - bot_profile (dict):
             - app_id (str): A[A-Z0-9]{10}
             - deleted (bool): True|False
             - icons (dict):
                 - image_36 (str): https://avatars.slack-edge.com/{...}_36.png
                 - image_48 (str): https://avatars.slack-edge.com/{...}_48.png
                 - image_72 (str): https://avatars.slack-edge.com/{...}_72.png
             - id (str): B[A-Z0-9]{10}
             - name (str): {bot_name}
             - team_id (str): T[A-Z0-9]{10}
             - updated (int): [0-9]{10}
        - team (str): T[A-Z0-9]{10}
        - text (str): {text}
        - ts (str): [0-9]{10}.[0-9]{6}
        - type (str): message|app_mention|message_changed|message_deleted
        - user (str): U[A-Z0-9]{10}
    - message_ts (str): [0-9]{10}.[0-9]{6}
    - response_url (str): https://hooks.slack.com/app/{team_id}/[0-9]{13}/[0-9a-zA-Z]{24}
    - team (dict):
        - domain (str): {team_domain}.slack.com
        - id (str): T[A-Z0-9]{10}
    - token (str): [0-9a-zA-Z]{24}
    - trigger_id (str): [0-9]{13}.[0-9]{13}.[a-z0-9]{32}
    - type (str): message_action|block_actions|view_submission
    - user (dict):
        - id (str): U[A-Z0-9]{10}
        - name (str): {user_name}@{email_domain}
        - team_id (str): T[A-Z0-9]{10}
        - username (str): {user_name}

    Returns:
        (iterable): values
    """
    return (shortcut.get(k, "") for k in values)


def delete_message(
    body: Dict[str, Any],
    logger: logging.Logger,
    client: slack_sdk.web.client.WebClient,
    shortcut: Dict[str, Any],
    ack: Ack,
):
    """
    delete message which is sent by the bot
    """
    logger.info(body)

    channel, ts = get_values(shortcut, ["channel", "message_ts"])
    channel_id = channel.get("id")
    ack()
    client.chat_delete(channel=channel_id, ts=ts)


def edit_message(
    body: Dict[str, Any],
    logger: logging.Logger,
    client: slack_sdk.web.client.WebClient,
    shortcut: Dict[str, Any],
    ack: Ack,
):
    """
    edit message which is sent by the bot
    """
    logger.info(body)

    channel, message, ts = get_values(shortcut, ["channel", "message", "message_ts"])
    channel_id = channel.get("id")
    if blocks := message.get("blocks"):
        # TOOD: other blocks?
        first, *_ = blocks
        if text := first.get("text"):
            text = text.get("text")
    else:
        text = message.get("text")

    blocks = [
        m.Input(
            element=m.plain_text_input(
                action_id="edit_message",
                multiline=True,
                placeholder=m.plain_text(text="메시지 편집"),
                initial_value=text,
                focus_on_load=True,
            ),
            label=m.plain_text(text="메시지 편집"),
        ),
        m.Actions(
            elements=[
                m.button(
                    text=m.plain_text(text=":x: 취소", emoji=True),
                    action_id="cancel_edit",
                    style="danger",
                ),
                m.button(
                    text=m.plain_text(text=":heavy_check_mark: 저장", emoji=True),
                    action_id="save_edit",
                    style="primary",
                ),
            ]
        ),
    ]

    ack()
    client.chat_update(channel=channel_id, ts=ts, blocks=blocks)
