import actions
import commands
import events
import views


def listen(app):
    app.message("@admin")(events.admin_mention)
    app.event("message")(events.echo)
    app.command("/echo")(commands.echo)
