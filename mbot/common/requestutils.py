from http.cookies import SimpleCookie


class RequestUtils:
    @staticmethod
    def cookie_str_to_simple_cookie(cookie_str: str):
        if not cookie_str:
            return
        cookie = SimpleCookie(cookie_str)
        cookies = {}
        for key, morsel in cookie.items():
            cookies[key] = morsel.value
        return cookies

    @staticmethod
    def get_etag(headers):
        etag = headers.get('etag')
        if not etag:
            return
        if etag.startswith('W/'):
            etag = etag[3:-1]
        return etag