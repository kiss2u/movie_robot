import logging
import re
from http.cookies import SimpleCookie

import httpx

from mbot.plugin.site_signin import SigninHandler, SigninResult, TIMEOUT, SigninStatus

_LOGGER = logging.getLogger(__name__)


class HdchinaSigninHandler(SigninHandler):
    def handle(self, cookies: SimpleCookie, user_agent: str, proxies: str = None,
               site_name: str = None, site_url: str = None, more_headers: dict = None) -> SigninResult:
        if site_url:
            site_url.rstrip('/')
        else:
            return SigninResult(site_name, SigninStatus.Failed, '站点访问地址错误')
        headers = {
            'user-agent': user_agent
        }
        with httpx.Client(cookies=cookies, timeout=TIMEOUT, proxies=proxies) as client:
            r = client.get(url=f'{site_url}', headers=headers)
            mcsrf = re.search(r'<meta name="x-csrf" content="([^"]+)"/>', r.text)
            if mcsrf:
                csrf = mcsrf.group(1)
            else:
                return SigninResult(site_name, SigninStatus.Failed, 'CSRF错误，无法签到')
            headers.update({'referer': site_url, 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'})
            r = client.post(url=f'{site_url}/plugin_sign-in.php?cmd=signin', headers=headers, data={
                'csrf': csrf
            })
            if r.status_code != 200:
                _LOGGER.error(f'{site_name}签到失败，HTTP状态码：{r.status_code}')
                return SigninResult(site_name, SigninStatus.Failed, '无法正常调用签到页面')
            data = r.json()
            if data.get('state') == 'success':
                return SigninResult(site_name, SigninStatus.Succeeded,
                                    f'已经连续签到{data.get("signindays")}天，获得魔力值{data.get("integral")}')
            else:
                return SigninResult(site_name, SigninStatus.Repeated, '今天已经签过了')
