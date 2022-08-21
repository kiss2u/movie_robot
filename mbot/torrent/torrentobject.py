import datetime
from enum import Enum
from typing import List

from mbot.common.dictutils import DictUtils
from mbot.common.jsonmodel import JsonModel
from mbot.common.osutils import OSUtils


class CateLevel1(str, Enum):
    Movie = '电影'
    TV = '剧集'
    Documentary = '纪录片'
    Anime = '动漫'
    Music = '音乐'
    Game = '游戏'
    AV = '成人'
    Other = '其他'

    @staticmethod
    def get_type(enum_name: str):
        for item in CateLevel1:
            if item.name == enum_name:
                return item
        return None


class SiteUserinfo(JsonModel):
    uid: int
    username: str
    user_group: str
    share_ratio: float
    uploaded: float
    downloaded: float
    seeding: int
    leeching: int
    vip_group: bool = False


class TorrentInfo(JsonModel):
    # 站点编号
    site_id: str
    # 种子编号
    id: int
    # 种子名称
    name: str
    # 种子标题
    subject: str
    # 以及类目
    cate_level1: CateLevel1 = None
    # 站点类目id
    cate_id: str
    # 种子详情页地址
    details_url: str
    # 种子下载链接
    download_url: str
    # 种子关联的imdbid
    imdb_id: str
    # 种子发布时间
    publish_date: datetime
    # 种子大小，转化为mb尺寸
    size_mb: float
    # 做种人数
    upload_count: int
    # 下载中人数
    downloading_count: int
    # 下载完成人数
    download_count: int
    # 免费截止时间
    free_deadline: datetime
    # 下载折扣，1为不免费
    download_volume_factor: float
    # 做种上传系数，1为正常
    upload_volume_factor: int
    minimum_ratio: float = 0
    minimum_seed_time: int = 0
    # 封面链接
    poster_url: str

    @staticmethod
    def build_by_parse_item(site_config, item):
        t = TorrentInfo()
        t.site_id = site_config.get('id')
        t.id = DictUtils.get_item_int_value(item, 'id', 0)
        t.name = DictUtils.get_item_value(item, 'title', '')
        t.subject = DictUtils.get_item_value(item, 'description', '')
        if t.subject:
            t.subject = t.subject.strip()
        t.free_deadline = DictUtils.get_item_value(item, 'free_deadline', None)
        t.imdb_id = DictUtils.get_item_value(item, 'imdbid', None)
        t.upload_count = DictUtils.get_item_int_value(item, 'seeders', 0)
        t.downloading_count = DictUtils.get_item_int_value(item, 'leechers', 0)
        t.download_count = DictUtils.get_item_int_value(item, 'grabs', 0)
        t.download_url = DictUtils.get_item_value(item, 'download', None)
        if t.download_url and not t.download_url.startswith('http'):
            t.download_url = site_config.get('domain') + t.download_url
        t.publish_date = DictUtils.get_item_value(item, 'date', datetime.datetime.now())
        t.cate_id = str(DictUtils.get_item_value(item, 'category', None))
        for c in site_config.get('category_mappings'):
            if c.get('id') == t.cate_id:
                t.cate_level1 = CateLevel1.get_type(c.get('cate_level1'))
        t.details_url = DictUtils.get_item_value(item, 'details', None)
        if t.details_url:
            t.details_url = site_config.get('domain') + t.details_url
        t.download_volume_factor = float(DictUtils.get_item_value(item, 'downloadvolumefactor', 1))
        t.upload_volume_factor = DictUtils.get_item_value(item, 'uploadvolumefactor', 1)
        t.size_mb = OSUtils.trans_size_str_to_mb(str(DictUtils.get_item_value(item, 'size', 0)))
        t.poster_url = DictUtils.get_item_value(item, 'poster', None)
        t.minimum_ratio = DictUtils.get_item_float_value(item, 'minimumratio', 0.0)
        t.minimum_seed_time = DictUtils.get_item_int_value(item, 'minimumseedtime', 0)
        if t.poster_url:
            if t.poster_url.startswith("./"):
                t.poster_url = site_config.get('domain') + t.poster_url[2:]
            elif not t.poster_url.startswith("http"):
                t.poster_url = site_config.get('domain') + t.poster_url
        return t


TorrentList = List[TorrentInfo]


class TVSeries(JsonModel):
    season_start: int = None
    season_end: int = None
    season_full_index: List[int] = []
    ep_start: int = None
    ep_end: int = None
    ep_full_index: List[int] = []
    season_is_fill: bool = False
    ep_is_fill: bool = False
    contains_complete_ep: bool = False
    contains_complete_season: bool = False
    contains_multiple_season: bool = False


class TorrentInfoExt(TorrentInfo):
    def __init__(self, t: TorrentInfo):
        for k, v in t.__dict__.items():
            self.__setattr__(k, v)

    cn_name: str = None
    en_name: str = None
    # 影视类型
    movie_type = None
    # 影视发行年份
    movie_release_year: str = None
    # 剧集系列信息，movie type为TV时有值
    tv_series: TVSeries = None
    # 分辨率
    resolution: str = None
    # 媒体来源介质
    media_source: str = None
    # 媒体编码
    media_encoding: str = None
    # 制作组
    release_team: str = None
    score = None


TorrentInfoExtList = List[TorrentInfoExt]
