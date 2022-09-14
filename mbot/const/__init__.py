import voluptuous as vol

from mbot.common.enums import StrValueEnum


class ServiceConst:
    class user(StrValueEnum):
        namespace = 'user'
        get_by_uid = 'get_by_uid'
        __get_by_uid_schema__: vol.Schema = vol.Schema(
            {
                vol.Required('uid'): int
            }
        )

    class douban(StrValueEnum):
        namespace = 'douban'
        get = 'get'
        __get_schema__: vol.Schema = vol.Schema(
            {
                vol.Required('douban_id'): vol.Any(int, str)
            }
        )

    class tmdb(StrValueEnum):
        namespace = 'tmdb'
        get = 'get'
        __get_schema__: vol.Schema = vol.Schema(
            {
                vol.Required('tmdb_id'): vol.Any(int, str),
                vol.Optional('media_type', default='movie'): vol.Any('movie', 'tv'),
                vol.Optional('language', default='zh-CN'): str
            }
        )

    class scraper(StrValueEnum):
        namespace = 'scraper'
        get_image = 'get_image'
        __get_image_schema__: vol.Schema = vol.Schema(
            {
                vol.Required('tmdb_id'): vol.Any(int, str),
                vol.Optional('media_type', default='movie'): vol.Any('movie', 'tv'),
                vol.Optional('season_number', default=None): vol.Any(int, None),
                vol.Optional('episode_number', default=None): vol.Any(int, None),
            }
        )

    class site(StrValueEnum):
        namespace = 'site'
        get_sites = 'get_sites'

    class notify(StrValueEnum):
        namespace = 'notify'
        send_app_message_by_template_name = 'send_app_message_by_template_name'
        __send_app_message_by_template_name_schema__: vol.Schema = vol.Schema(
            {
                vol.Optional('uid', default=None): vol.Any(int, None),
                vol.Required('template_name'): str,
                vol.Optional('context', default={}): dict
            }
        )

    class ocr(StrValueEnum):
        namespace = 'ocr'
        get_image_text = 'get_image_text'
        __get_image_text_schema__: vol.Schema = vol.Schema(
            {
                vol.Required('image'): vol.All()
            }
        )
