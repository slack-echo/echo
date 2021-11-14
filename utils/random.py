import random
from collections import Counter


def shuffle(members, options):
    exclude, include = options
    parse = lambda member: member[2:13]
    members = list(set(members) | set(map(parse, include)) - set(map(parse, exclude)))
    members.remove("U02EE3TDD5J")
    random.seed()
    random.shuffle(members)
    return members


def select(members, num_to_select):
    selected_members = []
    count = 0
    while count < min(num_to_select, len(set(members))):
        if members[count] not in selected_members:
            selected_members.append(members[count])
        count += 1
    return selected_members


def choices(members, num_to_select, options):
    exclude, include = options
    parse = lambda member: member[2:13]
    counter = (
        Counter(members) + Counter(map(parse, include)) - Counter(map(parse, exclude))
    )
    del counter["U02EE3TDD5J"]
    random.seed()
    selected_members = random.choices(
        tuple(counter.keys()), weights=counter.values(), k=num_to_select
    )
    return selected_members
