import logging
import urllib

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

from mbot.common.stringutils import StringUtils
from mbot.notify.notify import Notify


class BarkNotify(Notify):
    """IOS Bark推送应用
    """

    def __init__(self, args):
        """
        系统初始化时会把配置文件中对应的推送通道配置，传递过来；
        如果你想自定义一个推送通道，直接get所需参数就可以了
        :param args:
        """
        self.push_url = args.get('push_url')
        self.group = args.get('group')
        self.sound = args.get('sound')
        self.icon = args.get('icon')

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def send_text_message(self, title_message, text_message, to_user):
        url = str(to_user) if to_user else self.push_url
        if url[-1] != '/':
            url = url + '/'
        url = f'{url}{urllib.parse.quote_plus(title_message)}/{urllib.parse.quote_plus(text_message)}'
        params = 'isArchive=1&'
        if self.sound:
            params += f"sound={self.sound}&"
        if self.group:
            params += f"group={self.group}&"
        if self.icon:
            params += f"icon={self.icon}&"
        if params:
            url = url + "?" + params.rstrip("&")
        res = httpx.get(url).json()
        if res["code"] != 200:
            logging.info('bark 推送失败 %s' % url)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def send_by_template(self, user_id, title_template, body_template, context: dict):
        if not self.push_url:
            return
        if not title_template:
            logging.error('请提供标题模版：%s' % title_template)
            return
        if not body_template:
            logging.error('请提供内容模版：%s' % body_template)
            return
        url = str(user_id) if user_id else self.push_url
        if url[-1] != '/':
            url = url + '/'
        url = f'{url}{urllib.parse.quote_plus(StringUtils.render_text(title_template, **context))}/{urllib.parse.quote_plus(StringUtils.render_text(body_template, **context))}'
        params = 'isArchive=1&'
        if self.sound:
            params += f"sound={self.sound}&"
        if self.group:
            params += f"group={self.group}&"
        if self.icon:
            params += f"icon={self.icon}&"
        if params:
            url = url + "?" + params.rstrip("&")
        try:
            res = httpx.get(url).json()
            if res["code"] != 200:
                logging.info('bark 推送失败 %s' % url)
        except Exception as e:
            logging.info('bark 推送失败 %s' % url)
