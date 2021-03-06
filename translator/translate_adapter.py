import re
import os
import sys
import json
import random
from loguru import logger
import requests
import traceback

from threading import local
from functools import partial
from collections import defaultdict
from abc import ABC, abstractmethod

from . import sites
from msgacomm import retry_wrapper

__all__ = ["TranslateAdapter"]


class TranslateAdapter(ABC):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) '
                      'AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/41.0.2272.76 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application'
                  '/xml;q=0.9,*/*;q=0.8',
        "Accept-Language": "en-US,en;q=0.5",
    }
    local = local()

    def __init__(self):
        self.proxy = {}
        self.load(sites)

    @property
    @abstractmethod
    def web_site(self):
        pass

    @property
    @abstractmethod
    def translate_timeout(self):
        pass

    @property
    @abstractmethod
    def retry_times(self):
        pass

    def __enter__(self):
        self.session = requests.Session()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def set_logger(self, logger=None):
        if not logger:
            self.logger = logging.getLogger()
            self.logger.setLevel(20)
            self.logger.addHandler(logging.StreamHandler(sys.stdout))
        else:
            self.logger = logger
            # self.name = logger.name

    def load(self, module_str):
        if isinstance(module_str, str):
            sys.path.insert(0, os.getcwd())
            model = __import__(module_str, fromlist=module_str.split(".")[-1])
        else:
            model = module_str

        for k in dir(model):
            v = getattr(model, k)
            if hasattr(v, "__call__"):
                self.__dict__[k] = partial(v, self)

    @abstractmethod
    def proxy_choice(self):
        pass

    def trans_error_handler(self, func_name, retry_time, e, *args, **kwargs):
        """
        error_handler????????????
        :param func_name: ?????????????????????
        :param retry_time: ?????????????????????
        :param e: ?????????????????????
        :param args: ?????????????????????
        :param kwargs: ?????????????????????
        :return: ?????????True???????????????????????????????????????
        """
        self.logger.debug("Error in %s for retry %s times. Error: %s" % (
            func_name, retry_time, e))
        proxies = self.proxy_choice()
        if proxies:
            args[1].update(proxies)

    def translate(self, src):
        """
        ???????????????
        :param src: ???
        :return: ??????
        """
        try:
            # ?????????????????????????????????????????????????????????????????????????????????
            pattern = re.compile(r"(?:^|(?<=>))([\s\S]*?)(?:(?=<)|$)")
            ls = re.findall(pattern, src.replace("\n", ""))
            src_data = "\n".join(x.strip("\t ") for x in ls if x.strip())
            if src_data.strip():
                # ????????????%???????????????
                src_escape = src.replace("%", "%%")
                # ????????????????????????????????????????????????`%s`???
                #  ???????????????????????????????????????????????????????????????
                src_template = re.sub(
                    pattern,
                    lambda x: "%s" if x.group(1).strip() else "", src_escape)
                return retry_wrapper(
                    self.retry_times,
                    error_handler=self.trans_error_handler)(
                    self._translate)(
                    src_data, self.proxy or self.proxy_choice()
                              or self.proxy, src_template)
        except Exception:
            self.logger.error(
                "Error in translate, finally, we could not get "
                "the translate result. src: %s, Error:  %s" % (
                    src, traceback.format_exc()))
        return src

    def _translate(self, src, proxies, src_template):
        web_site = random.choice(self.web_site).strip()
        acq = globals().get("%sAcquirer" % web_site.capitalize())
        if acq:
            if not getattr(self.local, "acquirers", None):
                self.local.acquirers = dict()
            if not getattr(self.local, "proxies_cookies", None):
                self.local.proxies_cookies = defaultdict(dict)
            if web_site not in self.local.acquirers:
                self.local.acquirers[web_site] = acq(
                    self.session, self.headers, proxies)
            self.local.acquirers[web_site].enrich(
                self.local.proxies_cookies.setdefault(
                    json.dumps(proxies), dict()))
            return getattr(self, web_site)(
                src, proxies, src_template, self.local.acquirers[web_site])
        else:
            return getattr(self, web_site)(src, proxies, src_template)
