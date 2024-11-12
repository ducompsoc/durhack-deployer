import logging
import sys

logger = logging.getLogger('base')
logger.addHandler(logging.FileHandler("foo.log"))
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

childLogger = logger.getChild('ment')
childLogger.addHandler(logging.FileHandler("bar.log"))

logger.info('hi from parent')
childLogger.info('hi from child')
