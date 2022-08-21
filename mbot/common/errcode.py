from enum import Enum


class ErrCode(Enum):
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
