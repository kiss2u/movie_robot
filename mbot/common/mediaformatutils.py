import re

from mbot.common.numberutils import NumberUtils

TV_NUM_PATTERN = '[1234567890一二三四五六七八九十]{1,4}'

SEASON_PATTERNS = [
    re.compile('[sS](%s)?[-—~]{1,3}[sS]?(%s)' % (TV_NUM_PATTERN, TV_NUM_PATTERN)),
    re.compile('第(%s)[季部辑]?[-—~]{1,3}第?(%s)[季部辑]' % (TV_NUM_PATTERN, TV_NUM_PATTERN)),
    re.compile(r'S(?:eason)?[-]{0,3}(\d+)', re.IGNORECASE),
    re.compile('第(%s)[季部辑]' % TV_NUM_PATTERN),
    re.compile(r'^[^\d]+(\d+)$'),
]


class MediaFormatUtils:
    """媒体信息格式化工具类，待重构完成"""

    @staticmethod
    def parse_season(text):
        season_start = None
        season_end = None
        season_text = None
        for p in SEASON_PATTERNS:
            m = p.search(text)
            if m:
                season_text = m.group()
                if season_text == text:
                    season_text = m.group(1)
                if len(m.groups()) == 1:
                    season_start = NumberUtils.to_number(m.group(1))
                    season_end = None
                elif len(m.groups()) == 2:
                    season_start = NumberUtils.to_number(m.group(1))
                    season_end = NumberUtils.to_number(m.group(2))
                break
        return {'start': season_start, 'end': season_end, 'text': season_text}

    @staticmethod
    def episode_format(episode, prefix=''):
        if not episode:
            return
        if isinstance(episode, str):
            episode = list(filter(None, episode.split(',')))
            episode = [int(i) for i in episode]
        elif isinstance(episode, int):
            episode = [episode]
        if episode:
            episode.sort()
        if len(episode) <= 2:
            return ','.join([str(e).zfill(2) for e in episode])
        else:
            episode.sort()
            return '%s%s-%s%s' % (prefix, str(episode[0]).zfill(2), prefix, str(episode[len(episode) - 1]).zfill(2))

    @staticmethod
    def trim_name(name):
        if not name:
            return
        name = str(name)
        season = MediaFormatUtils.parse_season(name)
        if season and season.get('text'):
            simple_name = name.replace(season.get('text'), '').strip()
        else:
            simple_name = name
        return simple_name
