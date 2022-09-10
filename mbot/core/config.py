import os.path
from typing import Any

import yaml

"""默认配置的文件名称"""
BASE_CONFIG_FILENAME = 'base_config.yml'
"""通知模版配置文件名称"""
NOTIFY_TEMPLATE_CONFIG_FILENAME = 'notify_template.yml'
"""默认的基础配置文件内容"""
DEFAULT_BASE = {
    'server': {},
    'frontend': {},
    'media_server': {},
    'download_client': [],
    'media_path': [],
    'notify_channel': {},
    'web': {'host': '::', 'port': 1329, 'server_url': None},
    'free_download': {'avg_statistics_period': 5, 'enable': False},
    'movie_metadata': {
        'douban': {'cookie': None}
    },
    'file_link': {
        'movie': {
            'filename': '{{name}} ({{year}}){%if version %} - {{version}}{% endif %}',
            'folder': '{{name}} ({{year}})'
        },
        'tv': {
            'filename': '{{name}} S{{season}}E{{ep_start}}{%if ep_end %}-E{{ep_end}}{% endif %}{%if version %} - {{version}}{% endif %}',
            'folder': '{{name}} ({{year}})'
        },
        'recognize': True,
        'exact_year': False,
        'use_unknown_dir': True,
        'file_process_mode': 'link',
        'use_area_folder': False,
        'disc_single_folder': False,
        'fix_emby_bdmv_bug': False,
    },
    'scraper': {
        'generate_nfo': True,
        'use_cn_person_name': False,
        'person_nfo_path': None
    },
    'subtitle': {
        'enable': True,
        'finder_type': ['zimuku'],
        'file_name_template': '{{ name }}.{{ language[0] }}{% if language[0] == "zh-cn" and language | length == 2 %}.default{% endif%}{{ subtitle_ext }}',
        'filter_type': ['srt', 'ass'],
        'filter_language': ['双语', '简体', '繁体'],
        'sync_language': ['zh-cn', 'zh-tw'],
        'subhd_check_code': 329681,
        'exclude_area': ['中国大陆', '中国台湾']
    }
}
"""默认的通知模版"""
DEFAULT_TEMPLATES = {
    'download_start_movie': {
        'name': '电影开始下载',
        'enable': True,
        'title': '⏬{{title}}{% if rating %}  ⭐️{{"%.1f"|format(rating)}}{% endif %}',
        'body': """上映于{{year}}年{% if site_name %}，由 {{nickname}} 下载自「{{site_name}}」{% else %} 手动添加的下载任务{% endif %} 
{% if media_stream.media_source %}{{media_stream.media_source}}{% else %} 媒体属性未知{% endif %}{% if media_stream.resolution %} · {{media_stream.resolution}}{% endif %}{% if file_size %} · {{file_size}}{% endif %}{% if media_stream.release_team %} · {{media_stream.release_team}}压制{% endif %}
{% if intro -%}··········································
{{intro|replace(' ','')|replace('\n','')}}{%- endif %}"""
    },
    'download_start_tv': {
        'name': '剧集开始下载',
        'enable': True,
        'title': '⏬{{title}} {% if season_number %}S{{season_number}}{% endif %}{% if episodes %}E{{episodes}}{% endif %}{% if rating %}  ⭐️{{"%.1f"|format(rating)}}{% endif %}',
        'body': """上映于{{year}}年{% if site_name %}，由 {{nickname}} 下载自「{{site_name}}」{% else %} 手动添加的下载任务{% endif %} 
{% if media_stream.media_source %}{{media_stream.media_source}}{% else %} 媒体属性未知{% endif %}{% if media_stream.resolution %} · {{media_stream.resolution}}{% endif %}{% if file_size %} · {{file_size}}{% endif %}{% if media_stream.release_team %} · {{media_stream.release_team}}压制{% endif %}
{% if intro -%}··········································
{{intro|replace(' ','')|replace('\n','')}}{%- endif %}"""
    },
    'download_completed_movie': {
        'name': '电影下载完成',
        'enable': True,
        'title': '✅{{title}}{% if rating %}  ⭐️{{"%.1f"|format(rating)}}{% endif %}',
        'body': """上映于{{year}}年{% if site_name %}，由 {{nickname}} 下载自「{{site_name}}」{% else %} 手动下载完成{% endif %} 
{% if media_stream.media_source %}{{media_stream.media_source}}{% else %} 媒体属性未知{% endif %}{% if media_stream.resolution %} · {{media_stream.resolution}}{% endif %}{% if file_size %} · {{file_size}}{% endif %}{% if media_stream.release_team %} · {{media_stream.release_team}}压制{% endif %}
{% if intro -%}··········································
{{intro|replace(' ','')|replace('\n','')}}{%- endif %}"""
    },
    'download_completed_tv': {
        'name': '剧集下载完成',
        'enable': True,
        'title': '✅{{title}} {% if season_number %}S{{season_number}}{% endif %}{% if episodes %}E{{episodes}}{% endif %}{% if rating %}  ⭐️{{"%.1f"|format(rating)}}{% endif %}',
        'body': """上映于{{year}}年{% if site_name %}，由 {{nickname}} 下载自「{{site_name}}」{% else %} 手动下载完成{% endif %} 
{% if media_stream.media_source %}{{media_stream.media_source}}{% else %} 媒体属性未知{% endif %}{% if media_stream.resolution %} · {{media_stream.resolution}}{% endif %}{% if file_size %} · {{file_size}}{% endif %}{% if media_stream.release_team %} · {{media_stream.release_team}}压制{% endif %}
{% if intro -%}··········································
{{intro|replace(' ','')|replace('\n','')}}{%- endif %}"""
    },
    'sub_from_trending_movie': {
        'name': '来自榜单的电影订阅',
        'enable': True,
        'title': '榜单电影:{{ cn_name }}({{ release_year }}) 评分:{{ rating }}',
        'body': """{{ nickname }} 已订阅 「{{ title }}」
{{country|join(" · ")}}{% if genres %}   {{genres|join(" · ")}}{% else %}   分类未知{% endif %}{% if rating %}  ⭐️{{"%.1f"|format(rating)}}{% endif %}
{% if comment -%}··········································
{{comment|replace('　','')|replace(' ','')|replace('\n','')}}{%- endif %}"""
    }, 'sub_from_trending_tv': {
        'name': '来自榜单的剧集订阅',
        'enable': True,
        'title': '榜单剧集:{{ cn_name }}({{ release_year }}) 评分:{{ rating }}',
        'body': """{{ nickname }} 已订阅第 {{ season_number }} 季
{{country|join(" · ")}}{% if genres %}   {{genres|join(" · ")}}{% else %}   分类未知{% endif %}{% if rating %}  ⭐️{{"%.1f"|format(rating)}}{% endif %}
{% if comment -%}··········································
{{comment|replace('　','')|replace(' ','')|replace('\n','')}}{%- endif %}"""
    }, 'sub_movie': {
        'name': '新增电影订阅',
        'enable': True,
        'title': '🍿订阅：{{ cn_name }} {% if rating %}  ⭐️{{"%.1f"|format(rating)}}{% else %}{% if not is_aired %}  未上映{% endif %}{% endif %}',
        'body': """{% if not is_aired and  release_date %}将于{% endif %}{% if release_date %}{{ release_date }}上映{% else %}上映日期未知{% endif %}，由 {{ nickname }} 订阅
{{country|join(" · ")}}{% if genres %}   {{genres|join(" · ")}}{% else %}   分类未知{% endif %}
{% if intro -%}··········································
{{intro|replace(' ','')|replace('\n','')}}{%- endif %}"""
    }, 'sub_tv': {
        'name': '新增剧集订阅',
        'enable': True,
        'title': '📺订阅：{{ cn_name }} {% if rating %}  ⭐️{{"%.1f"|format(rating)}}{% else %}{% if not is_aired %}  未上映{% endif %}{% endif %}',
        'body': """第 {{ season_number }} 季 共 {{episode_count}} 集 上映于{{ release_year }}年，由 {{ nickname }} 订阅
{{country|join(" · ")}}{% if genres %}   {{genres|join(" · ")}}{% else %}   分类未知{% endif %}
{% if intro -%}··········································
{{intro|replace(' ','')|replace('\n','')}}{%- endif %}"""
    }, 'site_error': {
        'name': '站点异常',
        'enable': True,
        'title': '站点异常',
        'body': '访问{{ site_name }}异常，错误原因：{{ reason }}'
    }
}


def load_yaml_config(filepath: str):
    """
    加载一个yaml格式的文件
    :param filepath:
    :return:
    """
    if not filepath or not os.path.exists(filepath):
        raise FileNotFoundError(f'找不到配置文件: {filepath}')
    with open(filepath, 'r', encoding='utf-8') as file:
        user_config = yaml.safe_load(file)
    return user_config


class ConfigValues(dict):
    """封装后的配置文件内容，可以config.xxx 打点调用属性值；同时增加了一些配置文件操作方法"""

    def __init__(self, data: dict, config_filepath=None):
        self._config_filepath = config_filepath
        super().__init__(data)

    def __getattr__(self, attr) -> Any:
        result = self.get(attr)
        if result and not isinstance(result, ConfigValues):
            if isinstance(result, dict):
                self.update({attr: ConfigValues(result)})
            else:
                return result
            return self.get(attr)
        else:
            return result

    def exists(self):
        return os.path.exists(self._config_filepath)

    def _to_dict(self, data):
        """
        把包装类型还原成原始的dict来保证json yaml序列化可用
        :param data:
        :return:
        """
        if isinstance(data, ConfigValues):
            data = dict(data)
        elif isinstance(data, dict):
            for key in data:
                data.update({key: self._to_dict(data.get(key))})
        elif isinstance(data, list):
            if len(data) > 0 and isinstance(data[0], dict):
                new_list = []
                for item in data:
                    new_list.append(self._to_dict(item))
                data = new_list
        return data

    def save(self):
        """
        保存配置
        :return:
        """
        if not self._config_filepath:
            return
        path = os.path.dirname(self._config_filepath)
        if not os.path.exists(self._config_filepath) and not os.path.exists(path):
            os.makedirs(path)
        with open(self._config_filepath, "w",
                  encoding="utf-8") as f:
            yaml.dump(self._to_dict(self.copy()), f, default_style=False, encoding='utf-8', allow_unicode=True)


def merge_dict(a, b):
    """
    合并两个dict，只做一级合并，用于补充配置文件新增的变化
    :param a:
    :param b:
    :return:
    """
    if not b:
        b.update(a)
        return True
    update = False
    for key in a:
        if key not in b:
            b[key] = a[key]
            update = True
    return update


class Config:
    """配置文件管理的一个类"""

    def __init__(self):
        self.work_dir = None
        # 配置文件目录
        self.config_dir = None
        # 插件目录
        self.plugin_dir = None
        # 基础配置文件对象
        self.base: ConfigValues = None
        # 通知模版配置文件对象
        self.notify_templates: ConfigValues = None

    def load_config(self, config_dir):
        """
        加载目录内的配置文件
        :param config_dir:
        :return:
        """
        self.config_dir = config_dir
        base_config_filepath = os.path.join(config_dir, BASE_CONFIG_FILENAME)
        base = None
        if os.path.exists(base_config_filepath):
            base = load_yaml_config(base_config_filepath)
        # 记录是否第一次初始化，首次启动应用程序没有配置文件，不要为用户自动生成；以是否有配置文件作为系统是否完成初装的判断
        first_init = False
        if base is None:
            base = {}
            first_init = True
        # 合并配置中缺失的默认项
        merge_base = merge_dict(DEFAULT_BASE, base)
        # 转化成包装的配置操作类
        self.base = ConfigValues(base, base_config_filepath)
        if merge_base and not first_init:
            # 非瘦子初始化产生合并自动保存
            self.base.save()
        notify_tmpl_filepath = os.path.join(config_dir, NOTIFY_TEMPLATE_CONFIG_FILENAME)
        notify_templates = load_yaml_config(notify_tmpl_filepath)
        merge_tmpl = merge_dict(DEFAULT_TEMPLATES, notify_templates)
        self.notify_templates = ConfigValues(notify_templates, notify_tmpl_filepath)
        if merge_tmpl:
            self.notify_templates.save()
