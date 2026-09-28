# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Pinned by `AGENTS.md`: Python 3.10+ con Flask (backend), HTML5 + CSS3 + JavaScript vanilla con plantillas Jinja2 (frontend), lista doblemente enlazada implementada a mano (sin `list`, `deque` ni librerías que oculten los nodos), persistencia opcional en `data/galeria.json`. Sin frameworks de frontend ni dependencias además de Flask.

## Users

Estudiante que entrega y presenta el taller, y el profesor/compañeros que revisan la app durante una demostración. No hay usuarios finales externos.

## Product Purpose

GalleryFlow demuestra en un caso de estudio de la vida real el manejo de **listas doblemente enlazadas**: administrar y visualizar una colección de imágenes. El éxito es que las 10 funciones del taller sean visibles y tocables desde la interfaz, y que la navegación se haga exclusivamente con los punteros `next` y `prev`.

## Positioning

El mecanismo que lo hace ser lo que es: cada imagen es un nodo con `prev`/`next`, y la app entera —visor, indicador de posición, galería— es una proyección de esos punteros. No es un carrusel con índice numérico: eliminar un nodo reconecta sus vecinos en vivo y el usuario lo ve.

## Operating Context

- Ejecución local con `python app.py` en `127.0.0.1:5000`, con internet disponible (las imágenes de ejemplo usan URLs externas).
- Revisión en pantalla durante una presentación académica: un solo usuario a la vez, sin autenticación.
- El repositorio se evalúa también leyendo el código: nombres en español, docstrings y comentarios que expliquen las operaciones sobre punteros.
- Persistencia en `data/galeria.json` entre sesiones.

## Capabilities and Constraints

- Las 10 funciones son obligatorias y accesibles desde el frontend: agregar, eliminar, editar, siguiente, anterior, buscar, filtrar por categoría, mostrar información, ver todas, navegar con la lista doble.
- La lista doble se implementa a mano en `models/lista_doble.py`; prohibido usar `list`, `deque` u ocultar la lógica de nodos.
- API REST en `app.py` según la tabla de la sección 9 del `AGENTS.md`, más `GET /api/categorias` y `POST /api/ir/<id>` para navegar desde la galería.
- Imágenes por URL externa **o** subida de archivo (png/jpg/jpeg/gif/webp/svg, 5 MB máx., `secure_filename`, guardadas en `static/uploads/`).
- Casos borde obligatorios (sección 8): lista vacía, inserción/eliminación en `head` y `tail`, único nodo, extremos de navegación, búsqueda sin resultados, categoría inexistente.
- Accesibilidad: **WCAG AA** — contraste AA, navegación por teclado completo, `label` en todo control, foco visible, `aria-live` en mensajes de estado, botones deshabilitados con estado accesible.
- Sin dependencias nuevas más allá de Flask.

## Brand Commitments

- Nombre: **GalleryFlow**.
- Idioma de toda la interfaz, comentarios y mensajes: **español**.
- Debe ejecutarse con `python app.py` y respetar la estructura de carpetas sugerida en la sección 6 del `AGENTS.md`.

## Evidence on Hand

- `AGENTS.md`: requisitos completos del taller (caso de estudio, clases, rutas, casos borde, criterios de aceptación).
- `tests/test_lista_doble.py`: 27 pruebas `unittest` en verde sobre los casos borde.
- Sin material de marca, logo ni tipografía definidos. No inventar testimonios, métricas ni afirmaciones comerciales.

## Product Principles

1. La lista doble es el producto: toda la interfaz debe hacer visible el trabajo de `prev`/`next`.
2. Ningún caso borde rompe la app; los extremos responden, no fallan.
3. Separación estricta: datos (`models/`), rutas (`app.py`), interfaz (`templates/`, `static/`).
4. Código legible por un profesor: nombres en español, docstrings, comentarios de punteros.
5. Dependencia cero más allá de Flask.

## Accessibility & Inclusion

WCAG 2.1 nivel AA: contraste mínimo 4.5:1 en texto, navegación completa por teclado (incluidas flechas `←`/`→` para la galería), etiquetas explícitas en todos los campos, foco visible, mensajes de estado anunciados con `aria-live`, botones deshabilitados realmente deshabilitados y texto alternativo descriptivo en cada imagen.
