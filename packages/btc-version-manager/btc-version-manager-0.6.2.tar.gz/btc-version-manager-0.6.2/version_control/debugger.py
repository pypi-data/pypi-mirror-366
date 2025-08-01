import logging
import time
from collections import OrderedDict
from functools import partial, wraps
from typing import Any, Callable, Optional, Type

from django.conf import settings
from django.db import connection, reset_queries

from version_control.utils import get_class_from_settings

logger = logging.getLogger(__name__)


def get_version_manager_debugger_class() -> Type["BaseDebugger"]:
    """
    Returns current version manager debugger class from the project settings or original "VersionManagerDebugger"
    """

    error_message = (
        'Не найден указанный в "settings" класс дебага менеджера версий. Используется стандартный - '
        '"VersionManagerDebugger"'
    )
    return get_class_from_settings("VERSION_MANAGER_DEBUGGER_CLASS", error_message, VersionManagerDebugger)


class BaseDebugger:
    """
    A base class for collecting debugging information
    """

    __INFO: OrderedDict = OrderedDict()
    HASH: Optional[str] = None

    __TOTAL_TIME: float = 0
    __TOTAL_QUERIES_COUNT: int = 0

    use_settings: str = ""
    show_report: bool = False

    # global
    log_in_runtime: bool = True
    debug_value: bool = False

    def __init__(
        self,
        function: Callable,
        log_in_runtime: bool = None,
        debug_value: bool = None,
        prefix: str = "",
        postfix: str = "",
    ):
        self.__function = function

        self.log_in_runtime = self.get_config_bool_value("log_in_runtime", log_in_runtime)
        self.debug_value = self.get_config_bool_value("debug_value", debug_value)
        self.prefix = prefix
        self.postfix = postfix

    @classmethod
    def info(cls) -> dict:
        return cls.__INFO

    @property
    def total_time(self) -> float:
        return self.__class__.__TOTAL_TIME

    @property
    def total_queries_count(self) -> float:
        return self.__class__.__TOTAL_QUERIES_COUNT

    @classmethod
    def get_config_bool_value(cls, config_var_name: str, expected_value: Optional[bool]) -> Any:
        return expected_value or getattr(cls, config_var_name, False)

    def format_message(self, **kwargs):
        message_format = str(self.__class__.HASH) + ": {func_name!r} за {run_time:.4f} сек, запросов: {queries_count}"
        return message_format.format(**kwargs)

    def get_debug_info(self, *args, **kwargs) -> tuple:
        info_dict = dict()
        info_dict["func_name"] = self.__function.__name__
        info_dict["start_time"] = time.perf_counter()
        value = self.__function(*args, **kwargs)
        info_dict["end_time"] = time.perf_counter()

        run_time = info_dict["end_time"] - info_dict["start_time"]
        info_dict["run_time"] = run_time
        self.__class__.__TOTAL_TIME += run_time

        if self.debug_value:
            info_dict["value"] = value

        connection_queries = len(connection.queries)
        info_dict["queries_count"] = connection_queries
        self.__class__.__TOTAL_QUERIES_COUNT += connection_queries
        # reset queries count by django built-in func
        reset_queries()

        return value, info_dict

    def push_log_in_runtime(self, message: str) -> None:
        logger.debug(message)

    def log_info(self, **kwargs) -> None:
        formatted_message = self.format_message(**kwargs)
        if self.log_in_runtime:
            self.push_log_in_runtime(formatted_message)
        self.store_data(formatted_message)

    @classmethod
    def store_data(cls, data: str) -> None:
        """
        Saves debug info to INFO dict
        """

        if cls.HASH not in cls.__INFO:
            cls.__INFO[cls.HASH] = []

        cls.__INFO[cls.HASH] += [data]

    @classmethod
    def get_report(cls) -> str:
        """
        Returns result report string
        """

        data_dict = cls.__INFO or {}
        report_string = ""
        totals = f"Общее время: {cls.__TOTAL_TIME}, общее число запросов: {cls.__TOTAL_QUERIES_COUNT}"

        for key, value in data_dict.items():
            report_string += f"\n{key}\n"
            for item in value:
                report_string += f" {item}\n"

        report_string += f"\n{totals}\n"
        cls.flush()

        return report_string

    @classmethod
    def log_report(cls) -> None:
        if cls.show_report and cls.__INFO:
            report = cls.get_report()
            logger.debug(report)
            cls.HASH = None

    @classmethod
    def flush(cls) -> None:
        cls.__INFO = OrderedDict()

    def __call__(self, *args, **kwargs):
        if self.use_settings and getattr(settings, self.use_settings, False) or not self.use_settings:
            value, debug_info = self.get_debug_info(*args, **kwargs)
            self.log_info(**debug_info)
        else:
            value = self.__function(*args, **kwargs)
        return value


class VersionManagerDebugger(BaseDebugger):
    """
    A separate debug class for version manager
    """

    use_settings: str = "VERSION_MANAGER_DEBUG"
    show_report = True
    log_in_runtime = False


def debug_method(func: Optional[Callable] = None, **debug_kwargs):
    """
    Print the runtime of the decorated function
    """

    if func is None:
        return partial(debug_method, **debug_kwargs)

    @wraps(func)
    def wrapper(*args, **kwargs):
        debugger_class = get_version_manager_debugger_class()
        debugger = debugger_class(func, **debug_kwargs)
        value = debugger(*args, **kwargs)
        return value

    return wrapper
