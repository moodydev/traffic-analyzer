import os

from .development import Development
from .production import Production
from .test import Test

ENVIRONMENTS = {
    'production': Production,
    'development': Development,
    'test': Test,
}


class Settings:
    def __init__(self):
        self.__settings = ENVIRONMENTS['development']

    @property
    def settings(self):
        return self.__settings


settings = Settings().settings
