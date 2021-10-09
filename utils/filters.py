import yaml

file = open("utils/params.yaml", "r")
params = yaml.safe_load(file)


class ConversationFilter:
    def __new__(cls, *args, **kwargs):
        parameters = set(
            params.get(cls.__name__.upper(), set.union(*map(set, params.values())))
        )
        assert set(kwargs).issubset(parameters), "Invalid Parameters"
        return super().__new__(cls)

    def __init__(self, conversations, **conditions):
        self.conditions = conditions
        if conversations:
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
                conversation["user"]
                if conversation.get("is_im")
                else conversation["name"]
                for conversation in self.conversations
            ]
            self._created = [
                conversation["created"] for conversation in self.conversations
            ]
            self._parameter = (
                set.intersection(*self.parameters()) if self.parameters() else set()
            )

    def __del__(self):
        del self

    def parameters(self):
        return [set(conversation.keys()) for conversation in self.conversations]

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

    @parameter.deleter
    def parmeter(self):
        del self._parameter


class ChannelFilter(ConversationFilter):
    """public channel"""

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, conversations, **conditions):
        conditions.update({"is_channel": True})
        super().__init__(conversations, **conditions)


class GroupFilter(ConversationFilter):
    """private channel"""

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, conversations, **conditions):
        conditions.update({"is_group": True})
        super().__init__(conversations, **conditions)


class MpimFilter(ConversationFilter):
    """group direct message"""

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, conversations, **conditions):
        conditions.update({"is_mpim": True})
        super().__init__(conversations, **conditions)


class ImFilter(ConversationFilter):
    """direct message"""

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, conversations, **conditions):
        conditions.update({"is_im": True})
        super().__init__(conversations, **conditions)
