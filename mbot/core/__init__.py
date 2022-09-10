from mbot.core.config import Config
import logging
from typing import Any, List, Dict, Callable

import voluptuous as vol

from mbot.common.dictutils import ReadOnlyDict
from mbot.core.eventbus import EventBus
from mbot.core.events import EventListener
from mbot.core.task import Task
from mbot.exceptions import MovieBotException

_LOGGER = logging.getLogger(__name__)


class MovieBot:
    """应用超级对象，启动时初始化"""

    def __init__(self):
        # 配置文件操作类，包含所有配置信息
        self.config = Config()
        # 支持本地和远程调用的服务类
        self.services = ServiceRegistry(self)
        # 事件总线，系统内所有的事件会通过这里控制
        self.event_bus = EventBus()
        # 所有已经加载的插件信息
        self.plugins: Dict[str, Plugin] = dict()


class PluginContext:
    """插件上下文信息，包含一些实现插件执行前后一些关键对象，继承此对象，将自动设置值"""

    def __init__(self):
        self.mbot: MovieBot = None

    def set_mbot(self, mbot: MovieBot):
        self.mbot: MovieBot = mbot


class PluginManifest:
    """插件描述信息"""

    def __init__(self, json_manifest: dict = None):
        # 插件名称，中文名称，简短描述插件
        self.name: str = None
        # 作者
        self.author: str = None
        # 插件简介
        self.description: str = None
        # 插件版本
        self.version: str = None
        # 插件依赖的python模块
        self.requirements: List[str] = []
        # 使用的内置服务接口名称，用到了什么接口必须填写。用来提示用户或者授权。
        self.use_service_names: List[str] = []
        # 插件包含的定时任务文件名称，.py文件
        self.tasks: List[str] = []
        # 插件包含的事件监听器名称，.py文件
        self.listeners: List[str] = []
        # 传入的字典key映射为属性
        if json_manifest:
            for key in json_manifest:
                setattr(self, key, json_manifest[key])


class Plugin:
    """一个插件包含的所有信息"""
    __slots__ = ['module_name', 'manifest', 'listeners', 'tasks']

    def __init__(
            self,
            module_name: str,
            manifest: PluginManifest,
            listeners: List[EventListener],
            tasks: List[Task]
    ):
        # 插件名称
        self.module_name: str = module_name
        self.manifest: PluginManifest = manifest
        self.listeners: List[EventListener] = listeners
        self.tasks: List[Task] = tasks


class Service:
    """一个具体的服务，包含一个被包装的函数和参数结构定义"""
    __slots__ = ['func', 'schema']

    def __init__(self, func, schema: vol.Schema):
        self.func = ServiceFuncWrapper(func)
        self.schema: vol.Schema = schema


class ServiceNotFound(MovieBotException):
    """找不到服务时抛出此错误"""

    def __init__(self, namespace: str, service: str) -> None:
        super().__init__(self, f"Service {namespace}.{service} not found")
        self.namespace = namespace
        self.service = service


class ServiceCall:
    """一次服务调用所包含的参数"""
    __slots__ = ["namespace", "service", "data"]

    def __init__(
            self,
            domain: str,
            service: str,
            data: Dict[str, Any] = None
    ) -> None:
        self.namespace = domain.lower()
        self.service = service.lower()
        self.data = ReadOnlyDict(data or {})


class ServiceCallResult(dict):
    """服务调用返回的结果，所有dict和包含to_json的函数会自动包装为此结构"""

    def __getattr__(self, attr: str) -> Any:
        """
        覆盖属性调用实现 xxx.abc 时触发此调用，返回字典里的值，同时对value为字典类型的值再次包装
        :param attr:
        :return:
        """
        result = self.get(attr)
        if result:
            if isinstance(result, dict):
                return ServiceCallResult(result)
            elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                return [ServiceCallResult(r) for r in result]
            else:
                return result
        else:
            return result


class ServiceFuncWrapper:
    """服务函数的包装器。这个包装器会将自动把调用函数后返回的结果做封装"""

    def __init__(self, func):
        self._func = func

    def __call__(self, *args, **kwargs):
        """
        执行包装函数时触发，透过这个方法调用真正的函数
        :param args:
        :param kwargs:
        :return:
        """
        result = self._func(*args)
        if result:
            if isinstance(result, dict):
                return ServiceCallResult(result)
            elif hasattr(result, 'to_json'):
                return ServiceCallResult(result.to_json())
            return result
        return


class ServiceRegistry:
    """本地服务注册中心"""

    def __init__(self, mbot: MovieBot):
        self._mbot = mbot
        self._services: Dict[str, Dict[str, Service]] = dict()

    def register(
            self,
            namespace,
            service,
            service_func,
            schema: vol.Schema = None,
    ) -> None:
        """
        注册一个服务
        :param namespace: 命名空间
        :param service: 服务名
        :param service_func: 服务具体执行函数
        :param schema: 服务执行函数所需参数的结构定义，会自动验证传入参数是否符合结构
        :return:
        """
        namespace = str(namespace).lower()
        service = str(service).lower()
        service_obj = Service(service_func, schema)

        if namespace in self._services:
            self._services[namespace][service] = service_obj
        else:
            self._services[namespace] = {service: service_obj}

    def call(
            self,
            namespace,
            service,
            **service_data
    ):
        """
        调用一个服务
        :param namespace: 命名空间
        :param service:  服务名称
        :param service_data: 服务所需的数据，参数
        :return:
        """
        namespace = str(namespace).lower()
        service = str(service).lower()
        service_data = service_data or {}
        try:
            handler: Service = self._services[namespace][service]
        except KeyError:
            raise ServiceNotFound(namespace, service) from None
        if handler.schema:
            try:
                #  对提供了结构定义的服务，做参数验证
                processed_data: Dict[str, Any] = handler.schema(service_data)
            except vol.Invalid:
                _LOGGER.error(
                    f"Invalid data for service call {namespace}.{service}: {service_data}"
                )
                raise
        else:
            processed_data = service_data
        return handler.func(ServiceCall(namespace, service, processed_data))


import httpx


class RemoteServiceRegistry(ServiceRegistry):
    """远程服务注册中心"""

    def __init__(self, server_url: str, token: str, mbot: MovieBot):
        """
        初始化远程服务注册中心
        :param server_url: 远程服务访问地址http[s]://hostname
        :param token: 鉴权令牌
        :param mbot: 应用超级对象
        """
        super().__init__(mbot)
        if server_url:
            self._server_url = server_url.rstrip('/')
        self._token = token

    def register(
            self,
            namespace: str,
            service: str,
            service_func,
            schema: vol.Schema = None,
    ) -> None:
        raise MovieBotException('远程服务不支持注册')

    def call(
            self,
            namespace: str,
            service: str,
            **service_data
    ):
        """
        调用远程服务，实际为通过http请求远程服务提供的接口，并获得返回结果
        :param namespace:
        :param service:
        :param service_data:
        :return:
        """
        namespace = namespace.lower()
        service = service.lower()
        service_data = service_data or {}
        r = httpx.post(
            url=f'{self._server_url}/api/service/call',
            json={
                'namespace': namespace,
                'service': service,
                'data': service_data
            },
            headers={
                'Authorization': f'Bearer {self._token}'
            }
        )
        try:
            result = r.json()
        except:
            result = None
        if result:
            return ServiceCallResult(result)
        else:
            return
