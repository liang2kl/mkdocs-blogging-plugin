# Migration Guide

## v0.2.x to v0.3.x

Breaking changes:

- Added a new paramter `page` to `render_blog`.
    - **Effect:** This will stop previous macro definitions from working.
    - **Workaround:** Add a trailing parameter `page` to the marco.
- Introduced new reserved template file names: `blog-*-theme.html`. 
    - **Effect:** If you have templates using these names, they might stop working now or in the future.
    - **Workaround:** Rename them if your existing names of your templates have this pattern.

## v0.3.x to v1.0.x

Breaking changes:

- Introduced new reserved template file names: `blog-*.html`. 
    - **Effect:** If you have templates using these names, they might stop working now or in the future.
    - **Workaround:** Rename them if your existing names of your templates have this pattern.

## To v1.4.0

Breaking changes:

- Change post display behaviour when paging is disabled. 
    - **Effect:** Posts will be truncated if `paging = false` and `size` co-exist.
    - **Workaround:** If you need to keep all posts when paging is disabled, remove `size`.
