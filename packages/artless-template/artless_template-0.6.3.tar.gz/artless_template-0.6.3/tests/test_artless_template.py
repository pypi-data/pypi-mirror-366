from pathlib import Path
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import mock_open, patch

from artless_template import (
    _VOID_TAGS,
    Component,
    Tag,
    Template,
    aread_template,
    read_template,
)


class TestVoidTags(TestCase):
    def test_void_tags_are_correct(self):
        expected_tags = {
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "source",
            "track",
            "wbr",
        }
        self.assertEqual(_VOID_TAGS, expected_tags)
        self.assertIsInstance(_VOID_TAGS, frozenset)


class TestTag(TestCase):
    TEST_CASES = [
        # (name, attrs, children, text, expected)
        ("div", {}, None, None, "<div></div>"),
        ("div", {"id": "superblock"}, None, None, '<div id="superblock"></div>'),
        ("div", None, None, "Test", "<div>Test</div>"),
        ("div", {"id": "superblock"}, None, "Test", '<div id="superblock">Test</div>'),
        (
            "div",
            {"id": "some-id", "class": "some-class", "data-field": "some data field"},
            None,
            "Some text",
            '<div id="some-id" class="some-class" data-field="some data field">Some text</div>',
        ),
        (
            "div",
            {"class": "parent"},
            [Tag("div", {"class": "child"}, [Tag("span", "Span text")], "Child text")],
            "Parent text",
            '<div class="parent"><div class="child"><span>Span text</span>Child text</div>Parent text</div>',
        ),
        ("br", {}, None, None, "<br />"),
        (
            "area",
            {"data-url": "https://www.w3.org/"},
            None,
            None,
            '<area data-url="https://www.w3.org/" />',
        ),
        ("area", None, None, "Text that will not be shown", "<area />"),
        ("area", None, [Tag("span")], None, "<area />"),
    ]

    def test_tag_expected(self):
        for name, attrs, children, text, expected in self.TEST_CASES:
            with self.subTest(tag=name, expected=expected):
                self.assertEqual(str(Tag(name, attrs, children, text)), expected)

    def test_simple_tag_creation(self):
        tag = Tag("div")
        self.assertEqual(str(tag), "<div></div>")
        self.assertEqual(repr(tag), "<Tag: 'div'>")

    def test_tag_with_attributes(self):
        tag = Tag("div", {"id": "main", "class": "container"})
        self.assertEqual(str(tag), '<div id="main" class="container"></div>')

    def test_tag_with_text(self):
        tag = Tag("p", "Hello world")
        self.assertEqual(str(tag), "<p>Hello world</p>")

    def test_tag_children(self):
        child = Tag("span", "child")
        parent = Tag("div", [child])
        self.assertEqual(str(parent), "<div><span>child</span></div>")

    def test_tag_with_stringify_children(self):
        stringify_objects = ["string", 123, 123.0, None, True, [], {}, (None)]
        for obj in stringify_objects:
            tag = Tag("span", [obj])
            self.assertEqual(str(tag), f"<span>{obj}</span>")

    def test_void_tag_rendering(self):
        for tag_name in _VOID_TAGS:
            with self.subTest(tag=tag_name):
                tag = Tag(tag_name)
                self.assertTrue(str(tag).endswith(" />"))

    def test_add_child(self):
        parent = Tag("ul")
        child = Tag("li", "item")
        parent.add_child(child)
        self.assertEqual(str(parent), "<ul><li>item</li></ul>")
        self.assertEqual(child.parent, parent)

    def test_add_invalid_child(self):
        parent = Tag("ul")
        child = "not a Tag instance"
        with self.assertRaises(TypeError) as exc:
            parent.add_child(child)
        self.assertEqual(str(exc.exception), "Child must be Tag instance, got str")

    def test_tag_properties(self):
        leaf = Tag("div")
        parent = Tag("div", [Tag("span")])

        self.assertTrue(leaf.is_leaf)
        self.assertFalse(leaf.is_parent)
        self.assertFalse(parent.is_leaf)
        self.assertTrue(parent.is_parent)

    def test_invalid_child_type(self):
        with self.assertRaises(TypeError):
            Tag("div", "text", 123)  # 123 is not a valid child


class TestTemplate(TestCase):
    def setUp(self):
        self.template_content = "<html><body>@content</body></html>"
        self.template = Template(name="test", content=self.template_content)

    def test_template_repr(self):
        self.assertEqual(repr(self.template), "<Template: 'test'>")

    def test_render_with_simple_context(self):
        result = self.template.render(content="Hello")
        self.assertEqual(result, "<html><body>Hello</body></html>")

    def test_render_with_component(self):
        class TestComponent(Component):
            def view(self) -> Tag:
                return Tag("div", "Component content")

        result = self.template.render(content=TestComponent())
        self.assertEqual(result, "<html><body><div>Component content</div></body></html>")

    def test_render_with_multiple_vars(self):
        template = Template(name="multi", content="@a @b @a")
        result = template.render(a="1", b="2")
        self.assertEqual(result, "1 2 1")

    def test_render_with_empty_context(self):
        self.assertEqual(self.template.render(), self.template_content)


class TestTemplateReading(TestCase):
    def setUp(self):
        self.test_content = "<html>@test</html>"
        self.mock_file = mock_open(read_data=self.test_content)
        self.patcher = patch("builtins.open", self.mock_file)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_read_template(self):
        template = read_template("test.html")

        self.mock_file.assert_called_once_with("test.html", "r", encoding="utf-8")
        self.assertIsInstance(template, Template)
        self.assertEqual(template.content, self.test_content)

    def test_read_template_with_path_object(self):
        path = Path("test.html")
        template = read_template(path)
        self.mock_file.assert_called_once_with(path, "r", encoding="utf-8")
        self.assertEqual(repr(template), "<Template: PosixPath('test.html')>")

    def test_render_template(self):
        path = Path("test.html")
        template = read_template(path)

        self.assertIsNone(template._compiled_pattern)
        self.assertEqual(template.render(test="hello"), "<html>hello</html>")
        # After first render expects cached template value
        self.assertIsNotNone(template._compiled_pattern)
        self.assertEqual(template.render(test=""), "<html>hello</html>")


class TestAsyncTemplateReading(IsolatedAsyncioTestCase):
    async def test_aread_template(self):
        test_content = "<html>Async</html>"
        with patch("builtins.open", mock_open(read_data=test_content)):
            template = await aread_template("async.html")

        self.assertIsInstance(template, Template)
        self.assertEqual(template.content, test_content)


class TestComponentProtocol(TestCase):
    def test_component_protocol(self):
        class SimpleComponent(Component):
            def view(self) -> Tag:
                return Tag("div", "Simple")

        self.assertIsInstance(SimpleComponent(), Component)

        # Test non-component class
        class NotAComponent:
            pass

        self.assertNotIsInstance(NotAComponent(), Component)
