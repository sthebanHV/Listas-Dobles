"use strict";

const elements = {
  searchForm: document.getElementById("form-busqueda"),
  searchInput: document.getElementById("q"),
  clearSearch: document.getElementById("btn-limpiar"),
  categoryFilter: document.getElementById("cat-filtro"),
  timeline: document.getElementById("pauta"),
  timelineBand: document.getElementById("banda"),
  timelineBody: document.getElementById("pauta-cuerpo"),
  emptyTimeline: document.getElementById("pauta-vacia"),
  currentImage: document.getElementById("img-actual"),
  imageFrame: document.querySelector(".visor__marco"),
  emptyViewer: document.getElementById("visor-vacio"),
  viewerDetails: document.getElementById("visor-texto"),
  currentName: document.getElementById("nombre-actual"),
  currentCategory: document.getElementById("cat-actual"),
  currentDate: document.getElementById("fecha-actual"),
  currentDescription: document.getElementById("desc-actual"),
  counter: document.getElementById("contador"),
  counterPosition: document.querySelector(".contador__num"),
  counterTotal: document.querySelector(".contador__total"),
  previousPointer: document.getElementById("p-prev"),
  currentPointer: document.getElementById("p-actual"),
  nextPointer: document.getElementById("p-next"),
  previousButton: document.getElementById("btn-anterior"),
  nextButton: document.getElementById("btn-siguiente"),
  editButton: document.getElementById("btn-editar"),
  deleteButton: document.getElementById("btn-eliminar"),
  firstButton: document.getElementById("btn-primera"),
  imageForm: document.getElementById("form-imagen"),
  formTitle: document.getElementById("titulo-form"),
  saveButton: document.getElementById("btn-guardar"),
  cancelButton: document.getElementById("btn-cancelar"),
  nameInput: document.getElementById("f-nombre"),
  categoryInput: document.getElementById("f-categoria"),
  descriptionInput: document.getElementById("f-descripcion"),
  dateInput: document.getElementById("f-fecha"),
  positionInput: document.getElementById("f-posicion"),
  urlInput: document.getElementById("f-url"),
  fileInput: document.getElementById("f-archivo"),
  categoryOptions: document.getElementById("lista-categorias"),
  status: document.getElementById("estado"),
  legend: document.getElementById("leyenda"),
  gallery: document.getElementById("tira"),
  galleryCount: document.getElementById("tira-conteo"),
  emptyGallery: document.getElementById("tira-vacio"),
};

let galleryState = null;
let matchingIds = null;
let editingId = null;

function setStatus(message, isError = false) {
  elements.status.textContent = message;
  elements.status.dataset.tipo = isError ? "error" : "";
}

async function requestGallery(url, options = {}) {
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    if (data && Array.isArray(data.imagenes)) {
      galleryState = data;
      renderGallery();
    }
    if (!response.ok || data.ok === false) {
      setStatus(data.mensaje || "No se pudo completar la operación.", true);
    } else if (data.mensaje) {
      setStatus(data.mensaje);
    }
    return data;
  } catch (error) {
    setStatus("No se pudo conectar con el servidor.", true);
    return null;
  }
}

function createElement(tagName, className, text) {
  const element = document.createElement(tagName);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function renderPositionOptions(images) {
  const selectedPosition = elements.positionInput.value;
  const options = [];

  for (let index = 0; index <= images.length; index += 1) {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = index === images.length ? "Al final" : `Antes de ${images[index].nombre}`;
    options.push(option);
  }

  elements.positionInput.replaceChildren(...options);
  const matchingOption = options.find((option) => option.value === selectedPosition);
  elements.positionInput.value = matchingOption ? selectedPosition : String(images.length);
  elements.positionInput.disabled = editingId !== null;
}

function renderCategories(categories) {
  const selectedCategory = elements.categoryFilter.value;
  const filterOptions = [new Option("Todas", "")];
  const datalistOptions = [];

  categories.forEach((category) => {
    filterOptions.push(new Option(category, category));
    datalistOptions.push(new Option(category, category));
  });

  elements.categoryFilter.replaceChildren(...filterOptions);
  elements.categoryOptions.replaceChildren(...datalistOptions);
  if (categories.includes(selectedCategory)) elements.categoryFilter.value = selectedCategory;
}

function renderPointers(current, images, position) {
  elements.previousPointer.textContent = images[position - 2]?.nombre || "NULL";
  elements.currentPointer.textContent = current?.nombre || "NULL";
  elements.nextPointer.textContent = images[position]?.nombre || "NULL";
}

function isMatch(imageId) {
  return matchingIds === null || matchingIds.has(imageId);
}

function renderTimeline(images, current) {
  const currentIndex = images.findIndex((image) => image.id === current?.id);
  const categoryNames = [...new Set(images.map((image) => image.categoria))];
  elements.timeline.replaceChildren();

  images.forEach((image, index) => {
    const item = createElement("li", "pauta__item");
    const number = createElement("span", "pauta__num", String(index + 1).padStart(2, "0"));
    const button = createElement("button", "pauta__nodo");
    const categoryIndex = categoryNames.indexOf(image.categoria) % 4;

    item.dataset.actual = image.id === current?.id ? "si" : "no";
    item.dataset.fuera = isMatch(image.id) ? "no" : "si";
    button.type = "button";
    button.classList.add(`n${categoryIndex + 1}`);
    button.setAttribute("aria-label", `Mostrar imagen ${index + 1}: ${image.nombre}`);
    button.title = image.nombre;
    button.addEventListener("click", () => showImage(image.id));
    item.append(number, button);
    elements.timeline.append(item);
  });

  elements.emptyTimeline.hidden = images.length > 0;
  const currentItem = elements.timeline.children[currentIndex];
  if (currentItem) {
    elements.timelineBand.style.top = `${currentItem.offsetTop}px`;
    elements.timelineBand.style.height = `${currentItem.offsetHeight}px`;
  } else {
    elements.timelineBand.style.height = "0";
  }
}

function renderViewer(state) {
  const current = state.actual;
  const images = state.imagenes;
  const hasCurrent = current !== null;

  elements.emptyViewer.hidden = hasCurrent;
  elements.viewerDetails.hidden = !hasCurrent;
  elements.currentImage.hidden = !hasCurrent;
  elements.counterPosition.textContent = String(state.posicion || 0);
  elements.counterTotal.textContent = String(state.size);
  elements.counter.hidden = images.length === 0;
  elements.previousButton.disabled = !state.puede_anterior;
  elements.nextButton.disabled = !state.puede_siguiente;
  elements.editButton.disabled = !hasCurrent;
  elements.deleteButton.disabled = !hasCurrent;

  if (!hasCurrent) {
    elements.currentImage.removeAttribute("src");
    elements.currentImage.alt = "";
    elements.imageFrame.removeAttribute("data-error");
    elements.currentName.textContent = "";
    elements.currentCategory.querySelector(".nivel__texto").textContent = "";
    elements.currentDate.textContent = "";
    elements.currentDescription.textContent = "";
    renderPointers(null, images, 0);
    return;
  }

  elements.currentImage.alt = current.descripcion || current.nombre;
  elements.currentImage.src = current.url;
  elements.imageFrame.removeAttribute("data-error");
  elements.currentImage.onerror = () => {
    elements.imageFrame.dataset.error = "si";
  };
  elements.currentImage.onload = () => elements.imageFrame.removeAttribute("data-error");
  elements.currentName.textContent = current.nombre;
  elements.currentCategory.querySelector(".nivel__texto").textContent = current.categoria;
  elements.currentDate.textContent = current.fecha;
  elements.currentDate.dateTime = current.fecha;
  elements.currentDescription.textContent = current.descripcion;
  renderPointers(current, images, state.posicion);
}

function renderLegend(categories) {
  elements.legend.replaceChildren();
  categories.forEach((category, index) => {
    const item = createElement("li");
    const sample = createElement("span", `muestra n${(index % 4) + 1}`);
    sample.setAttribute("aria-hidden", "true");
    item.append(sample, createElement("span", "nombre", category));
    elements.legend.append(item);
  });
}

function renderThumbnails(images, current) {
  elements.gallery.replaceChildren();
  elements.galleryCount.textContent = `${images.length} imagen${images.length === 1 ? "" : "es"}`;
  elements.emptyGallery.hidden = images.length > 0;
  elements.emptyGallery.textContent = "No hay imágenes en la galería.";

  images.forEach((image, index) => {
    const item = createElement("li", "tira__item");
    const button = createElement("button", "tira__btn");
    const frame = createElement("span", "tira__foto");
    const thumbnail = document.createElement("img");
    const caption = createElement("span", "tira__pie");
    const name = createElement("span", "tira__nombre", image.nombre);

    item.dataset.actual = image.id === current?.id ? "si" : "no";
    item.dataset.fuera = isMatch(image.id) ? "no" : "si";
    button.type = "button";
    button.setAttribute("aria-label", `Mostrar imagen ${index + 1}: ${image.nombre}`);
    thumbnail.src = image.url;
    thumbnail.alt = "";
    thumbnail.loading = "lazy";
    thumbnail.onerror = () => {
      frame.dataset.error = "si";
    };
    caption.append(name, createElement("span", "tira__num", String(index + 1).padStart(2, "0")));
    frame.append(thumbnail);
    button.append(frame, caption);
    button.addEventListener("click", () => showImage(image.id));
    item.append(button);
    elements.gallery.append(item);
  });
}

function renderGallery() {
  if (!galleryState) return;
  const { imagenes, actual, categorias, posicion, size } = galleryState;
  renderCategories(categorias);
  renderPositionOptions(imagenes);
  renderViewer({ ...galleryState, posicion, size });
  renderTimeline(imagenes, actual);
  renderLegend(categorias);
  renderThumbnails(imagenes, actual);
}

function showImage(imageId) {
  return requestGallery(`/api/ir/${encodeURIComponent(imageId)}`, { method: "POST" });
}

function resetForm() {
  editingId = null;
  elements.imageForm.reset();
  elements.formTitle.textContent = "Levantar bloque";
  elements.saveButton.textContent = "Agregar";
  elements.cancelButton.hidden = true;
  elements.positionInput.disabled = false;
  if (galleryState) {
    elements.positionInput.value = String(galleryState.imagenes.length);
    renderPositionOptions(galleryState.imagenes);
  }
}

function startEditing() {
  const current = galleryState?.actual;
  if (!current) return;
  editingId = current.id;
  elements.nameInput.value = current.nombre;
  elements.categoryInput.value = current.categoria;
  elements.descriptionInput.value = current.descripcion;
  elements.dateInput.value = current.fecha;
  elements.urlInput.value = current.url.startsWith("/static/uploads/") ? "" : current.url;
  elements.fileInput.value = "";
  elements.formTitle.textContent = "Editar imagen";
  elements.saveButton.textContent = "Guardar cambios";
  elements.cancelButton.hidden = false;
  elements.positionInput.disabled = true;
  elements.nameInput.focus();
  elements.imageForm.scrollIntoView({ behavior: "smooth", block: "center" });
}

async function saveImage(event) {
  event.preventDefault();
  if (!elements.imageForm.reportValidity()) return;

  const formData = new FormData(elements.imageForm);
  const hasFile = Boolean(elements.fileInput.files[0]);
  let url = "/api/imagenes";
  let options;

  if (editingId) {
    formData.delete("posicion");
    url = `/api/imagenes/${encodeURIComponent(editingId)}`;
    options = hasFile
      ? { method: "PUT", body: formData }
      : {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(Object.fromEntries(formData)),
        };
  } else {
    options = hasFile
      ? { method: "POST", body: formData }
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(Object.fromEntries(formData)),
        };
  }

  const result = await requestGallery(url, options);
  if (result?.ok) resetForm();
}

function bindEvents() {
  elements.searchForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = elements.searchInput.value.trim();
    const result = await requestGallery(`/api/buscar?q=${encodeURIComponent(query)}`);
    matchingIds = result ? new Set(result.resultados) : null;
    if (galleryState) renderGallery();
  });

  elements.clearSearch.addEventListener("click", async () => {
    elements.searchInput.value = "";
    elements.categoryFilter.value = "";
    matchingIds = null;
    await requestGallery("/api/imagenes");
  });

  elements.categoryFilter.addEventListener("change", async () => {
    const category = elements.categoryFilter.value;
    const result = await requestGallery(`/api/filtrar?cat=${encodeURIComponent(category)}`);
    matchingIds = result ? new Set(result.resultados) : null;
    if (galleryState) renderGallery();
  });

  elements.previousButton.addEventListener("click", () => requestGallery("/api/anterior", { method: "POST" }));
  elements.nextButton.addEventListener("click", () => requestGallery("/api/siguiente", { method: "POST" }));
  elements.editButton.addEventListener("click", startEditing);
  elements.cancelButton.addEventListener("click", resetForm);
  elements.imageForm.addEventListener("submit", saveImage);
  elements.firstButton.addEventListener("click", () => {
    elements.nameInput.focus();
    elements.imageForm.scrollIntoView({ behavior: "smooth", block: "center" });
  });

  elements.deleteButton.addEventListener("click", async () => {
    const current = galleryState?.actual;
    if (!current || !window.confirm(`¿Eliminar “${current.nombre}”?`)) return;
    await requestGallery("/api/actual", { method: "DELETE" });
    if (editingId) resetForm();
  });

  document.addEventListener("keydown", (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    const target = event.target;
    const isEditingField = target instanceof HTMLElement
      && (target.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName));
    if (isEditingField) return;

    if (event.key === "ArrowLeft" && !elements.previousButton.disabled) {
      event.preventDefault();
      elements.previousButton.click();
    } else if (event.key === "ArrowRight" && !elements.nextButton.disabled) {
      event.preventDefault();
      elements.nextButton.click();
    } else if (event.key.toLowerCase() === "e" && !elements.editButton.disabled) {
      event.preventDefault();
      elements.editButton.click();
    }
  });
}

bindEvents();
requestGallery("/api/imagenes");