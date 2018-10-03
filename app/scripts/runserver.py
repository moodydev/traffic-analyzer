from .. import create_app


def runserver(environment):
    app = create_app(environment)
    app.start()
