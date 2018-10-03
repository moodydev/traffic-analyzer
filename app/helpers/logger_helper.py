import logging


class LoggerHelper(logging.LoggerAdapter):
    """Returns LoggerAdapter instance that prepends "[name]" to all messages.
    """

    def __init__(self, logger, prepend_name):
        self.prepend_name = prepend_name
        super().__init__(logger=logger, extra={})

    def process(self, msg, kwargs):
        return '[%s] %s' % (self.prepend_name, msg), kwargs
