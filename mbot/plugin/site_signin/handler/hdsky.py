import base64
from http.cookies import SimpleCookie

import httpx
from tenacity import wait_fixed, stop_after_attempt, retry

from mbot.const import ServiceConst
from mbot.plugin.site_signin import SigninHandler, SigninResult, TIMEOUT, SigninStatus


class HdskySigninHandler(SigninHandler):
    site_name: str = '天空'

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(10))
    def handle(self, cookies: SimpleCookie, user_agent: str, proxies: str = None,
               site_name: str = None, site_url: str = None, more_headers: dict = None) -> SigninResult:
        headers = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'user-agent': user_agent
        }
        with httpx.Client(headers=headers, cookies=cookies, timeout=TIMEOUT, proxies=proxies) as client:
            # 1、获取验证码hash
            r = client.post(
                url='https://hdsky.me/image_code_ajax.php',
                data={
                    'action': 'new'
                }
            )
            if not r:
                return SigninResult(self.site_name, SigninStatus.Failed, '')
            data = r.json()
            img_hash = data.get('code')
            # 2、请求图片
            r = client.get(
                url=f'https://hdsky.me/image.php?action=regimage&imagehash={img_hash}',
                params={
                    'action': 'regimage',
                    'imagehash': img_hash
                }
            )
            encoded_string = base64.b64encode(r.content)
            # 3、识别验证码
            image_str = self.mbot.services.call(ServiceConst.ocr.namespace, ServiceConst.ocr.get_image_text,
                                                image=encoded_string.decode())
            # 4、返回验证码
            r = client.post(url='https://hdsky.me/showup.php', data={
                'action': 'showup',
                'imagehash': img_hash,
                'imagestring': image_str
            })
            # 这里message返回的是签到所获的魔力值
            data = r.json()
            if not data.get('success'):
                if data.get('message') == 'date_unmatch':
                    return SigninResult(self.site_name, SigninStatus.Repeated, '今天已经签过了')
                raise RuntimeError('验证码错误')
            message = data.get('message')
            return SigninResult(self.site_name, SigninStatus.Succeeded, f'签到成功，获得{message}个魔力值')
