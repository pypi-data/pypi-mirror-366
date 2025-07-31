import docspec
import pytest

from pydoc_markdown_nuxt.renderer import NuxtMarkdownRenderer, NuxtRenderer


def make_location(filename):
    return docspec.Location(filename=filename, lineno=1)


def make_module(name, filename, members):
    return docspec.Module(
        name=name,
        docstring=None,
        location=make_location(filename),
        members=members,
    )


def make_class(name, filename):
    return docspec.Class(
        name=name,
        docstring=None,
        location=make_location(filename),
        bases=[],
        members=[],
        metaclass=None,
        decorations=[],
    )


def make_function(name, filename):
    return docspec.Function(
        name=name,
        docstring=None,
        location=make_location(filename),
        args=[],
        return_type=None,
        modifiers=[],
        decorations=[],
    )


@pytest.fixture
def temp_content_dir(tmp_path):
    content_dir = tmp_path / "content"
    content_dir.mkdir()
    return content_dir


def test_render_creates_module_and_member_files(temp_content_dir, monkeypatch):
    filename = "mod1.py"
    class1 = make_class("MyClass", filename)
    func1 = make_function("my_function", filename)
    private_func = make_function("_private_func", filename)
    ext_func = make_function("external_func", "other.py")
    module = make_module("package.mod1", filename, [class1, func1, private_func, ext_func])

    renderer = NuxtRenderer(content_dir=str(temp_content_dir), output_dir="references")

    single_page_calls = []
    object_calls = []

    def fake_render_single_page(*args, **kwargs):
        single_page_calls.append((args, kwargs))
        # args[0] is the file pointer (fp)
        fp = args[0]
        fp.write("dummy")

    def fake_render_object(*args, **kwargs):
        object_calls.append((args, kwargs))
        # args[0] is the file pointer (fp)
        fp = args[0]
        fp.write("dummy")

    monkeypatch.setattr(renderer.markdown, "render_single_page", fake_render_single_page)
    monkeypatch.setattr(renderer.markdown, "render_object", fake_render_object)
    renderer.markdown.encoding = "utf-8"

    renderer.render([module])

    mod_dir = temp_content_dir / "references" / "package" / "mod1"
    assert mod_dir.exists()

    index_md = mod_dir / "_index.md"
    assert index_md.exists()
    assert len(single_page_calls) == 1

    class_md = mod_dir / "MyClass.md"
    func_md = mod_dir / "my_function.md"
    private_md = mod_dir / "_private_func.md"
    ext_md = mod_dir / "external_func.md"

    assert class_md.exists()
    assert func_md.exists()
    assert not private_md.exists()
    assert not ext_md.exists()

    member_names = [call[0][1].name for call in object_calls]
    assert set(member_names) == {"MyClass", "my_function"}


def test_nuxt_markdown_renderer_templates():
    renderer = NuxtMarkdownRenderer()
    # Test that the templates are properly defined
    assert "title: '{{ title }}'" in renderer.module_frontmatter_template
    assert "description: '{{ description }}'" in renderer.module_frontmatter_template
    assert "navigation:" in renderer.module_frontmatter_template

    assert "::reference-header" in renderer.member_header_template
    assert "type: '{{ object_type }}'" in renderer.member_header_template
    assert "icon: '{{ icon }}'" in renderer.member_header_template


def test_init_calls_markdown_init(monkeypatch):
    renderer = NuxtRenderer()
    from pydoc_markdown.interfaces import Context

    context = Context(directory="test_directory")
    called = {}

    def fake_init(ctx):
        called["ctx"] = ctx

    monkeypatch.setattr(renderer.markdown, "init", fake_init)
    renderer.init(context)
    assert called["ctx"] is context
