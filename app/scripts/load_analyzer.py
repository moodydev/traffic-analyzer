from .. import create_app


def load_analyzer(environment: str) -> None:
    app = create_app(environment, 'load_analyzer')
    app.start()
