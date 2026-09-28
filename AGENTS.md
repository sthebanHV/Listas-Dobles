# AGENTS.md — GalleryFlow

Guía para agentes de IA y desarrolladores que trabajen en este proyecto.

## 1. Contexto académico

**Taller de LISTAS DOBLES aplicado en un caso de estudio.**

Requisitos del taller:

- Seleccionar un **caso de estudio de la vida real** donde se aplique el concepto y manejo de **listas dobles** (listas doblemente enlazadas).
- El script debe estar realizado en **Python**.
- El proyecto **debe tener Frontend** (interfaz visual para el usuario).

## 2. Caso de estudio 5: Galería de imágenes

**Nombre del proyecto:** GalleryFlow

**Idea:** aplicación web para administrar y visualizar una colección de imágenes mediante una **lista doblemente enlazada**. Cada imagen es un nodo con la siguiente información:

| Campo         | Descripción                          |
|---------------|--------------------------------------|
| `nombre`      | Nombre de la imagen                  |
| `categoria`   | Categoría (paisaje, retrato, etc.)   |
| `descripcion` | Descripción breve                    |
| `fecha`       | Fecha de la imagen o de registro     |
| `url`         | URL o ruta de la imagen              |
| `next`        | Referencia al nodo siguiente         |
| `prev`        | Referencia al nodo anterior          |

La función principal es **navegar entre imágenes hacia adelante y hacia atrás** usando las referencias `next` y `prev`.

## 3. ¿Cómo funciona?

```
[Imagen 1] ⇄ [Imagen 2] ⇄ [Imagen 3] ⇄ [Imagen 4]
                  ↑
               actual
```

Si el usuario está viendo la **Imagen 2**:

- **Anterior** → muestra Imagen 1.
- **Siguiente** → muestra Imagen 3.
- **Eliminar** → elimina Imagen 2 y conecta Imagen 1 con Imagen 3.
- **Agregar** → inserta una nueva imagen en la posición seleccionada.

## 4. Funciones principales

1. Agregar imagen
2. Eliminar imagen
3. Editar información
4. Siguiente imagen
5. Imagen anterior
6. Buscar imagen
7. Filtrar por categoría
8. Mostrar información de la imagen
9. Ver todas las imágenes
10. Navegar entre imágenes mediante la lista doble

## 5. Stack tecnológico

- **Backend:** Python 3.10+ con Flask.
- **Estructura de datos:** implementación propia de lista doblemente enlazada (**no usar** `list`, `deque` ni librerías que oculten la lógica de nodos).
- **Frontend:** HTML5 + CSS3 + JavaScript (plantillas Jinja2 de Flask).
- **Persistencia (opcional):** archivo JSON para conservar la galería entre sesiones.

## 6. Estructura sugerida del proyecto

```
GalleryFlow/
├── AGENTS.md
├── app.py                  # Servidor Flask y rutas
├── models/
│   ├── nodo.py             # Clase NodoImagen
│   └── lista_doble.py      # Clase ListaDoble
├── data/
│   └── galeria.json        # Persistencia opcional
├── templates/
│   └── index.html          # Interfaz principal
├── static/
│   ├── css/style.css
│   └── js/main.js
└── requirements.txt
```

## 7. Diseño de las clases

### `NodoImagen`
Atributos: `nombre`, `categoria`, `descripcion`, `fecha`, `url`, `next = None`, `prev = None`.

### `ListaDoble`
Atributos: `head`, `tail`, `actual`, `size`.

| Método                          | Función                                                        |
|---------------------------------|----------------------------------------------------------------|
| `agregar(imagen, posicion)`     | Inserta al inicio, al final o en una posición dada             |
| `eliminar_actual()`             | Elimina el nodo actual y reconecta `prev` con `next`           |
| `editar(nombre, datos)`         | Modifica la información de un nodo                             |
| `siguiente()`                   | Mueve `actual` a `actual.next` (si existe)                     |
| `anterior()`                    | Mueve `actual` a `actual.prev` (si existe)                     |
| `buscar(texto)`                 | Busca por nombre o descripción                                 |
| `filtrar_por_categoria(cat)`    | Devuelve las imágenes de una categoría                         |
| `obtener_actual()`              | Devuelve la información del nodo actual                        |
| `listar_todas()`                | Recorre la lista de `head` a `tail`                            |

## 8. Casos borde que deben manejarse

- Lista vacía (no hay `actual`, deshabilitar botones).
- Insertar/eliminar en la cabeza (`head`) y en la cola (`tail`).
- Eliminar el único nodo de la lista.
- Presionar **Siguiente** en el último nodo o **Anterior** en el primero (no debe fallar).
- Al eliminar el nodo actual, `actual` pasa al `next`; si no existe, al `prev`.
- Búsqueda sin resultados y categoría inexistente.

## 9. Rutas del backend (API)

| Método | Ruta                    | Acción                          |
|--------|-------------------------|---------------------------------|
| GET    | `/`                     | Carga la interfaz               |
| GET    | `/api/imagenes`         | Ver todas las imágenes          |
| GET    | `/api/actual`           | Imagen actual                   |
| POST   | `/api/imagenes`         | Agregar imagen                  |
| PUT    | `/api/imagenes/<id>`    | Editar información              |
| DELETE | `/api/actual`           | Eliminar imagen actual          |
| POST   | `/api/siguiente`        | Ir a la imagen siguiente        |
| POST   | `/api/anterior`         | Ir a la imagen anterior         |
| GET    | `/api/buscar?q=`        | Buscar imagen                   |
| GET    | `/api/filtrar?cat=`     | Filtrar por categoría           |

## 10. Requisitos del frontend

- Visor central con la imagen actual y su información (nombre, categoría, descripción, fecha).
- Botones **← Anterior** y **Siguiente →**.
- Formulario para agregar y editar imágenes.
- Botón para eliminar la imagen actual.
- Barra de búsqueda y selector de filtro por categoría.
- Vista de galería con todas las imágenes (miniaturas), resaltando la actual.
- Indicador de posición (ej. "Imagen 2 de 4").
- Diseño responsive y limpio.

## 11. Reglas para agentes

1. La lógica de la lista doble debe estar **implementada manualmente** con nodos y referencias `next`/`prev`.
2. Mantener la separación: lógica de datos (`models/`), rutas (`app.py`) e interfaz (`templates/`, `static/`).
3. Código en Python con nombres claros en español, docstrings y comentarios que expliquen las operaciones sobre punteros.
4. No agregar dependencias innecesarias.
5. Cada función principal (sección 4) debe ser accesible desde el frontend.
6. Probar los casos borde de la sección 8 antes de dar una tarea por terminada.

## 12. Criterios de aceptación

- [ ] Las 10 funciones principales funcionan desde la interfaz web.
- [ ] La navegación usa exclusivamente `next` y `prev`.
- [ ] Eliminar un nodo intermedio reconecta correctamente sus vecinos.
- [ ] Se puede insertar en la posición seleccionada.
- [ ] El proyecto corre con `python app.py`.
- [ ] Cumple con los requisitos del taller: Python, listas dobles y Frontend.
