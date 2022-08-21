import asyncio
import datetime
import random
import re
import time

import httpx
from cacheout import Cache
from httpx import Timeout
from magnet2torrent import Magnet2Torrent
from tenacity import retry, wait_fixed, stop_after_attempt, stop_after_delay, wait_exponential
from mbot.site.basesitehelper import BaseSiteHelper, request_interval, RateLimitException
from mbot.torrent.torrentobject import TorrentList, TorrentInfo, CateLevel1, SiteUserinfo

token_cache = Cache(maxsize=32, ttl=800, default=None)


class Rarbg(BaseSiteHelper):
    APP_ID = "m-bot"
    ENDPOINT = 'http://torrentapi.org/pubapi_v2.php'

    def __init__(self, site_config, proxies=None):
        self.token = None
        self.site_config = site_config
        self.category_mappings = self.__init_category_mappings__(site_config.get('category_mappings'))
        if proxies:
            self.proxies = proxies
        else:
            self.proxies = None

    @request_interval(action='default', min_sleep=3)
    def __do_get__(self, url, params=None, timeout=None):
        if not timeout:
            timeout = 10
        if not params:
            params = {}
        params.update({
            'app_id': self.APP_ID
        })
        headers = {
            'user-agent': self.user_agent_rotator.get_random_user_agent()
        }
        r = httpx.get(url, params=params, headers=headers, timeout=Timeout(timeout), proxies=self.proxies)
        return r

    @retry(wait=wait_fixed(3), stop=stop_after_attempt(3), reraise=True)
    def __get_token__(self):
        if token_cache.get('token'):
            return token_cache.get('token')
        r = self.__do_get__(self.ENDPOINT, {'get_token': 'get_token'})
        token = None
        if r:
            data = r.json()
            token = data.get('token')
        token_cache.set('token', token)
        return token

    @retry(stop=stop_after_delay(300), wait=wait_exponential(multiplier=1, min=30, max=90), reraise=True)
    def download(self, url, filepath):
        async def fetch_that_torrent():
            m2t = Magnet2Torrent(url)
            filename, torrent_data = await m2t.retrieve_torrent()
            with open(filepath, 'wb') as file:
                file.write(torrent_data)

        asyncio.run(fetch_that_torrent())

    def get_userinfo(self, refresh=False) -> SiteUserinfo:
        user = SiteUserinfo()
        user.username = 'rarbg'
        user.user_group = 'rarbg'
        user.seeding = 0
        user.vip_group = False
        user.downloaded = 0
        user.leeching = 0
        user.uid = 0
        user.share_ratio = 0
        user.uploaded = 0
        return user

    def search(self, keyword=None, imdb_id=None, cate_level1_list: list = None, free: bool = False, page: int = None,
               timeout=None) -> TorrentList:
        params = {
            'format': 'json_extended',
            'limit': 100
        }
        # 用全部分类去搜索
        input_cate2_ids = set(self.__get_cate_level2_ids__())
        params['category'] = ';'.join(input_cate2_ids)
        if not keyword and not imdb_id:
            params['mode'] = 'list'
        else:
            params['mode'] = 'search'
        if imdb_id:
            params['search_imdb'] = imdb_id
        elif keyword:
            if re.match('[^\x00-\xff]', keyword):
                return []
            params['search_string'] = keyword
        params['token'] = self.__get_token__()
        r = self.__do_get__(self.ENDPOINT, params, timeout=timeout)
        if r.status_code != 200:
            time.sleep(5)
            raise RateLimitException()
        data: dict = r.json()
        if data.get('error_code'):
            if data.get('error_code') == 10:
                # imdb 搜索不到
                return []
            raise RateLimitException()
        if data.get('rate_limit'):
            time.sleep(2)
            raise RateLimitException()
        torrents = data.get('torrent_results')
        if not torrents:
            return []
        result: TorrentList = []
        for t in torrents:
            try:
                torrent = TorrentInfo()
                torrent.name = t.get('title')
                torrent.subject = ''
                torrent.download_url = t.get('download')
                torrent.upload_count = t.get('seeders')
                torrent.downloading_count = 0
                torrent.download_count = t.get('leechers')
                torrent.size_mb = t.get('size') / 1024 / 1024 if t.get('size') else 0
                torrent.details_url = t.get('info_page')
                torrent.download_volume_factor = 0
                torrent.upload_volume_factor = 1
                if t.get('episode_info'):
                    torrent.imdb_id = t.get('episode_info').get('imdb')
                torrent.site_id = 'rarbg'
                torrent.free_deadline = datetime.datetime.max
                torrent.minimum_seed_time = 0
                torrent.minimum_ratio = 0
                utctime = time.strptime(t.get('pubdate'), '%Y-%m-%d %H:%M:%S +0000')
                torrent.publish_date = datetime.datetime.fromtimestamp(time.mktime(utctime))
                find = False
                for c in self.category_mappings:
                    if c.get('cate_level2') == t.get('category'):
                        torrent.cate_level1 = CateLevel1.get_type(c.get('cate_level1'))
                        torrent.cate_id = c.get('id')
                        find = True
                        break
                if not find:
                    torrent.cate_id = t.get('category')
                    if torrent.cate_id.startswith('Movies'):
                        torrent.cate_level1 = CateLevel1.Movie
                    else:
                        torrent.cate_level1 = CateLevel1.TV
                re_id = re.search(r'p=(.+)', torrent.details_url)
                if re_id:
                    arr = re_id.group(1).split('__')
                    torrent.id = arr[0].replace('_', '')
                else:
                    torrent.id = random.randint(1, 10000000)
            except Exception as e:
                pass
            result.append(torrent)
        return result
