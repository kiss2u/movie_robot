import datetime
import json
import logging

import httpx
from tenacity import wait_fixed, stop_after_attempt, retry

from mbot.common.stringutils import StringUtils
from mbot.core import remote_api
from mbot.notify.notify import Notify


class QywechatNotify(Notify):
    """企业微信推送通道
    """

    def __init__(self, args):
        self.server_url = args.get('server_url', 'https://qyapi.weixin.qq.com')
        self.corpid = args.get('corpid')
        self.corpsecret = args.get('corpsecret')
        self.agentid = args.get('agentid')
        self.touser = args.get('touser')
        self.token_cache = None
        self.token_expires_time = None
        self.use_server_proxy = args.get('use_server_proxy', False)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def __do_send_message__(self, access_token, params):
        if self.use_server_proxy:
            return remote_api.send_qywx_message(access_token, params)
        else:
            url = f'{self.server_url}/cgi-bin/message/send?access_token=' + access_token
            res = httpx.post(url, data=params)
            return res.json()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def get_access_token(self):
        if self.token_expires_time is not None and self.token_expires_time >= datetime.datetime.now():
            return self.token_cache
        res = httpx.get(
            'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s' % (
                self.corpid, self.corpsecret))
        json = res.json()
        if json['errcode'] == 0:
            self.token_expires_time = datetime.datetime.now() + datetime.timedelta(seconds=json['expires_in'] - 500)
            self.token_cache = json['access_token']
            return self.token_cache
        else:
            return None

    def send_by_template(self, user_id, title_template, body_template, context: dict):
        access_token = self.get_access_token()
        if access_token is None:
            logging.error('获取企业微信access_token失败，请检查你的corpid和corpsecret配置')
            return
        if not title_template:
            logging.error('请提供标题模版：%s' % title_template)
            return
        if not body_template:
            logging.error('请提供内容模版：%s' % body_template)
            return
        params = json.dumps({
            'touser': str(user_id) if user_id else self.touser,
            'agentid': self.agentid,
            'msgtype': 'news',
            'news': {
                "articles": [
                    {
                        "title": StringUtils.render_text(title_template, **context),
                        "description": StringUtils.render_text(body_template, **context),
                        "url": context.get('link_url'),
                        "picurl": context.get('pic_url')
                    }
                ]
            }
        }, ensure_ascii=False).encode('utf8')
        json_data = self.__do_send_message__(access_token, params)
        if json_data.get('errcode') != 0:
            logging.error('企业微信推送失败：%s' % json_data)

    def send_news(self, touser: str, news: dict, agent_id: str = None):
        access_token = self.get_access_token()
        if access_token is None:
            logging.error('获取企业微信access_token失败，请检查你的corpid和corpsecret配置')
            return
        params = json.dumps({
            'touser': touser,
            'agentid': self.agentid if agent_id is None else agent_id,
            'msgtype': 'news',
            'news': news
        }, ensure_ascii=False).encode('utf8')
        json_data = self.__do_send_message__(access_token, params)
        if json_data.get('errcode') != 0:
            logging.error('企业微信推送失败：%s' % json_data)

    def send_text_message(self, title_message, text_message, to_user):
        access_token = self.get_access_token()
        if access_token is None:
            logging.error('获取企业微信access_token失败，请检查你的corpid和corpsecret配置')
            return
        params = json.dumps({
            'touser': to_user.get('to_user'),
            'agentid': self.agentid if to_user.get('agent_id') is None else to_user.get('agent_id'),
            'msgtype': 'text',
            'text': {
                "content": text_message
            }
        }, ensure_ascii=False).encode('utf8')
        json_data = self.__do_send_message__(access_token, params)
        if json_data.get('errcode') != 0:
            logging.error('企业微信推送失败：%s' % json_data)
