import urllib

from mbot.common.dateformatutils import DateFormatUtils
from mbot.common.iso3166 import Countries
from mbot.common.mediaformatutils import MediaFormatUtils


class MediaDataSelector:
    @staticmethod
    def get_tmdb_area(meta):
        if not meta.get('production_countries') and not meta.get('origin_country'):
            return ['其他']
        areas: list = list()
        if meta.get('origin_country'):
            for c in meta.get('origin_country'):
                areas.append(Countries.get(c))
        if len(areas) == 0 and meta.get('production_countries'):
            for c in meta.get('production_countries'):
                areas.append(Countries.get(c.get('iso_3166_1')))
        return areas

    @staticmethod
    def get_tmdb_tv_date(tv):
        date = None
        release_date = tv['first_air_date']
        if release_date is not None:
            date = release_date
        elif tv['seasons'] is not None and len(tv['seasons']) > 0:
            if tv['seasons'][0].get('air_date') is not None:
                date = tv['seasons'][0].get('air_date')
        return date

    @staticmethod
    def get_tmdb_tv_year(tv):
        year = None
        release_date = tv['first_air_date']
        stryear = DateFormatUtils.parse_year_from_str(release_date, '%Y-%m-%d')
        if stryear is not None:
            year = stryear
        elif tv['seasons'] is not None and len(tv['seasons']) > 0:
            stryear = DateFormatUtils.parse_year_from_str(tv['seasons'][0]['air_date'], '%Y-%m-%d')
            if stryear is not None:
                year = stryear
        return year

    @staticmethod
    def get_proxy_image_url(url):
        if not url:
            return
        return '/api/common/get_image?url=' + urllib.parse.quote_plus(url)

    @staticmethod
    def get_genres(tmdb_meta, douban_meta):
        genres = None
        if not genres and tmdb_meta and tmdb_meta.get('genres'):
            arr = []
            for item in tmdb_meta.get('genres'):
                if item.get('name') == 'Sci-Fi & Fantasy':
                    arr.append('科幻')
                elif item.get('name') == 'War & Politics':
                    arr.append('战争')
                else:
                    arr.append(item.get('name'))
            genres = arr
        if not genres and douban_meta:
            genres = douban_meta.cates
        return genres

    @staticmethod
    def get_country(tmdb_meta, douban_meta):
        area = douban_meta.area if douban_meta else None
        if not area or area == ['其他']:
            area = MediaDataSelector.get_tmdb_area(tmdb_meta)
        return area

    @staticmethod
    def get_episode_count(tmdb_season, douban_meta):
        if douban_meta.total_ep_count:
            return douban_meta.total_ep_count
        if tmdb_season:
            return tmdb_season.get('episode_count')
        return 1

    @staticmethod
    def get_title(tmdb_meta, douban_meta):
        title = None
        if douban_meta:
            if str(douban_meta.type).lower() != 'movie':
                title = MediaFormatUtils.trim_name(douban_meta.name)
            else:
                title = douban_meta.name
            if title == '未知电视剧' or title == '未知电影':
                title = None
        if tmdb_meta and not title:
            title = tmdb_meta.get('title') if 'title' in tmdb_meta else tmdb_meta.get('name')
        return title

    @staticmethod
    def get_rating(tmdb_meta, douban_meta):
        rating = None
        if douban_meta:
            rating = douban_meta.rating
        if not rating and tmdb_meta:
            rating = tmdb_meta.get('vote_average')
        if rating:
            return round(rating, 1)
        else:
            return rating

    @staticmethod
    def get_url(tmdb_meta, douban_meta):
        if douban_meta:
            return 'https://movie.douban.com/subject/%s/' % douban_meta.id
        if tmdb_meta:
            if 'title' in tmdb_meta:
                return 'https://themoviedb.org/movie/%s' % tmdb_meta.get('id')
            else:
                return 'https://themoviedb.org/tv/%s' % tmdb_meta.get('id')
        return

    @staticmethod
    def get_intro(tmdb_meta, douban_meta):
        intro = None
        if douban_meta:
            intro = douban_meta.intro
        if tmdb_meta and not intro:
            intro = tmdb_meta.get('overview')
        if intro:
            return str(intro).strip()
        else:
            return intro

    @staticmethod
    def get_year(tmdb_meta, douban_meta):
        if douban_meta:
            return douban_meta.release_year
        if tmdb_meta:
            if 'title' in tmdb_meta:
                if tmdb_meta.get('release_date'):
                    return tmdb_meta['release_date'][0:4]
                else:
                    return None
            else:
                return MediaDataSelector.get_tmdb_tv_year(tmdb_meta)

    @staticmethod
    def get_release_date(tmdb_meta, douban_meta):
        date = None
        if tmdb_meta:
            if 'title' in tmdb_meta:
                if tmdb_meta.get('release_date'):
                    date = tmdb_meta['release_date']
            else:
                date = MediaDataSelector.get_tmdb_tv_date(tmdb_meta)
        if douban_meta and not date:
            date = douban_meta.release_date
        return date
