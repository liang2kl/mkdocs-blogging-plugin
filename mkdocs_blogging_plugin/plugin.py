import os
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from jinja2 import Environment, PackageLoader, select_autoescape, Template
import re


class BloggingPlugin(BasePlugin):
    """
    Mkdocs plugin to add blogging functionality
    to mkdocs site.
    """
    
    config_scheme = (
        ("dir", config_options.Type(str, default="blog")),
        ("size", config_options.Type(int, default=10)),
        ("sort", config_options.Type(dict, default={"from": "old", "by": "creation"})),
    )

    blog_pages = []
    size = 0
    additional_html = None
    sort = ""
    
    env = Environment(
        loader=PackageLoader("mkdocs_blogging_plugin"),
        autoescape=select_autoescape()
    )    
    template = env.get_template("blog.html")
    
    def on_pre_page(self, page, config, files):
        self.size = self.config.get("size")
        docs_dir = self.config.get("dir")
        self.sort = self.config.get("sort")

        if docs_dir[-1:] != "/":
            docs_dir += "/"
        
        self.blog_pages = [file for file in files if file.src_path[:len(docs_dir)] == docs_dir]
        

    def on_post_page(self, output, page, config):
        pattern = r"\{\{\s*blog_content\s*\}\}"
        if not re.findall(pattern, output, flags=re.IGNORECASE):
            return output
        if not self.additional_html:
            self.additional_html = self.template.render(
                pages=self.blog_pages, page_size=self.size, sort=self.sort)

        output = re.sub(
            r"\{\{\s*blog_content\s*\}\}",
            self.additional_html,
            output,
            flags=re.IGNORECASE,
        )

        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(dir_path + "/templates/pagination.js") as file:
            output += (r"<script>" + file.read() + r"</script>")

        return output