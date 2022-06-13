import logging
from typing import Any, Dict, Iterable

import slack_sdk
import utils.models as m
from slack_bolt import Ack, Respond


def get_values(body: Dict[str, Any], values: Iterable[Any]) -> Any:
    """
    get values from the body

    Args:
        body (dict): body of the request
        values (iterable): values to get from the body
    value:

    - actions (list : dict):
        - action_id (str): {action_id}
        - action_ts (str): [0-9]{10}.[0-9]{6}
        - block_id (str): {block_id}
        - type (str : data):
            - button : text (dict), value (str), style (str)
            - overflow : selected_option (dict)
            - checkbox : selected_options (list)
            - radio_buttons : selected_option (dict) , initial_option (dict)
            - static_select : selected_option (dict), initial_option (dict), placeholder (dict)
            - multi_static_select : selected_options (list), initial_options (list), placeholder (dict)
            - users_select : selected_user (str), initial_user (str)
            - multi_users_select : selected_users (list), initial_users (list)
            - channels_select : selected_channel (str), initial_channel (str)
            - conversations_select : selected_conversation (str), initial_conversation (str)
            - datepicker : selected_date (str), initial_date (str)
            - timepicker : selected_time (str), initial_time (str)
            - plain_text_input : value (str), initial_value (str)
        - &data (https://api.slack.com/reference/block-kit/composition-objects)
    - api_app_id (str): A[A-Z0-9]{10}
    - channel (dict):
        - id (str): [C|G]A-Z0-9]{10}
        - name (str): #{channel_name}
    - container (dict):
        - channel_id (str): [C|G]A-Z0-9]{10}
        - is_ephemeral (bool): True|False
        - message_ts (str): [0-9]{10}.[0-9]{6}
        - type (str): message
    - enterprise : None
    - is_enterprise_install (bool): True|False
    - message (dict):
        - app_id (str): A[A-Z0-9]{10}
        - attachments (list : dict)
        - blocks (list : dict)
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
        - edited (dict):
            - ts (str): [0-9]{10}.[0-9]{6}
            - user (str): [B|U][A-Z0-9]{10}
        - team (str): T[A-Z0-9]{10}
        - text (str): {text}
        - ts (str): [0-9]{10}.[0-9]{6}
        - type (str): message|app_mention|message_changed|message_deleted
        - user (str): U[A-Z0-9]{10}
    - response_url (str): https://hooks.slack.com/app/{team_id}/[0-9]{13}/[0-9a-zA-Z]{24}
    - state (dict):
        - values (dict):
            - {block_id} (dict):
                - {action_id} (dict): {block_element}
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
    return (body.get(k, "") for k in values)


def cancel_edit(
    body: Dict[str, Any],
    logger: logging.Logger,
    ack: Ack,
    respond: Respond,
):
    """
    cancel editing message which is sent by the bot
    """
    logger.info(body)

    metadata = body["message"]["metadata"]
    text = metadata["event_payload"].get("text")

    ack()
    respond(blocks=[m.Section(text=m.mrkdwn(text=text))])


def save_edit(
    body: Dict[str, Any],
    logger: logging.Logger,
    client: slack_sdk.web.client.WebClient,
    ack: Ack,
    respond: Respond,
):
    """
    save editing message which is sent by the bot
    """
    logger.info(body)

    channel, message, state = get_values(body, ["channel", "message", "state"])
    channel_id = channel.get("id")
    message_ts = message.get("ts")
    metadata = message["metadata"]

    if state_values := state.get("values"):
        _, block = state_values.popitem()  # block_id, block: {action_id, block_element}
        _, state_value = block.popitem()  # action_id, state_value
        text = state_value.get("value")
        metadata["event_payload"].update(text=text)
    else:
        text = metadata["event_payload"].get("text")

    ack()
    if text:
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            blocks=[m.Section(text=m.mrkdwn(text=text))],
            metadata=metadata,
        )
    else:
        respond(delete_original=True)


def join_meet(
    body: Dict[str, Any],
    logger: logging.Logger,
    client: slack_sdk.web.client.WebClient,
    ack: Ack,
):
    """
    join_meet action for `/meet` command
    """
    logger.info(body)
    ack()
