from . import commands
from . import shortcuts
from . import actions


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
    app.shortcut("delete_message")(shortcuts.delete_message)

    # actions
    app.action("join_meet")(actions.join_meet)
