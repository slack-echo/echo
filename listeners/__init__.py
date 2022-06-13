from . import actions, commands, views
from .shortcuts import global_shortcut, message_shortcut


def is_echo(shortcut):
    event_type = shortcut.get("message", {}).get("metadata", {}).get("event_type", "")
    return event_type == "echo"


def listen(app):
    # commands
    app.command("/echo")(commands.echo)
    app.command("/anonymous")(commands.echo)
    app.command("/disguise")(commands.echo)
    app.command("/>")(commands.echo)
    app.command("/send")(commands.send)
    app.command("/shuffle")(commands.rand)
    app.command("/choices")(commands.rand)
    app.command("/meet")(commands.meet)

    # shortcuts
    app.shortcut("delete_message", [is_echo])(message_shortcut.delete_message)
    app.shortcut("edit_message", [is_echo])(message_shortcut.edit_message)
    app.shortcut("poll")(global_shortcut.poll)

    # actions
    app.action("save_edit")(actions.save_edit)
    app.action("cancel_edit")(actions.cancel_edit)
    app.action("join_meet")(actions.join_meet)
    app.action("add_option")(actions.add_option)
    app.action("vote")(actions.vote)

    # views
    app.view("poll")(views.poll)
