import os
import logging
import re
from typing import Dict
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.exceptions import PluginError
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from mkdocs_blogging_plugin.config import BloggingConfig
from .util import Util
from pathlib import Path
from datetime import datetime

DIR_PATH = Path(os.path.dirname(os.path.realpath(__file__)))
BLOG_PAGE_PATTERN = re.compile(
    r"\{\{\s*blog_content\s+(([0-9]|[a-z]|[A-Z]|-|_)*)\s*\}\}", flags=re.IGNORECASE)
TAG_PAGE_PATTERN = re.compile(
    r"\{\{\s*tag_content\s*\}\}", flags=re.IGNORECASE)
THEMES = ["card", "button"]
with open(DIR_PATH / "templates" / "pagination.js") as file:
    SCRIPTS = "<script>" + file.read() + "</script>"

logger = logging.getLogger("mkdocs.plugins")


def get_config_scheme():
    # Using default values defined in BloggingConfig class
    c = BloggingConfig({})

    return (
        # Category-specific configurations, for 'global' category
        ("dirs", config_options.Type(list, default=c.dirs)),
        ("size", config_options.Type(int, default=c.size)),
        ("sort", config_options.Type(dict, default=c.sort)),
        ("paging", config_options.Type(bool, default=c.paging)),
        ("show_total", config_options.Type(bool, default=c.show_total)),
        ("template", config_options.Type(str, default=c.template)),
        ("theme", config_options.Type(dict, default=c.theme)),
        ("full_content", config_options.Type(bool, default=c.full_content)),

        # Global-only configurations
        ("meta_time_format", config_options.Type(str, default=None)),
        ("time_format", config_options.Type(str, default=None)),
        ("locale", config_options.Type(str, default=None)),
        ("features", config_options.Type(dict, default={})),

        # Extra: categories (list of configs)
        ("categories", config_options.Type(list, default=[])),
    )


class BloggingPlugin(BasePlugin):
    """
    Mkdocs plugin to add blogging functionality
    to mkdocs site.
    """
    def __init__(self):
        self.config_scheme = get_config_scheme()
        self.util = Util()

        # Global configs
        self.site_url = ""
        self.meta_time_format: str = None
        self.time_format: str = None
        self.locale: str = None
        self.features: dict = {}

        # Global vars
        self.mkdocs_template_context = None
        # Tags; TODO: Do we need to support categories?
        self.tags_index_template = None
        self.tags_template = None
        self.tags = {}
        self.tags_page_html = None
        self.tags_index_url = ""

        # Configs
        self.categories: Dict[str, BloggingConfig] = {}

        # Blog pages
        self.pages = {
            "global": {
                "html": None,
                "pages": []
            }
        }

        # Templates
        self.jinja_templates: Dict[str, Template] = {}

    def read_in_config(self, global_config):
        # Return if the config has already been read
        if len(self.categories) > 0:
            return

        # Get site url for hyperlinks
        self.site_url = global_config.get("site_url")
        if self.site_url is None:
            raise PluginError(
                "[blogging-plugin] Please specify `site_url` setting in your `mkdocs.yml` file. The blog index "
                "page will not properly function otherwise. Example:\n\n    site_url: https://myblog.com",
            )

        # Get global configurations
        self.meta_time_format = self.config.get("meta_time_format")
        self.time_format = self.config.get("time_format")
        self.locale = self.config.get("locale")
        self.features = self.config.get("features", {})
        if self.config.get("locale"):
            self.locale = self.config.get("locale")
        else:
            self.locale = global_config.get("locale")

        # Read in configs of all categories
        self.categories["global"] = BloggingConfig(self.config)
        categories = self.config.get("categories")
        if isinstance(categories, list):
            for c in categories:
                if isinstance(c, dict) and "name" in c:
                    self.categories[c["name"]] = BloggingConfig(c)
        elif categories is not None:
            logger.warning(
                "[blogging-plugin] Config entry'categories' is not a list"
            )

        # Validate configs
        # Check if paging is on in any category
        has_paging = False

        for _, config in self.categories.items():
            if config.paging:
                has_paging = True
                break

        # Abort with error with 'navigation.instant' feature on
        # because paging won't work with it.
        mkdocs_theme = global_config.get("theme")
        if mkdocs_theme and "features" in mkdocs_theme and \
                "navigation.instant" in mkdocs_theme["features"] and has_paging:
            raise PluginError("[blogging-plugin] Feature 'navigation.instant' "
                              "cannot be enabled with option 'paging' on.")

        # Walk through configs
        for _, config in self.categories.items():
            # Check sorting parameters
            if "from" not in config.sort:
                config.sort["from"] = "new"
            if "by" not in config.sort:
                config.sort["by"] = "creation"

            # Check theme
            if config.theme:
                if config.template:
                    logger.warning(
                        "[blogging-plugin] Custom template has higher priority than "
                        "predefined themes"
                    )
                elif "name" not in config.theme:
                    logger.warning(
                        f"[blogging-plugin] Theme name not found. Using default theme..."
                    )
                    config.theme = None
                elif config.theme["name"] not in THEMES:
                    logger.warning(
                        f"[blogging-plugin] Theme '{config.theme['name']}' not found. "
                        "Using default theme..."
                    )
                    config.theme = None

        # Setup jinja templates
        search_paths = [DIR_PATH / "templates"]
        root_url = Path(global_config.get("config_file_path")).parents[0]
        search_paths += [(root_url / c.template).parents[0]
                         for _, c in self.categories.items() if c.template]

        env = Environment(
            loader=FileSystemLoader(search_paths),
            autoescape=select_autoescape()
        )

        for name, config in self.categories.items():
            jinja_template = env.get_template(
                (root_url / config.template).name if config.template else
                (f"blog-{config.theme['name']}-theme.html" if config.theme else "blog.html")
            )
            self.jinja_templates[name] = jinja_template

        # Setup tags
        self.tags_index_template = env.get_template("blog-tags-index.html")
        self.tags_template = env.get_template("blog-tags.html")

        if "tags" in self.features:
            index_path = self.features["tags"].get("index_page")
            if index_path:
                index_path = Path(index_path)
                self.tags_index_url = self.site_url + \
                    (index_path.parents[0] / index_path.stem).as_posix()
                # Adapt mkdocs's `use_directory_urls` setting.
                # See https://www.mkdocs.org/user-guide/configuration/#use_directory_urls.
                if global_config.get("use_directory_urls") == False:
                    self.tags_index_url += ".html"

    def on_serve(self, server, config, builder):
        self.read_in_config(config)

        root_url = Path(config.get("config_file_path")).parents[0]
        # Watch the template files for live reload
        for _, c in self.categories.items():
            if c.template:
                server.watch(root_url / c.template)

        return server

    def on_config(self, config):
        # Remove all pages to adapt live reload
        self.pages = {}
        self.categories = {}
        self.tags = {}

        self.read_in_config(config)

    def on_template_context(self, context, template_name, config):
        self.mkdocs_template_context = context
        return context

    def on_page_markdown(self, markdown, page, config, files):
        if "tags" in self.features and "tags" in page.meta:
            tags = page.meta["tags"]
            page = self.with_timestamp(
                page, self.categories["global"].sort["by"] == "revision")
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

        if "exclude_from_blog" in page.meta and page.meta["exclude_from_blog"]:
            return

        file_path = Path(page.file.src_path)

        for name, config in self.categories.items():
            self.pages.setdefault(name, {"html": None, "pages": []})
            for dir in config.dirs:
                if Path(dir) in file_path.parents:
                    self.pages[name]["pages"].append(
                        self.with_timestamp(page, config.sort["by"] == "revision"))
                    break

    def on_post_page(self, output, page, config):
        match = BLOG_PAGE_PATTERN.search(output)
        if match:
            category = match.group(1)
            if not category:
                category = "global"
            if category not in self.pages:
                raise PluginError(
                    f"[blogging-plugin] category '{category}' not found in configuration file"
                )

            if self.pages[category]["html"] is None:
                self.pages[category]["html"] = self.generate_html(category)

            result = BLOG_PAGE_PATTERN.sub(
                self.pages[category]["html"],
                output,
            )

            output = result + SCRIPTS

        if "tags" in self.features and self.tags:
            if not self.tags_page_html:
                tag_names = [tag for tag in self.tags]
                sorted_entries = {tag: sorted(self.tags[tag],
                                              key=lambda page: page.meta["git-timestamp"],
                                              reverse=self.categories["global"].sort["from"] == "new"
                                              )
                                  for tag in self.tags}

                self.tags_page_html = self.tags_index_template.render(
                    tags=tag_names, entries=sorted_entries,
                    index_url=self.tags_index_url)

            output = TAG_PAGE_PATTERN.sub(self.tags_page_html, output)

        return output

    def generate_html(self, category) -> str:
        config = self.categories[category]
        template = self.jinja_templates[category]

        blog_pages = sorted(self.pages[category]["pages"],
                            key=lambda page: page.meta["git-timestamp"],
                            reverse=config.sort["from"] == "new"
                            )

        theme_options = config.theme.get("options") if config.theme else []

        return template.render(
            pages=blog_pages, page_size=config.size,
            paging=config.paging, is_revision=config.sort["by"] == "revision",
            show_total=config.show_total, theme_options=theme_options,
            index_url=self.tags_index_url, show_tags="tags" in self.features,
            mkdocs_context=self.mkdocs_template_context,
            full_content=config.full_content,
        )

    def with_timestamp(self, page, by_revision):
        timestamp = None
        if self.meta_time_format:
            if "time" in page.meta:
                timestamp = datetime.strptime(
                    page.meta["time"], self.meta_time_format).timestamp()
            elif "date" in page.meta:
                timestamp = datetime.strptime(
                    page.meta["date"], self.meta_time_format).timestamp()
        if not timestamp:
            timestamp = self.util.get_git_commit_timestamp(
                page.file.abs_src_path, is_first_commit=(not by_revision))
        page.meta["git-timestamp"] = timestamp
        page.meta["localized-time"] = self.util.get_localized_date(
            timestamp, False, format=self.time_format, _locale=self.locale)

        return page
