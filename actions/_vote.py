def vote(ack, body, respond, action):
    ack()

    user = body["user"]["id"]
    blocks = body["message"]["blocks"]
    for block in blocks:
        if block["block_id"] == action["block_id"]:
            break
    if user not in block["text"]["text"]:
        block["text"]["text"] += "<@" + user + ">\n"
    else:
        votes = block["text"]["text"]
        block["text"]["text"] = (
            votes[0 : votes.find(user) - 2] + votes[votes.find(user) + len(user) + 1 :]
        )

    respond(blocks=blocks, replace_original=True, delete_original=False)
