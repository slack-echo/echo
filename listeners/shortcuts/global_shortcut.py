import logging
from typing import Any, Dict

import slack_sdk
import utils.models as m
from slack_bolt import Ack


def poll(
    body: Dict[str, Any],
    logger: logging.Logger,
    client: slack_sdk.web.client.WebClient,
    ack: Ack,
):
    """
    make a poll
    """
    logger.info(body)

    ack()
    blocks = [
        m.Input(
            block_id="channel",
            label=m.plain_text(text=":hash: 채널", emoji=True),
            element=m.conversations_select(
                action_id="select",
                default_to_current_conversation=True,
                placeholder=m.plain_text(text="채널 선택"),
                filter=m.filter(
                    include=["public", "private", "mpim"],
                    exclude_bot_users=True,
                ),
            ),
        ),
        m.Divider(),
        m.Input(
            block_id="title",
            label=m.plain_text(text=":ballot_box_with_ballot: 투표 제목", emoji=True),
            element=m.plain_text_input(action_id="input"),
        ),
        m.Input(
            block_id="option_1",
            label=m.plain_text(text="항목 1"),
            element=m.plain_text_input(action_id="input"),
        ),
        m.Input(
            block_id="option_2",
            label=m.plain_text(text="항목 2"),
            element=m.plain_text_input(action_id="input"),
        ),
        m.Input(
            block_id="option_3",
            label=m.plain_text(text="항목 3"),
            element=m.plain_text_input(action_id="input"),
            optional=True,
        ),
        m.Actions(
            block_id="add_option",
            elements=[
                m.button(
                    text=m.plain_text(text=":heavy_plus_sign: 항목 추가"),
                    action_id="add_option",
                )
            ],
        ),
        m.Divider(),
        m.Input(
            block_id="settings",
            label=m.plain_text(text="설정"),
            element=m.checkboxes(
                action_id="checkboxes",
                options=[
                    m.option(
                        text=m.mrkdwn(text=":bust_in_silhouette: *익명으로 투표*"),
                        value="anonymous",
                    ),
                    m.option(
                        text=m.mrkdwn(text=":heavy_plus_sign: *항목 추가 허용*"),
                        value="allow_add_option",
                    ),
                ],
            ),
            optional=True,
        ),
        m.Input(
            block_id="limit",
            label=m.plain_text(text="1인당 투표 수 제한"),
            element=m.static_select(
                action_id="select",
                initial_option=m.option(text=m.plain_text(text="제한 없음"), value="0"),
                options=[
                    m.option(text=m.plain_text(text="제한 없음"), value="0"),
                    m.option(text=m.plain_text(text="1표"), value="1"),
                    m.option(text=m.plain_text(text="2표"), value="2"),
                ],
            ),
        ),
    ]
    client.views_open(
        trigger_id=body["trigger_id"],
        view=m.View(
            type="modal",
            callback_id="poll",
            title=m.plain_text(text="투표 올리기"),
            submit=m.plain_text(text="미리보기"),
            close=m.plain_text(text="취소"),
            blocks=blocks,
        ),
    )
