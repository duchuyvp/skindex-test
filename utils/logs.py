import dataclasses
import json
import logging
import os
from typing import Any
from . import configuration, dictionary
from .values import parsers

lib_config = configuration.load_config()

DEFAULT_LOG_CONFIG = {
    "format": {
        "inline": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "datatime": "%Y-%m-%d %H:%M:%S",
    },
    "metadata": {
        "fixed_keys": {
            "application",
            "environment",
            "host",
        },
        "keys": {}
    },
    "logger": {
        "file_name": f"{os.environ.get("SERVICE","")}.log",
        "file_mode": "a",
        "level": "INFO",
        "verbose": False,
        "outputs": [
            "stdout", "file",
        ]
    }
}


def get_config() -> dict[str, Any]:
    return lib_config.get("log", {})

def load_config() -> dict[str, Any]:
    global lib_config

    lib_config["log"] = dictionary.merge_dicts(
        DEFAULT_LOG_CONFIG,
        lib_config.get("log", {}),
    )

    lib_config["log"]["metadata"]["keys"] = set(
        lib_config["log"]["metadata"].get("keys", set())
    ).union(lib_config["log"]["metadata"]["fixed_keys"])
    return lib_config["log"]

load_config()

LOG_KEY_MAPPERS = {
    "levelname": "level_name",
    "filename": "file_name",
    "levelno": "level_no",
    "lineno": "line_no",
    "thread_name": "MainThread",
    "pathname": "path_name",
}

LOG_CONTEXT_KEYS = {
    "file_name",
    "func_name",
    "line_no",
    "module",
    "level_no",
}

def standardize_log_record(d: dict[str, Any]) -> dict[str, Any]:
    d_ = { parsers.string_to_snake_case(LOG_KEY_MAPPERS.get(key, key)) : val for key, val in d.items() }

    return d_

class DynamicObjectMixin:

    def __init__(self, **kwargs) -> None:
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __repr__(self) -> str:
        attributes = ", ".join([f"{k}={v!r}" for k, v in self.__dict__.items()])
        
        return f"{self.__class__.__name__}({attributes})"
    
@dataclasses.dataclass
class LogSource(DynamicObjectMixin):
    file_name: str
    func_name: str
    line_no: int
    module: str
    level_no: int

    def __init__(self, **kwargs) -> None:
        init_kwargs = {}

        for key, val in kwargs.items():
            standardized_key = parsers.string_to_snake_case(
                LOG_KEY_MAPPERS.get(key, key)
            )
            if standardized_key not in LOG_CONTEXT_KEYS:
                continue

            init_kwargs[standardized_key] = val

        super().__init__(**init_kwargs)

    @property
    def json(self):
        return self.__dict__

    def __repr__(self) -> str:
        return super().__repr__()
    

@dataclasses.dataclass(init=False)
class LogMetadata(DynamicObjectMixin):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        for key in get_config().get("metadata", {}).get("keys", set()):
            val = os.environ.get(key.upper())
            if val is not None:
                setattr(self, key, val)


    @property
    def json(self):
        return self.__dict__

    def __repr__(self) -> str:
        return super().__repr__()
    

    
@dataclasses.dataclass
class LogRecord(logging.LogRecord):
    source: LogSource
    metadata: LogMetadata

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.source = LogSource(**self.__dict__)
        self.metadata = LogMetadata()

    @property
    def json(self):
        return {
            "source": self.source.json,
            "metadata": self.metadata.json,
            "args": self.args,
            "message": self.getMessage(),
            "exc_info": self.exc_info,
            "stack_info": self.stack_info,
        }
    
    def __str__(self) -> str:
        return parsers.prettier_dict(self.json)

class InlineLogFormatter(logging.Formatter):
    def __init__(
        self,
        fmt = get_config().get("format", {}).get("inline"),
        datefmt = get_config().get("format", {}).get("datatime"),
        style = "%",
    ): 
        super().__init__(fmt, datefmt, style)


class JSONFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()

        if record.exc_info:
            record.exc_info = self.formatException(record.exc_info)
        else:
            record.exc_info = ""
        
        if record.stack_info:
            record.stack_info = self.formatStack(record.stack_info)

        d = {}
        try:
            d = record.json
        except AttributeError:
            d = record.__dict__

        d = standardize_log_record(d)
        return json.dumps(d, cls=parsers.JSONEncoder)
    

class PersistentLogHandler(logging.FileHandler):

    def __init__(
        self,
        file_name: str = get_config().get("logger", {}).get("file_name"),
        mode: str = "a",
        encoding: str = None,
        delay: str = False,
        errors: str = None,
        *args,
        **kwargs,
    ):
        super().__init__(file_name, mode, encoding, delay, errors, *args, **kwargs)
        json_formatter = JSONFormatter()
        self.setFormatter(json_formatter)

class TemporaryLogHandler(logging.StreamHandler):

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        inline_formatter = InlineLogFormatter()
        self.setFormatter(inline_formatter)


class Logger(logging.Logger):

    def __init__(
        self,
        name: str,
        file_name: str = get_config().get("logger", {}).get("file_name"),
        file_mode: str = "a",
    ):
        super().__init__(name)

        handlers = [
            TemporaryLogHandler(),
            PersistentLogHandler(file_name, mode=file_mode),
        ]
        for handler in handlers:
            self.addHandler(handler)

    def _log(
        self,
        level: int,
        msg: str,
        args: tuple,
        exc_info = None,
        extra = None,
        stack_info = False,
        stacklevel = 2,
        **kwargs,
    ):
        if extra is None:
            extra = {}
        
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel, **kwargs)


def bootstrap():
    logging.setLoggerClass(Logger)
    logging.setLogRecordFactory(LogRecord)

    load_config()

bootstrap()
