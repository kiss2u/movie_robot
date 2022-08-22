from abc import ABCMeta, abstractmethod


class Notify(metaclass=ABCMeta):
    """通知处理的接口，扩展通知应用需要实现此接口
    """

    @abstractmethod
    def send_text_message(self, title_message, text_message, to_user):
        """
        发送普通文本消息
        :param title_message: 消息标题
        :param text_message: 消息内容
        :param to_user: 具体的接收者标识
        :return:
        """
        pass

    @abstractmethod
    def send_by_template(self, to_user, title_template, body_template, context: dict):
        """
        发送模版消息，标题和内容均为模版
        :param to_user: 具体的接收者标识
        :param title_template: 标题模版
        :param body_template: 内容模版
        :param context: 模版所需的上下文变量
        :return:
        """
        pass
