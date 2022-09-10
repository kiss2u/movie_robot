import logging
from typing import Dict

from mbot.core.events import EventListener, EventType, Event

"""监听器绑定事件的快捷属性"""
BIND_EVENT_NAME = '__bind_event__'
"""监听器设定监听器顺序的快捷属性"""
ORDER_NAME = '__order__'

_LOGGER = logging.getLogger(__name__)


class EventBus:
    """事件处理总线"""

    def __init__(self):
        self.listeners: Dict[str, list] = dict()

    def add_listener(self, event_listener: EventListener, event_types=None):
        """
        添加一个监听器，并按order完成排序
        :param event_types:
        :param event_listener:
        :param order:
        :return:
        """
        if hasattr(event_listener, BIND_EVENT_NAME):
            event_types = getattr(event_listener, BIND_EVENT_NAME)
        if isinstance(event_types, EventType):
            event_types = [str(event_types)]
        elif isinstance(event_types, str):
            event_types = [event_types]
        order = getattr(event_listener, ORDER_NAME) if hasattr(event_listener, ORDER_NAME) else 100
        if order is None:
            order = 100
        for t in event_types:
            t = str(t)
            if t in self.listeners:
                l: list = self.listeners[t]
            else:
                l: list = []
                self.listeners[t] = l
            l.append({
                'listener': event_listener,
                'order': order
            })
            l.sort(key=lambda x: x['order'])
            self.listeners[t] = l
        _LOGGER.info(
            f'监听器已经添加: {type(event_listener).__module__} 绑定事件: {",".join([str(t) for t in event_types]) if event_types else ""} 顺序：{order}')

    def publish_event(self, event: Event):
        """
        触发一个事件
        :param event:
        :return:
        """
        listeners: list = self.listeners.get(event.event_type)
        if not listeners or len(listeners) == 0:
            return
        for l in listeners:
            listener = l['listener']
            try:
                listener.on_event(event)
            except Exception as e:
                _LOGGER.error(f'on_event error: {type(listener).__name__} event: {event.to_json()}', exc_info=True)
