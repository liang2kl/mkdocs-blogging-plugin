# mkdocs-blogging-plugin

A mkdocs plugin that generates a blog page listing selected pages by time.

![preview](https://i.loli.net/2021/09/09/LhX9IFkbu2K3lRi.png)

## Installation

```shell
pip3 install mkdocs-blogging-plugin
```

## Prerequisites

- Only `material` theme is adapted by far.

- `navigation.instant` feature cannot be enabled if blog paging is on.

## Usage

Add `blogging` in `plugins` and specify the directories to be included:

```yml
plugins:
  - blogging:
      dirs: # The directories to be included
        - blog
```

In the page you want to insert the blog content, just add a line `{{ blog_content }}` into your desired position:

```markdown
# Blogs

{{ blog_content }}
```

In articles, add meta tags providing article title and description, which will appear on the post list:

```markdown
---
title: Lorem ipsum dolor sit amet
description: Nullam urna elit, malesuada eget finibus ut, ac tortor.
---
```

To exclude certain pages from the blog collection, add a meta tag `exculde_from_blog` in the meta section of the markdown file:

```markdown
---
exculde_from_blog: true
---
```

And it's done! You can open the page where you insert `{{ blog_content }}` and see how it is working.

## Customization

### Options
Optionally, you can customize some behaviours of the plugin:

```yml
size: 5            # Number of articles in one page, default: 10
locale: en         # The locale for time localizations, default: system's locale
sort: 
  from: new        # Sort from new to old, default
  # or old         # Sort from old to new
  by: creation     # Sort by the first commit time, default
  # or revision    # Sort by the latest commit time
paging: false      # Disable paging
show_total: false  # Remove 'total pages' label
template: blog-override.html # Path to customized template, see below
```

### Overriding Template

The `template` entry in the configuration provides you a way to override the blog content to be rendered.

To customize the blog content, create an HTML template with name **other than** `blog.html`, then provide
**the path relative to the parent directory of `mkdocs.yml`** to the plugin's configuration.

> For example:
> 
> ```text
> .
> ├─ overrides/
> │  └─ template.html
> └─ mkdocs.yml
> ```
> 
> then the configuration should be `template: overrides/template.html`.

#### Partial Customization

You can override how the plugin render a single blog through this method.

In your template, define a macro that renders a single blog with the provided parameters `title`, `description`, `time` and `url`.
Then add a line `{% extends "blog.html" %}` **below** the macro.

Please note that `{{ caller() }}` must be present somewhere inside the macro.

```jinja
{% macro render_blog(title, description, time, url) -%}
  <a href="{{ url }}">
    <h3>{{ title }}</h3>
  </a>
  <div>{{ description }}</div>
  <div>{{ time }}</div>
  <hr/>
  {{ caller() }}
{%- endmacro %}

{% extends "blog.html" %}
```

The plugin now use your macro `render_blog` to generate the HTML.

Further more, if you want to customize the css, extend the block `style` below `{% extends "blog.html" %}`. Call `{{ super() }}` at
the top if you want to preserve the original style.

```jinja
{% block style %}
  {{ super() }}
  <style>
    {# your style goes here #}
  </style>
{% endblock %}
```

Check [the original template](mkdocs_blogging_plugin/templates/blog.html) for available customization points. Here are some common ones:

- `.md-typeset .blog-post-title`: post title
- `.md-typeset .blog-post-description`: post description
- `.md-typeset .blog-post-extra`: extra section for creation / revision time

For more about HTML templates, refer to [jinja2's documentation](https://jinja.palletsprojects.com/en/3.0.x/).

#### Global Override

Alternatively, you can provide a template that works completely independent from the original template.

These variables are available inside your template:

- `pages`: sorted blog pages, see mkdocs's documentation for available attributes
- `page_size`: page count in each page
- `is_revision`: `True` if sorted by revision time, `False` if by creation time
- `show_total`: whether to show the total number of the blog

You can refer to [the original template](mkdocs_blogging_plugin/templates/blog.html) for help.

## Publishing on Github Pages

A few more steps needs to be taken for hosting on Github Pages:

- Set `fetch-depth` to `0` when checking out with `actions/checkout`:

  ```yml
  - uses: actions/checkout@v2
    with:
      fetch-depth: 0
  ```
  
  Creation and revision time for articles rely on git log, so a complete respository
  is required.
  
- Configure your locale in the plugin's configuration:

  ```yml
  locale: zh-CN
  ```
  
  Otherwise, the plugin will use locale of the server, which is `en` by default.

## Credits

Inspired by [mkdocs-git-revision-date-localized-plugin](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin) and [mkdocs-material-blog](https://github.com/vuquangtrong/mkdocs-material-blog).
