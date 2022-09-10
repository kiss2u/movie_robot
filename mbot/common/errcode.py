import logging
from enum import Enum

_LOGGER = logging.getLogger(__name__)


class ErrCode(Enum):
    """系统内错误码定义，有助于给出错误码表，方便问题排查"""
    LOGIN_ERROR = (400001, '登录错误，请检查登录状态是否已经过期，尝试重新登录')
    TMDB_ERROR = (400002, 'TMDB访问异常')
    DOUBAN_ERROR = (400003, '豆瓣访问异常')
    MEDIA_SERVER_ERROR = (400004, '媒体服务器访问异常')
    DOWNLOAD_CLIENT_ERROR = (400005, '下载工具（%s）访问异常')

    TMDB_NO_CONFIG_ERROR = (401001, '没有配置TMDB信息')
    DOUBAN_NO_CONFIG_ERROR = (401002, '没有配置豆瓣信息')
    MEDIA_SERVER_NO_CONFIG_ERROR = (401003, '没有配置媒体服务器信息')
    TORRENT_NOT_FOUND_ERROR = (402404, '找不到需要下载的种子：%s')

    DB_ERROR = (500001, '数据库访问异常：%s')

    def message(self, args=None):
        return '错误码：%s 错误消息：%s' % (self.value[0], self.value[1] % (args) if args else self.value[1])


def print_error(err_code: ErrCode, message_args=None, logger=None):
    if not err_code:
        return
    if logger:
        logger.error(err_code.message(message_args))
    else:
        _LOGGER.error(err_code.message(message_args))
