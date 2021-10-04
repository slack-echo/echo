def echo(body, logger, command, ack, say):
    logger.info(body)
    text = command.get("text")
    if text is None or len(text) == 0:
        ack(":x: 사용법 `/echo 메시지`")
    else:
        ack()
        say(text)
