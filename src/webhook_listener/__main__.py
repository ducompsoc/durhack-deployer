from .app import app as application
from config import config

if __name__ == '__main__':
    application.run(host=config.listen.host, port=config.listen.port)
