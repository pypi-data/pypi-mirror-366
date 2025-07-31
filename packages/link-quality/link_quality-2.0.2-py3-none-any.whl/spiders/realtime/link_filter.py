import socket
import time
from datetime import timedelta
from enum import Enum
import base64
import json
from functools import partial
from threading import Thread, Event
from typing import Union
from urllib.parse import urlparse

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from tldextract import tldextract
import redis

from spiders.realtime.rt_logger import logger, TraceID


class Operator(Enum):
    """
    操作符
    """
    equal = "equal"
    gt = "gt"
    lt = "lt"
    contains = "contains"
    i = "in"
    endswith = "endswith"
    startswith = "startswith"
    split = "split"
    index = "index"
    lower = "lower"  # 新增
    len = "len"
    code = "code"


file_suffix = [".3gp", ".aac", ".amr", ".app", ".avi", ".cab",
               ".doc", ".docx", ".exe", ".gbc", ".hme", ".jad",
               ".jar", ".m4a", ".mbm", ".mid", ".mjp", ".mmf", ".mp3",
               ".mp4", ".mpeg", ".mpkg", ".mrp", ".mtf", ".nes",
               ".nth", ".pdf", ".prc", ".pxl", ".rar",
               ".rm", ".sdt", ".sis", ".sisx", ".swf", ".thm", ".tsk", ".utz",
               ".wav", ".wma", ".wmv", ".zip", ".css", ".js",
               ".bmp", ".jpg", ".png", ".tif", ".gif", ".pcx", ".tga",
               ".exif", ".fpx", ".svg", ".psd", ".cdr", ".pcd", ".dxf",
               ".ufo", ".eps", ".ai", ".raw", ".wmf", ".webp",
               ".mov", ".asf", ".mkv", ".flv", ".f4v", ".xlsx", ".xls",
               ".iso", ".7z", ".gz", ".tgz", ".bz2", ".xz", ".z",
               ".exe", ".msi", ".apk", ".ipa", ".tmp", ".mdf",
               ".txt", ".rtf", ".ppt", ".pptx", ".bin", ".csv", ".jpeg"]

redirect_keyword = ["signin", "login", "register", "redirect", "registration", "authorize", "logout", "signup",
                    "sign-up", "sign-in"]
global_conf = {
    "*": [
        {
            "rule": {
                "path":
                    [[Operator.split.value, "/"], [Operator.index.value, -1],
                     [Operator.endswith.value, file_suffix + [suffix.upper() for suffix in file_suffix]]
                     ]
            },
            "extra": {"reason": ["manual"], "owner": ["421966"], "time": ["2024-12-20"], "md5": "xxxxxxxxx"}
        },
        {
            "rule": {
                "path":
                    [[Operator.split.value, "/"], [Operator.index.value, -1], [Operator.split.value, "."],
                     [Operator.index.value, 0], [Operator.lower.value],
                     [Operator.i.value, redirect_keyword + [keyword.upper() for keyword in redirect_keyword]]]

            },
            "extra": {"reason": ["manual"], "owner": ["421966"], "time": ["2024-12-20"], "md5": "yyyyyyyyyy"}
        },
        {
            "rule": {
                "url":
                    [[Operator.len.value], [Operator.gt.value, 2048]]

            },
            "extra": {"reason": ["manual"], "owner": ["421966"], "time": ["2024-03-12"]}
        }
    ]
}


class ReturnType(Enum):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    normal = (0, "normal")  # 正常 url
    black_host = (1, "hit black host")  # black host
    black_domain = (2, "hit black domain")  # black_domain
    white_host = (0, "hit white host")  # white_host
    white_domain = (0, "hit white domain")  # white_domain
    super_white_domain = (0, "hit super white domain")  # super_white_domain
    black_prefix = (3, "hit black prefix")  # black_prefix
    black_rule = (4, "hit black rule")  # black_rule

    url_parse_error = (100, "url parse error")  # URL 解析异常（解析失败认为 URL 不合法应该删除 #2024-12-25）
    filter_error = (0, "filter error")  # link-filter 处理异常（处理异常暂时不删除 #2024-12-25）


class Result:
    def __init__(self, hit: bool, msg: str, code: int, rule: Union[str, dict], extra: dict):
        """
        响应结果类型。hit 决定是否删除，code 提示规则类型。前期需要保持一致，也就是 hit=False 时，code 一定等于 0。
        后期 hit 和 code 可以不一致，比如 hit=False 时，code 可以不等于 0，表明虽然暂时不删除，但是需要指明因为哪个规则不删除。

        :param hit: 决定是否删除。True：删除、 False 不删除
        :param msg: 命中类型提示信息
        :param code: 命中类型
        :param rule: 命中规则
        :param extra: 返回额外信息：{"reason": "规则上线原因", "owner": "规则所属人", "time": "规则上线时间"}
        """
        self.hit = hit
        self.msg = msg
        self.type = code
        self.rule = rule
        self.extra = extra
        self.trace_id = TraceID.get_trace_id()

    def __str__(self):
        return json.dumps(self.__dict__)

    __repr__ = __str__

    to_dict = lambda self: self.__dict__


class LinkFilter:
    # 依赖规则表 1. odps 2. redis
    resource_link_filter_black_rule_name = "resource_link_filter_black_rule"
    resource_link_filter_black_prefix_name = "resource_link_filter_black_prefix"
    resource_link_filter_super_white_domain_name = "resource_link_filter_super_white_domain"
    resource_link_filter_black_host_name = "resource_link_filter_black_host"
    resource_link_filter_white_host_name = "resource_link_filter_white_host"
    resource_link_filter_white_domain_name = "resource_link_filter_white_domain"
    resource_link_filter_black_domain_name = "resource_link_filter_black_domain"

    def get(self, table_name, key):
        result = self.client.hget(table_name, key)
        if result:
            return json.loads(result)
        return dict()

    def get_local(self, key):
        """因为实时服务因为质量问题不统一而使用不了离线规则，所以只需要同步人工规则"""
        result = self.cache_table.get(key)
        if result:
            return json.loads(result)
        return dict()

    def __init__(self, rds_host=None, rds_port=None, rds_password=None, use_local_cache=True):
        """
        :param rds_host: redis host
        :param rds_port: redis port
        :param rds_password: redis password
        :param use_local_cache: 是否使用本地缓存。默认开启
        """
        self.hostname = socket.gethostname()
        self.refresh_interval = 300
        self.client = redis.Redis(
            host=rds_host,
            port=rds_port,
            password=rds_password,
            db=4,
            max_connections=300,
            decode_responses=True
        )
        self.super_white_domain = partial(self.get, self.resource_link_filter_super_white_domain_name)  # 超级白名单
        self.white_domain = partial(self.get, self.resource_link_filter_white_domain_name)  # 域名白名单
        self.black_domain = partial(self.get, self.resource_link_filter_black_domain_name)  # 域名黑名单
        self.white_host = partial(self.get, self.resource_link_filter_white_host_name)  # host 白名单
        self.black_host = partial(self.get, self.resource_link_filter_black_host_name)  # host 黑名单
        self.black_rule = partial(self.get, self.resource_link_filter_black_rule_name)  # 规则黑名单 domain:rule
        self.black_prefix = partial(self.get, self.resource_link_filter_black_prefix_name)  # 前缀黑名单 host:prefix
        if use_local_cache:
            # 开关用于决定是否加载人工规则。默认开启
            self.cache_table = {}
            self.event = Event()
            Thread(target=self.sync_rules, daemon=True, args=(self.event,)).start()
            while not self.event.is_set():
                time.sleep(1)

    @retry(stop=(stop_after_attempt(3)),
           wait=wait_exponential(max=60),
           retry=retry_if_exception_type(Exception),
           after=lambda state: logger.error(f"{state.fn.__name__}:{str(state)}"),
           retry_error_callback=lambda state: 0
           )
    def pull_data(self):
        self.cache_table = self.client.hgetall(self.resource_link_filter_black_rule_name)
        return len(self.cache_table)

    @retry(stop=(stop_after_attempt(3)),
           wait=wait_exponential(max=60),
           retry=retry_if_exception_type(Exception),
           after=lambda state: logger.error(f"{state.fn.__name__}:{str(state)}"),
           retry_error_callback=lambda state: None
           )
    def send_heartbeat(self, cnt: int, expire: int):
        self.client.setex(f"link-filter:heartbeat:{self.hostname}", timedelta(seconds=expire), cnt)

    def sync_rules(self, event: Event):
        while True:
            update_cnt = self.pull_data()
            self.send_heartbeat(cnt=update_cnt, expire=self.refresh_interval)
            logger.info(f"link-filter sync rules, update_cnt: {update_cnt}")
            event.set()
            time.sleep(self.refresh_interval)

    def manual_evaluate(self, url, rules, serialize=True) -> Union[Result, dict]:
        """
        @param url: 链接
        @param rules: 规则
        {
            "chaxunmao.com": [
                {
                    "extra": {},
                    "rule": {
                        "path": [
                            ["split", "/"],
                            ["index", -1],
                            ["split", "-"],
                            ["len"],
                            ["gt", 5]
                        ]
                    }
                }
            ]
        }
        @param serialize: 是否返回 json 序列化字符串
        """
        result = None
        try:
            domain, host, path, params = self.parse_url(url)
        except Exception as exc:
            # link-filter 内部逻辑错误
            result = Result(hit=False, msg=str(exc), code=ReturnType.filter_error.code, rule="", extra={})
        else:
            is_hit, rule, extra = self.hit_black_rule(url, domain, host, path, params, rules)
            if is_hit:
                result = Result(hit=True, msg=ReturnType.black_rule.msg, code=ReturnType.black_rule.code,
                                rule=rule, extra=extra)
            else:
                # 所有规则均未命中并且没有报错
                result = Result(hit=False, msg=ReturnType.normal.msg, code=ReturnType.normal.code, rule="",
                                extra={})
        if result and serialize:
            return result.to_dict()
        return result

    def evaluate(self, url):
        """
        是否命中规则？命中了哪一个规则？规则责任人是谁？规则在什么时间配置的？
        :param url: 链接
        :return: 返回 json 结果
        """
        try:
            domain, host, path, params = self.parse_url(url)
        except Exception as exc:
            # URL 解析异常
            logger.exception(f"url parse error", exc)
            return Result(hit=True, msg=str(exc), code=ReturnType.url_parse_error.code, rule=url, extra={}).to_dict()
        else:
            try:
                # # 判断是否在超级白名单中
                # extra = self._in_super_white_domain(domain)
                # if extra:
                #     return Result(hit=False, msg=ReturnType.super_white_domain.msg,
                #                   code=ReturnType.super_white_domain.code, rule=domain, extra=extra).to_dict()

                # 判断是否命中人工规则
                is_hit, rule, extra = self.hit_black_rule(url, domain, host, path, params)
                if is_hit:
                    return Result(hit=True, msg=ReturnType.black_rule.msg, code=ReturnType.black_rule.code,
                                  rule=rule, extra=extra).to_dict()

                # # 判断是否命中 prefix 黑名单
                # is_hit, rule, extra = self.hit_black_prefix(url, host)
                # if is_hit:
                #     return Result(hit=True, msg=ReturnType.black_prefix.msg, code=ReturnType.black_prefix.code,
                #                   rule=rule, extra=extra).to_dict()
                #
                # # 判断是否命中 host 白名单
                # extra = self._in_white_host(host)
                # if extra:
                #     return Result(hit=False, msg=ReturnType.white_host.msg, code=ReturnType.white_host.code,
                #                   rule=host, extra=extra).to_dict()
                #
                # # 判断是否命中 host 黑名单
                # extra = self._in_black_host(host)
                # if extra:
                #     return Result(hit=True, msg=ReturnType.black_host.msg, code=ReturnType.black_host.code,
                #                   rule=host, extra=extra).to_dict()
                #
                # # 判断是否命中 domain 白名单
                # extra = self._in_white_domain(domain)
                # if extra:
                #     return Result(hit=False, msg=ReturnType.white_domain.msg, code=ReturnType.white_domain.code,
                #                   rule=domain, extra=extra).to_dict()
                #
                # # 判断是否命中 domain 黑名单
                # extra = self._in_black_domain(domain)
                # if extra:
                #     return Result(hit=True, msg=ReturnType.black_domain.msg, code=ReturnType.black_domain.code,
                #                   rule=domain, extra=extra).to_dict()
            except Exception as exc:
                # link-filter 内部逻辑错误
                logger.exception(f"link-filter internal error", exc)
                return Result(hit=False, msg=str(exc), code=ReturnType.filter_error.code, rule="", extra={}).to_dict()

            # 所有规则均未命中并且没有报错
            return Result(hit=False, msg=ReturnType.normal.msg, code=ReturnType.normal.code, rule="",
                          extra={}).to_dict()

    def hit_black_prefix(self, host, path, query):
        """path 左右都不带/，path 和 query 使用 ? 拼接。如果 path 为空并且 query 不为空那么以 ? 开头"""
        rest_part = f"{path.lstrip('/')}{'?' + query if query else ''}"
        rest_part_with_slash = f"{path.lstrip('/')}/{'?' + query if query else ''}"
        prefix_rule = self.black_prefix(host)
        if prefix_rule:
            for prefix_rule in prefix_rule:

                black_prefix = prefix_rule.get("rule")
                extra = prefix_rule.get("extra")

                if rest_part.startswith(black_prefix) or rest_part_with_slash.startswith(black_prefix):
                    return True, f"{black_prefix}", extra
        return False, "", ""

    def hit_black_rule(self, url, domain, host, path, params, rules=None):
        # 获取 domain 规则或者通配规则
        if rules:
            domain_rules = rules.get(domain) or rules.get("*")
        else:
            domain_rules: list = self.get_local(domain) or self.get_local("*")
            if not domain_rules:
                domain_rules = global_conf.get("*")
            else:
                domain_rules.extend(global_conf.get("*"))
        if domain_rules:
            for domain_rule in domain_rules:
                result = []
                rule = domain_rule.get("rule")
                extra = domain_rule.get("extra")

                url_rule = rule.get("url")
                host_rule = rule.get("host")
                path_rule = rule.get("path")
                params_rule = rule.get("params")

                # # 防止域名下面有规则，并且规则 key 配置错误（基本不可能），导致所有对应 rule 为空，会导致域名全量命中
                # assert any([url_rule, host_rule, path_rule, params_rule]), "rule is empty"

                rules = [("url", url, url_rule),
                         ("host", host, host_rule),
                         ("path", path, path_rule),
                         ("params", params, params_rule)
                         ]
                for name, part, part_rule in rules:
                    match = self.exec_rule(part, part_rule)
                    result.append(match)
                    if not match:
                        break
                if len(result) == len(rules) and all(result):
                    return True, rule, extra
        else:
            return False, "", {"msg": "no domain rules"}

        # 没有 domain 对应规则匹配失败，并返回没有匹配的原因
        return False, "", ""

    def _in_super_white_domain(self, domain):
        return self.super_white_domain(domain)

    def _in_black_host(self, host):
        return self.black_host(host)

    def _in_white_host(self, host):
        return self.white_host(host)

    def _in_black_domain(self, domain):
        return self.black_domain(domain)

    def _in_white_domain(self, domain):
        return self.white_domain(domain)

    @staticmethod
    def parse_url(url):
        parsed_url = urlparse(url)
        domain = tldextract.extract(url).registered_domain
        host = parsed_url.hostname
        path = parsed_url.path.strip("/")
        params = parsed_url.query
        return domain, host, path, params

    @staticmethod
    def exec_rule(part, rule: list):
        if not rule:
            return True
        result = part
        for r in rule:
            if r[0] == Operator.equal.value:
                result = result == r[1]
            elif r[0] == Operator.gt.value:
                result = result > r[1]
            elif r[0] == Operator.lt.value:
                result = result < r[1]
            elif r[0] == Operator.contains.value:
                result = r[1] in result
            elif r[0] == Operator.i.value:
                result = result in r[1]
            elif r[0] == Operator.endswith.value:
                if isinstance(r[1], list):
                    r[1] = tuple(r[1])
                result = result.endswith(r[1])
            elif r[0] == Operator.startswith.value:
                result = result.startswith(r[1])
            elif r[0] == Operator.split.value:
                result = result.split(r[1])
            elif r[0] == Operator.index.value:
                index = int(r[1])
                if index + 1 > len(result) and index != -1:
                    return False
                result = result[index]
            elif r[0] == Operator.len.value:
                result = len(result)
            elif r[0] == Operator.code.value:
                context = {}
                exec(base64.b64decode(r[1]).decode(), context)
                result = context["dynamic_function"](result)
            elif r[0] == Operator.lower.value:
                result = result.lower()
            else:
                raise RuntimeError(f"Unknown operator {r[0]}")
        return result
