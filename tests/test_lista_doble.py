"""Edge-case tests for the manually implemented doubly linked list."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.lista_doble import DoublyLinkedList  # noqa: E402
from models.nodo import ImageNode  # noqa: E402


def make_image(name: str, category: str = "landscape", description: str = "") -> ImageNode:
    """Create an image node for tests."""
    return ImageNode(
        name=name,
        category=category,
        description=description or f"Description of {name}",
        date="2026-01-01",
        url=f"https://example.com/{name}.jpg",
    )


def make_list(*names: str) -> DoublyLinkedList:
    """Create a list containing the given names in order."""
    linked_list = DoublyLinkedList()
    for name in names:
        linked_list.add(make_image(name), "final")
    linked_list.current = linked_list.head
    return linked_list


def image_names(linked_list: DoublyLinkedList) -> list:
    """Return image names by traversing from head to tail."""
    return [image["nombre"] for image in linked_list.to_list()]


class TestEmptyList(unittest.TestCase):
    def setUp(self) -> None:
        self.linked_list = DoublyLinkedList()

    def test_no_current_image(self):
        self.assertIsNone(self.linked_list.get_current())
        self.assertTrue(self.linked_list.is_empty())

    def test_navigation_does_not_fail(self):
        self.assertFalse(self.linked_list.move_next())
        self.assertFalse(self.linked_list.move_previous())

    def test_removing_from_empty_list_does_not_fail(self):
        self.assertIsNone(self.linked_list.remove_current())
        self.assertEqual(self.linked_list.size, 0)

    def test_queries_return_empty_results(self):
        self.assertEqual(self.linked_list.to_list(), [])
        self.assertEqual(self.linked_list.search("anything"), [])
        self.assertEqual(self.linked_list.filter_by_category("portrait"), [])
        self.assertEqual(self.linked_list.current_position(), 0)

    def test_first_inserted_node_becomes_current(self):
        self.linked_list.add(make_image("one"), "start")
        self.assertEqual(self.linked_list.get_current()["nombre"], "one")
        self.assertEqual(len(self.linked_list), 1)


class TestInsertionAtEnds(unittest.TestCase):
    def test_insert_at_head(self):
        linked_list = make_list("b", "c")
        linked_list.add(make_image("a"), "start")
        self.assertEqual(image_names(linked_list), ["a", "b", "c"])
        self.assertEqual(linked_list.head.name, "a")
        self.assertIsNone(linked_list.head.prev)
        self.assertEqual(linked_list.size, 3)

    def test_insert_at_tail(self):
        linked_list = make_list("a", "b")
        linked_list.add(make_image("c"), "final")
        self.assertEqual(image_names(linked_list), ["a", "b", "c"])
        self.assertIsNone(linked_list.tail.next)
        self.assertEqual(linked_list.tail.name, "c")

    def test_insert_between_nodes_reconnects_links(self):
        linked_list = make_list("a", "c")
        linked_list.add(make_image("b"), 1)
        self.assertEqual(image_names(linked_list), ["a", "b", "c"])
        self.assertIs(linked_list.head.next.prev, linked_list.head)
        self.assertIs(linked_list.head.next.next, linked_list.tail)
        self.assertIs(linked_list.tail.prev, linked_list.head.next)

    def test_out_of_range_position_is_clamped(self):
        linked_list = make_list("a", "b")
        linked_list.add(make_image("z"), 99)
        linked_list.add(make_image("y"), -5)
        self.assertEqual(image_names(linked_list), ["y", "a", "b", "z"])


class TestRemovingOnlyNode(unittest.TestCase):
    def test_list_becomes_empty(self):
        linked_list = make_list("only")
        linked_list.remove_current()
        self.assertEqual(linked_list.size, 0)
        self.assertIsNone(linked_list.head)
        self.assertIsNone(linked_list.tail)
        self.assertIsNone(linked_list.current)
        self.assertIsNone(linked_list.get_current())

    def test_node_can_be_added_again(self):
        linked_list = make_list("only")
        linked_list.remove_current()
        linked_list.add(make_image("another"), "final")
        self.assertEqual(image_names(linked_list), ["another"])
        self.assertEqual(linked_list.get_current()["nombre"], "another")


class TestNavigationAtEnds(unittest.TestCase):
    def test_next_at_tail_returns_false(self):
        linked_list = make_list("a", "b", "c")
        linked_list.go_to("c")
        self.assertFalse(linked_list.move_next())
        self.assertEqual(linked_list.get_current()["nombre"], "c")

    def test_previous_at_head_returns_false(self):
        linked_list = make_list("a", "b", "c")
        linked_list.go_to("a")
        self.assertFalse(linked_list.move_previous())
        self.assertEqual(linked_list.get_current()["nombre"], "a")

    def test_navigation_uses_prev_and_next_links(self):
        linked_list = make_list("a", "b", "c")
        self.assertIs(linked_list.head, linked_list.current)
        linked_list.move_next()
        self.assertIs(linked_list.head.next, linked_list.current)
        linked_list.move_next()
        self.assertIs(linked_list.tail, linked_list.current)
        linked_list.move_previous()
        self.assertIs(linked_list.tail.prev, linked_list.current)
        linked_list.move_previous()
        self.assertIs(linked_list.head, linked_list.current)

    def test_current_position(self):
        linked_list = make_list("a", "b", "c")
        self.assertEqual(linked_list.current_position(), 1)
        linked_list.move_next()
        self.assertEqual(linked_list.current_position(), 2)
        linked_list.move_next()
        self.assertEqual(linked_list.current_position(), 3)


class TestRemovingCurrentNode(unittest.TestCase):
    def test_remove_head_moves_current_to_next(self):
        linked_list = make_list("a", "b", "c")
        linked_list.go_to("a")
        removed = linked_list.remove_current()
        self.assertEqual(removed.name, "a")
        self.assertEqual(image_names(linked_list), ["b", "c"])
        self.assertIs(linked_list.head, linked_list.current)
        self.assertIsNone(linked_list.head.prev)
        self.assertEqual(linked_list.size, 2)

    def test_remove_tail_moves_current_to_previous(self):
        linked_list = make_list("a", "b", "c")
        linked_list.go_to("c")
        linked_list.remove_current()
        self.assertEqual(image_names(linked_list), ["a", "b"])
        self.assertIs(linked_list.tail, linked_list.current)
        self.assertIsNone(linked_list.tail.next)

    def test_remove_middle_reconnects_neighbors(self):
        linked_list = make_list("a", "b", "c")
        linked_list.go_to("b")
        linked_list.remove_current()
        self.assertEqual(image_names(linked_list), ["a", "c"])
        self.assertIs(linked_list.head.next, linked_list.tail)
        self.assertIs(linked_list.tail.prev, linked_list.head)
        self.assertEqual(linked_list.get_current()["nombre"], "c")

    def test_remove_all_nodes_one_by_one(self):
        linked_list = make_list("a", "b", "c")
        for _ in range(3):
            linked_list.remove_current()
        self.assertEqual(linked_list.size, 0)
        self.assertTrue(linked_list.is_empty())


class TestSearchAndFiltering(unittest.TestCase):
    def setUp(self) -> None:
        self.linked_list = make_list("sunset", "mountain")
        self.linked_list.head.category = "landscape"
        self.linked_list.head.description = "sun over the sea"
        self.linked_list.tail.category = "portrait"

    def test_search_by_name(self):
        self.assertEqual(len(self.linked_list.search("sun")), 1)

    def test_search_by_description_case_insensitively(self):
        self.assertEqual(len(self.linked_list.search("SEA")), 1)

    def test_search_without_matches(self):
        self.assertEqual(self.linked_list.search("flying fox"), [])

    def test_filter_for_missing_category(self):
        self.assertEqual(self.linked_list.filter_by_category("astronaut"), [])

    def test_filter_for_existing_category(self):
        self.assertEqual(len(self.linked_list.filter_by_category("landscape")), 1)

    def test_categories_have_no_case_insensitive_duplicates(self):
        self.linked_list.add(make_image("another", category="Landscape"), "final")
        self.assertEqual([item.lower() for item in self.linked_list.categories()], ["landscape", "portrait"])


class TestEditing(unittest.TestCase):
    def test_edit_by_id(self):
        linked_list = make_list("a", "b")
        node = linked_list.head.next
        updated = linked_list.edit(node.id, {"nombre": "b-edited", "fecha": "2026-02-02"})
        self.assertIsNotNone(updated)
        self.assertEqual(linked_list.get_by_id(node.id).name, "b-edited")
        self.assertEqual(linked_list.get_by_id(node.id).date, "2026-02-02")

    def test_edit_missing_image(self):
        self.assertIsNone(make_list("a").edit("missing", {"nombre": "x"}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
