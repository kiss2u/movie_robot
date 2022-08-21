import datetime
import re

import cn2an
import emoji
import math
from jinja2 import Template
from lxml import etree
from pypinyin import Style, lazy_pinyin


class StringUtils:
    @staticmethod
    def str_to_date(strdate, pattern: str) -> datetime:
        if strdate is None or strdate == '':
            return None
        return datetime.datetime.strptime(strdate, pattern)

    @staticmethod
    def str_to_year(strdate, pattern: str) -> datetime:
        if strdate is None or strdate == '':
            return None
        try:
            date = datetime.datetime.strptime(strdate, pattern)
            return date.year
        except Exception as e:
            return None

    @staticmethod
    def trim_emoji(text):
        return emoji.demojize(text)

    @staticmethod
    def trans_number(numstr: str):
        try:
            if numstr.isdigit():
                return int(numstr)
            else:
                return cn2an.cn2an(numstr)
        except Exception as e:
            return

    @staticmethod
    def noisestr(text):
        if text is None or len(text) == 0:
            return text
        if len(text) > 2:
            s = 2
        else:
            s = 0
        e = s + math.ceil(len(text) / 2)
        if e == s:
            e += 1
        n = []
        i = 0
        while i < (e - s):
            n.append('*')
            i += 1
        return text.replace(text[s:e], ''.join(n))

    @staticmethod
    def trimhtml(htmlstr):
        try:
            html = etree.HTML(text=htmlstr)
            return html.xpath('string(.)')
        except Exception as e:
            return htmlstr

    @staticmethod
    def replace_var(text, context):
        for m in re.findall(r'\$\{([^\}]+)\}', text):
            var_name = m
            text = text.replace('${%s}' % var_name,
                                str(context[var_name]) if var_name in context else '')
        return text

    @staticmethod
    def dict_str_is_empty(obj: dict, key: str):
        if obj is None or len(obj) == 0:
            return True
        if key is None or len(key) == 0:
            return True
        if key not in obj:
            return True
        if obj[key] is None:
            return True
        if len(obj[key]) == 0:
            return True
        return False

    @staticmethod
    def to_number(text):
        if text is None:
            return None
        if text.isdigit():
            return int(text)
        else:
            try:
                return cn2an.cn2an(text)
            except ValueError as e:
                return None

    @staticmethod
    def render_text(text, **context):
        template = Template(text)
        return template.render(**context)

    @staticmethod
    def is_en_name(text):
        if re.match(r'[a-zA-Z\W_\d]+', str(text)):
            return True
        else:
            return False

    @staticmethod
    def get_first_letter(text):
        if not text:
            return text
        if not StringUtils.is_en_name(text):
            return ''.join(lazy_pinyin(text, style=Style.FIRST_LETTER))
        return text
