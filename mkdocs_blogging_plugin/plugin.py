import os, logging
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.exceptions import PluginError

from jinja2 import Environment, FileSystemLoader, select_autoescape
from .util import Util
import re, os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
BLOG_PAGE_PATTERN = re.compile(r"\{\{\s*blog_content\s*\}\}", flags=re.IGNORECASE)
TAG_PAGE_PATTERN = re.compile(r"\{\{\s*tag_content\s*\}\}", flags=re.IGNORECASE)
PLACEHOLDER = "{{ PLACEHOLDER }}"
THEMES = ["card", "button"]
file = open(DIR_PATH + "/templates/pagination.js")
SCRIPTS = "<script>" + file.read() + "</script>"
del file

logger = logging.getLogger("mkdocs.plugins")

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
        ("template", config_options.Type(str, default=None)),
        ("theme", config_options.Type(dict, default=None)),
        ("features", config_options.Type(dict, default={})),
    )

    blog_pages = []

    site_url = ""

    # Config
    docs_dirs = []
    size = 0
    sort = {}
    locale = None
    paging = True
    show_total = True
    template_file = None
    theme = None
    features = []

    # Blog page
    blog_html = None
    
    # Tags
    tags_index_template = None
    tags_template = None
    tags = {}
    tags_page_html = None
    tags_index_url = ""

    util = Util()

    def on_serve(self, server, config, builder):
        self.get_template(config)

        if self.template_file:
            # Watch the template file for live reload
            server.watch(self.template_file)
        
        return server
    
    def on_config(self, config):
        # Abort with error with 'navigation.instant' feature on
        # because paging won't work with it.
        mkdocs_theme = config.get("theme")
        if mkdocs_theme and "features" in mkdocs_theme and \
            "navigation.instant" in mkdocs_theme["features"] and self.paging:
            raise PluginError("[blogging-plugin] Feature 'navigation.instant' "
                              "cannot be enabled with option 'paging' on.")
        
        self.site_url = config.get("site_url")

        if not self.template_file:
            self.get_template(config)

        self.size = self.config.get("size")
        self.docs_dirs = self.config.get("dirs")
        self.paging = self.config.get("paging")
        self.sort = self.config.get("sort")
        self.show_total = self.config.get("show_total")
        self.theme = self.config.get("theme")
        self.features = self.config.get("features")

        if "from" not in self.sort:
            self.sort["from"] = "new"
        if "by" not in self.sort:
            self.sort["by"] = "creation"

        if self.theme:
            if self.template_file:
                logger.warning(
                    "[blogging-plugin] Custom template has higher priority than "
                    "predefined themes"
                )
            elif "name" not in self.theme:
                logger.warning(
                    f"[blogging-plugin] Theme name not found. Using default theme..."
                )
                self.theme = None
            elif self.theme["name"] not in THEMES:
                logger.warning(
                    f"[blogging-plugin] Theme '{self.theme['name']}' not found. "
                    "Using default theme..."
                )
                self.theme = None

        search_paths = [DIR_PATH + "/templates"]
        if self.template_file:
            search_paths.append(os.path.dirname(self.template_file))

        env = Environment(
            loader=FileSystemLoader(search_paths),
            autoescape=select_autoescape()
        )

        self.template = env.get_template(
            os.path.basename(self.template_file) if self.template_file else 
                (f"blog-{self.theme['name']}-theme.html" if self.theme else "blog.html")
        )

        # TODO: Custom template
        self.tags_index_template = env.get_template("blog-tags-index.html")
        self.tags_template = env.get_template("blog-tags.html")

        if "tags" in self.features:
            index_path = self.features["tags"].get("index_page")
            if index_path:
                index_url = self.site_url + index_path
                if index_url[-3:] == ".md":
                    self.tags_index_url = index_url[:-3]
                else:
                    self.tags_index_url = index_url

        if self.config.get("locale"):
            self.locale = self.config.get("locale")
        else:
            self.locale = config.get("locale")

        for index, dir in enumerate(self.docs_dirs):
            if dir[-1:] != "/":
                self.docs_dirs[index] += "/"

        # Remove all pages to adapt live reload
        self.blog_pages = []
        self.tags = {}

    
    def on_page_markdown(self, markdown, page, config, files):
        if "tags" in self.features and "tags" in page.meta:
            tags = page.meta["tags"]
            if isinstance(tags, list):
                for tag in tags:
                    if tag not in self.tags:
                        self.tags[tag] = [page]
                    else:
                        self.tags[tag].append(page)
            else:
                logger.warning(
                    f"[blogging-plugin] Tags entry '{tags}' is not a list. "
                    "Skipping..."
                )
            
            # Insert tags into original page
            insert = self.features["tags"].get("insert")
            if insert:
                tags_html = "\n" + self.tags_template.render(tags=page.meta["tags"],
                    index_url=self.tags_index_url).strip() + "\n"
                if insert == "bottom":
                    markdown = markdown + "\n<br/>\n" + tags_html
                else:
                    markdown = tags_html + markdown

        return markdown

    def on_page_content(self, html, page, config, files):
        """
        Add meta information about creation date after the html has
        been generated, the time when the meta from markdown file
        has already been added into the page instance.
        """

        if not self.docs_dirs:
            return

        if "exclude_from_blog" in page.meta and page.meta["exclude_from_blog"]:
            return

        for dir in self.docs_dirs:
            if page.file.src_path[:len(dir)] == dir:
                timestamp = self.util.get_git_commit_timestamp(page.file.abs_src_path, is_first_commit=self.sort["by"] != "revision")
                page.meta["git-timestamp"] = timestamp
                page.meta["localized-time"] = self.util.get_localized_date(timestamp, False, self.locale)
                self.blog_pages.append(page)

                break

    def on_post_page(self, output, page, config):
        if self.docs_dirs and self.blog_pages:
            if not self.blog_html:            
                self.blog_html = self.generate_html(self.sorted_pages(self.blog_pages))

            result = BLOG_PAGE_PATTERN.subn(
                self.blog_html,
                output,
            )
        
            # There are matches
            if result[1]:
                """
                Add js script to the end of the document to manipulate paging
                bahaviours.
                """
                output = result[0] + SCRIPTS
        
        if "tags" in self.features and self.tags:
            tag_names = [tag for tag in self.tags]
            sorted_entries = {tag: self.sorted_pages(self.tags[tag]) for tag in self.tags}
            if not self.tags_page_html:
                self.tags_page_html = self.tags_index_template.render(
                    tags=tag_names, entries=sorted_entries, index_url=self.tags_index_url)

            output = TAG_PAGE_PATTERN.sub(self.tags_page_html, output)
        
        return output
    
    def get_template(self, config):
        if self.config.get("template"):
            root_url = os.path.dirname(config.get("config_file_path"))
            self.template_file = root_url + "/" + self.config.get("template")

    def generate_html(self, pages) -> str:
        blog_pages = sorted(pages, 
            key=lambda page: page.meta["git-timestamp"], 
            reverse=self.sort["from"] == "new"
        )
        theme_options = self.theme.get("options") if self.theme else []
        return self.template.render(
                pages=blog_pages, page_size=self.size, 
                paging=self.paging, is_revision=self.sort["by"] == "revision",
                show_total=self.show_total, theme_options=theme_options,
                index_url=self.tags_index_url, show_tags="tags" in self.features
            )
    
    def sorted_pages(self, pages):
        return sorted(pages,
            key=lambda page: page.meta["git-timestamp"], 
            reverse=self.sort["from"] == "new")