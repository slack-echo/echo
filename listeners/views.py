import logging
from typing import Any, Dict

import utils.models as m
from slack_bolt import Ack, Say


def preview_poll(
    body: Dict[str, Any],
    logger: logging.Logger,
    view: Dict[str, Any],
    ack: Ack,
):
    """
    preview a poll from the view submission

    settings (int): (0 ~ 3)
        - anonymous (1): anonymous vote
        - add_option_allowed (2): add option allowed
    limit (int):
        - unlimited (0): no limit
        - limited (1+): limited
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
    settings = sum(int(setting["value"]) for setting in settings)
    limit = state_values["limit"]["select"]["selected_option"]["value"]

    blocks = [
        m.Context(elements=[m.mrkdwn(text=f"<#{channel}>")]),
        m.Section(block_id="title", text=m.mrkdwn(text=title)),
        m.Divider(),
        *(
            m.Section(block_id=block_id, text=m.mrkdwn(text=f"{i+1}. {option}\n"))
            for i, (block_id, option) in enumerate(options.items())
        ),
        m.Divider(),
        m.Context(
            elements=[m.mrkdwn(text=f"<@{body['user']['id']}>님이 `/poll`를 실행하였습니다.")]
        ),
    ]
    ack(
        response_action="push",
        view=m.View(
            type="modal",
            callback_id="create_poll",
            title=m.plain_text(text="투표 미리보기"),
            submit=m.plain_text(text="투표 올리기"),
            close=m.plain_text(text="취소"),
            blocks=blocks,
            private_metadata=f"{channel}.{settings}.{limit}",
        ),
    )


def create_poll(
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

    channel, settings, limit = view["private_metadata"].split(".")

    metadata = m.metadata(
        event_type="poll",
        event_payload={
            "channel": channel,
            "settings": settings,
            "limit": limit,
        },
    )

    overflow = m.overflow(
        action_id="poll_overflow",
        options=[
            m.option(
                text=m.plain_text(text=":pushpin: 투표 종료", emoji=True),
                value="end_poll",
            ),
            m.option(
                text=m.plain_text(text=":x: 투표 취소", emoji=True),
                value="cancel_poll",
            ),
        ],
    ).to_dict()

    blocks = view["blocks"]
    _, *blocks = blocks

    title = blocks[0]
    title.update(accessory=overflow)

    options = blocks[2:-2]
    for i, option in enumerate(options):
        option.update(
            accessory=m.button(
                action_id="vote",
                text=m.plain_text(text=f"{i+1}"),
                value=f"{i+1}",
            ).to_dict(),
        )

    ack(response_action="clear")
    say(channel=channel, blocks=blocks, metadata=metadata)
