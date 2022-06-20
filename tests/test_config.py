from pathlib import Path
import unittest
from typing import Dict
import os
from mkdocs_blogging_plugin.config import BloggingConfig
from mkdocs_blogging_plugin.plugin import BloggingPlugin

FILE_PATH = Path(os.path.realpath(__file__))

class TestPluginConfig(unittest.TestCase):
    """Test basic config reading of categories."""
    @classmethod
    def setUpClass(cls):
        cls.config = {
            "dirs": "global_dir",
            "size": 4,
            "sort": {
                "from": "old",
                "by": "revision"
            },
            "paging": False,
            "show_total": False,
            "full_content": True,
        }

        cls.config["categories"] = [
            {
                "name": "c1",
                "dirs": "c1_dir",
                "size": 3,
                "sort": {
                    "from": "new",
                    "by": "creation"
                },
                "paging": True,
                "show_total": True,
                "full_content": False,
            },
            {
                "name": "c2",
                "dirs": "c2_dir"
            }
        ]

        global_config = {
            "site_url": "https://example.com",
            "config_file_path": FILE_PATH.as_posix()
        }

        cls.plugin = BloggingPlugin()
        cls.plugin.config = cls.config
        cls.plugin.read_in_config(global_config)

    def test_global_category(self):
        global_category = self.plugin.categories["global"]
        assert global_category.dirs == self.config["dirs"]
        assert global_category.size == self.config["size"]
        assert global_category.sort == self.config["sort"]
        assert global_category.paging == self.config["paging"]
        assert global_category.show_total == self.config["show_total"]

    def test_categories(self):
        c = BloggingConfig({})
        for name, category in self.plugin.categories.items():
            if name == "global":
                continue
            category_dict = [c for c in self.config["categories"] if c["name"] == name][0]
            assert category.dirs == category_dict.get("dirs", c.dirs)
            assert category.size == category_dict.get("size", c.size)
            assert category.sort == category_dict.get("sort", c.sort)
            assert category.paging == category_dict.get("paging", c.paging)
            assert category.show_total == category_dict.get("show_total", c.show_total)


if __name__ == '__main__':
    unittest.main()
