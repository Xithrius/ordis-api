import logging
from typing import Any, ClassVar

from gunicorn.app.base import BaseApplication
from gunicorn.glogging import Logger
from gunicorn.util import import_app  # pyright: ignore[reportUnknownVariableType]
from uvicorn.workers import UvicornWorker as BaseUvicornWorker

from api.logging import LOG_CONFIG, EndpointFilter

try:
    import uvloop
except ImportError:
    uvloop = None


class LoadConfigError(Exception):
    """Error raised when the config cannot be loaded."""


class CustomGunicornLogger(Logger):
    def setup(self, cfg: Any) -> None:
        super().setup(cfg)

        access_logger = logging.getLogger("gunicorn.access")
        access_logger.addFilter(EndpointFilter())


class UvicornWorker(BaseUvicornWorker):
    """
    Configuration for uvicorn workers.

    This class is subclassing UvicornWorker and defines
    some parameters class-wide, because it's impossible,
    to pass these parameters through gunicorn.
    """

    CONFIG_KWARGS: ClassVar = {  # pyright: ignore[reportIncompatibleVariableOverride]
        "loop": "uvloop" if uvloop is not None else "asyncio",
        "http": "httptools",
        "lifespan": "on",
        "factory": True,
        "proxy_headers": False,
        "log_config": LOG_CONFIG,
    }


class GunicornApplication(BaseApplication):
    """
    Custom gunicorn application.

    This class is used to start guncicorn
    with custom uvicorn workers.
    """

    def __init__(
        self,
        app: str,
        host: str,
        port: int,
        workers: int,
        **kwargs: Any,
    ) -> None:
        self.options = {
            "bind": f"{host}:{port}",
            "workers": workers,
            "worker_class": "api.gunicorn_runner.UvicornWorker",
            "logger_class": CustomGunicornLogger,
            **kwargs,
        }
        self.app = app
        super().__init__()

    def load_config(self) -> None:
        """
        Load config for web server.

        This function is used to set parameters to gunicorn
        main process. It only sets parameters that
        gunicorn can handle. If you pass unknown
        parameter to it, this will crash with an error.
        """
        if self.cfg is None:
            raise LoadConfigError("Failed to load Gunicorn Application config")

        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)  # pyright: ignore[reportUnknownArgumentType]

    def load(self) -> str:
        """
        Load actual application.

        Gunicorn loads application based on this
        function's returns. We return python's path to
        the app's factory.

        :returns: python path to app factory.
        """
        return str(import_app(self.app))
