import random
import requests
from typing import Any, Dict


class Request:
    """
    请求类，用于封装 HTTP 请求并提供相关功能。
    """

    __REQUEST_ATTRS__ = {
        "params",
        "headers",
        "cookies",
        "data",
        "json",
        "files",
        "auth",
        "timeout",
        "proxies",
        "hooks",
        "stream",
        "verify",
        "cert",
        "allow_redirects",
    }

    def __init__(
        self,
        url: str,
        seed: Any,
        random_ua: bool = True,
        check_status_code: bool = True,
        **kwargs,
    ):
        """
        初始化请求对象。
        :param url: 请求的 URL。
        :param seed: 种子对象或标识符。
        :param random_ua: 是否使用随机 User-Agent，默认为 True。
        :param check_status_code: 是否检查响应状态码，默认为 True。
        :param kwargs: 其他扩展参数。
        """
        self.url = url
        self.seed = seed
        self.check_status_code = check_status_code
        self.request_setting: Dict[str, Any] = {}

        for key, value in kwargs.items():
            if key in self.__class__.__REQUEST_ATTRS__:
                self.request_setting[key] = value
            else:
                setattr(self, key, value)

        self.method = getattr(self, "method", None) or (
            "POST" if self.request_setting.get("data") or self.request_setting.get("json") else "GET"
        )

        if random_ua:
            self._build_header()

    @property
    def _random_ua(self) -> str:
        v1 = random.randint(4, 15)
        v2 = random.randint(3, 11)
        v3 = random.randint(1, 16)
        v4 = random.randint(533, 605)
        v5 = random.randint(1000, 6000)
        v6 = random.randint(10, 80)
        return (f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{v1}_{v2}) "
                f"AppleWebKit/{v4}.{v3} (KHTML, like Gecko) "
                f"Chrome/105.0.0.0 Safari/{v4}.{v3} Edg/105.0.{v5}.{v6}")

    def _build_header(self):
        headers = self.request_setting.setdefault("headers", {})
        if not headers.get("user-agent"):
            headers["user-agent"] = self._random_ua

    def download(self) -> requests.Response:
        response = requests.request(self.method, self.url, **self.request_setting)
        if self.check_status_code:
            response.raise_for_status()
        return response

    @property
    def to_dict(self) -> Dict[str, Any]:
        excluded_keys = {"url", "seed", "check_status_code", "request_setting"}
        return {k: v for k, v in self.__dict__.items() if k not in excluded_keys}