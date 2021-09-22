import os
import yaml
from slack_bolt import App

# Initializes your app with your bot token and signing secret
# app = App(
#     token=os.environ.get("SLACK_BOT_TOKEN"),
#     signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
# )
file = open("functions/bolt/.env.yaml")
secrets = yaml.safe_load(file)
file.close()
app = App(
    token=secrets.get("SLACK_BOT_TOKEN"),
    signing_secret=secrets.get("SLACK_SIGNING_SECRET"),
)


def log(
    ack,
    action,
    body,
    client,
    command,
    context,
    event,
    next,
    next_,
    options,
    payload,
    req,
    request,
    resp,
    respond,
    response,
    say,
    shortcut,
    view,
):
    print("ack")
    print(ack)
    print()
    print("action")
    print(action)
    print()
    print("body")
    print(body)
    print()
    print("client")
    print(client)
    print()
    print("command")
    print(command)
    print()
    print("context")
    print(context)
    print()
    print("event")
    print(event)
    print()
    print("next")
    print(next)
    print()
    print("next_")
    print(next_)
    print()
    print("options")
    print(options)
    print()
    print("payload")
    print(payload)
    print()
    print("req")
    print(req)
    print()
    print("request")
    print(request)
    print()
    print("resp")
    print(resp)
    print()
    print("respond")
    print(respond)
    print()
    print("response")
    print(response)
    print()
    print("say")
    print(say)
    print()
    print("shortcut")
    print(shortcut)
    print()
    print("view")
    print(view)
    print()


@app.message("user")
def user_list(message, client, say):
    channel = message["channel"]
    users = client.conversations_members(
        token=secrets.get("SLACK_BOT_TOKEN"), channel=channel
    )
    text = ", ".join(list(map(lambda u: f"<@{u}>", users["members"])))
    say(text=text)


# TODO
# WEB API -> act
# - views.open, update, push : dynamic
# - views.publish : static
# - users.identity[u], user.info[b|u], users.profile.get[b|u] : info
# - users.list : all users
# - users.lookupByEmail : search by email
## identity:basic, uers:read.profile email, channels:read, groups:read, im:read, mpim:read
# - reactions.add, get, list, remove
## reactions:write, read,
# - files.upload : gif?
## files:write
# - dialog.open : knowledge?
# - conversations.history, info, invite, members, replies
## *:history, *:read, *:write,
# - chat.update, unfurl, scheduleMessage, postMessage, postEphemeral, meMessage, getPermalink, deleteScheduledMessage, delete
## chat:write, links:write
# - bot.info
## users:read
# - admin for Enterprise
# Event API -> read


# @app.event("message")
# def handle_message_events(body, logger, message, say):
#     logger.info(body)
#     say(f"{message['text']}")


@app.command("/echo")
def echo(body, logger, command, ack, say):
    logger.info(body)
    text = command.get("text")
    if text is None or len(text) == 0:
        # Acknowledge command request
        ack(f":x: 사용법 `/echo 텍스트`")
    else:

        ack()
        say(f"{command['text']}")


@app.message("hello")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click",
                },
            }
        ],
        text=f"Hey there <@{message['user']}>!",
    )


@app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    say(f"<@{body['user']['id']}> clicked the button")


@app.event("reaction_added")
def show_datepicker(event, say):
    print(event)
    reaction = event["reaction"]
    if reaction == "calendar":
        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Pick a date for me to remind you"},
                "accessory": {
                    "type": "datepicker",
                    "action_id": "datepicker_remind",
                    "initial_date": "2020-05-04",
                    "placeholder": {"type": "plain_text", "text": "Select a date"},
                },
            }
        ]
        say(blocks=blocks, text="Pick a date for me to remind you")


@app.action("datepicker_remind")
def handle_some_action(ack, body, logger):
    ack()
    logger.info(body)


@app.shortcut("create_poll")
def create_poll(ack, body, client, logger):
    ack()
    logger.info(body)
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "create_poll",
            "title": {"type": "plain_text", "text": "투표 올리기"},
            "submit": {"type": "plain_text", "text": "미리보기"},
            "close": {"type": "plain_text", "text": "취소"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "channel",
                    "element": {
                        "type": "conversations_select",
                        "default_to_current_conversation": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "채널 선택",
                            "emoji": True,
                        },
                        "filter": {
                            "include": [
                                "public",
                                "private",
                                "mpim",
                            ],
                            "exclude_bot_users": True,
                        },
                        "action_id": "conversations_select-action",
                    },
                    "label": {"type": "plain_text", "text": "#️⃣ 채널"},
                },
                {"type": "divider"},
                {
                    "type": "input",
                    "block_id": "title",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "plain_text_input-action",
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "🗳️ 투표 제목",
                        "emoji": True,
                    },
                },
                {
                    "type": "input",
                    "block_id": "option_1",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "plain_text_input-action",
                    },
                    "label": {"type": "plain_text", "text": "항목 1", "emoji": True},
                },
                {
                    "type": "input",
                    "block_id": "option_2",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "plain_text_input-action",
                    },
                    "label": {"type": "plain_text", "text": "항목 2", "emoji": True},
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": ":heavy_plus_sign: 항목 추가",
                                "emoji": True,
                            },
                            "action_id": "button_add_option",
                        }
                    ],
                },
                {"type": "divider"},
                {
                    "type": "input",
                    "optional": True,
                    "block_id": "settings",
                    "element": {
                        "type": "checkboxes",
                        "options": [
                            {
                                "text": {
                                    "type": "mrkdwn",
                                    "text": ":alphabet-white-question: *익명으로 투표*",
                                },
                                "value": "anonymous",
                            },
                            {
                                "text": {
                                    "type": "mrkdwn",
                                    "text": ":heavy_plus_sign: *항목 추가 허용*",
                                },
                                "value": "allow-add-options",
                            },
                        ],
                        "action_id": "checkboxes-action",
                    },
                    "label": {"type": "plain_text", "text": "설정", "emoji": True},
                },
                {
                    "type": "input",
                    "block_id": "limits",
                    "element": {
                        "type": "static_select",
                        "initial_option": {
                            "text": {"type": "plain_text", "text": "제한 없음"},
                            "value": "0",
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "제한 없음",
                                    "emoji": True,
                                },
                                "value": "0",
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "1표",
                                    "emoji": True,
                                },
                                "value": "1",
                            },
                        ],
                        "action_id": "static_select-action",
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "1인당 투표 수 제한",
                        "emoji": True,
                    },
                },
            ],
        },
    )


@app.options("limits")
# "type": "external_select",
# "placeholder": {"type": "plain_text", "text": "select"},
# "min_query_length": 0,
def show_selection(ack):
    options = [
        {
            "text": {
                "type": "plain_text",
                "text": "제한 없음",
                "emoji": True,
            },
            "value": "0",
        },
        {
            "text": {
                "type": "plain_text",
                "text": "1표",
                "emoji": True,
            },
            "value": "1",
        },
    ]
    ack(options=options)


@app.action("button_add_option")
def add_option(ack, body, client):
    ack()
    blocks = body["view"]["blocks"]
    last_option_text = blocks[-5]["label"]["text"]
    last_option_number = last_option_text.split()[-1]
    next_option_number = str(int(last_option_number) + 1)
    add_option_text = last_option_text.replace(last_option_number, next_option_number)
    blocks.insert(
        -4,
        {
            "type": "input",
            "optional": True,
            "block_id": "option_" + next_option_number,
            "element": {
                "type": "plain_text_input",
                "action_id": "plain_text_input-action",
            },
            "label": {
                "type": "plain_text",
                "text": add_option_text,
                "emoji": True,
            },
        },
    )
    limits = blocks[-1]["element"]["options"]
    limits.append(
        {
            "text": {
                "type": "plain_text",
                "text": last_option_number + "표",
                "emoji": True,
            },
            "value": last_option_number,
        }
    )
    client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        view={
            "type": "modal",
            "callback_id": "create_poll",
            "title": body["view"]["title"],
            "submit": body["view"]["submit"],
            "close": body["view"]["close"],
            "blocks": blocks,
        },
    )


@app.action("checkboxes-action")
def check(ack, action, body):
    ack()
    blocks = body["message"]["blocks"]
    initial_options = action["selected_options"]
    blocks[3]["accessory"]["initial_options"] = initial_options


@app.view("create_poll")
def handle_submission(ack, body, client, view, logger, say):
    values = view["state"]["values"]
    user = body["user"]["id"]
    channel = values["channel"]["conversations_select-action"]["selected_conversation"]
    title = values["title"]["plain_text_input-action"]["value"]
    options = [
        value["plain_text_input-action"]["value"]
        for key, value in values.items()
        if "option" in key and value["plain_text_input-action"].get("value")
    ]
    options = [
        {
            "text": {
                "type": "mrkdwn",
                "text": text,
            },
            "value": f"{i+1}",
        }
        for i, text in enumerate(options)
    ]
    settings = values["settings"]["checkboxes-action"]["selected_options"]
    settings = [setting["value"] for setting in settings]
    limits = values["limits"]["static_select-action"]["selected_option"]["value"]
    ack()
    logger.info(body)
    say(
        channel=channel,
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Q. {title}",
                    "emoji": True,
                },
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"Poll by <@{user}>"}],
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "This is a section block with checkboxes.",
                },
                "accessory": {
                    "type": "checkboxes",
                    "initial_options": [],
                    "options": options,
                    "action_id": "checkboxes-action",
                },
            },
            {
                "type": "context",
                "elements": [
                    {"type": "plain_text", "emoji": True, "text": f" 명"},
                ],
            },
            # {"type": "context", "elements": [{"type": "mrkdwn", "text": "No votes"}]},
            {"type": "divider"},
            {
                "dispatch_action": True,
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "input_add_option",
                },
                "label": {"type": "plain_text", "text": "항목 추가", "emoji": True},
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ":heavy_plus_sign: 항목 추가",
                            "emoji": True,
                        },
                        "action_id": "button_add_option",
                    }
                ],
            },
        ],
    )


@app.action("input_add_option")
def add_option(ack, action, body, say, res):
    ack()
    blocks = body["message"]["blocks"]
    values = body["state"]["values"]
    text = action["value"]


# Handle a view_submission request
@app.view("view_1")
def handle_submission(ack, body, client, view, logger):
    # Assume there's an input block with `block_c` as the block_id and `dreamy_input`
    hopes_and_dreams = view["state"]["values"]["input_c"]["dreamy_input"]["value"]
    user = body["user"]["id"]
    # Validate the inputs
    errors = {}
    if hopes_and_dreams is not None and len(hopes_and_dreams) <= 5:
        errors["block_c"] = "The value must be longer than 5 characters"
    if len(errors) > 0:
        ack(response_action="errors", errors=errors)
        return
    # Acknowledge the view_submission request and close the modal
    ack()
    # Do whatever you want with the input data - here we're saving it to a DB
    # then sending the user a verification of their submission

    # Message to send user
    msg = ""
    try:
        # Save to DB
        msg = f"Your submission of {hopes_and_dreams} was successful"
    except Exception as e:
        # Handle error
        msg = "There was an error with your submission"

    # Message the user
    try:
        client.chat_postMessage(channel=user, text=msg)  # cannot delete
    except e:
        logger.exception(f"Failed to post a message {e}")


# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
