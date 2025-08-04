import logging
import os
import pathlib

from mopidy import config, ext
from tornado.web import StaticFileHandler

__version__ = "0.1.0-rc4"

# If you need to log, use loggers named after the current Python module
logger = logging.getLogger(__name__)


class Extension(ext.Extension):
    dist_name = "Mopidy-Cranberry"
    ext_name = "cranberry"
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), "ext.conf")
        return config.read(conf_file)

    def validate_environment(self):
        # Any manual checks of the environment to fail early.
        # Dependencies described by setup.py are checked by Mopidy, so you
        # should not check their presence here.
        pass

    def setup(self, registry):
        from .frontend import CranberryFrontend

        # Add web extension
        registry.add("http:app", {"name": self.ext_name, "factory": cranberry_factory})

        registry.add("frontend", CranberryFrontend)


def cranberry_factory(config, core):
    path = pathlib.Path(__file__).parent / "static"

    return [
        (r"/assets/(.*)", StaticFileHandler, {"path": path / "assets"}),
        (
            r"/((.*)(?:css|js|json|map|wasm|ico|png|br)$)",
            StaticFileHandler,
            {"path": path},
        ),
        (r"/(.*)", StaticFileHandler, {"path": path / "index.html"}),
    ]
