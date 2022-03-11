import random


def shuffle(members, options):
    exclude, include = options
    parse = lambda member: member[2:13]
    members = list(set(members) | set(map(parse, include)) - set(map(parse, exclude)))
    members.remove("U02EE3TDD5J")
    random.seed()
    random.shuffle(members)
    return members
