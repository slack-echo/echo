from . import commands


def listen(app):
    app.command("/echo")(commands.echo)
    app.command("/send")(commands.send)
    app.command("/shuffle")(commands.rand)
    app.command("/choices")(commands.rand)
    app.command("/meet")(commands.meet)
