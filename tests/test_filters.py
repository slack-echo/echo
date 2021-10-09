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
    {
        "id": "C012AB3CD",
        "name": "general",
        "testtest": True,
        "last_read": "1502126650.228446",
        "topic": {
            "value": "For public discussion of generalities",
            "creator": "W012A3BCD",
            "last_set": 1449709364,
        },
        "created": 1449252889,
    },
]


def test_conversation_filter(conversations, **conditions):
    conversation = ConversationFilter(conversations, **conditions)
    print(conversation.id)
    print(conversation.name)


def test_channel_filter(conversations, **conditions):
    channel = ChannelFilter(conversations, **conditions)
    print(channel.id)
    print(channel.name)


def test_group_filter(conversations, **conditions):
    group = GroupFilter(conversations, **conditions)
    print(group.id)
    print(group.name)


def test_mpim_filter(conversations, **conditions):
    mpim = MpimFilter(conversations, **conditions)
    print(mpim.id)
    print(mpim.name)


def test_im_filter(conversations, **conditions):
    im = ImFilter(conversations, **conditions)
    print(im.id)
    print(im.name)


if __name__ == "__main__":
    test_conversation_filter(conversations, id="C012AB3CD")
    test_channel_filter(conversations, id="C012AB3CD")
    test_group_filter(conversations, id="C012AB3CD")
    test_mpim_filter(conversations, id="C012AB3CD")
    test_im_filter(conversations, id="C012AB3CD")
