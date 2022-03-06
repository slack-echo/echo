import re


def get_mentioned_channels(text: str) -> list:
    """
    get mentioned channels from the text

    Args:
        text: the text

    Returns:
        mentioned_channels: the mentioned channels
    """
    # if the text is not empty, return the mentioned channel id list if exists
    if text:
        channels = re.findall(r"[C|G][A-Z0-9]{10}", text)  # ['Cxxxxxxxxxx', ...]: list
        return channels if channels else []
    # if the text is empty, return an empty list
    else:
        return []


def text_replace(text: str, replace_dict: dict = {}):
    """
    replace &lt; and |&gt; with < and > respectively and replace the text with the replace_dict

    Args:
        text: the text
        replace_dict: the replace dict

    Returns:
        text: the replaced text
    """
    default_dict = {"&lt;": "<", "|&gt;": ">"}
    default_dict.update(replace_dict)

    # replace keys in text with values in replace_dict and return the replaced text
    try:
        for key, value in default_dict.items():
            text = text.replace(key, value)
    except:
        pass
    return text


def parse_random_command(text):
    if text:
        if re.search(r"^help\s*", text):
            return 0, [], []
        else:
            num = re.search(r"^[1-9]\d*", text)
            exclude = re.search(r"(\-(\s<@U[A-Z0-9]{10}\|[a-z0-9_.-]+>)+)", text)
            include = re.search(r"(\+(\s<@U[A-Z0-9]{10}\|[a-z0-9_.-]+>)+)", text)
            return int(num.group()) if num else 1, exclude.group().split()[1:] if exclude else [], include.group().split()[1:] if include else []  # type: ignore
    else:
        return 1, [], []
