"""Image node used by GalleryFlow's manually linked list."""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional


class ImageNode:
    """A gallery image and its previous/next node references."""

    def __init__(
        self,
        name: str,
        category: str,
        description: str,
        date: str,
        url: str,
        id: Optional[str] = None,
    ) -> None:
        self.name = name
        self.category = category
        self.description = description
        self.date = date
        self.url = url
        self.prev: Optional["ImageNode"] = None
        self.next: Optional["ImageNode"] = None
        self.id: str = id or uuid.uuid4().hex[:12]

    # ------------------------------------------------------------------
    # Conversion to and from API/persistence dictionaries.
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """Return serializable image data without linked node references."""
        return {
            "id": self.id,
            "nombre": self.name,
            "categoria": self.category,
            "descripcion": self.description,
            "fecha": self.date,
            "url": self.url,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageNode":
        """Create an image node from the existing Spanish API data shape."""
        return cls(
            name=str(data.get("nombre", data.get("name", ""))).strip(),
            category=str(data.get("categoria", data.get("category", ""))).strip(),
            description=str(data.get("descripcion", data.get("description", ""))).strip(),
            date=str(data.get("fecha", data.get("date", ""))).strip(),
            url=str(data.get("url", "")).strip(),
            id=data.get("id") or None,
        )

    def __repr__(self) -> str:
        return f"<ImageNode {self.name!r} ({self.category})>"
