import os
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.exceptions import PluginError

from jinja2 import Environment, PackageLoader, select_autoescape
from .util import Util
import re

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

class BloggingPlugin(BasePlugin):
    """
    Mkdocs plugin to add blogging functionality
    to mkdocs site.
    """
    
    config_scheme = (
        ("dirs", config_options.Type(list, default=[])),
        ("size", config_options.Type(int, default=10)),
        ("sort", config_options.Type(dict, default={"from": "new", "by": "creation"})),
        ("locale", config_options.Type(str, default=None)),
        ("paging", config_options.Type(bool, default=True)),
        ("show_total", config_options.Type(bool, default=True)),
    )

    blog_pages = []

    # Config
    size = 0
    additional_html = None
    docs_dirs = []
    sort = {}
    locale = None
    paging = True
    show_total = True

    util = Util()
    
    env = Environment(
        loader=PackageLoader("mkdocs_blogging_plugin"),
        autoescape=select_autoescape()
    )    
    template = env.get_template("blog.html")
    
    def on_config(self, config):
        self.size = self.config.get("size")
        self.docs_dirs = self.config.get("dirs")
        self.paging = self.config.get("paging")
        self.sort = self.config.get("sort")
        self.show_total = self.config.get("show_total")

        if "from" not in self.sort:
            self.sort["from"] = "new"
        if "by" not in self.sort:
            self.sort["by"] = "creation"

        # Abort with error with 'navigation.instant' feature on
        # because paging won't work with it.
        theme = config.get("theme")
        if theme and "features" in theme and \
            "navigation.instant" in theme["features"] and self.paging:
            raise PluginError("[blogging-plugin] Feature 'navigation.instant' "
                              "cannot be enabled with option 'paging' on.")

        if self.config.get("locale"):
            self.locale = self.config.get("locale")
        else:
            self.locale = config.get("locale")

        for index, dir in enumerate(self.docs_dirs):
            if dir[-1:] != "/":
                self.docs_dirs[index] += "/"

        # Remove all posts to adapt live reload
        self.blog_pages = []

    def on_page_content(self, html, page, config, files):
        """
        Add meta information about creation date after the html has
        been generated, the time when the meta from markdown file
        has already been added into the page instance.
        """

        if not self.docs_dirs:
            return

        for dir in self.docs_dirs:
            if page.file.src_path[:len(dir)] == dir \
                and (not "exclude_from_blog" in page.meta or not page.meta["exclude_from_blog"]):
                timestamp = self.util.get_git_commit_timestamp(page.file.abs_src_path, is_first_commit=self.sort["by"] != "revision")
                page.meta["git-timestamp"] = timestamp
                page.meta["localized-time"] = self.util.get_localized_date(timestamp, False, self.locale)
                self.blog_pages.append(page)
                break

    def on_post_page(self, output, page, config):
        if not self.docs_dirs or not self.blog_pages:
            return

        pattern = r"\{\{\s*blog_content\s*\}\}"
        if not re.findall(pattern, output, flags=re.IGNORECASE):
            return output
        if not self.additional_html:
            self.blog_pages = sorted(self.blog_pages, 
                key=lambda page: page.meta["git-timestamp"], 
                reverse=self.sort["from"] == "new")
            self.additional_html = self.template.render(
                pages=self.blog_pages, page_size=self.size, sort=self.sort, 
                paging=self.paging, is_revision=self.sort["by"] == "revision",
                show_total=self.show_total
            )

        output = re.sub(
            pattern,
            self.additional_html,
            output,
            flags=re.IGNORECASE,
        )
        
        """
        Add js script to the end of the document to manipulate paging
        bahaviours.
        """
        with open(DIR_PATH + "/templates/pagination.js") as file:
            output += ("<script>" + file.read() + "</script>")

        return output

