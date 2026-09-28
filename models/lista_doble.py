"""Manually implemented doubly linked list for GalleryFlow."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from .nodo import ImageNode


class DoublyLinkedList:
    """Image collection linked through each node's ``prev`` and ``next``."""

    EDITABLE_FIELDS = {
        "nombre": "name",
        "categoria": "category",
        "descripcion": "description",
        "fecha": "date",
        "url": "url",
        "name": "name",
        "category": "category",
        "description": "description",
        "date": "date",
    }

    def __init__(self) -> None:
        self.head: Optional[ImageNode] = None
        self.tail: Optional[ImageNode] = None
        self.current: Optional[ImageNode] = None
        self.size = 0

    def add(self, image: Union[ImageNode, Dict[str, Any]], position: Any = "final") -> ImageNode:
        """Insert a node at the start, end, or a zero-based position."""
        node = image if isinstance(image, ImageNode) else ImageNode.from_dict(image)
        if self.head is None:
            self.head = self.tail = self.current = node
            self.size = 1
            return node

        index = self._normalize_position(position)
        if index == 0:
            node.next = self.head
            self.head.prev = node
            self.head = node
        elif index >= self.size:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        else:
            target = self._node_at(index)
            previous = target.prev
            node.prev = previous
            node.next = target
            previous.next = node
            target.prev = node

        self.size += 1
        return node

    def _normalize_position(self, position: Any) -> int:
        """Clamp the requested position to a valid insertion index."""
        if position in (None, "", "final", "fin", "cola", "end"):
            return self.size
        if position in ("inicio", "primero", "head", "start", "first"):
            return 0
        try:
            index = int(position)
        except (TypeError, ValueError):
            return self.size
        return max(0, min(index, self.size))

    def _node_at(self, index: int) -> ImageNode:
        """Return the node at an index by following ``next`` links."""
        node = self.head
        for _ in range(index):
            node = node.next
        return node

    def remove_current(self) -> Optional[ImageNode]:
        """Remove the current node, linking its neighbors together."""
        if self.current is None:
            return None

        node = self.current
        previous = node.prev
        following = node.next
        if previous is not None:
            previous.next = following
        else:
            self.head = following
        if following is not None:
            following.prev = previous
        else:
            self.tail = previous

        self.current = following if following is not None else previous
        node.prev = node.next = None
        self.size -= 1
        if self.size == 0:
            self.head = self.tail = self.current = None
        return node

    def edit(self, key: str, data: Dict[str, Any]) -> Optional[ImageNode]:
        """Update editable image fields on a node matching an id or name."""
        node = self.get_by_id(key) or self._find_by_name(key)
        if node is None:
            return None

        for field, value in data.items():
            attribute = self.EDITABLE_FIELDS.get(field)
            if attribute and value is not None and str(value).strip():
                setattr(node, attribute, str(value).strip())
        return node

    def move_next(self) -> bool:
        """Move the current cursor to ``current.next`` when available."""
        if self.current is None or self.current.next is None:
            return False
        self.current = self.current.next
        return True

    def move_previous(self) -> bool:
        """Move the current cursor to ``current.prev`` when available."""
        if self.current is None or self.current.prev is None:
            return False
        self.current = self.current.prev
        return True

    def go_to(self, key: str) -> Optional[ImageNode]:
        """Move the cursor to a node matching its id or exact name."""
        node = self.get_by_id(key) or self._find_by_name(key)
        if node is not None:
            self.current = node
        return node

    def search(self, text: str) -> List[Dict[str, Any]]:
        """Find images whose names or descriptions contain the text."""
        term = (text or "").strip().lower()
        if not term:
            return self.to_list()

        results = []
        node = self.head
        while node is not None:
            if term in node.name.lower() or term in node.description.lower():
                results.append(node.to_dict())
            node = node.next
        return results

    def filter_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Return images in the given category, case-insensitively."""
        term = (category or "").strip().lower()
        if not term:
            return self.to_list()

        results = []
        node = self.head
        while node is not None:
            if node.category.lower() == term:
                results.append(node.to_dict())
            node = node.next
        return results

    def categories(self) -> List[str]:
        """Return sorted category names without case-insensitive duplicates."""
        categories = {}
        node = self.head
        while node is not None:
            if node.category:
                categories.setdefault(node.category.lower(), node.category)
            node = node.next
        return sorted(categories.values(), key=str.lower)

    def get_current(self) -> Optional[Dict[str, Any]]:
        """Return the current image in the API-compatible data shape."""
        return self.current.to_dict() if self.current is not None else None

    def to_list(self) -> List[Dict[str, Any]]:
        """Return every image by traversing from ``head`` to ``tail``."""
        results = []
        node = self.head
        while node is not None:
            results.append(node.to_dict())
            node = node.next
        return results

    def get_by_id(self, identifier: str) -> Optional[ImageNode]:
        """Find a node by traversing the list and matching its id."""
        node = self.head
        while node is not None:
            if node.id == identifier:
                return node
            node = node.next
        return None

    def _find_by_name(self, name: str) -> Optional[ImageNode]:
        """Return the first node with an exact name match."""
        node = self.head
        while node is not None:
            if node.name == name:
                return node
            node = node.next
        return None

    def current_position(self) -> int:
        """Return the one-based current position, or zero for an empty list."""
        if self.current is None:
            return 0
        position = 1
        node = self.current
        while node.prev is not None:
            node = node.prev
            position += 1
        return position

    def is_empty(self) -> bool:
        return self.head is None

    def __len__(self) -> int:
        return self.size
