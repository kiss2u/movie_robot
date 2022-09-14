"""
系统插件的加载器核心实现，所有的系统内置插件、外部自定义插件，均有此加载为可执行的实例
系统内提供了多种插件扩展点，当前支持的有：事件监听、定时任务，持续扩充中
"""
import importlib
import json
import logging
import os.path
from typing import List

from mbot.common.typeutils import TypeUtils
from mbot.core import MovieBot, PluginManifest, Plugin, PluginContext, InitializingPlugin
from mbot.core.events import EventListener
from mbot.exceptions import MovieBotException

MANIFEST_FILENAME = 'manifest.json'
SKIP_FOLDER = ['__pycache__']


class ManifestErrorException(MovieBotException):
    """插件描述信息错误"""
    pass


_LOGGER = logging.getLogger(__name__)


def new_plugin_instance(cls, mbot: MovieBot):
    """
    构造一个对象，并设置好上下文信息
    :param cls:
    :return:
    """
    if not cls:
        return
    if PluginContext in cls.__bases__:
        obj = cls(mbot=mbot)
    else:
        obj = cls()
    if InitializingPlugin in cls.__bases__:
        obj.after_properties_set()
    return obj


class PluginLoader:
    """插件加载器"""

    def __init__(self, plugin_folder, namespace, mbot: MovieBot):
        """
        初始化事件加载器
        :param plugin_folder: 插件所在目录
        :param namespace: 插件目录在系统内的模块包路径
        :param mbot: 应用超级对象
        """
        if not plugin_folder:
            return
        self.plugin_folder = plugin_folder
        self.namespace = namespace
        self.mbot = mbot

    @staticmethod
    def get_manifest(plugin_path) -> PluginManifest:
        """
        获取插件描述信息
        :param plugin_path: 插件文件夹
        :return:
        """
        plugin_meta_filepath = os.path.join(plugin_path, MANIFEST_FILENAME)
        if not os.path.exists(plugin_meta_filepath):
            return
        with open(plugin_meta_filepath, 'r', encoding='utf-8') as file:
            meta = json.load(file)
        return PluginManifest(meta)

    def load(self) -> List[Plugin]:
        """
        加载目录下所有插件
        :return:
        """
        if not os.path.exists(self.plugin_folder):
            _LOGGER.error(f'插件目录不存在：{self.plugin_folder}')
            return
        plugins: List[Plugin] = []
        for p in os.listdir(self.plugin_folder):
            plugin_path = os.path.join(self.plugin_folder, p)
            if os.path.isfile(plugin_path) or p in SKIP_FOLDER:
                continue
            plugin = self.setup(plugin_path)
            if not plugin:
                continue
            plugins.append(plugin)
        return plugins

    def import_mod(self, cls_path):
        """
        导入模块
        :param cls_path:
        :return:
        """
        if not cls_path:
            return
        try:
            return importlib.import_module(cls_path)
        except Exception as e:
            _LOGGER.error(f'加载类失败：{cls_path}', exc_info=True)
            return

    def import_listeners(self, pkg_path: str, names: list):
        """
        导入包目录下所有的监听器
        :param pkg_path:
        :param names:
        :return:
        """
        if not names or len(names) == 0:
            return
        listeners: List[EventListener] = []
        for name in names:
            if name.endswith('.py'):
                name = name[0:len(name) - 3]
            mod_path = f'{pkg_path}.{name}'
            mod = self.import_mod(mod_path)
            listener: EventListener = new_plugin_instance(
                TypeUtils.find_subclass_from_mod(mod, EventListener), self.mbot)
            if not listener:
                continue
            self.mbot.event_bus.add_listener(listener)
            listeners.append(listener)
        return listeners

    def import_tasks(self, pkg_path: str, names: list):
        """
        导入包目录下所有的任务
        :param pkg_path:
        :param names:
        :return:
        """
        if not names or len(names) == 0:
            return
        # tasks: List[Task] = []
        for name in names:
            if name.endswith('.py'):
                name = name[0:len(name) - 3]
            cls_path = f'{pkg_path}.{name}'
            mod = self.import_mod(cls_path)
            # task: Task = self.new_instance_with_context(TypeUtils.find_subclass_from_mod(mod, Task))
            # if not task:
            #     continue
            # tasks.append(task)
        # return tasks

    def setup(self, plugin_path) -> Plugin:
        """
        初始化插件
        :param plugin_path: 插件所在目录
        :return:
        """
        manifest = self.get_manifest(plugin_path)
        if not manifest:
            _LOGGER.error(f'加载插件时没有发现插件描述文件: {plugin_path}/manifest.json')
            return
        mod_name = os.path.split(plugin_path)[-1]
        full_mod_name = f'{self.namespace}.{mod_name}'
        # 加载插件中的监听器
        listeners = self.import_listeners(full_mod_name, manifest.listeners)
        # 加载插件中的任务
        self.import_tasks(full_mod_name, manifest.tasks)
        plugin = Plugin(full_mod_name, manifest)
        self.mbot.plugins.update({full_mod_name: plugin})
        return plugin
