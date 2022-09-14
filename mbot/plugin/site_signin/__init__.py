from abc import ABCMeta, abstractmethod
from enum import Enum
from http.cookies import SimpleCookie

from httpx import Timeout

from mbot.common.serializable import Serializable
from mbot.core import MovieBot

TIMEOUT = Timeout(15)
"""没有签到的站点id"""
SKIP_SITE = ['mteam', 'ssd', 'chdbits', 'keepfrds', 'tjupt']


class SigninStatus(str, Enum):
    """签到状态"""
    Succeeded = '签到成功'
    Failed = '签到失败'
    Repeated = '重复签到'


class SigninResult(Serializable):
    def __init__(self, site_name: str, status: SigninStatus, message: str):
        self.site_name: str = site_name
        self.status: SigninStatus = status
        self.message: str = message


class SigninHandler(metaclass=ABCMeta):
    def __init__(self, mbot: MovieBot):
        self.mbot: MovieBot = mbot

    @abstractmethod
    def handle(self, cookies: SimpleCookie, user_agent: str, proxies: str = None,
               site_name: str = None, site_url: str = None, more_headers: dict = None) -> SigninResult:
        pass
