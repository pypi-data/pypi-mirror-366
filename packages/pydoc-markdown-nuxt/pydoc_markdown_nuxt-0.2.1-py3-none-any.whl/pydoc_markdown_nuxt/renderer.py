# -*- coding: utf8 -*-

"""
Module for rendering Python API documentation in a format suitable for Nuxt Content.
This module defines a customized Markdown renderer that generates Markdown files
with a specific structure for Nuxt Content.
"""

import dataclasses
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, TextIO

import docspec
import jinja2
import typing_extensions as te
from databind.core import DeserializeAs
from pydoc_markdown.contrib.renderers.markdown import MarkdownReferenceResolver, MarkdownRenderer
from pydoc_markdown.interfaces import Context, Renderer
from pydoc_markdown.util.misc import escape_except_blockquotes

logger: logging.Logger = logging.getLogger(__name__)


@dataclasses.dataclass
class NuxtReferenceResolver(MarkdownReferenceResolver):
    """
    Custom reference resolver for Nuxt Content.
    This resolver generates links to the Markdown files in the Nuxt Content structure.
    """

    output_dir: str = dataclasses.field(default="references")

    def resolve_ref(self, scope: docspec.ApiObject, ref: str) -> str | None:
        """
        Resolve a reference to an object by its name and return the link to its Markdown file.
        This method overrides the default reference resolver to generate links
        in the format expected by Nuxt Content.
        Args:
            scope (docspec.ApiObject): The API object to resolve the reference for.
            ref (str): The reference string to resolve.
        Returns:
            str | None: The resolved link or None if not found.
        """
        target: docspec.ApiObject | None = self._resolve_local_reference(scope, ref.split("."))
        if target:
            if isinstance(target, docspec.Indirection):
                # For indirections, the full path is in the 'target' attribute.
                path = target.target.replace(".", "/").lower()
            else:
                path = self.generate_object_id(target).replace(".", "/").lower()

            # Prepend the output_dir to the path, stripping Nuxt Content numeric prefixes
            if self.output_dir:
                # Remove numeric prefix like `3.` from `3.references` for link generation
                link_output_dir = re.sub(r"^\d+\.", "", self.output_dir)
                return f"/{link_output_dir}/{path}"
            return f"/{path}"
        return None


@dataclasses.dataclass
class NuxtMarkdownRenderer(MarkdownRenderer):
    """
    Customized Markdown Renderer for Nuxt Content.
    This renderer generates Markdown files with a specific structure for Nuxt Content.

    Args:
        insert_header_anchors (bool): Whether to insert anchors in headers.
        escape_html_in_docstring (bool): Whether to escape HTML in docstrings.
        object_icons (dict): Icons for different object types.
        module_frontmatter_template (str): Template for the frontmatter of module files.
    """

    insert_header_anchors: bool = False
    escape_html_in_docstring: bool = True
    output_dir: str = dataclasses.field(default="references")
    jinja_env: jinja2.Environment = dataclasses.field(init=False, repr=False)

    object_icons: Dict[str, str] = dataclasses.field(
        default_factory=lambda: {
            "module": "i-codicon-library",
            "class": "i-codicon-symbol-class",
            "function": "i-codicon-symbol-method",
            "method": "i-codicon-symbol-method-arrow",
            "variable": "i-codicon-symbol-variable",
            "indirection": "i-codicon-symbol-namespace",
            "argument": "i-codicon-symbol-parameter",
            "default": "i-codicon-symbol-property",
        }
    )

    module_frontmatter_template: str = (
        "---\n"
        "title: '{{ title }}'\n"
        "description: '{{ description }}'\n"
        "navigation:\n"
        "    title: '{{ title }}'\n"
        "    icon: '{{ icon }}'\n"
        "---\n"
    )

    member_header_template: str = (
        "{% if level > 0 %}"
        "{{ '#' * (level + 1) }} {{ title }}\n"
        "{% endif %}"
        "::reference-header\n"
        "---\n"
        "description: >\n"
        "    {{ description }}\n"
        "lang: 'python'\n"
        "type: '{{ object_type }}'\n"
        "{% if object_typing %}"
        "typing: '{{ object_typing }}'\n"
        "{% endif %}"
        "navigation:\n"
        "    title: '{{ title }}'\n"
        "    icon: '{{ icon }}'\n"
        "    level: {{ level }}\n"
        "---\n"
        "{% if object_value %}\n"
        "```python\n"
        "{% if object_typing %}"
        "{{ title }}: {{ object_typing }} = {{ object_value }}\n"
        "{% else %}"
        "{{ title }} = {{ object_value }}\n"
        "{% endif %}"
        "```\n"
        "{% endif %}"
        "::\n"
    )

    def init(self, context: Context) -> None:
        """
        Initializes the renderer. This is called after the configuration is loaded
        but before rendering begins. We create the reference resolver here to ensure
        it receives the correct `output_dir`.

        Args:
            context (Context): The context in which the renderer is initialized.
        """
        super().init(context)
        self._resolver: MarkdownReferenceResolver = NuxtReferenceResolver(
            output_dir=self.output_dir,
        )
        self.jinja_env = jinja2.Environment(
            loader=jinja2.DictLoader(
                {
                    "module_frontmatter": self.module_frontmatter_template,
                    "member_header": self.member_header_template,
                }
            )
        )

    def _get_object_type(self, obj: docspec.ApiObject) -> str:
        """Get the icon key for the object type.
        This method determines the icon key based on the type of the object.

        Args:
            obj (docspec.ApiObject): The API object to get the icon key for.
        Returns:
            str: The icon key for the object type.
        """
        if isinstance(obj, docspec.Class):
            return "class"
        if isinstance(obj, docspec.Function):
            is_method = obj.parent and isinstance(obj.parent, docspec.Class)
            return "method" if is_method else "function"
        if isinstance(obj, docspec.Module):
            return "module"
        if isinstance(obj, docspec.Variable):
            return "variable"
        if isinstance(obj, docspec.Indirection):
            return "indirection"
        if isinstance(obj, docspec.Argument):
            return "argument"
        return "default"

    def _render_header(self, fp: TextIO, level: int, obj: docspec.ApiObject) -> None:
        """
        Render the header for the object.
        Args:
            fp (TextIO): The file pointer to write the header to.
            level (int): The header level.
            obj (docspec.ApiObject): The API object to render the header for.
        """
        title = obj.name
        description = (obj.docstring.content.split("\n", 1)[0]) if obj.docstring else f"API reference for {obj.name}"

        object_type = self._get_object_type(obj)
        if object_type == "indirection":
            return  # Indirections do not have a header
        icon = self.object_icons.get(object_type, self.object_icons["default"])

        template_name = "member_header" if level > 0 else "module_frontmatter"
        template = self.jinja_env.get_template(template_name)

        context = {
            "title": title,
            "description": description,
            "icon": icon,
            "level": level,
            "object_name": obj.name,
            "object_type": object_type,
            "object_typing": getattr(obj, "datatype", None),
            "object_value": getattr(obj, "value", None),
        }

        fp.write(template.render(**context))
        fp.write("\n\n")

    def _render_object(self, fp: TextIO, level: int, obj: docspec.ApiObject) -> None:
        """
        Render the object (class, function, etc.) to the file pointer.

        Args:
            fp (TextIO): The file pointer to write the object to.
            level (int): The header level for the object.
            obj (docspec.ApiObject): The API object to render.
        """
        self._render_header(fp, level, obj)

        render_view_source = not isinstance(obj, (docspec.Module, docspec.Variable))
        source_string = self._get_source_string(obj) if render_view_source else None

        if source_string and self.source_position == "before signature":
            fp.write(source_string + "\n\n")

        self._render_signature_block(fp, obj)

        if source_string and self.source_position == "after signature":
            fp.write(source_string + "\n\n")

        self._render_docstring(fp, obj)

    def _get_source_string(self, obj: docspec.ApiObject) -> Optional[str]:
        """
        Get the source string for the object.

        Args:
            obj (docspec.ApiObject): The API object to get the source string for.

        Returns:
            Optional[str]: The formatted source string or None if no source URL is available.
        """
        url = self.source_linker.get_source_url(obj) if self.source_linker else None
        return self.source_format.replace("{url}", str(url)) if url else None

    def _render_docstring(self, fp: TextIO, obj: docspec.ApiObject) -> None:
        """
        Render the docstring for the object.
        Args:
            fp (TextIO): The file pointer to write the docstring to.
            obj (docspec.ApiObject): The API object to render the docstring for.
        """
        if obj.docstring:
            docstring = (
                escape_except_blockquotes(obj.docstring.content)
                if self.escape_html_in_docstring
                else obj.docstring.content
            )
            lines = docstring.split("\n")
            if self.docstrings_as_blockquote:
                lines = ["> " + x for x in lines]
            fp.write("\n".join(lines))
            fp.write("\n\n")


@dataclasses.dataclass
class NuxtRenderer(Renderer):
    """
    Renderer for Nuxt Content, generating a directory structure for each module
    and a Markdown file for each member (class/function) of the module.

    Attributes:
        content_dir (str): The directory where the content will be stored.
        output_dir (str): The subdirectory where the rendered files will be placed.
        markdown (MarkdownRenderer): The Markdown renderer to use for rendering the content.

    """

    markdown: te.Annotated[MarkdownRenderer, DeserializeAs(NuxtMarkdownRenderer)] = dataclasses.field(
        default_factory=NuxtMarkdownRenderer
    )
    content_dir: str = "content"
    output_dir: str = "references"

    def init(self, context: Context) -> None:
        if isinstance(self.markdown, NuxtMarkdownRenderer):
            self.markdown.output_dir = self.output_dir
        self.markdown.init(context)

    def render(self, modules: List[docspec.Module]) -> None:
        """
        Renderiza los módulos, creando una carpeta por módulo y un archivo por miembro.

        Args:
            modules (List[docspec.Module]): Lista de módulos a renderizar.

        """
        output_path: Path = Path(self.content_dir) / self.output_dir

        for module in modules:
            module_path_parts: list[str] = module.name.split(".")

            # Crea el directorio para el módulo.
            # Ej: content/references/mi_paquete/mi_modulo
            module_dir = output_path.joinpath(*module_path_parts)
            module_dir.mkdir(parents=True, exist_ok=True)
            # --- 1. Renderizar el archivo de navegación del módulo ---
            navigation_path = module_dir / ".navigation.yml"
            with navigation_path.open("w", encoding=self.markdown.encoding) as nav_fp:
                logger.info("Generando navegación del módulo: %s", navigation_path)
                nav_fp.write(f'title: "{module.name}"\n')
                nav_fp.write('icon: "i-codicon-library"\n')

            # --- 2. Renderizar el archivo _index.md para el módulo ---
            index_path = module_dir / "index.md"

            with index_path.open("w", encoding=self.markdown.encoding) as fp:
                logger.info("Generando índice de módulo: %s", index_path)
                # render_single_page usa el 'render_module_header_template'
                self.markdown.render_object(fp, module, {})
