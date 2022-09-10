"""这是一个很好的事件监听型插件示范"""
from mbot.common.dictutils import DictWrapper
from mbot.common.mediaformatutils import MediaFormatUtils
from mbot.thirdparty.mediadataselector import MediaDataSelector
from mbot.core import PluginContext
from mbot.core.events import EventListener, Event, EventType
from mbot.const import ServiceConst


class NotifyListener(EventListener, PluginContext):
    """监听事件，实现通知功能"""
    """
    绑定事件
    事件值可以是字符串值，也可以是EventType枚举，支持同时绑定多个事件
    """
    __bind_event__ = [EventType.DownloadCompleted, EventType.SubMedia, EventType.DownloadStart, EventType.SiteError]
    """
    当有多个监听器订阅了同一个事件时的执行顺序
    """
    __order__ = 1

    def send_app_message_by_template_name(self, uid, template_name, context):
        """
        调用服务发送模版消息
        :param uid:
        :param template_name:
        :param context:
        :return:
        """
        self.mbot.services.call(
            ServiceConst.notify.namespace,
            ServiceConst.notify.send_app_message_by_template_name,
            uid=uid,
            template_name=template_name,
            context=context
        )

    def notify_download_completed(self, data):
        if not data.get('tmdb_id') and not data.get('douban_id'):
            # 未识别的下载记录，或者AV等特殊分类
            return
        media_stream = data.get('media_stream')
        if not media_stream:
            media_stream = {}
        # 把接收到的一些事件处理，处理为通知用
        data.update({
            'season_number': str(data.get('season_number')).zfill(2) if data.get('season_number') else None,
            'episodes': MediaFormatUtils.episode_format(data.get('episodes'))
        })
        # 按模版发送消息
        if data.get('media_type') == 'Movie':
            self.send_app_message_by_template_name(data.get('uid'), 'download_completed_movie', data)
        else:
            self.send_app_message_by_template_name(data.get('uid'), 'download_completed_tv', data)

    def notify_sub_media(self, data):
        if data.get('type') == 'Movie':
            self.send_app_message_by_template_name(data.get('uid'), 'sub_movie', data)
        else:
            self.send_app_message_by_template_name(data.get('uid'), 'sub_tv', data)

    def notify_download_start(self, data):
        if not data.get('tmdb_id') and not data.get('douban_id'):
            return
        # 把接收到的一些事件处理，处理为通知用
        data.update({
            'season_number': str(data.get('season_number')).zfill(2) if data.get('season_number') else None,
            'episodes': MediaFormatUtils.episode_format(data.get('episodes'))
        })
        # 按模版发送消息
        if data.get('media_type') == 'Movie':
            self.send_app_message_by_template_name(data.get('uid'), 'download_start_movie', data)
        else:
            self.send_app_message_by_template_name(data.get('uid'), 'download_start_tv', data)

    @staticmethod
    def __get_media_type__(data):
        media_type = data.get('media_type')
        if not media_type:
            # 订阅来源的数据结构是type
            media_type = data.get('type')
        return media_type.lower() if media_type else None

    def __get_tmdb_meta__(self, data):
        if 'tmdb_meta' in data:
            return data.get('tmdb_meta')
        if not data.get('tmdb_id'):
            return
        return self.mbot.services.call(ServiceConst.tmdb.namespace, ServiceConst.tmdb.get, tmdb_id=data.get('tmdb_id'),
                                       media_type=NotifyListener.__get_media_type__(data))

    def __get_douban_meta__(self, data):
        if 'douban_meta' in data:
            return data.get('douban_meta')
        if not data.get('douban_id'):
            return
        return self.mbot.services.call(ServiceConst.douban.namespace, ServiceConst.douban.get,
                                       douban_id=data.get('douban_id'))

    def on_event(self, event: Event):
        """
        触发事件，发生事件时的入口方法
        :param event:
        :return:
        """
        data = DictWrapper(event.data.copy())
        media_type = NotifyListener.__get_media_type__(data)
        tmdb_meta = self.__get_tmdb_meta__(data)
        douban_meta = self.__get_douban_meta__(data)
        # x_meta是自建影视数据，可能有，可能没有，需要做特殊处理
        x_meta = data.get('x_meta')
        if x_meta:
            background_url = None
            media_image = self.mbot.services.call(
                ServiceConst.scraper.namespace,
                ServiceConst.scraper.get_image,
                tmdb_id=x_meta.get('tmdbId'),
                media_type=media_type,
                season_number=data.get('season_number')
            )
            if media_image:
                background_url = media_image.main_background
            data.update({
                'title': x_meta.get('title'),
                'rating': x_meta.get('rating'),
                'link_url': 'https://movie.douban.com/subject/%s/' % x_meta.get('doubanId'),
                'pic_url': background_url,
                'genres': x_meta.get('genres'),
                'country': x_meta.get('country'),
                'year': x_meta.get('releaseYear'),
                'intro': x_meta.get('intro'),
                'release_date': x_meta.get('premiereDate')
            })
        else:
            if tmdb_meta or douban_meta:
                background_url = None
                # 这里如果只有豆瓣，怎么通知
                media_image = self.mbot.services.call(
                    ServiceConst.scraper.namespace,
                    ServiceConst.scraper.get_image,
                    tmdb_id=tmdb_meta.get('id'),
                    media_type=media_type,
                    season_number=data.get('season_number')
                )
                if media_image:
                    background_url = media_image.main_background
                data.update({
                    'title': MediaDataSelector.get_title(tmdb_meta, douban_meta),
                    'rating': MediaDataSelector.get_rating(tmdb_meta, douban_meta),
                    'link_url': MediaDataSelector.get_url(tmdb_meta, douban_meta),
                    'pic_url': background_url,
                    'genres': MediaDataSelector.get_genres(tmdb_meta, douban_meta),
                    'country': MediaDataSelector.get_country(tmdb_meta, douban_meta),
                    'year': MediaDataSelector.get_year(tmdb_meta, douban_meta),
                    'intro': MediaDataSelector.get_intro(tmdb_meta, douban_meta),
                    'release_date': MediaDataSelector.get_release_date(tmdb_meta, douban_meta)
                })
        if data.get('uid') and not data.get('nickname'):
            user = self.mbot.services.call(ServiceConst.user.namespace, ServiceConst.user.get_by_uid,
                                           uid=data.get_int('uid'))
            if user:
                data.update({
                    'nickname': user.nickname
                })
        if not data.get('nickname'):
            data['nickname'] = '未知用户'
        # 根据不同的事件类型，对可用数据做些转化，再发送消息
        if event.event_type == EventType.DownloadCompleted.name:
            self.notify_download_completed(data)
        elif event.event_type == EventType.SubMedia.name:
            self.notify_sub_media(data)
        elif event.event_type == EventType.DownloadStart.name:
            self.notify_download_start(data)
        elif event.event_type == EventType.SiteError.name:
            self.send_app_message_by_template_name(data.get('uid'), 'site_error', data)
