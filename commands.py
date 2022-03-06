from utils.text import is_channel_mention, parse_random_command
from utils.random import shuffle


def echo(body, logger, command, ack, say):
    logger.info(body)
    channel_id = command.get("channel_id")
    text = command.get("text")
    channel_mentioned, channels = is_channel_mention(text)
    if text is None:
        ack(
            ":x: 실행되지 않았습니다."
            + "\n\n:information_source: 사용법"
            + "\n`/echo 메시지 [@admin|@운영위원회|...]` : 현재 채널에서 에코 메시지 [@채널 멘션 알림]\n"
        )
    else:
        ack()
        say(text)
        if channel_mentioned:
            attachments = [
                {
                    "mrkdwn_in": ["text", "footer"],
                    "color": "#d0d0d0",
                    "pretext": f"이 채널이 <#{channel_id}>에서 멘션되었습니다.",
                    "text": text,
                    "fallback": "",
                }
            ]
            for channel in channels:
                say(attachments=attachments, channel=channel)


def send(body, logger, command, ack, say):
    logger.info(body)
    user_id = command.get("user_id")
    text = command.get("text")
    channel_mention, channels = is_channel_mention(text)
    if channel_mention:
        ack(f"#{' #'.join(channels)}로 메시지를 보냈습니다.\n> {text}")
        attachments = [
            {
                "mrkdwn_in": ["text", "footer"],
                "color": "#d0d0d0",
                "pretext": f"<@{user_id}>님이 보낸 메시지 입니다.",
                "text": text,
                "fallback": " ",
            }
        ]
        for channel in channels:
            say(attachments=attachments, channel=channel)
    else:
        ack(
            ":x: 실행되지 않았습니다."
            + "\n\n:information_source: 사용법"
            + "\n`/send (@admin|@운영위원회|...) 메시지` : @채널로 메시지 전달"
        )


def random(body, logger, client, command, ack, say):
    logger.info(body)
    channel_id = command.get("channel_id")
    user_id = command.get("user_id")
    text = command.get("text")
    num_to_select, *options = parse_random_command(text)
    members = client.conversations_members(channel=channel_id).get("members")
    shuffle(members, options)
    selectable = len(set(members))
    if selectable and num_to_select:
        ack()
        selected_members = []
        count = 0
        while (count < num_to_select) and (count < selectable):
            if members[count] not in selected_members:
                selected_members.append(members[count])
            count += 1
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join(
                        [f"{i+1}. <@{user}>" for i, user in enumerate(selected_members)]
                    ),
                    "verbatim": False,
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"<@{user_id}>님이 "
                        + (f"`/random {text}`" if text else "`/random`")
                        + "로 랜덤 선택하였습니다.",
                        "verbatim": False,
                    }
                ],
            },
        ]
        say(blocks=blocks)
    else:
        ack(
            ":information_source: 사용법"
            + "\n`/random [숫자] [옵션]` : [숫자]인원만큼 랜덤 선택 (기본값=1)"
            + "\n\n:heavy_plus_sign: 옵션"
            + "\n`-` : 인원에서 제외"
            + "\n`+` : 인원에 포함"
            + "\n\n:mag: 예시"
            + "\n`/random` : 1명 랜덤 선택"
            + "\n`/random 2` : 2명 랜덤 선택"
            + f"\n`/random 3 - <@{user_id}>` : <@{user_id}>을 제외하여 3명 랜덤 선택"
            + f"\n`/random 4 + <@{user_id}>` : <@{user_id}>을 포함하여 4명 랜덤 선택"
            + "\n\n:bulb: 팁"
            + "\n `+` 옵션을 이용하여 채널 외부 인원을 포함하거나, 추가한 횟수만큼 선택될 확률을 높일 수 있습니다."
        )
