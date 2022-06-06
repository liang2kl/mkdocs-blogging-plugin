## Tags

This feature enables you to set tags for articles, which can be used to group them into different topics.

![preview](https://s2.loli.net/2021/12/03/H8wD4yY6W57TFbg.png)

### Setup

First, enable `tags` in the `features` entry of the configuration. Note that it is a dict, so by default (with no customize options), you should provide an empty dict `{}`:

```yaml title="mkdocs.yml"
features:
  tags: {}
```

And, in any article to be tagged (including those not in the designated blog collection), add any number of tags in the meta section:

```markdown title="article"
---
tags:
  - mkdocs
  - blogging
---
```

Now, if you are not using customized templates, the tags will be displayed on the blog entries.

For those who use a [customized template](template.md), you need a little extra work to get there. In the place you want to insert the tags of a page, insert following content, where `page` should be replaced by your naming of the variable, if necessary:

```jinja title="template"
{% if show_tags and "tags" in page.meta %}
    {% call render_tags(page.meta["tags"], index_url) %}
    {% endcall %}
{% endif %}
```

### Get an index page

Additionally, you can create an index page for all the tags and associated entries out of the box. Just like the blog content, add `{{ tag_content }}` in your desired position, and an index page will be there for you.

```markdown title="tags index page"
# Tags

{{ tag_content }}
```

![preview](https://s2.loli.net/2021/12/03/AudcmgG9N5HzEn4.png)

Although you can insert the "index" page in multiple pages, it is recommended to specify a single index page, so that we can navigate the viewer to that page when they click on the tags. To achieve this, set `index_page` with the relative path of one of the page with `{{ tag_content }}`:

```yaml title="mkdocs.yml"
features:
  tags:
    index_page: tags.md
```

### Insert tags in articles

You can display the tags of the article inside it if you like. Set `insert` to `top` or `bottom`, to add the tags to the top or bottom of all articles with at least one tag.

```yaml title="mkdocs.yml"
features:
  tags:
    insert: top
```

![preview](https://s2.loli.net/2021/12/03/DrYHLcmbqNKQznx.png)

!!!tip "Best practices"

    rather than using Header 1 in the markdown, set the title in the meta section:

    ```markdown title="article"
    ---
    title: Lorem ipsum dolor sit amet
    ---
    ```

    With this, the tags will be correctly displayed below the header, rather than above it.
