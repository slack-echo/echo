import sys

sys.path = [
    "/home/ubuntu/Documents/google-cloud-platform/gbme/functions/echo"
] + sys.path
from utils.filters import *

conversations = [
    {
        "id": "C012AB3CD",
        "name": "general",
        "is_channel": True,
        "is_group": False,
        "is_im": False,
        "created": 1449252889,
        "creator": "W012A3BCD",
        "is_archived": False,
        "is_general": True,
        "unlinked": 0,
        "name_normalized": "general",
        "is_read_only": False,
        "is_shared": False,
        "is_ext_shared": False,
        "is_org_shared": False,
        "pending_shared": [],
        "is_pending_ext_shared": False,
        "is_member": True,
        "is_private": False,
        "is_mpim": False,
        "last_read": "1502126650.228446",
        "topic": {
            "value": "For public discussion of generalities",
            "creator": "W012A3BCD",
            "last_set": 1449709364,
        },
        "purpose": {
            "value": "This part of the workspace is for fun. Make fun here.",
            "creator": "W012A3BCD",
            "last_set": 1449709364,
        },
        "previous_names": ["specifics", "abstractions", "etc"],
        "num_members": 23,
        "locale": "en-US",
    },
]


def test_conversation_filter(conversations, **conditions):
    conversation = conversation_filter(conversations, **conditions)
    print(len(conversation.parameter))
    print(conversation.id)
    print(conversation.name)


def test_channel_filter(conversations, **conditions):
    channel = channel_filter(conversations, **conditions)
    print(len(channel.parameter))
    print(channel.id)
    print(channel.name)


def test_group_filter(conversations, **conditions):
    group = group_filter(conversations, **conditions)
    print(len(group.parameter))
    print(group.id)
    print(group.name)


def test_mpim_filter(conversations, **conditions):
    mpim = mpim_filter(conversations, **conditions)
    print(len(mpim.parameter))
    print(mpim.id)
    print(mpim.name)


def test_im_filter(conversations, **conditions):
    im = im_filter(conversations, **conditions)
    print(len(im.parameter))
    print(im.id)
    print(im.name)


if __name__ == "__main__":
    test_conversation_filter(conversations, id="C012AB3CD")
    test_channel_filter(conversations, id="C012AB3CD")
    test_group_filter(conversations, id="C012AB3CD")
    test_mpim_filter(conversations, id="C012AB3CD")
    test_im_filter(conversations, id="C012AB3CD")
