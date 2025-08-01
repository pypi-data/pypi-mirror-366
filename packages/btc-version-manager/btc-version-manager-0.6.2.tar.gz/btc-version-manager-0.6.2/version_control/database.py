import logging
import traceback
from typing import Any, Collection, Union

from django.db import transaction

logger = logging.getLogger(__name__)


def format_message(log_message: str, log_message_args: Collection, log_message_args_dict: dict) -> str:
    return log_message % tuple(log_message_args_dict.get(arg, "") for arg in log_message_args)


def get_exception_info(exc_type: Any, exc_val: str, exc_tb: traceback) -> dict:
    """
    Gets exception information.
    :param exc_type: type of exception
    :param exc_val: message in exception constructor
    :param exc_tb: traceback
    :return: dict
    """

    exception_info = dict()

    # common info
    exception_info["exc_type"] = exc_type
    exception_info["exc_val"] = exc_val
    exception_info["exc_tb"] = exc_tb

    # additional info
    exception_info["exc_type_name"] = exc_type.__name__
    exception_info["exc_val_message"] = str(exc_val)
    exception_info["exc_tb_filename"] = exc_tb.tb_frame.f_code.co_filename
    exception_info["exc_tb_lineno"] = exc_tb.tb_lineno
    exception_info["exc_tb_func_name"] = exc_tb.tb_frame.f_code.co_name

    return exception_info


class TransactionManagerError(Exception):
    """
    A custom transaction manager exception class.
    """

    def __init__(self, exc_type, exc_val, exc_tb):
        self.exc_type, self.exc_val, self.exc_tb = exc_type, exc_val, exc_tb

    def __str__(self):
        return f"{self.exc_type}: {self.exc_val}: {self.exc_tb}"


class TransactionManager:
    """
    A context manager for handling exceptions and commit / rollback transaction.
    """

    transaction_rollback_log_message = ""
    transaction_commit_log_message = ""
    log_message_args = (
        "exc_type",
        "exc_val",
    )

    def __init__(
        self,
        *exc_types,
        using: Union[str, None] = None,
        savepoint=None,
        raise_exc: bool = False,
    ):
        """
        :param exc_types: greedy parameter - list exceptions to handle
        :param savepoint: savepoint for rollback, if not specified, a new one will be created at manager init
        :param using: database name, 'default' if None
        :param raise_exc: flag to raise the exception 'TransactionManagerError'
        """

        self.__exception_types = exc_types
        self.__using = using
        self.__sid = savepoint or transaction.savepoint(self.__using)
        self.__raise_exc = raise_exc

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and isinstance(exc_type(), self.__exception_types):
            transaction.savepoint_rollback(self.__sid, self.__using)
            if self.transaction_rollback_log_message:
                logger.error(
                    format_message(
                        self.transaction_rollback_log_message,
                        self.log_message_args,
                        get_exception_info(exc_type, exc_val, exc_tb),
                    )
                )
            if self.__raise_exc:
                raise TransactionManagerError(exc_type, exc_val, exc_tb)
        else:
            transaction.savepoint_commit(self.__sid, self.__using)
            if self.transaction_commit_log_message:
                logger.info(self.transaction_commit_log_message)
        return True
