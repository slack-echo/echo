import logging
from typing import Any, Dict

import utils.models as m
from slack_bolt import Ack, Say


def poll(
    body: Dict[str, Any],
    logger: logging.Logger,
    view: Dict[str, Any],
    ack: Ack,
    say: Say,
):
    """
    make a poll from the view submission
    """
    logger.info(body)

    state_values = view["state"]["values"]

    channel = state_values["channel"]["select"]["selected_conversation"]
    title = state_values["title"]["input"]["value"]
    options = [
        option
        for block_id, block in state_values.items()
        if block_id.startswith("option") and (option := block["input"]["value"])
    ]
    options = {f"option_{i+1}": option for i, option in enumerate(options)}
    settings = state_values["settings"]["checkboxes"]["selected_options"]
    settings = {setting["value"]: True for setting in settings}
    limit = state_values["limit"]["select"]["selected_option"]["value"]

    metadata = m.metadata(
        event_type="poll",
        event_payload={
            "channel": channel,
            "title": title,
            "options": options,
            "settings": settings,
            "limit": limit,
        },
    )

    blocks = [
        m.Header(block_id="title", text=m.plain_text(text=title, emoji=True)),
        m.Divider(),
        *(
            m.Section(
                block_id=block_id,
                text=m.mrkdwn(text=f"{i+1}. {option}\n"),
                accessory=m.button(
                    action_id="vote",
                    text=m.plain_text(text=f"{i+1}"),
                    value=option,
                ),
            )
            for i, (block_id, option) in enumerate(options.items())
        ),
        m.Divider(),
    ]

    ack()
    say(channel=channel, blocks=blocks, metadata=metadata)
