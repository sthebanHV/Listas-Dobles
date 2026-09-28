"""GalleryFlow Flask server and REST API.

Run the application with ``python app.py``. The gallery is stored in a
manually implemented doubly linked list and persisted as JSON.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from models.lista_doble import DoublyLinkedList
from models.nodo import ImageNode

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "galeria.json"
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

gallery = DoublyLinkedList()


def seed_images() -> List[Dict[str, str]]:
    """Return sample images used when no saved gallery is available."""
    samples = [
        (
            "Atardecer en el río",
            "paisaje",
            "Reflejo del sol sobre el agua al final del día.",
            "https://picsum.photos/id/1015/900/600",
        ),
        (
            "Retrato con luz natural",
            "retrato",
            "Retrato tomado junto a una ventana con luz suave.",
            "https://picsum.photos/id/1005/900/600",
        ),
        (
            "Calles de la ciudad",
            "urbano",
            "Movimiento y luces en el centro de la ciudad.",
            "https://picsum.photos/id/1076/900/600",
        ),
        (
            "Bosque de niebla",
            "naturaleza",
            "Sendero entre árboles cubiertos por la niebla matinal.",
            "https://picsum.photos/id/1018/900/600",
        ),
        (
            "Detalle de frutos",
            "macro",
            "Primer plano con poca profundidad de campo.",
            "https://picsum.photos/id/1080/900/600",
        ),
        (
            "Líneas de arquitectura",
            "arquitectura",
            "Fachada moderna con patrones geométricos repetidos.",
            "https://picsum.photos/id/1048/900/600",
        ),
    ]
    return [
        {
            "name": name,
            "category": category,
            "description": description,
            "date": "2026-01-01",
            "url": url,
        }
        for name, category, description, url in samples
    ]


def seed_gallery() -> None:
    """Populate and persist the sample gallery."""
    for image_data in seed_images():
        gallery.add(ImageNode.from_dict(image_data), "final")
    gallery.current = gallery.head
    save_gallery()


def load_gallery() -> None:
    """Restore image nodes from JSON and rebuild their linked references."""
    if not DATA_FILE.exists():
        seed_gallery()
        return

    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        seed_gallery()
        return

    images = data.get("imagenes", []) if isinstance(data, dict) else []
    if not isinstance(images, list) or not images:
        seed_gallery()
        return

    for image_data in images:
        if isinstance(image_data, dict):
            gallery.add(ImageNode.from_dict(image_data), "final")

    current_id = data.get("actual_id")
    gallery.current = gallery.get_by_id(current_id) if current_id else None
    if gallery.current is None:
        gallery.current = gallery.head


def save_gallery() -> None:
    """Persist the images and the current node identifier to JSON."""
    payload = {
        "imagenes": gallery.to_list(),
        "actual_id": gallery.current.id if gallery.current else None,
        "actualizado": date.today().isoformat(),
    }
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def api_state(message: str = "", ok: bool = True, **extra: Any):
    """Build the Spanish response shape consumed by the existing frontend."""
    payload: Dict[str, Any] = {
        "ok": ok,
        "mensaje": message,
        "size": gallery.size,
        "posicion": gallery.current_position(),
        "actual": gallery.get_current(),
        "imagenes": gallery.to_list(),
        "categorias": gallery.categories(),
        "puede_anterior": gallery.current is not None and gallery.current.prev is not None,
        "puede_siguiente": gallery.current is not None and gallery.current.next is not None,
    }
    payload.update(extra)
    return jsonify(payload)


def api_error(message: str, status_code: int = 400):
    return api_state(message, ok=False), status_code


def _request_data() -> Dict[str, Any]:
    """Read JSON or multipart form data, saving an uploaded image if present."""
    if request.files or request.form:
        data = {field: value for field, value in request.form.items()}
        upload = request.files.get("archivo")
        if upload and upload.filename:
            filename = _save_upload(upload)
            if filename is None:
                raise ValueError(
                    "Archivo no permitido. Usa png, jpg, jpeg, gif, webp o svg "
                    f"(máximo {MAX_UPLOAD_SIZE // (1024 * 1024)} MB)."
                )
            data["url"] = f"/static/uploads/{filename}"
        return data
    return request.get_json(silent=True) or {}


def _save_upload(upload) -> Optional[str]:
    """Save an allowed image under a unique secure filename."""
    filename = secure_filename(upload.filename or "")
    if not filename:
        return None
    extension = os.path.splitext(filename)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return None
    unique_name = f"{uuid.uuid4().hex[:10]}{extension}"
    upload.save(UPLOAD_FOLDER / unique_name)
    return unique_name


def _validate_image(data: Dict[str, Any], require_url: bool = True) -> Optional[str]:
    """Return a validation message when required image fields are missing."""
    if not str(data.get("nombre", "")).strip():
        return "El nombre es obligatorio."
    if require_url and not str(data.get("url", "")).strip():
        return "Debes indicar una URL o subir un archivo."
    return None


@app.route("/")
def index():
    """Render the gallery interface."""
    return render_template("index.html")


@app.route("/api/imagenes", methods=["GET"])
def get_images():
    return api_state("Galería completa.")


@app.route("/api/actual", methods=["GET"])
def get_current_image():
    if gallery.is_empty():
        return api_state("La galería está vacía.", ok=False)
    return api_state("Imagen actual cargada.")


@app.route("/api/imagenes", methods=["POST"])
def add_image():
    try:
        data = _request_data()
    except ValueError as exception:
        return api_error(str(exception))

    validation_message = _validate_image(data)
    if validation_message:
        return api_error(validation_message)

    data.setdefault("fecha", date.today().isoformat())
    data.setdefault("categoria", "general")
    position = data.pop("posicion", "final")
    image = gallery.add(data, position)
    save_gallery()
    return api_state(f"Imagen “{image.name}” agregada."), 201


@app.route("/api/imagenes/<string:identifier>", methods=["PUT"])
def edit_image(identifier: str):
    data = _request_data()
    if "nombre" in data and not str(data["nombre"]).strip():
        return api_error("El nombre no puede quedar vacío.")

    image = gallery.edit(identifier, data)
    if image is None:
        return api_error("Imagen no encontrada.", 404)

    save_gallery()
    return api_state(f"Imagen “{image.name}” actualizada.")


@app.route("/api/actual", methods=["DELETE"])
def delete_current_image():
    removed = gallery.remove_current()
    if removed is None:
        return api_state("No hay imagen que eliminar.", ok=False)

    save_gallery()
    return api_state(f"Imagen “{removed.name}” eliminada.")


@app.route("/api/siguiente", methods=["POST"])
def move_next():
    if gallery.is_empty():
        return api_state("La galería está vacía.", ok=False)
    if not gallery.move_next():
        return api_state("Ya estás en la última imagen.", movido=False)
    save_gallery()
    return api_state("Siguiente imagen.", movido=True)


@app.route("/api/anterior", methods=["POST"])
def move_previous():
    if gallery.is_empty():
        return api_state("La galería está vacía.", ok=False)
    if not gallery.move_previous():
        return api_state("Ya estás en la primera imagen.", movido=False)
    save_gallery()
    return api_state("Imagen anterior.", movido=True)


@app.route("/api/ir/<string:identifier>", methods=["POST"])
def go_to_image(identifier: str):
    image = gallery.go_to(identifier)
    if image is None:
        return api_error("Imagen no encontrada.", 404)
    save_gallery()
    return api_state(f"Mostrando “{image.name}”.", movido=True)


@app.route("/api/buscar", methods=["GET"])
def search_images():
    query = request.args.get("q", "")
    results = gallery.search(query)
    message = f"{len(results)} resultado(s) para “{query}”." if query else "Galería completa."
    return api_state(
        message,
        resultados=[image["id"] for image in results],
        consultado=query,
    )


@app.route("/api/filtrar", methods=["GET"])
def filter_images():
    category = request.args.get("cat", "")
    results = gallery.filter_by_category(category)
    message = f"{len(results)} imagen(es) en “{category}”." if category else "Galería completa."
    return api_state(
        message,
        resultados=[image["id"] for image in results],
        consultado=category,
    )


@app.route("/api/categorias", methods=["GET"])
def get_categories():
    return api_state("Categorías disponibles.")


load_gallery()

if __name__ == "__main__":
    print(f"GalleryFlow → http://127.0.0.1:5000 ({gallery.size} imágenes)")
    app.run(debug=True, host="127.0.0.1", port=5000)
