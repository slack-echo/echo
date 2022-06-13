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
    - view (dict):
        - app_id : A[A-Z0-9]{10}
        - app_installed_team_id (str): T[A-Z0-9]{10}
        - blocks (list : dict)
        - bot_id (str): B[A-Z0-9]{10}
        - callback_id (str): {callback_id}
        - clear_on_close (bool): False
        - close (dict): {block}
        - external_id (str): ''
        - hash (str): [0-9]{10}.[a-zA-Z]{8}
        - id (str): V[A-Z0-9]{10}
        - notify_on_close (bool): False
        - previous_view_id (str): V[A-Z0-9]{10}|None
        - private_metadata (str)
        - root_view_id (str): V[A-Z0-9]{10}
        - state (dict): {state}
        - submit (dict): {block}
        - team_id (str): T[A-Z0-9]{10}
        - title (dict): {block}
        - type (str): modal

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


def add_option(
    body: Dict[str, Any],
    logger: logging.Logger,
    client: slack_sdk.web.client.WebClient,
    action: Dict[str, Any],
    ack: Ack,
):
    """
    add poll option
    """
    logger.info(body)

    index, value = map(int, action.get("value").split("."))
    option = m.Input(
        block_id=f"option_{value}",
        label=m.plain_text(text=f"항목 {value}"),
        element=m.plain_text_input(action_id="input"),
        optional=True,
    )
    limit_option = m.option(text=m.plain_text(text=f"{value-1}표"), value=str(value - 1))

    view = body["view"]
    blocks = view["blocks"]
    blocks[index] = m.Actions(
        block_id="add_option",
        elements=[
            m.button(
                text=m.plain_text(text=":heavy_plus_sign: 항목 추가"),
                action_id="add_option",
                value=f"{index+1}.{value+1}",
            )
        ],
    )
    blocks.insert(index, option)
    blocks[-1]["element"]["options"].append(limit_option)

    view_id = view.get("id")
    hash = view.get("hash")
    ack()
    client.views_update(
        view=m.View(
            type=view["type"],
            callback_id=view["callback_id"],
            title=view["title"],
            submit=view["submit"],
            close=view["close"],
            blocks=blocks,
        ),
        view_id=view_id,
        hash=hash,
    )


def vote(
    body: Dict[str, Any],
    logger: logging.Logger,
    action: Dict[str, Any],
    ack: Ack,
    respond: Respond,
):
    """
    vote selected option for poll
    """
    logger.info(body)

    message, user = get_values(body, ["message", "user"])
    blocks = message.get("blocks")
    user_id = user.get("id")
    block_id = action.get("block_id")

    for block in blocks:
        if block["block_id"] == block_id:
            break
    state_value = block.get("text", {})
    text = state_value.get("text")

    if user_id in text:
        state_value.update(text=text.replace(f"<@{user_id}> ", ""))
    else:
        state_value.update(text=text + f"<@{user_id}> ")

    ack()
    respond(blocks=blocks)
