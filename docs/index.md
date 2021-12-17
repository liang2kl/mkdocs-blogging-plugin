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

Add `blogging` in `plugins` and specify the directories to be included:

``` yaml title="mkdocs.yml"
plugins:
  - blogging:
      dirs: # The directories to be included
        - blog
```

In the page you want to insert the blog content, just add a line `{{ blog_content }}` into your desired place:

```markdown title="blog index page"
# Blogs

{{ blog_content }}
```

Optionally, in your articles, add meta tags providing their titles and descriptions, which will be displayed on the blog page:

```markdown title="article"
---
title: Lorem ipsum dolor sit amet
description: Nullam urna elit, malesuada eget finibus ut, ac tortor.
---
```

Additionally, you can also set tags for all articles, which can be access on certain pages. First, turn on this feature in the configuration:

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

To exclude certain pages from the blog collection, add a meta tag `exculde_from_blog` in the meta section of the markdown file:

```markdown title="article"
---
exculde_from_blog: true
---
```

And it's done! You can open the page where you insert `{{ blog_content }}` and see how it is working.

## Options

Configure the plugin via following options:

```yaml title="mkdocs.yml"
theme:             # Use a predefined theme
  name: card
features:          # Additional features
  tags:
    ...
size: 5            # Number of articles in one page, default: 10
locale: en         # The locale for time localizations, default: system's locale
time_format: '%Y-%m-%d %h:%m:%s' # The format used to display the time
meta_time_format: '%Y-%m-%d %h:%m:%s' # The format used to parse the time from meta
sort: 
  from: new        # Sort from new to old, default
  # or old         # Sort from old to new
  by: creation     # Sort by the first commit time, default
  # or revision    # Sort by the latest commit time
paging: false      # Disable paging
show_total: false  # Remove 'total pages' label
template: blog-override.html # Path to customized template
```

`time_format` is used to change the display style of the time, with higher priority than `locale`. 

`meta_time_format` is used to tell the plugin how to parse the given time string from the meta. 
When `meta_time_format` is set, for all posts with a `time` or `date` metadata, the plugin will
use this format to parse the that time, and replace the time from git logs. This is
useful to alter specific posts' time where git commit time is not accurate or desired.

For more about themes and custom templates, see [Themes](theme.md) and [Template](template.md) respectively.

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
