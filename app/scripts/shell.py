import redis  # type: ignore

from ..helpers import *
from ..infrastructure import *
from ..services import *

from .. import create_app


def shell(environment: str) -> None:
    app = create_app(environment, 'shell')
    from IPython import embed
    embed()
