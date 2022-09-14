from mbot.site.basesitehelper import BaseSiteHelper
from mbot.site.rarbg import Rarbg
from mbot.site.sitehelper import SiteHelper


class SiteBuilder:
    @staticmethod
    def build(site_config, cookie=None, proxies=None, user_agent=None) -> BaseSiteHelper:
        if not site_config:
            return
        if site_config.get('parser'):
            parser = site_config.get('parser')
        else:
            parser = 'NexusPHP'
        if parser == 'NexusPHP':
            return SiteHelper(site_config, cookie, proxies=proxies, user_agent=user_agent)
        elif parser == 'RARBG':
            return Rarbg(site_config, proxies=proxies)
