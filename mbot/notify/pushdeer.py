import json
import logging

import httpx
from tenacity import stop_after_attempt, retry, wait_fixed

from mbot.common.stringutils import StringUtils
from mbot.notify.notify import Notify


class PushdeerNotify(Notify):
    """Pushdeer应用推送通道
    """

    def __init__(self, args):
        self.api = args.get('api')
        self.pushkey = args.get('pushkey')

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def send_text_message(self, title_message, text_message, to_user):
        res = httpx.get(
            self.api,
            params={
                'pushkey': str(to_user) if to_user else self.pushkey,
                'type': 'markdown',
                'text': title_message,
                'desp': text_message
            }
        ).json()
        if res["content"]["result"]:
            result = json.loads(res["content"]["result"][0])
            if result["success"] != "ok":
                logging.error('pushdeer推送失败：%s' % res.json())

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def send_by_template(self, user_id, title_template, body_template, context: dict):
        if not title_template:
            logging.error('请提供标题模版：%s' % title_template)
            return
        if not body_template:
            logging.error('请提供内容模版：%s' % body_template)
            return
        if not self.pushkey and not user_id:
            logging.error('没有可用的pushkey，无法推送')
            return
        if context and context.get('pic_url'):
            # 利用markdown推送时自动带上图片和链接
            body_template = '''[![image]({{ pic_url }})]({{ link_url }})
    ''' + body_template
        res = httpx.get(self.api, params={
            'pushkey': str(user_id) if user_id else self.pushkey,
            'type': 'markdown',
            'text': StringUtils.render_text(title_template, **context),
            'desp': StringUtils.render_text(body_template, **context)
        }).json()
        if res["content"]["result"]:
            result = json.loads(res["content"]["result"][0])
            if result["success"] != "ok":
                logging.error('pushdeer推送失败：%s' % res.json())
