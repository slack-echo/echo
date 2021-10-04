import copy


def poll(ack, body, say, command, respond):
    ack()
    user_id = body["user_id"]
    convert = [
        ":zero:",
        ":one:",
        ":two:",
        ":three:",
        ":four:",
        ":five:",
        ":six:",
        ":seven:",
        ":eight:",
        ":nine:",
    ]
    if "text" in command:
        if chr(8220) not in command["text"] and '"' not in command["text"]:
            respond(
                text="Error, please use quotation marks to separate each item!",
                replace_original=False,
                delete_original=False,
            )
            return
        message = (
            command["text"].replace(chr(8221), '"').replace(chr(8220), '"').split('"')
        )
        message = [x for x in message if x != "" and x != " "]
        question = message[0]
        options = message[1:]

        block_template = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "", "verbatim": False},
            "accessory": {
                "type": "button",
                "action_id": "vote",
                "text": {"type": "plain_text", "text": "", "emoji": True},
            },
        }
        blocks = [
            {
                "type": "section",
                # "block_id": "poll-9c223f52-1e8d-4c85-974f-9b6ed21e395e-title-and-menu",
                "text": {"type": "mrkdwn", "text": question, "verbatim": False},
                "accessory": {
                    "type": "overflow",
                    "action_id": "title-and-menu",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": ":information_source: View info",
                                "emoji": True,
                            },
                            "value": "view_info",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": ":pushpin: Capture Decision from Poll",
                                "emoji": True,
                            },
                            "value": "capture_decision_from_poll",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": ":x: Delete Poll",
                                "emoji": True,
                            },
                            "value": "delete_poll",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": ":house: Go to App Home",
                                "emoji": True,
                            },
                            "value": "go_to_app_home",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": ":bar_chart: Create new Poll",
                                "emoji": True,
                            },
                            "value": "create_new_poll",
                        },
                    ],
                },
            }
        ]
        for i in range(len(options)):
            curr = copy.deepcopy(block_template)
            curr["text"]["text"] = options[i] + "\n"
            num_str = ""
            num = i + 1
            while num > 0:
                num_str = convert[num % 10] + num_str
                num //= 10
            curr["accessory"]["text"]["text"] = num_str
            blocks.append(curr)
        blocks.append(
            {
                "type": "context",
                # "block_id": "nSR",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Created by <@" + command["user_id"] + "> with /poll",
                        "verbatim": False,
                    }
                ],
            }
        )
        print(blocks)
        say(blocks=blocks, text=f"`{command['text']}`")
