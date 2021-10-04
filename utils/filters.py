def getitem(object):
    return list(object)[0]


from abc import ABC, abstractmethod


class conversation_filter:
    class parameters:
        channel = {
            "id",
            "name",
            "is_channel",
            "created",
            "creator",
            "is_archived",
            "is_general",
            "name_normalized",
            "is_shared",
            "is_org_shared",
            "is_member",
            "is_private",
            "is_mpim",
            "last_read",
            "latest",
            "unread_count",
            "unread_count_display",
            "members",
            "topic",
            "purpose",
            "previous_names",
        }
        group = {
            "id",
            "name",
            "is_group",
            "created",
            "creator",
            "is_archived",
            "is_mpim",
            "members",
            "topic",
            "purpose",
            "last_read",
            "latest",
            "unread_count",
            "unread_count_display",
        }
        mpim = {
            "id",
            "name",
            "is_mpim",
            "is_group",
            "created",
            "creator",
            "members",
            "last_read",
            "latest",
            "unread_count",
            "unread_count_display",
        }
        im = {
            "id",
            "is_im",
            "user",
            "created",
            "is_user_deleted",
        }

        def __new__(cls, supcls=None):
            if supcls:
                if "channel" in supcls.__name__:
                    return cls.channel
                elif "group" in supcls.__name__:
                    return cls.group
                elif "mpim" in supcls.__name__:
                    return cls.mpim
                elif "im" in supcls.__name__:
                    return cls.im
            parameters = [cls.channel, cls.group, cls.mpim, cls.im]
            return set.union(*parameters)

        def __init__(self):
            self._channel = self.channel
            self._group = self.group
            self._mpim = self.mpim
            self._im = self.im
            self._conversation = set.union(self.channel, self.group, self.mpim, self.im)

        def __call__(self, supcls=None):
            if supcls:
                if "channel" in supcls.__name__:
                    return self._channel
                elif "group" in supcls.__name__:
                    return self._group
                elif "mpim" in supcls.__name__:
                    return self._mpim
                elif "im" in supcls.__name__:
                    return self._im
            return self._conversation

    def __new__(cls, *args, **kwargs):
        parameters = cls.parameters.__new__(cls.parameters, cls.__class__)
        assert set(kwargs).issubset(parameters), "Invalid Parameters"
        return super().__new__(cls)

    def __init__(self, conversations, **conditions):
        self.conditions = conditions
        self.conversations = list(
            filter(
                lambda c: all(
                    condition in c.items() for condition in conditions.items()
                ),
                conversations,
            )
        )
        self._id = [conversation["id"] for conversation in self.conversations]
        self._name = [
            conversation["user"] if conversation.get("is_im") else conversation["name"]
            for conversation in self.conversations
        ]
        self._created = [conversation["created"] for conversation in self.conversations]
        self._parameter = self.parameters.__new__(self.parameters, self.__class__)

    @property
    def id(self):
        return self._id

    @id.deleter
    def id(self):
        del self._id

    @property
    def name(self):
        return self._name

    @name.deleter
    def name(self):
        del self._name

    @property
    def created(self):
        return self._created

    @created.deleter
    def created(self):
        del self._created

    @property
    def parameter(self):
        return self._parameter


class channel_filter(conversation_filter):
    """public channel"""

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, conversations, **conditions):
        conditions.update({"is_channel": True})
        super().__init__(conversations, **conditions)


class group_filter(conversation_filter):
    """private channel"""

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, conversations, **conditions):
        conditions.update({"is_group": True})
        super().__init__(conversations, **conditions)


class mpim_filter(conversation_filter):
    """group direct message"""

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, conversations, **conditions):
        conditions.update({"is_mpim": True})
        super().__init__(conversations, **conditions)


class im_filter(conversation_filter):
    """direct message"""

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, conversations, **conditions):
        conditions.update({"is_im": True})
        super().__init__(conversations, **conditions)
