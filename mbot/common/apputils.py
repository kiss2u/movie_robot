import logging
import os
import signal

_LOGGER = logging.getLogger(__name__)

SPID_FILE = "/app/supervisord.pid"


def kill_app(msg=None):
    """
    杀掉docker中的守护信息
    :param msg: 杀死之前打印的日志
    :return:
    """
    if msg:
        _LOGGER.info(msg)
    if os.path.exists(SPID_FILE):
        with open(SPID_FILE) as f:
            pid = int(f.readline()[0])
            os.kill(pid, signal.SIGKILL)
    os.kill(os.getpid(), signal.SIGKILL)
