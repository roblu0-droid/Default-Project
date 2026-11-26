/* ==========================================================================
   Hatod Akean — admin console
   Master order queue, status controls, live customer notifications.
   ========================================================================== */

(function () {
  "use strict";

  const config = window.HATOD || {};
  const STATUSES = config.statuses || [
    "Preparing", "Ready", "Out for delivery", "Delivered", "Cancelled",
  ];
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const toastStack = $("#toastStack");
  const table = $("#adminTable");

  const state = {
    orders: [],
    filter: "All",
    busy: new Set(),
    timer: null,
  };

  function esc(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function money(value) {
    const amount = Number(value) || 0;
    return "₱" + amount.toLocaleString("en-PH", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  function formatDateTime(value) {
    const date = new Date(String(value || "").replace(" ", "T"));
    if (Number.isNaN(date.getTime())) return String(value || "");
    return date.toLocaleString("en-PH", {
      month: "short", day: "numeric", hour: "numeric", minute: "2-digit",
    });
  }

  async function api(path, options = {}) {
    const response = await fetch(path, {
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    let payload = null;
    try { payload = await response.json(); } catch (error) { payload = null; }
    if (!response.ok) {
      const detail = payload && payload.detail;
      const message = typeof detail === "string" ? detail : "Request failed. Please try again.";
      const error = new Error(message);
      error.status = response.status;
      throw error;
    }
    return payload;
  }

  function toast(title, message, type = "info") {
    if (!toastStack) return;
    const el = document.createElement("div");
    el.className = "toast is-" + type;
    el.innerHTML =
      '<span class="toast-icon" aria-hidden="true">' +
      (type === "error" ? "!" : type === "success" ? "✓" : "✦") +
      '</span><div class="toast-copy"><strong></strong><p></p></div>';
    el.querySelector("strong").textContent = title;
    el.querySelector("p").textContent = message || "";
    toastStack.appendChild(el);
    const remove = () => {
      el.classList.add("is-leaving");
      window.setTimeout(() => el.remove(), 280);
    };
    el.addEventListener("click", remove);
    window.setTimeout(remove, 5200);
  }

  function statusClass(status) {
    const value = String(status || "").toLowerCase();
    if (value.includes("cancel") || value.includes("review")) return "status-needs-review";
    if (value.includes("out for delivery")) return "status-out";
    if (value.includes("delivered")) return "status-delivered";
    if (value.includes("ready")) return "status-ready";
    return "status-preparing";
  }

  function statusBadge(status) {
    return '<span class="order-status ' + statusClass(status) + '"><span class="status-dot"></span>' +
      esc(status) + "</span>";
  }

  function renderStats(payload) {
    const counts = payload.counts || {};
    const set = (id, value) => { const el = $(id); if (el) el.textContent = value; };
    set("#statTotal", (payload.orders || []).length);
    set("#statPreparing", counts.Preparing || 0);
    set("#statReady", counts.Ready || 0);
    set("#statOut", counts["Out for delivery"] || 0);
    set("#statDelivered", counts.Delivered || 0);
    set("#statRevenue", money(payload.total_revenue_php || 0));
  }

  function renderFilters() {
    const wrap = $("#adminFilters");
    if (!wrap) return;
    const options = ["All", ...STATUSES];
    wrap.innerHTML = options
      .map((status) => {
        const count = status === "All"
          ? state.orders.length
          : state.orders.filter((order) => order.status === status).length;
        return '<button type="button" data-filter="' + esc(status) + '"' +
          (state.filter === status ? ' class="is-active"' : "") + ">" +
          esc(status) + " · " + count + "</button>";
      })
      .join("");
  }

  function renderTable() {
    if (!table) return;
    const orders = state.filter === "All"
      ? state.orders
      : state.orders.filter((order) => order.status === state.filter);

    if (!orders.length) {
      table.innerHTML = '<div class="admin-empty"><strong>Nothing here yet</strong>' +
        (state.filter === "All"
          ? "Customer orders will appear as soon as someone checks out."
          : "No orders currently at " + esc(state.filter) + ".") + "</div>";
      return;
    }

    table.innerHTML =
      '<table class="admin-table"><thead><tr>' +
      "<th>Order</th><th>Customer</th><th>Items</th><th>Deliver to</th>" +
      "<th>Total</th><th>Status</th><th>Update</th>" +
      "</tr></thead><tbody>" +
      orders.map((order) => {
        const items = order.items || [];
        const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);
        const itemText = items
          .map((item) => item.quantity + "× " + item.name)
          .join(", ");
        const busy = state.busy.has(order.id);
        const options = STATUSES.map((status) =>
          '<option value="' + esc(status) + '"' +
          (status === order.status ? " selected" : "") + ">" + esc(status) + "</option>"
        ).join("");
        return (
          "<tr>" +
          '<td><span class="admin-ref">' + esc(order.reference) + "</span>" +
          '<span class="admin-sub">' + esc(formatDateTime(order.created_at)) + "</span></td>" +
          '<td class="admin-customer"><strong>' + esc(order.customer_name) + "</strong>" +
          '<span class="admin-sub">' + esc(order.customer_email || "—") + "</span></td>" +
          '<td><div class="admin-items">' + esc(itemText || "—") + "</div>" +
          '<span class="admin-sub">' + itemCount + " item" + (itemCount === 1 ? "" : "s") + "</span></td>" +
          '<td><div class="admin-address">' + esc(order.barangay) + ", " + esc(order.municipality) +
          '</div><span class="admin-sub">' + esc(order.payment_method) + "</span></td>" +
          '<td class="admin-total">' + money(order.total_php) + "</td>" +
          "<td>" + statusBadge(order.status) + "</td>" +
          '<td><div class="admin-actions">' +
          '<select class="admin-status-select" data-status-select="' + order.id + '"' +
          (busy ? " disabled" : "") + ">" + options + "</select>" +
          '<button class="admin-update" type="button" data-update="' + order.id + '"' +
          (busy ? " disabled" : "") + ">Update</button>" +
          '<button class="admin-auto" type="button" data-auto="' + order.id + '"' +
          (busy || order.status === "Delivered" || order.status === "Cancelled" ? " disabled" : "") +
          ">Auto progress</button>" +
          "</div></td>" +
          "</tr>"
        );
      }).join("") +
      "</tbody></table>";
  }

  async function loadOrders(quiet = false) {
    try {
      const payload = await api("/api/admin/orders");
      state.orders = payload.orders || [];
      renderStats(payload);
      renderFilters();
      renderTable();
    } catch (error) {
      if (!quiet && table) {
        table.innerHTML = '<div class="admin-empty"><strong>Unable to load orders</strong>' +
          esc(error.message) + "</div>";
      }
    }
  }

  async function updateStatus(orderId, newStatus, notify = true) {
    const order = state.orders.find((item) => item.id === orderId);
    if (!order) return false;
    if (order.status === newStatus) return false;
    state.busy.add(orderId);
    renderTable();
    try {
      const payload = await api("/api/admin/orders/" + orderId + "/status", {
        method: "PATCH",
        body: JSON.stringify({ status: newStatus }),
      });
      const index = state.orders.findIndex((item) => item.id === orderId);
      if (index >= 0) state.orders[index] = payload.order;
      if (notify) {
        toast("Customer notified", payload.notification.title + " — sent live to " +
          order.customer_name + ".", "success");
      }
      return true;
    } catch (error) {
      if (notify) toast("Update failed", error.message, "error");
      return false;
    } finally {
      state.busy.delete(orderId);
      renderTable();
      renderFilters();
    }
  }

  function wait(ms) {
    return new Promise((resolve) => window.setTimeout(resolve, ms));
  }

  async function autoProgress(orderId, button) {
    const order = state.orders.find((item) => item.id === orderId);
    if (!order) return;
    const start = STATUSES.indexOf(order.status);
    const targets = STATUSES.slice(start + 1).filter(
      (status) => status !== "Cancelled"
    );
    if (!targets.length) return;

    if (button) button.disabled = true;
    for (const status of targets) {
      const ok = await updateStatus(orderId, status);
      if (!ok) break;
      await wait(2600);
    }
    if (button) button.disabled = false;
    toast("Demo complete", "The customer received a notification at every step.", "success");
    await loadOrders(true);
  }

  // ---------------------------------------------------------------- events
  if (table) {
    table.addEventListener("click", (event) => {
      const updateButton = event.target.closest("[data-update]");
      if (updateButton) {
        const id = Number(updateButton.dataset.update);
        const select = $('[data-status-select="' + id + '"]', table);
        if (select) updateStatus(id, select.value);
        return;
      }
      const autoButton = event.target.closest("[data-auto]");
      if (autoButton) autoProgress(Number(autoButton.dataset.auto), autoButton);
    });
  }

  const filters = $("#adminFilters");
  if (filters) {
    filters.addEventListener("click", (event) => {
      const button = event.target.closest("[data-filter]");
      if (!button) return;
      state.filter = button.dataset.filter;
      renderFilters();
      renderTable();
    });
  }

  const refreshButton = $("#refreshOrdersButton");
  if (refreshButton) {
    refreshButton.addEventListener("click", () => loadOrders());
  }

  const logoutButton = $("#adminLogoutButton");
  if (logoutButton) {
    logoutButton.addEventListener("click", async () => {
      try { await api("/api/auth/logout", { method: "POST" }); } catch (error) { /* ignore */ }
      window.location.href = "/";
    });
  }

  loadOrders();
  state.timer = window.setInterval(() => {
    if (state.busy.size === 0) loadOrders(true);
  }, 15000);
})();
