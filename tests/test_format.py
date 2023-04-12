import datetime
import os
import unittest
from pathlib import Path
from types import SimpleNamespace

from mkdocs_blogging_plugin.plugin import BloggingPlugin

FILE_PATH = Path(os.path.realpath(__file__))

class TestPluginFormatting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = {
            "meta_time_format": "%Y-%m-%d %H:%M:%S",
            "time_format": "%Y/%m/%d %H:%M:%S"
        }

        global_config = {
            "site_url": "https://example.com",
            "config_file_path": FILE_PATH.as_posix()
        }

        cls.plugin = BloggingPlugin()
        cls.plugin.config = cls.config
        cls.plugin.read_in_config(global_config)

    def test_date(self):
        meta_date_str = "2022-05-03 11:09:00"
        page = SimpleNamespace(meta={"time": meta_date_str})

        date = datetime.datetime.strptime(
            meta_date_str, self.config["meta_time_format"])
        
        page = self.plugin.with_timestamp(page, False)

        expected_output = datetime.datetime.strftime(
            date, self.config["time_format"])

        assert page.meta["localized-time"] == expected_output

    def test_date_object(self):
        page = SimpleNamespace(meta={"date": datetime.date(2023, 4, 12)})
        page = self.plugin.with_timestamp(page, False)

        assert page.meta["localized-time"] == "2023/04/12 00:00:00"

    def test_datetime_object(self):
        page = SimpleNamespace(meta={"date": datetime.datetime(2023, 4, 12, 9, 15, 30)})
        page = self.plugin.with_timestamp(page, False)

        assert page.meta["localized-time"] == "2023/04/12 09:15:30"

    def test_datetime_object_fallback(self):
        """
        If meta.time is present but is an invalid type, we want to fall
        back to using meta.date if available and valid.
        """
        page = SimpleNamespace(
            meta={
                "time": 500,
                "date": datetime.datetime(2023, 4, 12, 9, 15, 30),
            }
        )
        page = self.plugin.with_timestamp(page, False)

        assert page.meta["localized-time"] == "2023/04/12 09:15:30"
