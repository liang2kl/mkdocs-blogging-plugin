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

Finally, to exclude certain pages from the blog collection, add a meta tag `exculde_from_blog` in the meta section of the markdown file:

```markdown title="article"
---
exculde_from_blog: true
---
```

## Options

### Category-specific Settings

The plugin supports generating different blog index pages based on a concept
named *category*. You can specify the included directories for each category
and configure the customizing options seperately. It enables you to setup multiple
blog index pages, each with specific purpose.
For example, one might setup a page for technical articles, and another for life recording.

The category-specific settings include:

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
template: blog-override.html # Path to customized template
theme:             # Use a predefined theme
  name: card
```

For more about themes and custom templates, see [Themes](theme.md) and [Template](template.md) respectively.

The structure for the configuration in `mkdocs.yml`:

```yaml title="mkdocs.yml"
plugins:
  - blogging:
      # --- GLOBAL-CATEGORY: configs for {{ blog_content }} ---
      dirs:
        - blogs
      size: 5
      ...
      # --- END GLOBAL CATEGORY ---

      # --- INDIVIDUAL CATEGORIES: configs for {{ blog_content name }} ---
      categories:
        - name: review
          dirs:
            - review
          size: 5
          ...
      # --- END INDIVIDUAL CATEGORIES ---
```

Noted that you can either setup settings mentioned above at the root level of the plugin config,
or define them within a specific category. The former will apply to `{{ blog_content }}`, and the
latter will apply to `{{ blog_content name }}`, where `name` is the name of the category.

### Global Settings

Aside from the category settings, there are some globally applied options, which should be defined
at the root level of the plugin configuration:

```yaml title="mkdocs.yml"
features:          # Additional features
  tags:
    ...
locale: en         # The locale for time localizations, default: system's locale
time_format: '%Y-%m-%d %H:%M:%S' # The format used to display the time
meta_time_format: '%Y-%m-%d %H:%M:%S' # The format used to parse the time from meta
```

Of all the options mentioned above, these parameters deserve special attention:

- `time_format` in *global settings* is used to change the display style of the time, with higher priority than `locale`. 

- `meta_time_format` in *global settings* is used to tell the plugin how to parse the given time string from the meta. 
When `meta_time_format` is set, for all posts with a `time` or `date` metadata, the plugin will
use this format to parse the that time, and replace the time from git logs. This is
useful to alter specific posts' time when git commit time is not accurate or desired.
See [the list of datetime placeholders](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes).

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
If it is not set, the plugin will take the latest commit time as fallback.

**Configure your locale in the plugin's configuration**

```yaml title="article"
plugins:
  - blogging:
      locale: zh-CN
```

Otherwise, the plugin will use locale of the server, which might not be expected.
