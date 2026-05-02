const state = {
  data: null,
  filters: {
    query: "",
    category: "",
    storage: "",
    status: "all",
  },
  recordFilters: {
    query: "",
    status: "all",
  },
};

const elements = {
  statsGrid: document.getElementById("statsGrid"),
  lastUpdated: document.getElementById("lastUpdated"),
  sessionTableBody: document.getElementById("sessionTableBody"),
  inventoryTableBody: document.getElementById("inventoryTableBody"),
  recordsTableBody: document.getElementById("recordsTableBody"),
  categoryTableBody: document.getElementById("categoryTableBody"),
  categoryBreakdown: document.getElementById("categoryBreakdown"),
  storageBreakdown: document.getElementById("storageBreakdown"),
  scanMessage: document.getElementById("scanMessage"),
  checkoutMessage: document.getElementById("checkoutMessage"),
  itemFormMessage: document.getElementById("itemFormMessage"),
  categoryFormMessage: document.getElementById("categoryFormMessage"),
  categoryList: document.getElementById("categoryList"),
  storageList: document.getElementById("storageList"),
  filterCategory: document.getElementById("filterCategory"),
  filterStorage: document.getElementById("filterStorage"),
  filterStatus: document.getElementById("filterStatus"),
  searchQuery: document.getElementById("searchQuery"),
  itemModal: document.getElementById("itemModal"),
  categoryModal: document.getElementById("categoryModal"),
  recordSearchQuery: document.getElementById("recordSearchQuery"),
  recordStatusFilter: document.getElementById("recordStatusFilter"),
};

document.querySelectorAll(".tab-link").forEach((button) => {
  button.addEventListener("click", () => activateTab(button.dataset.tab));
});

document.querySelectorAll("[data-close-modal]").forEach((button) => {
  button.addEventListener("click", () => document.getElementById(button.dataset.closeModal).close());
});

document.getElementById("scanForm").addEventListener("submit", onScanSubmit);
document.getElementById("approveSessionBtn").addEventListener("click", approveSession);
document.getElementById("filterForm").addEventListener("submit", onFilterSubmit);
document.getElementById("checkoutForm").addEventListener("submit", onCheckoutSubmit);
document.getElementById("itemForm").addEventListener("submit", onItemSubmit);
document.getElementById("categoryForm").addEventListener("submit", onCategorySubmit);
document.getElementById("recordFilterForm").addEventListener("submit", onRecordFilterSubmit);
document.getElementById("newCategoryBtn").addEventListener("click", () => openCategoryModal());
document.getElementById("newRecordBtn").addEventListener("click", () => openItemModal("record-create", { archived: true }));
document.getElementById("itemCategory").addEventListener("change", syncRecommendedDate);
document.getElementById("itemCategory").addEventListener("input", syncRecommendedDate);
document.getElementById("itemPurchaseDate").addEventListener("change", syncRecommendedDate);

bootstrap();

async function bootstrap() {
  await loadState();
}

async function loadState() {
  const params = new URLSearchParams(state.filters);
  const response = await fetch(`/api/bootstrap?${params.toString()}`);
  state.data = await response.json();
  render();
}

function activateTab(tabId) {
  document.querySelectorAll(".tab-link").forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tabId);
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === tabId);
  });
}

function render() {
  renderStats();
  renderSessionItems();
  renderInventory();
  renderRecords();
  renderOverview();
  renderCategories();
  renderFilterOptions();
  renderDataLists();
  elements.lastUpdated.textContent = `Last updated ${state.data.timestamp}`;
}

function renderStats() {
  const stats = state.data.stats;
  const cards = [
    ["Total Items", stats.total_items],
    ["Expiring Soon", stats.warning_count],
    ["Expired", stats.expired_count],
    ["Categories", stats.categories],
    ["Storage Zones", stats.storage_locations],
  ];

  elements.statsGrid.innerHTML = cards.map(([label, value]) => `
    <article class="stat-card">
      <span>${label}</span>
      <strong>${value}</strong>
    </article>
  `).join("");
}

function renderSessionItems() {
  const rows = state.data.session_items;
  if (rows.length === 0) {
    elements.sessionTableBody.innerHTML = `<tr><td colspan="9">No items in the current session yet.</td></tr>`;
    return;
  }

  elements.sessionTableBody.innerHTML = rows.map((item) => `
    <tr>
      <td>${item.session_id}</td>
      <td>${escapeHtml(item.barcode)}</td>
      <td>${escapeHtml(item.name)}</td>
      <td>${escapeHtml(item.category)}</td>
      <td>${escapeHtml(item.storage_location)}</td>
      <td>${escapeHtml(item.purchase_date)}</td>
      <td>${escapeHtml(item.exp_date)}</td>
      <td>${statusPill(item.status)}</td>
      <td>
        <div class="row-actions">
          <button type="button" class="secondary" data-edit-session="${item.session_id}">Edit</button>
        </div>
      </td>
    </tr>
  `).join("");

  document.querySelectorAll("[data-edit-session]").forEach((button) => {
    button.addEventListener("click", () => {
      const item = state.data.session_items.find((entry) => entry.session_id === Number(button.dataset.editSession));
      openItemModal("session", item);
    });
  });
}

function renderInventory() {
  const groups = state.data.inventory_groups;
  if (groups.length === 0) {
    elements.inventoryTableBody.innerHTML = `<tr><td colspan="8">No matching items found.</td></tr>`;
    return;
  }

  elements.inventoryTableBody.innerHTML = groups.map((group, index) => `
    <tr class="inventory-group">
      <td>${escapeHtml(group.barcode)}</td>
      <td>${escapeHtml(group.name)}</td>
      <td>${escapeHtml(group.category)}</td>
      <td>${escapeHtml(group.storage_location)}</td>
      <td>${group.quantity}</td>
      <td>${escapeHtml(group.top_exp_date)}</td>
      <td>${statusPill(group.top_status)}</td>
      <td>
        <div class="row-actions">
          <button type="button" class="secondary" data-toggle-group="group-${index}">Show ${group.quantity} Item${group.quantity === 1 ? "" : "s"}</button>
          <button type="button" class="danger-button" data-archive-group="${escapeAttribute(group.barcode)}">Archive Group</button>
        </div>
      </td>
    </tr>
    <tr id="group-${index}" hidden>
      <td colspan="8">
        <div class="group-items">
          ${group.items.map((item) => `
            <article class="group-item-card">
              <div class="group-item-meta">
                <span>Serial ID: ${item.item_id}</span>
                <span>Purchased: ${escapeHtml(item.purchase_date)}</span>
                <span>Expires: ${escapeHtml(item.exp_date)}</span>
                <span>Status: ${statusLabel(item.status)}</span>
              </div>
              <div class="row-actions">
                <button type="button" class="secondary" data-edit-item="${item.item_id}">Edit</button>
              </div>
            </article>
          `).join("")}
        </div>
      </td>
    </tr>
  `).join("");

  document.querySelectorAll("[data-toggle-group]").forEach((button) => {
    button.addEventListener("click", () => {
      const target = document.getElementById(button.dataset.toggleGroup);
      const isHidden = target.hasAttribute("hidden");
      target.toggleAttribute("hidden");
      button.textContent = `${isHidden ? "Hide" : "Show"} ${button.textContent.replace(/^(Show|Hide)\s/, "")}`;
    });
  });

  document.querySelectorAll("[data-edit-item]").forEach((button) => {
    button.addEventListener("click", () => {
      const itemId = Number(button.dataset.editItem);
      openItemModal("inventory", recordById(itemId));
    });
  });

  document.querySelectorAll("[data-archive-group]").forEach((button) => {
    button.addEventListener("click", async () => {
      if (!window.confirm(`Archive all active inventory items for barcode ${button.dataset.archiveGroup}?`)) {
        return;
      }
      const response = await postJson("/api/inventory/archive-group", {
        barcode: button.dataset.archiveGroup,
      });
      showMessage(elements.checkoutMessage, response.payload.error || response.payload.message, !response.ok);
      if (response.ok) {
        await loadState();
      }
    });
  });
}

function renderRecords() {
  const rows = filteredRecords();
  if (rows.length === 0) {
    elements.recordsTableBody.innerHTML = `<tr><td colspan="9">No records match this filter.</td></tr>`;
    return;
  }

  elements.recordsTableBody.innerHTML = rows.map((item) => `
    <tr>
      <td>${item.item_id}</td>
      <td>${escapeHtml(item.barcode)}</td>
      <td>${escapeHtml(item.name)}</td>
      <td>${escapeHtml(item.category)}</td>
      <td>${escapeHtml(item.storage_location)}</td>
      <td>${escapeHtml(item.purchase_date)}</td>
      <td>${escapeHtml(item.exp_date)}</td>
      <td><span class="record-flag ${item.archived ? "record-archived" : "record-active"}">${item.archived ? "Archived" : "Active"}</span></td>
      <td>
        <div class="row-actions">
          <button type="button" class="secondary" data-edit-record="${item.item_id}">Edit</button>
        </div>
      </td>
    </tr>
  `).join("");

  document.querySelectorAll("[data-edit-record]").forEach((button) => {
    button.addEventListener("click", () => {
      openItemModal("record-edit", recordById(Number(button.dataset.editRecord)));
    });
  });
}

function renderOverview() {
  renderBreakdown(elements.categoryBreakdown, state.data.stats.items_by_category);
  renderBreakdown(elements.storageBreakdown, state.data.stats.items_by_storage);
}

function renderCategories() {
  const rows = state.data.categories;
  if (rows.length === 0) {
    elements.categoryTableBody.innerHTML = `<tr><td colspan="6">No categories saved yet.</td></tr>`;
    return;
  }

  elements.categoryTableBody.innerHTML = rows.map((category) => `
    <tr>
      <td>${escapeHtml(category.name)}</td>
      <td>${escapeHtml(category.storage_location)}</td>
      <td>${category.recommended_exp_days}</td>
      <td>${category.warning_threshold_percent}</td>
      <td>${category.item_count}</td>
      <td>
        <div class="row-actions">
          <button type="button" class="secondary" data-edit-category="${escapeAttribute(category.name)}">Edit</button>
        </div>
      </td>
    </tr>
  `).join("");

  document.querySelectorAll("[data-edit-category]").forEach((button) => {
    button.addEventListener("click", () => {
      const category = state.data.categories.find((entry) => entry.name === button.dataset.editCategory);
      openCategoryModal(category);
    });
  });
}

function renderFilterOptions() {
  fillSelect(elements.filterCategory, state.data.category_names, "All categories", state.filters.category);
  fillSelect(elements.filterStorage, state.data.storage_names, "All storage", state.filters.storage);
  elements.searchQuery.value = state.filters.query;
  elements.filterStatus.value = state.filters.status;
  elements.recordSearchQuery.value = state.recordFilters.query;
  elements.recordStatusFilter.value = state.recordFilters.status;
}

function renderDataLists() {
  elements.categoryList.innerHTML = state.data.category_names
    .map((name) => `<option value="${escapeAttribute(name)}"></option>`)
    .join("");
  elements.storageList.innerHTML = state.data.storage_names
    .map((name) => `<option value="${escapeAttribute(name)}"></option>`)
    .join("");
}

function renderBreakdown(target, data) {
  const entries = Object.entries(data);
  if (entries.length === 0) {
    target.innerHTML = `<p class="feedback">No active inventory to chart yet.</p>`;
    return;
  }

  const max = Math.max(...entries.map(([, count]) => count), 1);
  target.innerHTML = entries.map(([label, count]) => `
    <div class="breakdown-item">
      <div class="breakdown-meta">${escapeHtml(label)} · ${count}</div>
      <div class="breakdown-bar"><span style="width: ${(count / max) * 100}%"></span></div>
    </div>
  `).join("");
}

async function onScanSubmit(event) {
  event.preventDefault();
  const barcode = document.getElementById("scanBarcode").value.trim();
  const response = await postJson("/api/session/scan", { barcode });
  showMessage(elements.scanMessage, response.payload.error || response.payload.message, !response.ok);
  if (!response.ok) {
    return;
  }

  if (response.payload.mode === "new") {
    openItemModal("create", response.payload.defaults);
  } else {
    document.getElementById("scanBarcode").value = "";
    await loadState();
  }
}

async function approveSession() {
  const response = await postJson("/api/session/approve", {});
  showMessage(elements.scanMessage, response.payload.error || response.payload.message, !response.ok);
  if (response.ok) {
    await loadState();
  }
}

async function onFilterSubmit(event) {
  event.preventDefault();
  state.filters.query = elements.searchQuery.value.trim();
  state.filters.category = elements.filterCategory.value;
  state.filters.storage = elements.filterStorage.value;
  state.filters.status = elements.filterStatus.value;
  await loadState();
}

async function onCheckoutSubmit(event) {
  event.preventDefault();
  const barcode = document.getElementById("checkoutBarcode").value.trim();
  const response = await postJson("/api/checkout", { barcode });
  showMessage(elements.checkoutMessage, response.payload.error || response.payload.message, !response.ok);
  if (response.ok) {
    document.getElementById("checkoutBarcode").value = "";
    await loadState();
  }
}

async function onItemSubmit(event) {
  event.preventDefault();
  if (!event.currentTarget.reportValidity()) {
    showMessage(elements.itemFormMessage, "Please fill in the required fields before saving.", true);
    return;
  }
  const mode = document.getElementById("itemFormMode").value;
  const targetId = document.getElementById("itemFormTargetId").value;
  const payload = {
    barcode: document.getElementById("itemBarcode").value.trim(),
    name: document.getElementById("itemName").value.trim(),
    category: document.getElementById("itemCategory").value.trim(),
    storage_location: document.getElementById("itemStorage").value.trim(),
    purchase_date: document.getElementById("itemPurchaseDate").value,
    exp_date: document.getElementById("itemExpDate").value,
    archived: document.getElementById("itemArchived").value === "true",
  };

  let response;
  if (mode === "create") {
    response = await postJson("/api/session/items", payload);
  } else if (mode === "session") {
    response = await fetchJson(`/api/session/items/${targetId}`, "PUT", payload);
  } else if (mode === "record-create") {
    response = await postJson("/api/records", payload);
  } else if (mode === "record-edit") {
    response = await fetchJson(`/api/records/${targetId}`, "PUT", payload);
  } else {
    response = await fetchJson(`/api/items/${targetId}`, "PUT", payload);
  }

  showMessage(elements.itemFormMessage, response.payload.error || response.payload.message, !response.ok);
  if (response.ok) {
    elements.itemModal.close();
    document.getElementById("scanBarcode").value = "";
    await loadState();
  }
}

async function onRecordFilterSubmit(event) {
  event.preventDefault();
  state.recordFilters.query = elements.recordSearchQuery.value.trim();
  state.recordFilters.status = elements.recordStatusFilter.value;
  renderRecords();
}

async function onCategorySubmit(event) {
  event.preventDefault();
  const payload = {
    name: document.getElementById("categoryName").value.trim(),
    storage_location: document.getElementById("categoryStorage").value.trim(),
    recommended_exp_days: Number(document.getElementById("categoryDays").value),
    warning_threshold_percent: Number(document.getElementById("categoryWarning").value),
  };
  const response = await postJson("/api/categories", payload);
  showMessage(elements.categoryFormMessage, response.payload.error || response.payload.message, !response.ok);
  if (response.ok) {
    elements.categoryModal.close();
    await loadState();
  }
}

function openItemModal(mode, source) {
  const titleMap = {
    create: ["New Item", "Add item from barcode"],
    session: ["Session Edit", "Edit session item"],
    inventory: ["Inventory Edit", "Edit inventory item"],
    "record-create": ["New Record", "Add active or archived record"],
    "record-edit": ["Record Edit", "Edit active or archived record"],
  };
  const [eyebrow, title] = titleMap[mode];
  document.getElementById("itemModalEyebrow").textContent = eyebrow;
  document.getElementById("itemModalTitle").textContent = title;
  document.getElementById("itemFormMode").value = mode;
  document.getElementById("itemFormTargetId").value = source.session_id || source.item_id || "";
  document.getElementById("itemBarcode").value = source.barcode || "";
  document.getElementById("itemName").value = source.name || "";
  document.getElementById("itemCategory").value = source.category || "";
  document.getElementById("itemStorage").value = source.storage_location || "";
  document.getElementById("itemPurchaseDate").value = source.purchase_date || todayString();
  document.getElementById("itemPurchaseDate").disabled = false;
  document.getElementById("itemExpDate").value = source.exp_date || "";
  document.getElementById("itemArchived").value = String(Boolean(source.archived));
  document.getElementById("itemArchivedField").hidden = !mode.startsWith("record");
  document.getElementById("itemBarcode").readOnly = mode !== "create" && mode !== "record-create";
  showMessage(elements.itemFormMessage, "", false);
  elements.itemModal.showModal();
  if ((mode === "create" || mode === "record-create") && source.category) {
    syncRecommendedDate();
  }
}

function openCategoryModal(category = null) {
  document.getElementById("categoryModalTitle").textContent = category ? "Edit category" : "Add category";
  document.getElementById("categoryName").value = category?.name || "";
  document.getElementById("categoryStorage").value = category?.storage_location || "";
  document.getElementById("categoryDays").value = category?.recommended_exp_days || 7;
  document.getElementById("categoryWarning").value = category?.warning_threshold_percent || 80;
  showMessage(elements.categoryFormMessage, "", false);
  elements.categoryModal.showModal();
}

async function syncRecommendedDate() {
  const category = document.getElementById("itemCategory").value.trim();
  const purchaseDate = document.getElementById("itemPurchaseDate").value || todayString();
  if (!category) {
    return;
  }
  const response = await fetch(`/api/recommendation?category=${encodeURIComponent(category)}&purchase_date=${encodeURIComponent(purchaseDate)}`);
  const payload = await response.json();
  if (["create", "record-create"].includes(document.getElementById("itemFormMode").value)) {
    document.getElementById("itemExpDate").value = payload.exp_date;
  }
}

function fillSelect(select, values, emptyLabel, selectedValue) {
  select.innerHTML = [`<option value="">${emptyLabel}</option>`]
    .concat(values.map((value) => `<option value="${escapeAttribute(value)}">${escapeHtml(value)}</option>`))
    .join("");
  select.value = selectedValue || "";
}

function showMessage(target, message, isError) {
  target.textContent = message || "";
  target.classList.toggle("error", Boolean(isError));
}

function statusPill(status) {
  return `<span class="status-pill status-${status}">${statusLabel(status)}</span>`;
}

function statusLabel(status) {
  const labels = {
    fresh: "Fresh",
    expiring_soon: "Expiring Soon",
    expired: "Expired",
  };
  return labels[status] || status;
}

function filteredRecords() {
  return state.data.records.filter((item) => {
    const query = state.recordFilters.query.toLowerCase();
    if (query) {
      const haystack = `${item.item_id} ${item.barcode} ${item.name}`.toLowerCase();
      if (!haystack.includes(query)) {
        return false;
      }
    }
    if (state.recordFilters.status === "active" && item.archived) {
      return false;
    }
    if (state.recordFilters.status === "archived" && !item.archived) {
      return false;
    }
    return true;
  });
}

function recordById(itemId) {
  return state.data.records.find((entry) => entry.item_id === itemId);
}

function todayString() {
  return new Date().toISOString().slice(0, 10);
}

async function postJson(url, payload) {
  return fetchJson(url, "POST", payload);
}

async function fetchJson(url, method, payload) {
  const response = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return {
    ok: response.ok,
    payload: await response.json(),
  };
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function escapeAttribute(value) {
  return escapeHtml(value);
}