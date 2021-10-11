import re


def is_channel_mention(text):
    if text is None:
        return False, None
    else:
        channels = re.findall(r"(^@[가-힣a-z0-9_-]+|\s@[가-힣a-z0-9_-]+)", text)
        for i, _ in enumerate(channels):
            channels[i] = channels[i].strip().strip("@")
        return (True, channels) if channels else (False, None)


def parse_random_command(text):
    if text is None:
        return 1, [], []
    else:
        if re.search(r"^help\s*", text):
            return 0, [], []
        else:
            num = re.search(r"^[1-9]\d*", text)
            exclude = re.search(r"(\-(\s<@U[A-Z0-9]{10}\|[a-z0-9_.-]+>)+)", text)
            include = re.search(r"(\+(\s<@U[A-Z0-9]{10}\|[a-z0-9_.-]+>)+)", text)
            return (
                int(num.group()) if num else 1,
                exclude.group().split()[1:] if exclude else [],
                include.group().split()[1:] if include else [],
            )
