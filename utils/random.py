import random


def shuffle(members, options):
    exclude, include = options
    for user in include:
        members.append(user[2:13])
    for user in exclude:
        if user[2:13] in members:
            members.remove(user[2:13])
    members.remove("U02EE3TDD5J")
    random.seed()
    random.shuffle(members)
    return members
