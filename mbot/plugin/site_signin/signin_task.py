import logging
import random
import time
import typing
from itertools import groupby

from mbot.common.requestutils import RequestUtils
from mbot.const import ServiceConst
from mbot.core import PluginContext, InitializingPlugin
from mbot.core.events import Event
from mbot.core.task import Task, Tasks
from mbot.plugin.site_signin import SKIP_SITE, SigninResult, SigninStatus, SigninHandler
from mbot.plugin.site_signin.handler.hares import HaresSigninHandler
from mbot.plugin.site_signin.handler.hdchina import HdchinaSigninHandler
from mbot.plugin.site_signin.handler.hdsky import HdskySigninHandler
from mbot.plugin.site_signin.handler.nexusphp import NexusPHPSigninHandler
from mbot.plugin.site_signin.handler.ttg import TTGSigninHandler

_LOGGER = logging.getLogger(__name__)
EVENT_TYPE = 'SigninComplete'


@Tasks.register(
    name='signin_task',
    desc='签到任务',
    cron_expression='0 8 * * *',
    jitter=random.randint(1, 3600)
)
class SigninTask(Task, PluginContext, InitializingPlugin):
    """定时签到任务
    使用Tasks.register装饰器，设置定时任务的详细信息，执行周期。
    此任务继承了关键的Task接口，来实现任务执行时的run方法；
    PluginContext的作用是插件加载时会自动将系统内应用对象和一些运行时上下文参数，自动设置值；
    InitializingPlugin的作用是在这个插件每次初始化完成并设置完一系列属性后，运行after_properties_set方法，此方法是插件生命周期的一部分，类似java中spring bean的初始化完成；
    """
    signin_handler: typing.Dict[str, typing.Callable] = dict()
    nexusphp_handler: typing.Callable

    def after_properties_set(self):
        """
        在插件初始化完成，并设置好属性后；运行此方法，初始化一些签到的处理器；
        处理器以站点ID作为Key，供扩展一些特殊的站点处理器
        :return:
        """
        self.signin_handler.update({
            'hdsky': HdskySigninHandler(self.mbot).handle,
            'hdchina': HdchinaSigninHandler(self.mbot).handle,
            'ttg': TTGSigninHandler(self.mbot).handle,
            'hares': HaresSigninHandler(self.mbot).handle,
        })
        # 初始化一个NexusPHP的统一处理器
        self.nexusphp_handler = NexusPHPSigninHandler(self.mbot).handle

    def run(self):
        # 每天的真正执行时间增加一些随机性
        time.sleep(random.randint(1, 3600))
        _LOGGER.info('开始运行签到任务')
        """利用开放接口，获取应用配置的所有站点信息"""
        site_list: list = self.mbot.services.call(ServiceConst.site.namespace, ServiceConst.site.get_sites)
        if not site_list:
            _LOGGER.info('没有配置任何站点信息，无需签到')
        _LOGGER.info(f"开始进行签到，有{len(site_list)}个站点配置：{','.join([x.get('site_name') for x in site_list])}")
        skip_sites = []
        results: typing.List[SigninResult] = []
        for site in site_list:
            """
            1、检查站点适配的parser类型，是否NexusPHP，其他暂不支持
            2、查找当前站点是否拥有特殊的签到处理器，找到并使用
            """
            site_name = site.get('site_name')
            if site.get('parser') != 'NexusPHP':
                skip_sites.append(site_name)
                continue
            site_id = site.get('site_id')
            if site_id in SKIP_SITE:
                skip_sites.append(site_name)
                continue
            ck = RequestUtils.cookie_str_to_simple_cookie(site.get('cookie'))
            result: SigninResult = None
            try:
                if site_id in self.signin_handler:
                    result = self.signin_handler[site_id](ck, site.get('user_agent'), site.get('proxies'), site_name,
                                                          site.get('server_url'))
                else:
                    result = self.nexusphp_handler(ck, site.get('user_agent'), site.get('proxies'), site_name,
                                                   site.get('server_url'))
            except Exception as e:
                result = SigninResult(site_name, SigninStatus.Failed, '未知错误，请查看日志')
                _LOGGER.error(f"{site_name}签到失败: {e}")
            if result:
                results.append(result)
        if not results:
            _LOGGER.info(f'签到任务完成，以下站点无需签到：{",".join([s for s in skip_sites])}')
            return
        """把签到的结果集按状态进行分组，分组后的结果，方便做后续的通知等操作"""
        status_result: typing.Dict[str, typing.List[SigninResult]] = dict()
        for key, grouped in groupby(results, key=lambda x: x.status.name):
            group_list = list(grouped)
            status_result.update({key: group_list})
        for status in SigninStatus:
            s = status.name
            if s not in status_result:
                status_result.update({s: []})
        _LOGGER.info(
            f"签到任务完成，成功({len(status_result[SigninStatus.Succeeded.name])})：{','.join([x.site_name for x in status_result[SigninStatus.Succeeded.name]])} 失败({len(status_result[SigninStatus.Failed.name])})：{','.join([x.site_name for x in status_result[SigninStatus.Failed.name]])} 重复签到({len(status_result[SigninStatus.Repeated.name])})：{','.join([x.site_name for x in status_result[SigninStatus.Repeated.name]])} 跳过({len(skip_sites)})：{','.join([x for x in skip_sites])}")
        """发送签到完成的事件作为扩展点"""
        self.mbot.event_bus.publish_event(Event.builder().set_event_type(EVENT_TYPE).set_event_type(status_result))
