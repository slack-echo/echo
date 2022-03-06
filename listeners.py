import commands


def listen(app):
    app.command("/echo")(commands.echo)
    app.command("/send")(commands.send)
    app.command("/shuffle")(commands.shuffle)
    app.command("/choices")(commands.choices)
