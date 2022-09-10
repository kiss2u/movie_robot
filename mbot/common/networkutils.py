import os

import dns


class NetworkUtils:
    """网络工具类"""

    @staticmethod
    def resolver_dns_first_ip(domain):
        """
        解析域名响应的第一个IP地址
        :param domain:
        :return:
        """
        if os.environ.get('SERVER_URL'):
            return os.environ.get('SERVER_URL')
        my_resolver = dns.resolver.Resolver()
        my_resolver.nameservers = ['119.29.29.29']
        A = my_resolver.resolve(domain)
        ip = None
        for i in A.response.answer:
            try:
                ip = list(i.items.keys())[0].address
                if not ip:
                    break
            except:
                pass
        if not ip:
            raise RuntimeWarning(f'无法解析: {domain} 请检查你的容器是否可以上网，DNS解析是否正常工作！')
        return ip
