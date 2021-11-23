# mkdocs-blogging-plugin

A mkdocs plugin that generates a blog page listing selected pages, sorted by time.

![preview](https://i.loli.net/2021/09/09/LhX9IFkbu2K3lRi.png)

## Installation

```shell
pip3 install mkdocs-blogging-plugin
```

## Prerequisites

- Only `material` theme is adapted by far (pull requests are welcome).
- `navigation.instant` feature cannot be enabled if blog paging is on.
- Windows is not supported currently (pull requests are welcome).

## Usage

Add `blogging` in `plugins` and specify the directories to be included:

```yml
plugins:
  - blogging:
      dirs: # The directories to be included
        - blog
```

In the page you want to insert the blog content, just add a line `{{ blog_content }}` into your desired place:

```markdown
# Blogs

{{ blog_content }}
```

Optionally, in your articles, add meta tags providing their titles and descriptions, which will be displayed on the blog page:

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

Some more steps need to be taken if you want to host your blog with GitHub Pages.
Please refer to [Publishing on Github Pages](#publishing-on-github-pages).

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

### Override the Template

The `template` entry in the configuration allows you to override the appearance of the blog page.

To customize the appearance, create an HTML template with name **other than `blog.html`**, then provide
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

For introduction and usage of HTML templates, refer to [jinja's documentation](https://jinja.palletsprojects.com/en/3.0.x/).

You have the following customization options:

#### Partial Customization

You can override how the plugin render a single blog entry through this method. An example can be found [here](https://github.com/liang2kl/mkdocs-blogging-plugin-example).

In your template, import the original template:

```jinja
{% extends "blog.html" %}
```

Then, define a macro named `render_blog` with parameters `title`, `description`, `time` and `url`, which
returns HTML elements that represent a single blog entry.
Please note that `{{ caller() }}` must be present somewhere inside the macro, though it has no use here.

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
```

Further more, if you want to customize the css, write a block named `style`. Call `{{ super() }}` first
if you want to preserve the original styles.

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

#### Global Override

Alternatively, you can provide a template that works completely independent from the original template.

These variables are available inside your template:

- `pages`: sorted blog pages, see mkdocs' documentation for available attributes
- `page_size`: number of articles on a single page
- `is_revision`: `True` if sorted by revision time, `False` if by creation time
- `show_total`: whether to show the total number of the blog

You can refer to [the original template](mkdocs_blogging_plugin/templates/blog.html) for help.

## Publishing on Github Pages

A few more steps need to be taken for hosting with Github Pages:

- Set `fetch-depth` to `0` when checking out with `actions/checkout`:

  ```yml
  - uses: actions/checkout@v2
    with:
      fetch-depth: 0
  ```
  
  Creation and revision time for articles rely on git logs, so a complete respository is required.
  If it is not set, the plugin will take the latest commit time as fallback.

- Configure your locale in the plugin's configuration:

  ```yml
  locale: zh-CN
  ```
  
  Otherwise, the plugin will use locale of the server, which might not be expected.

## Credits

Inspired by [mkdocs-git-revision-date-localized-plugin](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin) and [mkdocs-material-blog](https://github.com/vuquangtrong/mkdocs-material-blog).
