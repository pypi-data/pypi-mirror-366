import os
import sys
from uuid import uuid4
import atexit
import platform

from multipledispatch import dispatch
from loguru._logger import Logger, Core
from contextvars import ContextVar

_trace_id: ContextVar[str] = ContextVar('x_trace_id', default="")  # 任务ID


class TraceID:
    """全链路追踪ID"""

    @staticmethod
    def set_trace_id(trace_id: str) -> ContextVar[str]:
        """设置全链路追踪ID
        Returns:
            ContextVar[str]: trace_id
        """
        _trace_id.set(trace_id)
        return _trace_id

    @staticmethod
    def get_trace_id() -> str:
        """获取全链路追踪ID
        Returns:
            str: trace_id
        """
        trace_id = _trace_id.get()
        if not trace_id:
            trace_id = str(uuid4()) + "-0000"
        return trace_id


def _logger_filter(record):
    record['trace_msg'] = f"[trace_id:{TraceID.get_trace_id()}]"
    return record['trace_msg']


loguru_logger = Logger(core=Core(),
                       exception=None,
                       depth=0,
                       record=False,
                       lazy=False,
                       colors=False,
                       raw=False,
                       capture=True,
                       patchers=[],
                       extra={}
                       )
atexit.register(loguru_logger.remove)

os_name = platform.system()

if os_name == "Darwin":
    colorize = True
else:
    colorize = False

log_level = os.getenv("RT_LOG_LEVEL") or "INFO"
if log_level not in ["OFF", "NONE"]:
    loguru_logger.add(sys.stdout,
                      format="<green><b>{time:YYYY-MM-DD HH:mm:ss.SSS}</b></green> <red>|</red> {level:<8} <red>|</red> "
                             "<yellow>{trace_msg}</yellow><blue><red>:</red>{name}<red>:</red>{function}<red>:</red>{line}"
                             "</blue> <red>-</red> {message}",
                      colorize=colorize,
                      filter=_logger_filter,
                      enqueue=True,
                      backtrace=True,
                      level=log_level
                      )
    loguru_logger.info(f"{os_name} realtime logger init success")
else:
    loguru_logger.remove()


class RealtimeLogger:
    PREFIX = "-*-JUHE-*- "

    @classmethod
    def info(cls, __message: str):
        loguru_logger.info(cls.PREFIX + str(__message))

    @dispatch(str, Exception)
    def error(self, __message: str, error: Exception):
        loguru_logger.exception(self.PREFIX + str(__message), error)

    @dispatch(str)
    def error(self, __message: str):
        loguru_logger.error(self.PREFIX + str(__message))

    @dispatch(Exception)
    def error(self, error: Exception):
        loguru_logger.error(self.PREFIX + str(error))

    @dispatch(str, Exception)
    def exception(self, __message: str, error: Exception):
        loguru_logger.exception(self.PREFIX + str(__message), error)

    @dispatch(str)
    def exception(self, __message: str):
        loguru_logger.error(self.PREFIX + str(__message))

    @dispatch(Exception)
    def exception(self, error: Exception):
        loguru_logger.exception(self.PREFIX, error)

    def log(self, __level, __message):
        loguru_logger.log(__level, self.PREFIX + str(__message))


logger = RealtimeLogger()
