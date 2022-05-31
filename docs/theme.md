You can select one from the plugin's built-in themes to render your content. If you are to use one of them, in the plugin's config, specify the theme's name, and optionally specify some options to customize the appearance.

Note that this is a *category-specific* setting, so you should set them for each category seperately.

```yaml title="mkdocs.yml"
plugins:
  - blogging:
      theme:
        name: <theme name>
        options:
          <theme options>
```

You can use one of the predefined themes:

### Card

Display the blog entries as cards with hover effects.

```yaml title="mkdocs.yml"
plugins:
  - blogging:
      theme:
        name: card
```

![card](https://i.loli.net/2021/12/02/91UlyeKPOVuRwvq.png)

### Button

Add "Continue Reading" button.

```yaml title="mkdocs.yml"
plugins:
  - blogging:
      theme:
        name: button
        options: # Optional
          # `true` if display the button as plain text
          # `false` or not present if display as rectangle button
          plain_button: true
          # Replacement for 'Continue Reading'
          label: Read
```

![button](https://i.loli.net/2021/12/02/r1eEQYmFwXOT5jD.png)