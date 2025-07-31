import logging


class RecordNotFound(Exception):
    def __init__(self, message='未找到记录'):
        if not message.startswith('未找到'):
            message = '未找到' + message

        self.message = message
        super().__init__(message)
        logging.error(message)


class CustomException(Exception):
    pass
