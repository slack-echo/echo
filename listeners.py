import commands


def listen(app):
    app.command("/echo")(commands.echo)
    app.command("/send")(commands.send)
    app.command("/random")(commands.random)
