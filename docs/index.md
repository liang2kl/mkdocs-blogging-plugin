---
title: Setup
---

## Installation

```shell
# macOS or Linux
pip3 install mkdocs-blogging-plugin

# Windows
pip install mkdocs-blogging-plugin
```

## Prerequisites

- Only `material` theme is adapted by far
- `navigation.instant` feature cannot be enabled if blog paging is on

Pull requests are welcome to break these constraints.

## Usage

Before setting up the plugin, set `site_url` to the url of your published site:

``` yaml title="mkdocs.yml"
site_url: https://liang2kl.github.io/mkdocs-blogging-plugin/
```

### Basic

Add `blogging` in `plugins` and specify the directories to be included. This is the
minimum configuration needed.

``` yaml title="mkdocs.yml"
plugins:
  - blogging:
      dirs: # The directories to be included
        - blog
```

In the page you want to insert the blog content, add a line `{{ blog_content }}` into your desired place:

```markdown title="blog index page"
# Blogs

{{ blog_content }}
```

That's all. You can open the page where you insert `{{ blog_content }}` and see how it is working.

### More Configurations

Optionally, in your articles, add meta tags providing their titles and descriptions, which will be displayed on the blog page:

```markdown title="article"
---
title: Lorem ipsum dolor sit amet
description: Nullam urna elit, malesuada eget finibus ut, ac tortor.
---
```

You can also set tags for all articles. First, turn on this feature in the configuration:

```yaml title="mkdocs.yml"
plugins:
  - blogging:
      features:
        tags: {}
```

And in articles:

```markdown title="article"
---
tags:
  - mkdocs
  - blogging
---
```

For more detail, check [Features - tags](features.md#tags).

Finally, to exclude certain pages from the blog collection, add a meta tag `exclude_from_blog` in the meta section of the markdown file:

```markdown title="article"
---
exclude_from_blog: true
---
```

### Categories

Some people might need to setup different blog page, serving different sets of articles (see [this issue](https://github.com/liang2kl/mkdocs-blogging-plugin/issues/17)). For example,
one might setup a page for technical articles, and another for life recording. Another example is a
multi-language site, where we use different blog pages to display articles of different languages.

The plugin supports generating different blog index pages based on a concept
named *category*. A category is simply a group of directories used to generate
a blog page. For example:

```yaml title="categories"
plugins:
  - blogging:
      # {{ blog_content }}
      dirs:
        - blogs

      # {{ blog_content review }}
      categories:
        - name: review
          dirs:
            - review
```

We setup two categories here. The first one is the **default category** defining at the top level which includes
the articles in `blogs`, and the second is a **named category** which includes the articles
in `reviews`.

!!! question "Why there's a default category"

    Versions before `v2.0` didn't support category-based
    settings, so we preserve the top-level configuration
    for backward compatibility.

To generate a blog page for the default category:

```markdown title="index page for the default category"
{{ blog_content }}
```

To generate a blog page for a named category (in our case, `review`):

```markdown title="index page for category 'review'"
{{ blog_content review }}
```

## Options

### Category-specific Settings

You can specify the included directories for each category
and configure the options seperately. The *category-specific* settings include:

```yaml title="category settings"
dirs:              # The directories included in the category
  - reviews
  - ...
size: 5            # Number of articles in one page, default: 10
sort: 
  from: new        # Sort from new to old, default
  # or old         # Sort from old to new
  by: creation     # Sort by the first commit time, default
  # or revision    # Sort by the latest commit time
paging: false      # Disable paging
show_total: false  # Remove 'total pages' label
full_content: true # Use the full content for blog description
template: blog-override.html # Path to customized template
theme:             # Use a predefined theme
  name: card
```

The structure for the configuration in `mkdocs.yml`:

```yaml title="mkdocs.yml"
plugins:
  - blogging:
      dirs:
        - blogs
      size: 5
      ...

      categories:
        - name: review
          dirs:
            - review
          size: 10
          ...
```

For more about themes and custom templates, see [Themes](theme.md) and [Template](template.md) respectively.

### Global Settings

Aside from the category settings, there are some globally applied options, which should be defined
at the top level of the plugin configuration:

```yaml title="mkdocs.yml"
features:          # Additional features
  tags:
    ...
locale: en         # The locale for time localizations, default: system's locale
time_format: '%Y-%m-%d %H:%M:%S' # The format used to display the time
meta_time_format: '%Y-%m-%d %H:%M:%S' # The format used to parse the time from meta
```

Of all the options mentioned above, these deserve special attention:

- `time_format` in *global settings* is used to change the display style of the time, with higher priority than `locale`. 

- `meta_time_format` in *global settings* is used to tell the plugin how to parse the given time string from the meta. 
  - When `meta_time_format` is set, for all posts with a `time` or `date` metadata, the plugin will
  use this format to parse the time, and replace the timestamp from git logs. This is
  useful to alter specific posts' time if git commit time is not accurate or desired.
  See [the list of datetime placeholders](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) for reference.
  
    Please make sure that the time is wrapped by quotes \(issue [#48](https://github.com/liang2kl/mkdocs-blogging-plugin/issues/48)\). Otherwise, native YAML date and time literals will always be used if present in the file metadata, regardless of this setting. For example:

    ```yaml
    time: 2023-4-13 00:48               # without quotes
    time: !!timestamp "2023-4-13 00:48" # provide the `timestamp` tag
    ```

- When `paging` in *category settings* is set to `false`, if `size` is not set, all posts will be displayed on the first page; otherwise the first
`size` posts will be displayed and *the rest will not*.

## Publish with Github Pages

A few more steps need to be taken for hosting with Github Pages:

**Set `fetch-depth` to `0` when checking out with `actions/checkout`**

```yaml title="github action"
- uses: actions/checkout@v2
  with:
    fetch-depth: 0
```

Creation and revision time for articles rely on git logs, so a complete respository is required.
If it is not set, the plugin will take the build time as fallback.

**Configure your locale in the plugin's configuration**

```yaml title="article"
plugins:
  - blogging:
      locale: zh_CN
```

Otherwise, the plugin will use locale of the server, which might not be expected.
