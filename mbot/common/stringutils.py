import re

import emoji
import math
from jinja2 import Template
from lxml import etree
from pypinyin import Style, lazy_pinyin


class StringUtils:
    """字符串操作工具"""

    @staticmethod
    def trim_emoji(text):
        """
        去掉字符串中的emoji表情
        :param text:
        :return:
        """
        return emoji.demojize(text)

    @staticmethod
    def noisestr(text):
        """
        把一个字符串中间替换成*号干扰字符
        :param text:
        :return:
        """
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
    def trim_html(text):
        """
        去掉字符串中的html标签
        :param text:
        :return:
        """
        try:
            html = etree.HTML(text=text)
            return html.xpath('string(.)')
        except Exception as e:
            return text

    @staticmethod
    def replace_var(text, context):
        """
        替换字符串中的简单占位变量 格式 {var name}
        :param text:
        :param context:
        :return:
        """
        for m in re.findall(r'\$\{([^\}]+)\}', text):
            var_name = m
            text = text.replace('${%s}' % var_name,
                                str(context[var_name]) if var_name in context else '')
        return text

    @staticmethod
    def render_text(text, **context):
        """
        把模版语法渲染成最终字符串
        :param text:
        :param context:
        :return:
        """
        if not context or len(context) == 0:
            return text
        template = Template(text)
        return template.render(**context)

    @staticmethod
    def is_en_text(text):
        """
        是否为一个全英文字符串
        :param text:
        :return:
        """
        if re.match(r'[a-zA-Z\W_\d]+', str(text)):
            return True
        else:
            return False

    @staticmethod
    def get_chinese_first_letter(text):
        """
        获取中文拼音首字母组合
        :param text:
        :return:
        """
        if not text:
            return text
        if not StringUtils.is_en_text(text):
            return ''.join(lazy_pinyin(text, style=Style.FIRST_LETTER))
        return text
