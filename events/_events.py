from utils.filters import channel_filter


def admin_mention(message, logger, client, say, respond):
    logger.info(message)
    user_id = message.get("user")
    channel_id = message.get("channel")
    conversations = client.conversations_list()
    channel = channel_filter(conversations, channel_id)
    ts = message.get("ts")
    text = message.get("text")
    text = text.replace("@admin", "").strip()
    pretext = f"<@{user_id}>님이 <#{channel_id}>에서 멘션했습니다."
    attachments = [
        {
            "mrkdwn_in": ["text", "footer"],
            "color": "#d0d0d0",
            "pretext": pretext,
            "author_name": f"<@{user_id}>",
            "author_link": f"<@{user_id}>",
            "text": text,
            "footer": f"<https://skkuwiki.slack.com/archives/{channel_id}/p{ts.replace('.','')}|에 게시됨>",
            "ts": ts,
        }
    ]
    say(attachments=attachments, channel="#admin_notion")


def echo(message, say):
    text = message.get("text")
    say(text)
