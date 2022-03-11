import re


def is_channel_mentioned(text):
    if text:
        channels = re.findall(r"[C|G][A-Z0-9]{10}", text)
        return channels if channels else []
    else:
        return []


def parse_random_command(text):
    if text:
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
    else:
        return 1, [], []
