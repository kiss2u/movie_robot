import logging
from http.cookies import SimpleCookie

import httpx
from bs4 import BeautifulSoup
from tenacity import stop_after_attempt, retry, wait_fixed

from mbot.plugin.site_signin import SigninHandler, SigninResult, SigninStatus, TIMEOUT

_LOGGER = logging.getLogger(__name__)


class NexusPHPSigninHandler(SigninHandler):
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(10))
    def handle(self, cookies: SimpleCookie, user_agent: str, proxies: str = None,
               site_name: str = None, site_url: str = None, more_headers: dict = None) -> SigninResult:
        if site_url:
            site_url.rstrip('/')
        else:
            return SigninResult(site_name, SigninStatus.Failed, '站点访问地址错误')
        url = f'{site_url}/attendance.php'
        headers = {
            'referer': site_url,
            'user-agent': user_agent
        }
        if more_headers:
            for key in more_headers:
                headers.update({key: more_headers[key]})
        r = httpx.get(url, headers=headers, cookies=cookies, timeout=TIMEOUT, follow_redirects=True)
        if r.status_code != 200:
            return SigninResult(site_name, SigninStatus.Failed, '不支持attendance.php签到方式')
        text = r.text
        if text.find('您今天已经签到过了，请勿重复刷新。') != -1:
            return SigninResult(site_name, SigninStatus.Repeated, '今天已经签过了')
        soup = BeautifulSoup(text, 'lxml')
        p = soup.select_one('td.text > p')
        if p:
            return SigninResult(site_name, SigninStatus.Succeeded, p.text)
        else:
            _LOGGER.error(f'{site_name}未能有效读取到签到结果，请把日志信息发到Github')
            _LOGGER.error(text)
            return SigninResult(site_name, SigninStatus.Succeeded, '未识别到签到结果信息，请把日志信息发到Github')
