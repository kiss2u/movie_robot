import logging
import random
import re
import time
from http.cookies import SimpleCookie

import httpx

from mbot.plugin.site_signin import SigninHandler, SigninResult, TIMEOUT, SigninStatus

_LOGGER = logging.getLogger(__name__)


class TTGSigninHandler(SigninHandler):
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
            r_json = re.search(r'\{signed_timestamp:\s+"(\d+)", signed_token: "([^"]+)"\}', r.text)
            if r_json:
                signed_timestamp = r_json.group(1)
                signed_token = r_json.group(2)
            else:
                return SigninResult(site_name, SigninStatus.Failed, '读不到签到密钥，无法签到')
            # 休息一下，ttg反爬严重
            time.sleep(random.randint(1, 3))
            headers.update({'referer': site_url, 'content-type': 'application/x-www-form-urlencoded'})
            r = client.post(url=f'{site_url}/signed.php', headers=headers, data={
                'signed_timestamp': signed_timestamp,
                'signed_token': signed_token
            })
            if r.status_code != 200:
                _LOGGER.error(f'{site_name}签到失败，HTTP状态码：{r.status_code}')
                return SigninResult(site_name, SigninStatus.Failed, '无法正常调用签到页面')
            text = r.text
            if text == '亲，您今天已签到过，不要太贪哦。欢迎明天再来！':
                return SigninResult(site_name, SigninStatus.Repeated, '今天已经签过了')
            else:
                return SigninResult(site_name, SigninStatus.Succeeded, text)
