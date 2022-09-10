import logging
import time

import httpx
from tenacity import retry, stop_after_delay, wait_exponential, retry_if_not_exception_type

from mbot.exceptions import RateLimitException
from mbot.site.siteexceptions import RequestOverloadException, LoginRequired


class SiteSearcher:
    logger = logging.getLogger(__name__)
    run_time = None
    interval_secs = 10

    def __init__(self, site_helper, querys, cate_level1_list: list = None, network_error_retry=False,
                 timeout: int = None, search_value_type=None):
        self.site_helper = site_helper
        self.querys = []
        for q in querys:
            if search_value_type and q.get('value_type') and q.get('value_type') not in search_value_type:
                continue
            self.querys.append(q)
        self.network_error_retry = network_error_retry
        self.cate_level1_list = cate_level1_list
        self.timeout = timeout

    def get_run_time(self):
        return self.run_time

    def get_site_id(self):
        return self.site_helper.get_id()

    def get_site_name(self):
        return self.site_helper.get_name()

    def get_query_str(self):
        return [i.get('value') for i in self.querys]

    @retry(retry=retry_if_not_exception_type(LoginRequired), stop=stop_after_delay(600),
           wait=wait_exponential(multiplier=1, min=20, max=120))
    async def __retry_search__(self, query):
        return await self.__search__(query)

    async def __search__(self, query):
        """
                自动重试的搜索方式
                :param keyword:
                :return:
                """
        try:
            params = {
                query.get('key'): query.get('value'),
                'cate_level1_list': self.cate_level1_list,
                'timeout': self.timeout
            }
            return await self.site_helper.search(**params)
        except LoginRequired as le:
            raise le
        except httpx.ReadTimeout as rte:
            raise rte
        except httpx.ConnectError as ce:
            raise ce
        except httpx.RemoteProtocolError as rpe:
            raise rpe
        except httpx.ConnectTimeout as cte:
            raise cte
        except RequestOverloadException as roe:
            time.sleep(roe.stop_secs)
            raise roe
        except RateLimitException as rle:
            raise rle
        except Exception as e:
            self.logger.error('从%s搜索 %s 失败了，错误信息: %s' % (self.site_helper.get_name(), self.get_query_str(), e))
            raise e

    async def search(self):
        start = time.perf_counter()
        try:
            ids: set = set()
            res = []
            for i, q in enumerate(self.querys):
                if self.network_error_retry:
                    r = await self.__retry_search__(q)
                else:
                    r = await self.__search__(q)
                if not r:
                    continue
                for t in r:
                    if t.id in ids:
                        continue
                    res.append(t)
                    ids.add(t.id)
                if i + 1 < len(self.querys):
                    time.sleep(self.interval_secs)
            return {'code': 0, 'data': res}
        except LoginRequired as e:
            raise e
        except Exception as e:
            self.logger.error(f'从{self.site_helper.get_name()}搜索{self.get_query_str()}失败了 错误：%s' % e, exc_info=True)
            return {'code': 1, 'data': []}
        finally:
            end = time.perf_counter()
            self.run_time = end - start
