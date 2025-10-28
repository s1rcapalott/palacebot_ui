import logging
import time 
class task:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        