The `template` entry in the *category settings* allows you to override the appearance of the blog page.

To customize the appearance, create an HTML template with name **other than `blog.html` and `blog-*.html`**, then provide
**the path relative to the parent directory of `mkdocs.yml`** to the plugin's configuration.

For introduction and usage of HTML templates, refer to [jinja's documentation](https://jinja.palletsprojects.com/en/3.0.x/).

You have following customization options:

## Partial Customization

You can override how the plugin render a single blog entry through this method. An example can be found [here](https://github.com/liang2kl/mkdocs-blogging-plugin-example).

### Customize HTML

In your template, import the original template. The template can be the basic `blog.html`, or one of the built-in themes, like `blog-card-theme.html`:

```jinja title="template"
{% extends "blog.html" %}
```

Then, define a macro named `render_blog` with parameters `title`, `description`, `time`, `url`, `page`, which
returns HTML elements that represent a single blog entry.
Please note that `{{ caller() }}` must be present somewhere inside the macro, though it has no use here.

```jinja title="template"
{% macro render_blog(title, description, time, url, page) -%}
<a href="{{ url }}">
    <h3>{{ title }}</h3>
</a>
<div>{{ description }}</div>
<div>{{ time }}</div>
<hr/>
{{ caller() }}
{%- endmacro %}
```

The parameter `page` allows you to add arbitary additional information to any page using its `meta` attribute. For example, to show the author's name on the blog page, add an entry `author` in the markdown file's meta section:

```markdown title="article"
---
author: Liang Yesheng
---
```

Then, access it through `page.meta`:

```jinja title="template"
{% if "author" in page.meta %}
<div>{{ page.meta["author"] }}</div>
{% endif %}
```

and it will display the author.

### Customize styles

Further more, if you want to customize the css, write a block named `style`. Call `{{ super() }}` first
if you want to preserve the original styles.

```jinja title="template"
{% block style %}
    {{ super() }}
    <style>
        {# your style goes here #}
    </style>
{% endblock %}
```

Check the original template for available customization points. Here are some common ones:

- `.md-typeset .blog-post-title`: post title
- `.md-typeset .blog-post-description`: post description
- `.md-typeset .blog-post-extra`: extra section for creation / revision time

## Global Override

Alternatively, you can provide a template that works completely independent from the original template.

These variables are available inside your template:

- `pages`: sorted blog pages, see mkdocs' documentation for available attributes
- `page_size`: number of articles on a single page
- `is_revision`: `True` if sorted by revision time, `False` if by creation time
- `show_total`: whether to show the total number of the blog

You can refer to the original template for help.

## Access to the Original MkDocs Template Variables

Use `mkdocs_context` inside your template to access variables that are available inside MkDocs' templates. For example, to access `config.site_url`:

```jinja
<img src="{{ mkdocs_context.config.site_url }}/img/1.png" alt="">
```
