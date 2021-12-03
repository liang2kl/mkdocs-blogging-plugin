import os, logging, uuid
from mkdocs.structure.files import File
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
        ("features", config_options.Type(dict, default=[])),
    )

    blog_pages = []

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
    site_url = ""

    # Blog page
    blog_html = None
    
    # Tags
    tags_template = ""
    tags = {}
    site_dir = ""
    tags_page_html = None
    tag_tmp_file_name = ""

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
        
        self.site_dir = config.get("site_dir")
        self.site_url = config.get("site_url")

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
        self.tags_template = env.get_template("blog-tags-index.html")

        if self.config.get("locale"):
            self.locale = self.config.get("locale")
        else:
            self.locale = config.get("locale")

        for index, dir in enumerate(self.docs_dirs):
            if dir[-1:] != "/":
                self.docs_dirs[index] += "/"

        # Remove all posts to adapt live reload
        self.blog_pages = []
        self.tags = {}

        if not self.template_file:
            self.get_template(config)

    def on_files(self, files, config):
        if "tags" in self.features:
            # Add a temp file to the collection to generate HTML
            tag_dest_dir = self.get_tag_abs_dir()
            if not os.path.isdir(tag_dest_dir):
                os.mkdir(tag_dest_dir)
            self.tag_tmp_file_name = "blogging-tmp-" + str(uuid.uuid1())
            file_path = tag_dest_dir + self.tag_tmp_file_name + ".md"

            with open(file_path, "w") as file:
                file.write(f"{PLACEHOLDER}\n")
            file = File(file_path, tag_dest_dir, tag_dest_dir, False)
            file.name = "Tag"
            files.append(file)

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
                break

    def on_post_page(self, output, page, config):
        if not self.docs_dirs or not self.blog_pages:
            return
        
        if "tags" in self.features and not self.blog_html:            
            self.blog_html = self.generate_html(self.sorted_pages(self.blog_pages))

        if not self.tags_page_html:
            tag_names = [tag for tag in self.tags]
            sorted_entries = {tag: self.sorted_pages(self.tags[tag]) for tag in self.tags}
            self.tags_page_html = self.tags_template.render(
                tags=tag_names, entries=sorted_entries, tag_base_dir=self.get_tag_abs_url())

        result = BLOG_PAGE_PATTERN.subn(
            self.blog_html,
            output,
        )
        
        # There are matches
        if result[1]:
            output = result[0]
            """
            Add js script to the end of the document to manipulate paging
            bahaviours.
            """
            with open(DIR_PATH + "/templates/pagination.js") as file:
                output += ("<script>" + file.read() + "</script>")

        output = TAG_PAGE_PATTERN.sub(self.tags_page_html, output)

        return output

    def on_post_build(self, config):
        if "tags" in self.features and self.tags:
            tag_abs_dir = self.get_tag_abs_dir()
            html = ""
            
            with open(tag_abs_dir + f"{self.tag_tmp_file_name}.html") as file:
                html = file.read()
            
            for tag in self.tags:
                abs_url = tag_abs_dir + tag
                if not os.path.isdir(abs_url):
                    os.mkdir(abs_url)
                content = f"<h3><code>#{tag}</code></h3>\n"
                # FIXME: Paging
                pages = self.sorted_pages(self.tags[tag])
                content += self.generate_html(pages)
                result = html.replace(PLACEHOLDER, content)
                with open(abs_url + "/index.html", "w") as file:
                    file.write(result)
            # FIXME: No pages?

            os.remove(tag_abs_dir + f"{self.tag_tmp_file_name}.md")
            os.remove(tag_abs_dir+ f"{self.tag_tmp_file_name}.html")
    
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
                tag_base_dir=self.get_tag_abs_url(), show_tags="tags" in self.features
            )
    
    def get_tag_rel_dir(self) -> str:
        return self.features["dir"] if "dir" in self.features else "tag"
    
    def get_tag_abs_dir(self) -> str:
        return self.site_dir + "/" + self.get_tag_rel_dir() + "/"
    
    def get_tag_abs_url(self) -> str:
        return self.site_url + self.get_tag_rel_dir()  + "/"
    
    def get_tags_section_name(self) -> str:
        if "tags" in self.features:
            if "section_name" in self.features["tags"]:
                return self.features["tags"]["section_name"]
        return "Tags"

    def sorted_pages(self, pages):
        return sorted(pages,
            key=lambda page: page.meta["git-timestamp"], 
            reverse=self.sort["from"] == "new")