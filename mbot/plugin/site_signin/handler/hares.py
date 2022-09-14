import logging
from http.cookies import SimpleCookie

import httpx
from tenacity import wait_fixed, stop_after_attempt, retry

from mbot.plugin.site_signin import SigninResult, SigninStatus, TIMEOUT, SigninHandler

_LOGGER = logging.getLogger(__name__)


class HaresSigninHandler(SigninHandler):
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(10))
    def handle(self, cookies: SimpleCookie, user_agent: str, proxies: str = None,
               site_name: str = None, site_url: str = None, more_headers: dict = None) -> SigninResult:
        if site_url:
            site_url = site_url.rstrip('/')
        else:
            return SigninResult(site_name, SigninStatus.Failed, '站点访问地址错误')
        url = f'{site_url}/attendance.php?action=sign'
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'referer': site_url,
            'user-agent': user_agent,
            'x-requested-with': 'XMLHttpRequest'
        }
        r = httpx.get(url, headers=headers, cookies=cookies, timeout=TIMEOUT,
                      follow_redirects=True)
        if r.status_code != 200:
            return SigninResult(site_name, SigninStatus.Failed, '不支持attendance.php签到方式')
        data = r.json()
        if data.get('msg') == '您今天已经签到过了':
            return SigninResult(site_name, SigninStatus.Repeated, '今天已经签过了')
        return SigninResult(site_name, SigninStatus.Succeeded, data.get('msg'))
