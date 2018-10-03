import logging

from .services import QueueAnalyzer, QueueManager
from .settings import ENVIRONMENTS


def create_app(env: str='development', app_type: str='queue_manager'):
    """TODO: write function explanation
    """

    print('Starting {}'.format(app_type))
    if app_type == 'queue_manager':
        return QueueManager()
    elif app_type == 'load_analyzer':
        return QueueAnalyzer()
