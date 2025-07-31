import logging

LOG_LEVEL = 'INFO'
LOGGER = logging.getLogger('CS-Logger')
LOGGER.setLevel(LOG_LEVEL)

logging.basicConfig(
    format='[%(asctime)s] [%(threadName)s][%(filename)s:%(lineno)d][%(name)s-%(levelname)s]: %(message)s',
    level=LOG_LEVEL
)