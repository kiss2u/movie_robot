import datetime
import logging

from tenacity import retry, wait_fixed, stop_after_attempt

from mbot.common.chrome import Chrome


class HDChinaHandler:
    hdchina_freesession_check_time = None

    @retry(wait=wait_fixed(3), stop=stop_after_attempt(5), reraise=True)
    def handle(self, domain, paths, query, cookies):
        """
        hdc需要30分钟内访问一次页面，保证free session续期，不然获取免费时间会出错
        :param domain:
        :param paths:
        :param query:
        :param cookies:
        :return:
        """
        if not paths:
            return
        if self.hdchina_freesession_check_time and (
                datetime.datetime.now() - self.hdchina_freesession_check_time).total_seconds() < 1500:
            return
        try:
            url = f'{domain}{paths[0].get("path")}'
            chrome = Chrome()
            chrome.get(url, cookies)
        except Exception as e:
            logging.error('内置Chrome访问hdc失败：%s' % e)
        finally:
            chrome.quit()
            self.hdchina_freesession_check_time = datetime.datetime.now()


hdchina_handler = HDChinaHandler

search_pre_handlers = {
    # 'hdchina_freesession_check_handler': hdchina_handler
}
