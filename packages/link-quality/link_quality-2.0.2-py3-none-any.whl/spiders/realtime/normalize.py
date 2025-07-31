import json
import socket
import string
import sys
import time
from datetime import timedelta
from enum import Enum
from html import unescape
from typing import (
    Callable,
    List,
    Optional,
    Tuple,
    Union,
    cast,
)
from urllib.parse import urlparse, urlunparse, ParseResult, quote, quote_plus, unquote_plus, \
    _coerce_args
import redis
from tenacity import stop_after_attempt, retry_if_exception_type, retry, wait_exponential
from tldextract import tldextract
from threading import Thread, Event

from spiders.realtime.link_filter import LinkFilter, Result
from spiders.realtime.rt_logger import logger

_ASCII_TAB_OR_NEWLINE = "\t\n\r"
_ASCII_WHITESPACE = "\t\n\x0c\r "
_C0_CONTROL = "".join(chr(n) for n in range(32))
_C0_CONTROL_OR_SPACE = _C0_CONTROL + " "
_ASCII_DIGIT = string.digits
_ASCII_HEX_DIGIT = string.hexdigits
_ASCII_ALPHA = string.ascii_letters
_ASCII_ALPHANUMERIC = string.ascii_letters + string.digits

_ASCII_TAB_OR_NEWLINE_TRANSLATION_TABLE = {
    ord(char): None for char in _ASCII_TAB_OR_NEWLINE
}

# constants from RFC 3986, Section 2.2 and 2.3
RFC3986_GEN_DELIMS = b":/?#[]@"
RFC3986_SUB_DELIMS = b"!$&'()*+,;="
RFC3986_RESERVED = RFC3986_GEN_DELIMS + RFC3986_SUB_DELIMS
RFC3986_UNRESERVED = (string.ascii_letters + string.digits + "-._~").encode("ascii")
EXTRA_SAFE_CHARS = b"|"  # see https://github.com/scrapy/w3lib/pull/25

RFC3986_USERINFO_SAFE_CHARS = RFC3986_UNRESERVED + RFC3986_SUB_DELIMS + b":"
_safe_chars = RFC3986_RESERVED + RFC3986_UNRESERVED + EXTRA_SAFE_CHARS + b"%"
_path_safe_chars = _safe_chars.replace(b"#", b"")

StrOrBytes = Union[str, bytes]


def _strip(url: str) -> str:
    return url.strip(_C0_CONTROL_OR_SPACE).translate(
        _ASCII_TAB_OR_NEWLINE_TRANSLATION_TABLE
    )


def _safe_ParseResult(
        parts: ParseResult, encoding: str = "utf8", path_encoding: str = "utf8"
) -> Tuple[str, str, str, str, str, str]:
    # IDNA encoding can fail for too long labels (>63 characters)
    # or missing labels (e.g. http://.example.com)
    try:
        netloc = parts.netloc.encode("idna").decode()
    except UnicodeError:
        netloc = parts.netloc

    return (
        parts.scheme,
        netloc,
        quote(parts.path.encode(path_encoding), _path_safe_chars),
        quote(parts.params.encode(path_encoding), _safe_chars),
        quote(parts.query.encode(encoding), _safe_chars),
        quote(parts.fragment.encode(encoding), _safe_chars),
    )


def parse_url(
        url: Union[StrOrBytes, ParseResult], encoding: Optional[str] = None
) -> ParseResult:
    """URL 解析"""
    if isinstance(url, ParseResult):
        return url
    return urlparse(to_unicode(url, encoding))


def to_unicode(
        text: StrOrBytes, encoding: Optional[str] = None, errors: str = "strict"
) -> str:
    """如果是 str，则直接返回，如果是 bytes，则解码为 str"""
    if isinstance(text, str):
        return text
    if not isinstance(text, (bytes, str)):
        raise TypeError(
            f"to_unicode must receive bytes or str, got {type(text).__name__}"
        )
    if encoding is None:
        encoding = "utf-8"
    return text.decode(encoding, errors)


def parse_qsl_to_bytes(
        qs: str, keep_blank_values: bool = False
) -> List[Tuple[bytes, bytes]]:
    """
    query 解析，返回一个列表包含 name 和 value 对的字节形式。
    qs：百分号编码的 query string
    keep_blank_values: 是否保留 value 为空的 key，默认不保留
    """
    # 这个函数和parse_qsl一致，除了 unquote(s, encoding, errors) 调用被替换为 unquote_to_bytes(s)
    coerce_args = cast(Callable[..., Tuple[str, Callable[..., bytes]]], _coerce_args)
    qs, _coerce_result = coerce_args(qs)
    pairs = [s2 for s1 in qs.split("&") for s2 in s1.split(";")]
    r = []
    for name_value in pairs:
        if not name_value:
            continue
        nv = name_value.split("=", 1)
        if len(nv) != 2:
            # Handle case of a control-name with no equal sign
            if keep_blank_values:
                nv.append("")
            else:
                continue
        if len(nv[1]) or keep_blank_values:
            name: StrOrBytes = nv[0].replace("+", " ")
            name = unquote_to_bytes(name)
            name = _coerce_result(name)
            value: StrOrBytes = nv[1].replace("+", " ")
            value = unquote_to_bytes(value)
            value = _coerce_result(value)
            r.append((name, value))
    return r


def _unquotepath(path: str) -> bytes:
    # 确保 / 和 ? 不要被解码
    for reserved in ("2f", "2F", "3f", "3F"):
        path = path.replace("%" + reserved, "%25" + reserved.upper())

    # 标准库中的 unquote 函数对非 utf-8 的百分号转义字符不起作用，这些字符会丢失。例如'%a3' 变成 'REPLACEMENT CHARACTER' (U+FFFD)。
    # 而 unquote_to_bytes() 返回原始字节，而不是尝试解码为字符串。
    return unquote_to_bytes(path)


_hexdig = '0123456789ABCDEFabcdef'
_hextobyte = None


def unquote_to_bytes(s):
    """unquote_to_bytes('abc%20def') -> b'abc def'."""
    # s 是被 utf-8编码的字符串，不应该包含未编码的非 ascii 码字符
    if not s:
        # Is it a string-like object?
        _ = s.split
        return b''
    if isinstance(s, str):
        s = s.encode('utf-8')
    bits = s.split(b'%')
    if len(bits) == 1:
        return s
    res = [bits[0]]
    append = res.append
    # 延迟创建映射表
    global _hextobyte
    if _hextobyte is None:
        _hextobyte = {(a + b).encode(): bytes.fromhex(a + b)
                      for a in _hexdig for b in _hexdig}
    for item in bits[1:]:
        try:
            append(_hextobyte[item[:2]])
            append(item[2:])
        except KeyError:
            append(b'%')
            append(item)
    return b''.join(res)


def unescape_url(url):
    """实体字符解码"""
    previous_url, current_url = None, url

    while previous_url != current_url:
        previous_url = current_url
        current_url = unescape(current_url)
    return current_url


def decode_url(url):
    """url decode"""
    previous_url, current_url = None, url

    while previous_url != current_url:
        previous_url = current_url
        current_url = unquote_plus(current_url)

    return current_url


def decode(url):
    return unescape_url(decode_url(url))


class ReturnType(Enum):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    ## 规则匹配成功
    normal = (0, "normal")

    no_rules = (0, "no corresponding rules")  # 没有域名对应规则

    ## 异常
    url_parse_error = (1, "url parse error")  # URL 解析异常
    rule_not_match = (2, "rule not match")  # 规则引擎匹配失败
    normalize_error = (3, "normalize error")  # 归一化处理异常
    url_is_invalid = (4, "url is invalid")  # URL 非法


class NormalizeResult(Result):
    def __init__(self, hit: bool, msg: str, code: int, rule: Union[str, dict], extra: dict, url, normalize_url):
        super().__init__(hit=hit, msg=msg, code=code, rule=rule, extra=extra)
        self.url = url
        self.normalize_url = normalize_url


class Normalizer:
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
        self.link_filter = LinkFilter(rds_host=rds_host, rds_port=rds_port, rds_password=rds_password,
                                      use_local_cache=False)
        self.normalize_table_key = "normalize:rules"
        if use_local_cache:
            self.cache_table = {}
            self.event = Event()
            self.runner = Thread(target=self.sync_rules, daemon=True, args=(self.event,))
            self.runner.start()
            while not self.event.is_set():
                time.sleep(1)

    @retry(stop=(stop_after_attempt(3)),
           wait=wait_exponential(max=60),
           retry=retry_if_exception_type(Exception),
           after=lambda state: logger.error(f"{state.fn.__name__}:{str(state)}"),
           retry_error_callback=lambda state: 0
           )
    def pull_data(self):
        self.cache_table = self.client.hgetall(self.normalize_table_key)
        return len(self.cache_table)

    @retry(stop=(stop_after_attempt(3)),
           wait=wait_exponential(max=60),
           retry=retry_if_exception_type(Exception),
           after=lambda state: logger.error(f"{state.fn.__name__}:{str(state)}"),
           retry_error_callback=lambda state: None
           )
    def send_heartbeat(self, cnt: int, expire: int):
        self.client.setex(f"normalize:heartbeat:{self.hostname}", timedelta(seconds=expire), cnt)

    def sync_rules(self, event: Event):
        while True:
            update_cnt = self.pull_data()
            self.send_heartbeat(cnt=update_cnt, expire=self.refresh_interval)
            logger.info(f"normalize sync rules, update_cnt: {update_cnt}")
            event.set()
            time.sleep(self.refresh_interval)

    def get(self, domain):
        return self.cache_table.get(domain)

    @staticmethod
    def urlencode(query, doseq=False, safe='', encoding=None, errors=None,
                  quote_via=quote_plus):
        """
        query 编码，同 urllib.parse.urlencode。唯一的改动是当 query items value 值为空时不保留“=”。
        如果 value 是序列类型并且 doseq 为 True，每个序列元素都转换为单独的参数，并且按照输入的顺序。
        如果 query arg 是两个元素的元组序列，输出的参数顺序与输入的参数顺序一致。
        e.g. 输入{'a': ['1', '3', '2'], "b": '4'} 并且 doseq 为 True 输出 a=1&a=3&a=2&b=4，如果 doseq 为 False 输出 a=%5B%271%27%2C+%273%27%2C+%272%27%5D&b=4
        e.g. 输入[('a', 1), ('b', 2)] 输出 a=1&b=2。
        注意：quote_via 参数使用 quote_plus 空格会被编码为'+' 而不是 '%20'，前者更适合查询参数编码，后者更适合路径编码。
        """
        if hasattr(query, "items"):
            query = query.items()
        else:
            # It's a bother at times that strings and string-like objects are
            # sequences.
            try:
                # non-sequence items should not work with len()
                # non-empty strings will fail this
                if len(query) and not isinstance(query[0], tuple):
                    raise TypeError
                # Zero-length sequences of all types will get here and succeed,
                # but that's a minor nit.  Since the original implementation
                # allowed empty dicts that type of behavior probably should be
                # preserved for consistency
            except TypeError:
                ty, va, tb = sys.exc_info()
                raise TypeError("not a valid non-string sequence "
                                "or mapping object").with_traceback(tb)

        l = []
        if not doseq:
            for k, v in query:
                if isinstance(k, bytes):
                    k = quote_via(k, safe)
                else:
                    k = quote_via(str(k), safe, encoding, errors)

                if isinstance(v, bytes):
                    v = quote_via(v, safe)
                else:
                    v = quote_via(str(v), safe, encoding, errors)
                if not v:
                    l.append(k)
                else:
                    l.append(k + '=' + v)
        else:
            for k, v in query:
                if isinstance(k, bytes):
                    k = quote_via(k, safe)
                else:
                    k = quote_via(str(k), safe, encoding, errors)

                if isinstance(v, bytes):
                    v = quote_via(v, safe)
                    if not v:
                        l.append(v)
                    else:
                        l.append(k + '=' + v)
                elif isinstance(v, str):
                    v = quote_via(v, safe, encoding, errors)
                    if not v:
                        l.append(k)
                    else:
                        l.append(k + '=' + v)
                else:
                    try:
                        # Is this a sufficient test for sequence-ness?
                        x = len(v)
                    except TypeError:
                        # not a sequence
                        v = quote_via(str(v), safe, encoding, errors)
                        if not v:
                            l.append(k)
                        else:
                            l.append(k + '=' + v)
                    else:
                        # loop over the sequence
                        for elt in v:
                            if isinstance(elt, bytes):
                                elt = quote_via(elt, safe)
                            else:
                                elt = quote_via(str(elt), safe, encoding, errors)
                            if not elt:
                                l.append(k)
                            else:
                                l.append(k + '=' + elt)
        return '&'.join(l)

    def get_manual_rule(self, url, domain) -> tuple[dict, dict]:
        """获取人工规则。注意当有多条规则并且多条 link filter 规则通过，最终规则会按照配置时间排序合并，如果有冲突后配置会覆盖先配置的。"""
        mirror = None
        keys = {}
        extra = {}
        rules = self.get(domain)
        if not rules:
            return {"keys": keys, "mirror": mirror}, extra
        rules = json.loads(rules)
        sorted_rules = sorted(rules, key=lambda x: x["extra"]["time"])

        for rule in sorted_rules:
            link_filter_result = self.link_filter.manual_evaluate(url, {domain: [rule]}, serialize=False)
            if link_filter_result.hit:
                keys.update(rule["data"]["keys"])
                extra = rule["extra"]
                if rule["data"].get("mirror") is not None:
                    mirror = rule["data"]["mirror"]
        return {"keys": keys, "mirror": mirror}, extra

    def canonicalize_url(self,
                         url: Union[StrOrBytes, ParseResult],
                         keep_blank_values: bool = True,
                         keep_fragments: bool = False,
                         encoding: Optional[str] = None,
                         data: Optional[dict] = None
                         ):
        """
        safe encode
        参数排序
        所有 query 中空格编码为 '+'
        百分号编码统一为 upper case
        keep_blank_values选择是否移除无效参数
        移除锚点
        移除末尾空端口
        添加缺失 path
        非 ascii 域名归一化为 punycode 编码
        """
        extra = dict()

        try:
            # 如果提供的 encoding 与 url 中所有字符不兼容，那么退回到utf-8编码
            if isinstance(url, str):
                url = _strip(url)
            try:
                scheme, netloc, path, params, query, fragment = _safe_ParseResult(
                    parse_url(url), encoding=encoding or "utf8"
                )
            except UnicodeEncodeError:
                scheme, netloc, path, params, query, fragment = _safe_ParseResult(
                    parse_url(url), encoding="utf8"
                )

            # 特殊处理 @玄瑾
            if netloc == "www.sohu.com" and path.startswith("/a"):
                path = path.rstrip('/')

            # 基础验证
            if not all([scheme, netloc]):
                return url, data, extra, ReturnType.url_is_invalid

            domain = tldextract.extract(netloc).registered_domain

            # query 实体字符解码
            query = decode(query)
            # 解码 query 为 raw bytes 然后排序、编码
            keyvals = parse_qsl_to_bytes(query, keep_blank_values)

            keyvals = list(set(keyvals))
            keyvals.sort()

            # 查询归一化人工规则
            if not data:
                data, extra = self.get_manual_rule(url, domain)
            if data:
                manual_keys = data.get("keys")
                manual_mirror = data.get("mirror")
                # manual_scheme = data.get("scheme")

                black_keys = {key for key in manual_keys if manual_keys[key] == 1}
                removed_pairs = [(key, value) for key, value in keyvals if key.decode() in black_keys]
                for pair in removed_pairs:
                    keyvals.remove(pair)

                # scheme = manual_scheme or scheme
                netloc = manual_mirror or netloc

            query = self.urlencode(keyvals)

            # 解码 path 为 raw bytes 然后编码
            uqp = _unquotepath(path)
            path = quote(uqp, _path_safe_chars) or "/"

            fragment = "" if not keep_fragments else fragment

            # host 统一为小写，而不改变 user info
            netloc_parts = netloc.split("@")
            netloc_parts[-1] = netloc_parts[-1].lower().rstrip(":")
            netloc = "@".join(netloc_parts)

            # 每个 part 都应该被安全编码过了
            return urlunparse((scheme, netloc, path, "", query, fragment)), data, extra, ReturnType.normal
        except Exception as exc:
            logger.exception("url normalize error", exc)
            return url, data, extra, ReturnType.normalize_error

    def manual_evaluate(self, url, rules=None, data=None):
        """
        归一化手动传入规则。如果有链接匹配规则先判断是否匹配，匹配后再判断再做归一化。如果 mirror 和 scheme 存在则替换为相应的值。
        @param url: 链接
        @param rules: 链接匹配规则
        @param data 归一化规则
        """
        # 判断是否命中前置规则（规则引擎）
        link_filter_result: Result = self.link_filter.manual_evaluate(url, rules, serialize=False)
        if link_filter_result.hit:
            new_url, rule, extra, return_type = self.canonicalize_url(url, keep_blank_values=True, data=data)
        else:
            new_url, rule, extra, return_type = self.canonicalize_url(url, keep_blank_values=True)
        return Result(hit=url != new_url, msg=return_type.msg, code=return_type.code, rule=rules,
                      extra={"ori_url": url, "new_url": new_url, "data": data}).to_dict()

    def evaluate(self, url):
        """归一化接口"""
        new_url, rule, extra, return_type = self.canonicalize_url(url)
        return NormalizeResult(hit=url != new_url, msg=return_type.msg, code=return_type.code, rule=rule,
                               extra=extra, url=url, normalize_url=new_url).to_dict()
