import logging

import httpx
from tenacity import stop_after_attempt, retry, wait_fixed

from mbot.common.stringutils import StringUtils
from mbot.notify.notify import Notify


class TelegramNotify(Notify):
    """Telegram应用推送通道
    """

    def __init__(self, args):
        self.token = args.get('token')
        self.proxy = args.get('proxy')
        self.chat_id = args.get('chat_id')
        self.server_url = args.get('server_url', 'https://api.telegram.org')

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def send_text_message(self, title_message, text_message, to_user):
        # 效验
        if not self.token:
            logging.error('没有可用的telegram token，无法推送')
            return
        if not self.chat_id:
            logging.error('没有可用的chat_id，无法推送')
            return
        # 拼接
        message = f'*{title_message}*\r\n{text_message}'
        # 发送
        res = httpx.post(
            '%s/bot%s/sendMessage' % (self.server_url, self.token),
            params={
                'chat_id': self.chat_id,
                'parse_mode': 'MarkdownV2',
                'text': message,
            },
            proxies=self.proxy
        ).json()
        if not res["ok"]:
            logging.error('telegram推送失败：%s' % res["description"])

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def send_by_template(self, user_id, title_template, body_template, context: dict):
        # 效验
        if not title_template:
            logging.error('请提供标题模版：%s' % title_template)
            return
        if not body_template:
            logging.error('请提供内容模版：%s' % body_template)
            return
        if not self.token:
            logging.error('没有可用的telegram token，无法推送')
            return
        if not self.chat_id:
            logging.error('没有可用的chat_id，无法推送')
            return

        message = f'*{StringUtils.render_text(title_template, **context)}*\r\n'
        message += f'{StringUtils.render_text(body_template, **context)}'

        if context and context.get('pic_url'):
            url = '%s/bot%s/sendPhoto' % (self.server_url, user_id)
            data = {
                'chat_id': self.chat_id,
                'parse_mode': 'MarkdownV2',
                'photo': context.get('pic_url'),
                'caption': message
            }
        else:
            url = '%s/bot%s/sendMessage' % (self.server_url, user_id)
            data = {
                'chat_id': self.chat_id,
                'parse_mode': 'MarkdownV2',
                'text': message,
            }

        res = httpx.post(url, params=data, proxies=self.proxy).json()
        if not res["ok"]:
            logging.error('telegram推送失败：%s' % res["description"])
