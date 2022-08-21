from bs4 import BeautifulSoup

from mbot.site.htmlparser import HtmlParser
from mbot.site.siteexceptions import LoginRequired
from mbot.torrent.torrentobject import TorrentList, TorrentInfo


class SiteParser:
    def __init__(self, site_config):
        self.site_config = site_config

    def test_login(self, html_text):
        if not html_text:
            return False
        login_config = self.site_config.get('login')
        if not login_config:
            return
        test = login_config.get('test')
        soup = BeautifulSoup(html_text, 'lxml')
        tag = soup.select_one(test.get('selector'))
        if tag:
            return True
        else:
            return False

    def parse_userinfo(self, html_text):
        if not self.test_login(html_text):
            raise LoginRequired(self.site_config.get('id'), self.site_config.get('name'),
                                f'{self.site_config.get("name")}登陆失败！')
        user_rule = self.site_config.get('userinfo')
        if not user_rule:
            return
        field_rule = user_rule.get('fields')
        if not field_rule:
            return
        soup = BeautifulSoup(html_text, 'lxml')
        item_tag = soup.select_one(user_rule.get('item')['selector'])
        result = HtmlParser.parse_item_fields(item_tag, field_rule)
        return result

    def parse_torrents(self, html_text, context=None) -> TorrentList:
        torrents_rule = self.site_config.get('torrents')
        if not torrents_rule:
            return []
        list_rule = torrents_rule.get('list')
        fields_rule = torrents_rule.get('fields')
        if not fields_rule:
            return []
        soup = BeautifulSoup(html_text, 'lxml')
        rows = soup.select(list_rule['selector'])
        if not rows:
            return []
        result: TorrentList = []
        for tag in rows:
            item = HtmlParser.parse_item_fields(tag, fields_rule, context=context)
            result.append(TorrentInfo.build_by_parse_item(self.site_config, item))
        return result
