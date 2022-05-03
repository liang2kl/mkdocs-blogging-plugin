from datetime import datetime
import os
from pathlib import Path
from types import SimpleNamespace
import unittest

from mkdocs_blogging_plugin.plugin import BloggingPlugin

FILE_PATH = Path(os.path.realpath(__file__))


class TestPluginFormatting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = {
            "template": "test_data/template.html"
        }

        cls.config["categories"] = [{
            "name": "c1",
            "template": "test_data/template.html"
        }]

        global_config = {
            "site_url": "https://example.com",
            "config_file_path": FILE_PATH.as_posix()
        }

        cls.plugin = BloggingPlugin()
        cls.plugin.config = cls.config
        cls.plugin.read_in_config(global_config)

    def test_template(self):
        assert self.plugin.jinja_templates["global"].filename.split("/")[-1] == "template.html"
        assert self.plugin.jinja_templates["c1"].filename.split("/")[-1] == "template.html"
