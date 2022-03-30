import re


def get_channels(text: str) -> list:
    """
    get mentioned channels from the text

    Args:
        text (str): the text to be parsed

    Returns:
        channels (list): the list of mentioned channels
    """
    # if the text is not empty, return the list of mentioned channels id from the text (if exist)
    # else return an empty list
    if text and (channels := re.findall(r"[C|G][A-Z0-9]{10}", text)):
        return channels  # ['Cxxxxxxxxxx', ...]: list
    else:
        return []


def get_users(text: str) -> list:
    """
    get mentioned users from the text

    Args:
        text (str): the text to be parsed

    Returns:
        users (list): the list of mentioned users
    """
    # if the text is not empty, return the list of mentioned users id from the text (if exist)
    # else return an empty list
    if text and (users := re.findall(r"U[A-Z0-9]{10}", text)):
        return users  # ['Uxxxxxxxxxx', ...]: list
    else:
        return []


def get_emojis(text: str) -> list:
    """
    get emojis from the text

    Args:
        text (str): the text to be parsed

    Returns:
        emojis (list): the list of emojis in text
    """
    # if the text is not empty, return the list of emojis from the text (if exist)
    # else return an empty list
    if text and (emojis := re.findall(r":[^\s]+:", text)):
        return emojis  # [':emoji:', ...]: list
    else:
        return []


def get_urls(text: str) -> list:
    """
    get urls from the text

    Args:
        text (str): the text to be parsed

    Returns:
        urls (list): the list of urls in text
    """
    # if the text is not empty, return the list of urls from the text (if exist)
    # else return an empty list
    if text and (urls := re.findall(r"<https?://[^\s]+>", text)):
        return urls  # ['<https://...>', ...]: list
    else:
        return []
