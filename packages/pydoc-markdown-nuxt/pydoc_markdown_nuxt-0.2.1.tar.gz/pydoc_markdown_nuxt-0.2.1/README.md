# pydoc-markdown-nuxt

A pydoc-markdown renderer for generating documentation compatible with Nuxt Content and MDC (Markdown Components).

## Overview

`pydoc-markdown-nuxt` extends [pydoc-markdown](https://github.com/NiklasRosenstein/pydoc-markdown) with a renderer that generates Markdown files following the [Nuxt Content](https://content.nuxtjs.org/) structure and conventions. This allows you to seamlessly integrate Python API documentation into Nuxt.js websites.

## Features

- **Nuxt Content Compatible**: Generates Markdown files with YAML frontmatter that work with Nuxt Content's file-based routing
- **Flexible Directory Structure**: Configure custom directory structures and file organization
- **YAML Frontmatter**: Full control over page metadata through configurable frontmatter
- **MDC Support**: Ready for MDC (Markdown Components) syntax extensions
- **Clean Integration**: Works with existing pydoc-markdown configurations and processors

## Installation

```bash
pip install pydoc-markdown-nuxt
```

## Quick Start

Create a `pydoc-markdown.yml` configuration file:

```yaml
loaders:
  - type: python
    search_path: [src]

processors:
  - type: filter
    expression: not name.startswith('_')
  - type: smart
  - type: crossref

renderer:
  type: nuxt
  content_dir: docs/content
  output_dir: 3.references
```

Then run:

```bash
pydoc-markdown
```

This will generate Nuxt Content compatible Markdown files in the `docs/content/3.references` directory with a hierarchical structure based on your Python modules.

## Configuration

### Basic Options

- `content_dir`: Directory where content files are generated (default: `content`)
- `output_dir`: Subdirectory within content_dir where the rendered files will be placed (default: `references`)

The renderer uses the `NuxtMarkdownRenderer` internally which provides additional customization options:

- `insert_header_anchors`: Whether to insert anchors in headers (default: `false`)
- `escape_html_in_docstring`: Whether to escape HTML in docstrings (default: `true`)
- `object_icons`: Dictionary mapping object types to icon classes
- `module_frontmatter_template`: Jinja2 template for module frontmatter
- `member_header_template`: Jinja2 template for member headers

### Directory Structure

The renderer generates a hierarchical directory structure based on your Python modules:

```
content/
└── {output_dir}/
    └── {module_name}/
        ├── .navigation.yml
        ├── index.md
        └── {submodules}/
```

### Example Configuration

```yaml
loaders:
  - type: python
    search_path: [src]

processors:
  - type: filter
    expression: not name.startswith('_')
  - type: filter
    expression: not name.startswith('test_')
  - type: smart
  - type: crossref

renderer:
  type: nuxt
  content_dir: docs/content
  output_dir: 3.references
```

## Generated Output

The renderer generates Markdown files with YAML frontmatter following Nuxt Content structure:

### Module Files (`index.md`)
```markdown
---
title: 'module_name'
description: 'Module description from docstring'
navigation:
    title: 'module_name'
    icon: 'i-codicon-library'
---

# Module Documentation

Module docstring content here...
```

### Class/Function Files (with MDC components)
```markdown
## MyClass

::reference-header
---
description: >
    A sample class for demonstration.
lang: 'python'
type: 'class'
navigation:
    title: 'MyClass'
    icon: 'i-codicon-symbol-class'
    level: 1
---
::

Class docstring content...

### my_method

::reference-header
---
description: >
    A sample method that does something useful.
lang: 'python'
type: 'method'
navigation:
    title: 'my_method'
    icon: 'i-codicon-symbol-method-arrow'
    level: 2
---
::

Method docstring content...
```

### Navigation Files (`.navigation.yml`)
```yaml
title: "module_name"
icon: "i-codicon-library"
```

## Integration with Nuxt Content

The generated files work seamlessly with Nuxt Content:

1. **File-based Routing**: Files in `content/` automatically become pages
2. **Hierarchical Navigation**: Automatic navigation based on directory structure
3. **Navigation Files**: `.navigation.yml` files control sidebar appearance
4. **MDC Components**: Uses `::reference-header` component for rich documentation display
5. **Icon Support**: Integrated with Iconify for consistent iconography

## MDC Components

The renderer uses custom MDC components for enhanced documentation:

```markdown
::reference-header
---
description: >
    Method or class description
lang: 'python'
type: 'method'
typing: 'str'  # Optional type annotation
navigation:
    title: 'method_name'
    icon: 'i-codicon-symbol-method'
    level: 2
---
::
```

This allows for rich, interactive documentation with consistent styling across your API reference.

## Development

To contribute to this project:

```bash
git clone https://github.com/UrielCuriel/pydoc-markdown-nuxt
cd pydoc-markdown-nuxt
pip install -e .
```

Run tests:

```bash
pytest
```

Generate documentation for testing:

```bash
pydoc-markdown
```

## License

MIT License - see LICENSE file for details.
