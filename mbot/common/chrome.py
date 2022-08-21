import logging

from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class Chrome:
    driver = None

    def __init__(self, executable_path=None):
        chrome_options = Options()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('blink-settings=imagesEnabled=false')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36")
        self.chrome_options = chrome_options
        self.executable_path = executable_path

    def get_driver(self):
        if self.driver:
            return self.driver
        if self.executable_path:
            driver = webdriver.Chrome(self.executable_path,
                                      options=self.chrome_options)
        else:
            driver = webdriver.Chrome(options=self.chrome_options)
        self.driver = driver
        return driver

    @staticmethod
    def cookies_to_dict(cookiestr, domain):
        cookie_arr = cookiestr.split(';')
        arr = []
        for c in cookie_arr:
            c = c.strip()
            if c == '':
                continue
            pair = c.split('=')
            arr.append({
                'name': pair[0],
                'value': pair[1],
                # 'domain': domain
            })
        return arr

    def quit(self):
        if self.driver:
            self.driver.quit()

    def set_cookie(self, driver, cookies, hostname):
        if isinstance(cookies, str):
            cookies = self.cookies_to_dict(cookies, hostname)
        elif isinstance(cookies, dict):
            tmp = []
            for key in cookies.keys():
                tmp.append({'name': key, 'value': cookies[key]})
            cookies = tmp
        for ck in cookies:
            driver.add_cookie(ck)

    def get(self, url, cookies=None):
        driver = self.get_driver()
        if cookies:
            url_parsed = urlparse(url)
            # 先访问一次，才能添加cookie
            driver.get('%s://%s' % (url_parsed.scheme, url_parsed.hostname))
            self.set_cookie(driver, cookies, url_parsed.hostname)
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        driver.get(url)
        try:
            el = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'img.pro_free')))
        except Exception as e:
            raise e
        html_source = driver.page_source
        return html_source
