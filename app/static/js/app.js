/* ==========================================================================
   Hatod Akean — ordering application
   Menu + cart + checkout + orders + live EIP trace + overlays.
   ========================================================================== */

(function () {
  "use strict";

  const config = window.HATOD || {};
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  const state = {
    user: config.user || {},
    menu: [],
    zones: {},
    cart: new Map(),
    activeCategory: "All",
    search: "",
    municipality: "All",
    logIds: new Set(),
    orders: [],
    lastOrderId: null,
    stream: null,
    streamRetry: null,
  };

  const CART_KEY = "hatod_cart_v1";
  const toastStack = $("#toastStack");
  const menuGrid = $("#menuGrid");
  const menuEmpty = $("#menuEmpty");
  const menuResultCount = $("#menuResultCount");
  const cartDrawer = $("#cartDrawer");
  const cartBackdrop = $("#cartBackdrop");
  const cartItemsEl = $("#cartItems");
  const cartEmpty = $("#cartEmpty");
  const cartFooter = $("#cartFooter");
  const cartCount = $("#cartCount");
  const integrationLog = $("#integrationLog");
  const consolePlaceholder = $("#consolePlaceholder");

  /* ------------------------------------------------------------------ */
  /* Utilities                                                           */
  /* ------------------------------------------------------------------ */
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

  function moneyShort(value) {
    const amount = Number(value) || 0;
    const decimals = Number.isInteger(amount) ? 0 : 2;
    return "₱" + amount.toLocaleString("en-PH", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: 2,
    });
  }

  function parseDate(value) {
    if (!value) return null;
    let source = String(value);
    if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(source)) {
      source = source.replace(" ", "T") + "Z";
    }
    const date = new Date(source);
    return Number.isNaN(date.getTime()) ? null : date;
  }

  function formatDateTime(value) {
    const date = parseDate(value);
    if (!date) return String(value || "");
    return date.toLocaleString("en-PH", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  }

  function formatTime(value) {
    const date = parseDate(value);
    if (!date) return "";
    return date.toLocaleTimeString("en-PH", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  }

  function debounce(fn, wait) {
    let timer = null;
    return function debounced(...args) {
      window.clearTimeout(timer);
      timer = window.setTimeout(() => fn.apply(this, args), wait);
    };
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

  async function api(path, options = {}) {
    const response = await fetch(path, {
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });

    let payload = null;
    try {
      payload = await response.json();
    } catch (error) {
      payload = null;
    }

    if (!response.ok) {
      let message = "Something went wrong. Please try again.";
      if (payload && payload.detail) {
        message = Array.isArray(payload.detail)
          ? payload.detail
              .map((item) => item.msg || item.message || "")
              .filter(Boolean)
              .join(" ")
          : payload.detail;
      }
      const error = new Error(message);
      error.status = response.status;
      if (response.status === 401) {
        toast("Session expired", "Please sign in again to continue.", "error");
        window.setTimeout(() => window.location.assign("/"), 1400);
      }
      throw error;
    }
    return payload;
  }

  function syncBodyLock() {
    const hasModal = $$(".modal-backdrop").some((modal) => !modal.hidden);
    const hasDrawer = cartDrawer && cartDrawer.classList.contains("is-open");
    document.body.classList.toggle("no-scroll", hasModal || hasDrawer);
  }

  function sectionForScroll(id) {
    const target = document.getElementById(id);
    if (!target) return;
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  /* ------------------------------------------------------------------ */
  /* Menu                                                                */
  /* ------------------------------------------------------------------ */
  function stockLabel(item) {
    if (!item.is_available || item.stock_qty <= 0) return { text: "Sold out", cls: "is-out" };
    if (item.stock_qty <= 6) return { text: item.stock_qty + " left", cls: "low" };
    return { text: item.stock_qty + " in stock", cls: "" };
  }

  function menuCard(item, index) {
    const stock = stockLabel(item);
    const inCart = state.cart.get(item.id) || 0;
    const canAdd = item.is_available && item.stock_qty > inCart;
    const tags = [];
    if (item.prep_minutes) tags.push(item.prep_minutes + " min prep");
    if (item.allergens && /none/i.test(item.allergens)) tags.push("No allergens declared");
    else if (item.allergens) tags.push("Allergens listed");
    if (item.is_signature) tags.push("House favorite");

    return (
      '<article class="menu-card" data-id="' + item.id + '" style="animation-delay:' +
      Math.min(index * 35, 380) +
      'ms">' +
      '<div class="menu-card-media" data-dish-open="' + item.id + '">' +
      '<img src="' + esc(item.image_url) + '" alt="' + esc(item.name) + '" loading="lazy">' +
      (item.is_signature ? '<span class="signature-tag">Signature</span>' : "") +
      '<span class="menu-stock ' + stock.cls + '">' + esc(stock.text) + "</span>" +
      "</div>" +
      '<div class="menu-card-body">' +
      '<div class="menu-card-top">' +
      '<span class="menu-card-category">' + esc(item.category) + "</span>" +
      '<span class="menu-card-loc"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-5.2 7-11a7 7 0 1 0-14 0c0 5.8 7 11 7 11Z"/><circle cx="12" cy="10" r="2.4"/></svg>' +
      esc(item.municipality) +
      "</span></div>" +
      '<h3 class="menu-card-title" data-dish-open="' + item.id + '">' + esc(item.name) + "</h3>" +
      '<p class="menu-card-desc">' + esc(item.description) + "</p>" +
      '<div class="menu-card-tags">' + tags.map((tag) => "<span>" + esc(tag) + "</span>").join("") + "</div>" +
      '<div class="menu-card-footer">' +
      '<div class="menu-price">' + moneyShort(item.price_php) + "<small>/ order</small></div>" +
      '<button class="add-button" type="button" data-add="' + item.id + '"' +
      (canAdd ? "" : " disabled") +
      ' aria-label="Add ' + esc(item.name) + ' to your bag">' +
      (canAdd ? "+ Add" : inCart >= item.stock_qty ? "Maxed" : "Sold out") +
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M12 5v14"/></svg></button>' +
      "</div></div></article>"
    );
  }

  function filteredMenu() {
    const term = state.search.trim().toLowerCase();
    return state.menu.filter((item) => {
      if (state.activeCategory !== "All" && item.category !== state.activeCategory) return false;
      if (state.municipality !== "All" && item.municipality !== state.municipality) return false;
      if (!term) return true;
      return [item.name, item.description, item.ingredients, item.category, item.municipality]
        .join(" ")
        .toLowerCase()
        .includes(term);
    });
  }

  function renderMenu() {
    if (!menuGrid) return;
    const items = filteredMenu();
    menuGrid.innerHTML = items.map(menuCard).join("");
    if (menuEmpty) menuEmpty.hidden = items.length > 0;
    if (menuResultCount) {
      menuResultCount.textContent = items.length + (items.length === 1 ? " dish" : " dishes") + " on the table";
    }
    $$(".category-tab").forEach((tab) => {
      tab.classList.toggle("is-active", tab.dataset.category === state.activeCategory);
    });
  }

  async function loadMenu() {
    try {
      const payload = await api("/api/menu");
      state.menu = payload.items || [];
      renderMenu();
    } catch (error) {
      if (menuGrid) {
        menuGrid.innerHTML = "";
      }
      if (menuEmpty) menuEmpty.hidden = false;
      if (menuResultCount) menuResultCount.textContent = "Menu unavailable";
      toast("Could not load the menu", error.message, "error");
    }
  }

  /* ------------------------------------------------------------------ */
  /* Dish modal                                                          */
  /* ------------------------------------------------------------------ */
  let dishModal = null;

  function ensureDishModal() {
    if (dishModal) return dishModal;
    dishModal = document.createElement("div");
    dishModal.className = "modal-backdrop";
    dishModal.id = "dishModal";
    dishModal.hidden = true;
    dishModal.innerHTML =
      '<div class="dish-modal" role="dialog" aria-modal="true" aria-labelledby="dishModalTitle">' +
      '<button class="modal-close" type="button" data-dish-close aria-label="Close dish details">' +
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg></button>' +
      '<div class="dish-modal-media">' +
      '<img id="dishModalImage" src="" alt="">' +
      '<span class="signature-tag" id="dishModalSignature" hidden>Signature</span>' +
      '<span class="dish-modal-loc" id="dishModalLoc"></span>' +
      "</div>" +
      '<div class="dish-modal-copy">' +
      '<div class="dish-modal-top">' +
      '<span class="menu-card-category" id="dishModalCategory"></span>' +
      '<span class="menu-card-loc" id="dishModalStock"></span>' +
      "</div>" +
      '<h2 id="dishModalTitle"></h2>' +
      '<p class="dish-modal-desc" id="dishModalDesc"></p>' +
      '<div class="dish-detail-grid">' +
      '<div><span>Ingredients</span><p id="dishModalIngredients"></p></div>' +
      '<div><span>Cooking notes</span><p id="dishModalNotes"></p></div>' +
      '<div><span>Allergens</span><p id="dishModalAllergens"></p></div>' +
      '<div><span>Prep time</span><p id="dishModalPrep"></p></div>' +
      "</div>" +
      '<div class="dish-modal-footer">' +
      '<div class="menu-price" id="dishModalPrice"></div>' +
      '<button class="primary-cta" type="button" id="dishModalAdd"><span>Add to bag</span>' +
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></button>' +
      "</div></div></div>";
    document.body.appendChild(dishModal);

    dishModal.addEventListener("click", (event) => {
      if (event.target === dishModal || event.target.closest("[data-dish-close]")) {
        closeDishModal();
      }
    });

    $("#dishModalAdd").addEventListener("click", () => {
      const id = Number(dishModal.dataset.id);
      if (id) {
        addToCart(id, 1);
        closeDishModal();
        openCart();
      }
    });

    return dishModal;
  }

  function openDishModal(id) {
    const item = state.menu.find((entry) => entry.id === id);
    if (!item) return;
    ensureDishModal();
    const stock = stockLabel(item);
    dishModal.dataset.id = String(id);
    $("#dishModalImage").src = item.image_url;
    $("#dishModalImage").alt = item.name;
    $("#dishModalSignature").hidden = !item.is_signature;
    $("#dishModalLoc").innerHTML =
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-5.2 7-11a7 7 0 1 0-14 0c0 5.8 7 11 7 11Z"/><circle cx="12" cy="10" r="2.4"/></svg>' +
      esc(item.municipality);
    $("#dishModalCategory").textContent = item.category;
    $("#dishModalStock").textContent = stock.text;
    $("#dishModalTitle").textContent = item.name;
    $("#dishModalDesc").textContent = item.description;
    $("#dishModalIngredients").textContent = item.ingredients || "Ask the kitchen for today's ingredients.";
    $("#dishModalNotes").textContent = item.cooking_notes || "Prepared fresh by a local Aklanon kitchen.";
    $("#dishModalAllergens").textContent = item.allergens || "None declared.";
    $("#dishModalPrep").textContent = (item.prep_minutes || 30) + " minutes · " + item.municipality;
    $("#dishModalPrice").innerHTML = moneyShort(item.price_php) + "<small>/ order</small>";
    const addButton = $("#dishModalAdd");
    const inCart = state.cart.get(item.id) || 0;
    const canAdd = item.is_available && item.stock_qty > inCart;
    addButton.disabled = !canAdd;
    addButton.querySelector("span").textContent = canAdd
      ? "Add to bag"
      : inCart >= item.stock_qty
        ? "Maximum in bag"
        : "Sold out";
    dishModal.hidden = false;
    syncBodyLock();
    const close = dishModal.querySelector(".modal-close");
    close && close.focus({ preventScroll: true });
  }

  function closeDishModal() {
    if (!dishModal) return;
    dishModal.hidden = true;
    syncBodyLock();
  }

  /* ------------------------------------------------------------------ */
  /* Cart                                                                */
  /* ------------------------------------------------------------------ */
  function cartQuantity() {
    let total = 0;
    state.cart.forEach((qty) => {
      total += qty;
    });
    return total;
  }

  function cartSubtotal() {
    let total = 0;
    state.cart.forEach((qty, id) => {
      const item = state.menu.find((entry) => entry.id === id);
      if (item) total += Number(item.price_php) * qty;
    });
    return Math.round(total * 100) / 100;
  }

  function hydrateCart() {
    let stored = null;
    try {
      stored = JSON.parse(window.localStorage.getItem(CART_KEY) || "null");
    } catch (error) {
      stored = null;
    }
    state.cart.clear();
    if (stored && typeof stored === "object") {
      Object.keys(stored).forEach((key) => {
        const id = Number(key);
        const qty = Math.max(0, Math.min(20, parseInt(stored[key], 10) || 0));
        const item = state.menu.find((entry) => entry.id === id);
        if (item && qty > 0 && item.is_available && item.stock_qty > 0) {
          state.cart.set(id, Math.min(qty, item.stock_qty));
        }
      });
    }
    persistCart();
    updateCartBadge();
    renderCart();
  }

  function persistCart() {
    try {
      const plain = {};
      state.cart.forEach((qty, id) => {
        if (qty > 0) plain[id] = qty;
      });
      window.localStorage.setItem(CART_KEY, JSON.stringify(plain));
    } catch (error) {
      /* storage may be unavailable */
    }
  }

  function updateCartBadge() {
    if (!cartCount) return;
    const count = cartQuantity();
    cartCount.textContent = String(count);
    cartCount.hidden = count === 0;
    if (count > 0) {
      cartCount.animate(
        [
          { transform: "scale(1)" },
          { transform: "scale(1.28)" },
          { transform: "scale(1)" },
        ],
        { duration: 320, easing: "ease-out" }
      );
    }
  }

  function renderCart() {
    if (!cartItemsEl) return;
    const entries = [];
    state.cart.forEach((qty, id) => {
      const item = state.menu.find((entry) => entry.id === id);
      if (item && qty > 0) entries.push({ item, qty });
    });

    cartItemsEl.innerHTML = entries
      .map(({ item, qty }) => {
        return (
          '<div class="cart-item" data-cart-row="' + item.id + '">' +
          '<div class="cart-item-media"><img src="' + esc(item.image_url) + '" alt="' + esc(item.name) + '"></div>' +
          '<div class="cart-item-copy"><strong>' + esc(item.name) + "</strong>" +
          "<span>" + money(item.price_php) + " each</span>" +
          '<div class="qty-control">' +
          '<button class="qty-button" type="button" data-cart-dec="' + item.id + '" aria-label="Remove one ' + esc(item.name) + '">−</button>' +
          '<span class="qty-value">' + qty + "</span>" +
          '<button class="qty-button" type="button" data-cart-inc="' + item.id + '" aria-label="Add one ' + esc(item.name) + '">+</button>' +
          '<button class="remove-button" type="button" data-cart-remove="' + item.id + '">Remove</button>' +
          "</div></div>" +
          '<div class="cart-item-total">' + money(item.price_php * qty) + "</div>" +
          "</div>"
        );
      })
      .join("");

    if (cartEmpty) cartEmpty.hidden = entries.length > 0;
    if (cartFooter) cartFooter.hidden = entries.length === 0;
    if (cartItemsEl) cartItemsEl.hidden = entries.length === 0;

    const countEl = $("#cartItemCount");
    if (countEl) countEl.textContent = "(" + cartQuantity() + ")";
    const subtotal = cartSubtotal();
    const subtotalEl = $("#cartSubtotal");
    const totalEl = $("#cartTotal");
    if (subtotalEl) subtotalEl.textContent = money(subtotal);
    if (totalEl) totalEl.textContent = money(subtotal);

    updateCartBadge();
    if (!$("#checkoutModal") || $("#checkoutModal").hidden === false) updateCheckoutSummary();
  }

  function addToCart(id, qty = 1) {
    const item = state.menu.find((entry) => entry.id === id);
    if (!item) return;
    const current = state.cart.get(id) || 0;
    const next = Math.min(current + qty, item.stock_qty, 20);
    if (next === current) {
      toast("Stock limit reached", "Only " + item.stock_qty + " portion(s) of " + item.name + " are available.", "error");
      return;
    }
    state.cart.set(id, next);
    persistCart();
    renderCart();
    renderMenu();
    toast(item.name + " added", "Your hatod bag now has " + cartQuantity() + " item(s).", "success");
  }

  function setCartQuantity(id, qty) {
    const item = state.menu.find((entry) => entry.id === id);
    if (!item) return;
    if (qty <= 0) {
      state.cart.delete(id);
    } else {
      state.cart.set(id, Math.min(qty, item.stock_qty, 20));
    }
    persistCart();
    renderCart();
    renderMenu();
  }

  function openCart() {
    if (!cartDrawer) return;
    cartBackdrop.hidden = false;
    cartDrawer.classList.add("is-open");
    cartDrawer.setAttribute("aria-hidden", "false");
    syncBodyLock();
    const closeButton = $("#cartCloseButton");
    closeButton && closeButton.focus({ preventScroll: true });
  }

  function closeCart() {
    if (!cartDrawer) return;
    cartDrawer.classList.remove("is-open");
    cartDrawer.setAttribute("aria-hidden", "true");
    cartBackdrop.hidden = true;
    syncBodyLock();
  }

  /* ------------------------------------------------------------------ */
  /* Delivery zones + checkout                                           */
  /* ------------------------------------------------------------------ */
  async function loadZones() {
    try {
      const payload = await api("/api/zones");
      state.zones = {};
      (payload.zones || []).forEach((zone) => {
        state.zones[zone.municipality] = zone;
      });
    } catch (error) {
      toast("Delivery zones unavailable", error.message, "error");
    }
  }

  function populateBarangays(municipality, selected) {
    const select = $("#checkoutBarangay");
    if (!select) return;
    const zone = state.zones[municipality];
    const list = zone ? zone.barangays : [];
    select.innerHTML = list.map((name) => '<option value="' + esc(name) + '">' + esc(name) + "</option>").join("");
    if (selected && list.includes(selected)) select.value = selected;
  }

  function updateCheckoutSummary() {
    const municipality = $("#checkoutMunicipality")?.value || state.user.municipality;
    const zone = state.zones[municipality];
    const subtotal = cartSubtotal();
    const fee = zone ? Number(zone.fee) : 0;

    const hubEl = $("#checkoutHub");
    const etaEl = $("#checkoutEta");
    const subtotalEl = $("#checkoutSubtotal");
    const deliveryEl = $("#checkoutDelivery");
    const totalEl = $("#checkoutTotal");
    const summaryItems = $("#checkoutSummaryItems");

    if (hubEl) hubEl.textContent = zone ? zone.hub : "Choose a delivery zone";
    if (etaEl) etaEl.textContent = zone ? zone.eta + " delivery" : "Delivery estimate pending";
    if (subtotalEl) subtotalEl.textContent = money(subtotal);
    if (deliveryEl) deliveryEl.textContent = zone ? money(fee) : "—";
    if (totalEl) totalEl.textContent = money(subtotal + fee);

    if (summaryItems) {
      const lines = [];
      state.cart.forEach((qty, id) => {
        const item = state.menu.find((entry) => entry.id === id);
        if (item && qty > 0) {
          lines.push(
            '<div class="summary-item"><span><b>' + qty + "×</b>" + esc(item.name) + "</span><span>" +
              money(item.price_php * qty) +
              "</span></div>"
          );
        }
      });
      summaryItems.innerHTML = lines.join("") || '<div class="summary-item"><span>Your bag is empty</span></div>';
    }
  }

  function openCheckout() {
    if (cartQuantity() === 0) {
      toast("Your bag is empty", "Add a heritage dish before checking out.", "error");
      return;
    }
    const modal = $("#checkoutModal");
    if (!modal) return;
    closeCart();
    $("#checkoutPanel").hidden = false;
    $("#orderSuccess").hidden = true;
    $("#checkoutError").hidden = true;

    const municipalitySelect = $("#checkoutMunicipality");
    const preferred = state.user.municipality;
    if (municipalitySelect && state.zones[preferred]) municipalitySelect.value = preferred;
    const municipality = municipalitySelect ? municipalitySelect.value : preferred;
    populateBarangays(municipality);
    updateCheckoutSummary();

    modal.hidden = false;
    syncBodyLock();
    modal.scrollTop = 0;
    const closeButton = $("#checkoutCloseButton");
    closeButton && closeButton.focus({ preventScroll: true });
  }

  function closeCheckout() {
    const modal = $("#checkoutModal");
    if (!modal) return;
    modal.hidden = true;
    $("#checkoutPanel").hidden = false;
    $("#orderSuccess").hidden = true;
    syncBodyLock();
  }

  function showOrderSuccess(order, integration) {
    $("#checkoutPanel").hidden = true;
    const success = $("#orderSuccess");
    success.hidden = false;
    const modal = $("#checkoutModal");
    modal.scrollTop = 0;

    const firstName = (order.customer_name || "friend").split(" ")[0];
    $("#successName").textContent = firstName;
    $("#successHub").textContent = order.hub;
    $("#successReference").textContent = order.reference;

    const route = integration && integration.route;
    const lane = route ? route.lane : "kitchen";
    const steps = [
      { label: "Order accepted", hub: true },
      { label: order.hub },
      { label: lane },
      { label: order.barangay + ", " + order.municipality },
    ];
    $("#successRoute").innerHTML = steps
      .map((step, index) => {
        const cls = step.hub ? "route-step is-hub" : "route-step";
        const arrow = index < steps.length - 1 ? '<span class="route-arrow">→</span>' : "";
        return '<span class="' + cls + '">' + esc(step.label) + "</span>" + arrow;
      })
      .join("");

    const logs = (integration && integration.logs) || [];
    const timeline = logs.slice(0, 5);
    $("#successTimeline").innerHTML = timeline.length
      ? timeline
          .map(
            (log, index) =>
              '<div class="timeline-step" style="animation-delay:' + index * 45 + 'ms">' +
              '<span class="timeline-icon">' + (log.status === "error" ? "!" : "✓") + "</span>" +
              '<div class="timeline-copy"><strong>' + esc(log.pattern) + "</strong><span>" + esc(log.title) + "</span></div></div>"
          )
          .join("")
      : '<div class="timeline-step"><span class="timeline-icon">✦</span><div class="timeline-copy"><strong>Kitchen notified</strong><span>' +
        esc(order.hub) +
        " is preparing your order.</span></div></div>";

    state.lastOrderId = order.id;
    toast("Salamat, " + firstName + "!", "Order " + order.reference + " is now in the live EIP bus.", "success");
  }

  const checkoutForm = $("#checkoutForm");
  checkoutForm &&
    checkoutForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const errorEl = $("#checkoutError");
      errorEl.hidden = true;

      const municipality = $("#checkoutMunicipality").value;
      const barangay = $("#checkoutBarangay").value;
      const delivery_address = $("#checkoutAddress").value.trim();
      const contact_number = $("#checkoutContact").value.trim();
      const paymentInput = checkoutForm.querySelector('input[name="payment_method"]:checked');
      const payment_method = paymentInput ? paymentInput.value : "Cash on Delivery";
      const notes = $("#checkoutNotes").value.trim();

      if (cartQuantity() === 0) {
        errorEl.textContent = "Your bag is empty. Add a dish first.";
        errorEl.hidden = false;
        return;
      }
      if (!state.zones[municipality]) {
        errorEl.textContent = "Choose one of our Aklan delivery municipalities.";
        errorEl.hidden = false;
        return;
      }
      if (!barangay) {
        errorEl.textContent = "Choose your barangay.";
        errorEl.hidden = false;
        return;
      }
      if (delivery_address.length < 5) {
        errorEl.textContent = "Add a complete delivery address so the rider can find you.";
        errorEl.hidden = false;
        $("#checkoutAddress").focus();
        return;
      }
      if (!/^[0-9+\-\s()]{7,20}$/.test(contact_number)) {
        errorEl.textContent = "Enter a valid mobile number, for example 0917 000 0000.";
        errorEl.hidden = false;
        $("#checkoutContact").focus();
        return;
      }

      const items = [];
      state.cart.forEach((quantity, menu_item_id) => {
        if (quantity > 0) items.push({ menu_item_id, quantity });
      });

      const button = $("#placeOrderButton");
      const label = button.querySelector("span");
      const original = label ? label.textContent : "";
      button.disabled = true;
      button.classList.add("is-busy");
      if (label) label.textContent = "Sending to the bus…";

      try {
        const payload = await api("/api/orders", {
          method: "POST",
          body: JSON.stringify({
            items,
            municipality,
            barangay,
            delivery_address,
            contact_number,
            payment_method,
            notes,
          }),
        });

        state.cart.clear();
        persistCart();
        renderCart();
        await loadMenu();
        showOrderSuccess(payload.order, payload.integration);
        ingestLogs((payload.integration && payload.integration.logs) || []);
        window.setTimeout(loadIntegrationLogs, 700);
        loadOrders();
      } catch (error) {
        errorEl.textContent = error.message;
        errorEl.hidden = false;
        toast("Order not placed", error.message, "error");
      } finally {
        button.disabled = false;
        button.classList.remove("is-busy");
        if (label) label.textContent = original;
      }
    });

  /* ------------------------------------------------------------------ */
  /* Orders                                                              */
  /* ------------------------------------------------------------------ */
  function statusClass(status) {
    const value = String(status || "").toLowerCase();
    if (value.includes("review")) return "status-needs-review";
    if (value.includes("deliver")) return "status-delivered";
    return "status-preparing";
  }

  function orderItemsSummary(items) {
    const names = items.map((item) => item.quantity + "× " + item.name);
    if (names.length <= 2) return names.join(" · ");
    return names.slice(0, 2).join(" · ") + " +" + (names.length - 2) + " more";
  }

  function renderOrders() {
    const list = $("#ordersList");
    if (!list) return;
    if (!state.orders.length) {
      list.innerHTML =
        '<div class="menu-empty"><span class="empty-icon">🍽️</span><h3>No hatod orders yet</h3>' +
        "<p>Your first Aklanon feast is one tap away.</p>" +
        '<button type="button" class="text-button" data-browse-menu>Browse the menu</button></div>';
      return;
    }

    list.innerHTML = state.orders
      .map((order, index) => {
        const itemCount = order.items.reduce((sum, item) => sum + item.quantity, 0);
        return (
          '<article class="order-card" style="animation-delay:' + Math.min(index * 40, 240) + 'ms">' +
          '<div class="order-card-head">' +
          '<span class="order-status ' + statusClass(order.status) + '"><span class="status-dot"></span>' + esc(order.status) + "</span>" +
          '<span class="order-date">' + esc(formatDateTime(order.created_at)) + "</span>" +
          "</div>" +
          '<div class="order-card-main"><div>' +
          '<span class="order-ref">' + esc(order.reference) + "</span>" +
          "<h3>" + itemCount + " item" + (itemCount === 1 ? "" : "s") + " · " + esc(order.hub) + "</h3>" +
          "<p>" + esc(orderItemsSummary(order.items)) + " · " + esc(order.barangay) + ", " + esc(order.municipality) + "</p>" +
          "</div>" +
          '<div class="order-total"><span>Total</span><strong>' + money(order.total_php) + "</strong></div>" +
          "</div>" +
          '<div class="order-card-footer"><span class="order-eta">' +
          '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/></svg>' +
          esc(order.payment_method) + " · " + esc(order.status === "Needs review" ? "ops review" : "in the kitchen") +
          "</span>" +
          '<div class="order-actions">' +
          '<button class="outline-button small" type="button" data-order-trace="' + order.id + '">EIP trace</button>' +
          '<button class="primary-cta small" type="button" data-order-view="' + order.id + '"><span>View order</span></button>' +
          "</div></div></article>"
        );
      })
      .join("");
  }

  async function loadOrders() {
    try {
      const payload = await api("/api/orders");
      state.orders = payload.orders || [];
      renderOrders();
    } catch (error) {
      const list = $("#ordersList");
      if (list) {
        list.innerHTML =
          '<div class="menu-empty"><span class="empty-icon">⚠️</span><h3>Orders unavailable</h3><p>' +
          esc(error.message) +
          '</p><button type="button" class="text-button" id="retryOrdersButton">Try again</button></div>';
      }
    }
  }

  function logEntryMarkup(log) {
    const status = ["success", "error", "info"].includes(log.status) ? log.status : "info";
    return (
      '<div class="log-entry status-' + status + '">' +
      '<div class="log-rail"><span class="log-node"></span></div>' +
      '<div class="log-body">' +
      '<div class="log-top"><span class="log-pattern">' + esc(log.pattern) + '</span><span class="log-time">' +
      esc(formatTime(log.created_at)) +
      "</span></div>" +
      '<strong class="log-title">' + esc(log.title) + "</strong>" +
      (log.detail ? '<p class="log-detail">' + esc(log.detail) + "</p>" : "") +
      '<div class="log-footer"><code>' + esc(log.channel) + '</code><span class="log-badge ' + status + '">' +
      esc(log.event_type) +
      "</span></div></div></div>"
    );
  }

  function orderDetailMarkup(order) {
    const items = order.items
      .map(
        (item) =>
          '<div class="detail-item"><div><strong>' + esc(item.name) + "</strong><span>" +
          money(item.unit_price_php) + " each · qty " + item.quantity + "</span></div>" +
          "<span>" + money(item.line_total_php) + "</span></div>"
      )
      .join("");

    const logs = order.integration_logs || [];
    const trace = logs.length
      ? '<div class="console-log">' + logs.map(logEntryMarkup).join("") + "</div>"
      : '<div class="trace-empty">No integration events were recorded for this order yet.</div>';

    return (
      '<div class="order-detail-head">' +
      "<div>" +
      '<span class="order-status ' + statusClass(order.status) + '"><span class="status-dot"></span>' + esc(order.status) + "</span>" +
      "<h2>" + esc(order.hub) + "</h2>" +
      '<span class="order-detail-ref">' + esc(order.reference) + "</span>" +
      "</div>" +
      '<div class="order-total"><span>Total</span><strong>' + money(order.total_php) + "</strong></div>" +
      "</div>" +
      '<div class="order-detail-meta">' +
      '<div class="detail-block"><span>Deliver to</span><strong>' + esc(order.barangay) + ", " + esc(order.municipality) +
      "</strong><small>" + esc(order.delivery_address) + "</small></div>" +
      '<div class="detail-block"><span>Contact</span><strong>' + esc(order.contact_number) +
      "</strong><small>Customer: " + esc(order.customer_name) + "</small></div>" +
      '<div class="detail-block"><span>Payment</span><strong>' + esc(order.payment_method) + "</strong><small>Placed " +
      esc(formatDateTime(order.created_at)) + "</small></div>" +
      '<div class="detail-block"><span>Kitchen notes</span><strong>' + esc(order.notes || "None provided") + "</strong></div>" +
      "</div>" +
      '<div class="detail-items">' + items + "</div>" +
      '<div class="detail-lines">' +
      '<div class="detail-line"><span>Subtotal</span><strong>' + money(order.subtotal_php) + "</strong></div>" +
      '<div class="detail-line"><span>Delivery fee</span><strong>' + money(order.delivery_fee_php) + "</strong></div>" +
      '<div class="detail-line detail-total-line"><span>Total</span><strong>' + money(order.total_php) + "</strong></div>" +
      "</div>" +
      '<div class="trace-mini"><h3>Integration trail</h3>' + trace + "</div>" +
      '<div class="detail-actions">' +
      '<button class="primary-cta small" type="button" data-reorder="' + order.id + '"><span>Re-order these dishes</span></button>' +
      '<button class="outline-button small" type="button" data-close-order>Close</button>' +
      "</div>"
    );
  }

  async function openOrderModal(orderId, focusTrace = false) {
    const modal = $("#orderModal");
    const content = $("#orderDetailContent");
    if (!modal || !content) return;
    modal.hidden = false;
    content.innerHTML = '<div class="order-loading"><span class="spinner"></span>Loading your order…</div>';
    syncBodyLock();
    try {
      const payload = await api("/api/orders/" + orderId);
      content.innerHTML = orderDetailMarkup(payload.order);
      if (focusTrace) {
        const trace = content.querySelector(".trace-mini");
        trace && trace.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    } catch (error) {
      content.innerHTML = '<div class="menu-empty"><span class="empty-icon">⚠️</span><h3>Order unavailable</h3><p>' +
        esc(error.message) + "</p></div>";
    }
  }

  function closeOrderModal() {
    const modal = $("#orderModal");
    if (modal) modal.hidden = true;
    syncBodyLock();
  }

  /* ------------------------------------------------------------------ */
  /* Live integration bus                                                */
  /* ------------------------------------------------------------------ */
  function updateLogCount() {
    const count = $("#logCount");
    if (count) count.textContent = String(state.logIds.size);
  }

  function highlightLane(channel) {
    if (!channel) return;
    const lane = document.querySelector('.channel-lane[data-channel="' + channel + '"]');
    if (!lane) return;
    lane.classList.add("is-active");
    window.setTimeout(() => lane.classList.remove("is-active"), 1600);
  }

  function appendLog(log) {
    if (!integrationLog) return;
    if (log && log.id != null) {
      if (state.logIds.has(log.id)) return;
      state.logIds.add(log.id);
    }
    if (consolePlaceholder) consolePlaceholder.hidden = true;
    const nearBottom = integrationLog.scrollHeight - integrationLog.scrollTop - integrationLog.clientHeight < 90;
    integrationLog.insertAdjacentHTML("beforeend", logEntryMarkup(log));
    if (nearBottom) integrationLog.scrollTop = integrationLog.scrollHeight;
    updateLogCount();
    highlightLane(log.channel);
  }

  function ingestLogs(logs) {
    if (!Array.isArray(logs)) return;
    const ordered = logs
      .filter(Boolean)
      .slice()
      .sort((a, b) => (Number(a.id) || 0) - (Number(b.id) || 0));
    ordered.forEach(appendLog);
  }

  async function loadIntegrationLogs() {
    try {
      const payload = await api("/api/integration/logs?limit=60");
      ingestLogs(payload.logs || []);
      if (payload.channels) {
        const active = Object.keys(payload.channels).length;
        const channelCount = $("#channelCount");
        if (channelCount) channelCount.textContent = String(active || 4);
      }
    } catch (error) {
      /* The stream will still work; keep the console quiet on first load. */
    }
  }

  function setStreamStatus(message, offline) {
    const status = $("#streamStatus");
    const pill = $("#streamPill");
    if (status) status.textContent = message;
    if (pill) pill.classList.toggle("is-offline", Boolean(offline));
  }

  function connectStream() {
    if (!window.EventSource) {
      setStreamStatus("Live updates unavailable in this browser", true);
      return;
    }
    if (state.stream) state.stream.close();

    const stream = new EventSource("/api/integration/stream");
    state.stream = stream;

    stream.onopen = () => {
      setStreamStatus("Live · listening for order events", false);
    };

    stream.addEventListener("ready", () => {
      setStreamStatus("Live · listening for order events", false);
    });

    stream.addEventListener("integration", (event) => {
      try {
        const log = JSON.parse(event.data);
        appendLog(log);
      } catch (error) {
        /* ignore malformed frames */
      }
    });

    stream.onerror = () => {
      setStreamStatus("Reconnecting to the event bus…", true);
    };
  }

  function runFilterDemo() {
    const button = $("#demoFilterButton");
    if (!button) return;
    const original = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="spinner" style="width:13px;height:13px;border-width:2px"></span> Filtering…';
    api("/api/integration/demo", { method: "POST" })
      .then((payload) => {
        ingestLogs((payload.result && payload.result.logs) || []);
        toast("Filter fired", "A Manila order was rejected into channel.deadletter.", "success");
        window.setTimeout(loadIntegrationLogs, 500);
      })
      .catch((error) => toast("Filter demo failed", error.message, "error"))
      .finally(() => {
        button.disabled = false;
        button.innerHTML = original;
      });
  }

  /* ------------------------------------------------------------------ */
  /* Navigation, profile, videos, help                                   */
  /* ------------------------------------------------------------------ */
  function closeUserMenu() {
    const menu = $("#userMenu");
    const button = $("#userButton");
    if (menu) menu.hidden = true;
    if (button) button.setAttribute("aria-expanded", "false");
  }

  function closeMobileNav() {
    const nav = $("#mobileNav");
    const button = $("#mobileMenuButton");
    if (nav) nav.hidden = true;
    if (button) {
      button.setAttribute("aria-expanded", "false");
      button.setAttribute("aria-label", "Open navigation");
    }
  }

  async function logout() {
    try {
      await api("/api/auth/logout", { method: "POST" });
    } catch (error) {
      /* sign out regardless */
    }
    window.location.assign("/");
  }

  function openProfile() {
    closeUserMenu();
    const modal = $("#profileModal");
    if (!modal) return;
    modal.hidden = false;
    syncBodyLock();
    const select = $("#profileMunicipality");
    if (select) select.value = state.user.municipality || "Kalibo";
    const error = $("#profileError");
    if (error) error.hidden = true;
  }

  function closeProfile() {
    const modal = $("#profileModal");
    if (modal) modal.hidden = true;
    syncBodyLock();
  }

  const videoModal = $("#videoModal");
  const videoFrame = $("#videoFrame");

  function openVideo(card) {
    if (!videoModal || !videoFrame) return;
    const id = card.dataset.videoId;
    const title = card.dataset.videoTitle || "Aklanon culture";
    $("#videoModalTitle").textContent = title;
    videoFrame.src =
      "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0&modestbranding=1&playsinline=1";
    videoModal.hidden = false;
    syncBodyLock();
    const close = $("#videoCloseButton");
    close && close.focus({ preventScroll: true });
  }

  function closeVideo() {
    if (!videoModal || !videoFrame) return;
    videoModal.hidden = true;
    videoFrame.src = "";
    syncBodyLock();
  }

  function openHelpModal() {
    const modal = $("#helpModal");
    if (!modal) return;
    modal.hidden = false;
    syncBodyLock();
  }

  function closeHelpModal() {
    const modal = $("#helpModal");
    if (modal) modal.hidden = true;
    syncBodyLock();
  }

  /* ------------------------------------------------------------------ */
  /* Event bindings                                                      */
  /* ------------------------------------------------------------------ */
  menuGrid &&
    menuGrid.addEventListener("click", (event) => {
      const add = event.target.closest("[data-add]");
      if (add) {
        event.stopPropagation();
        addToCart(Number(add.dataset.add), 1);
        openCart();
        return;
      }
      const dish = event.target.closest("[data-dish-open]");
      if (dish) openDishModal(Number(dish.dataset.dishOpen));
    });

  $("#cartButton") && $("#cartButton").addEventListener("click", openCart);
  $("#cartCloseButton") && $("#cartCloseButton").addEventListener("click", closeCart);
  cartBackdrop && cartBackdrop.addEventListener("click", closeCart);
  $("#cartBrowseButton") &&
    $("#cartBrowseButton").addEventListener("click", () => {
      closeCart();
      sectionForScroll("menu");
    });
  $("#checkoutButton") && $("#checkoutButton").addEventListener("click", openCheckout);

  cartItemsEl &&
    cartItemsEl.addEventListener("click", (event) => {
      const inc = event.target.closest("[data-cart-inc]");
      const dec = event.target.closest("[data-cart-dec]");
      const remove = event.target.closest("[data-cart-remove]");
      if (inc) {
        const id = Number(inc.dataset.cartInc);
        setCartQuantity(id, (state.cart.get(id) || 0) + 1);
      } else if (dec) {
        const id = Number(dec.dataset.cartDec);
        setCartQuantity(id, (state.cart.get(id) || 0) - 1);
      } else if (remove) {
        setCartQuantity(Number(remove.dataset.cartRemove), 0);
        toast("Removed from bag", "The dish was taken out of your hatod bag.", "info");
      }
    });

  $("#checkoutMunicipality") &&
    $("#checkoutMunicipality").addEventListener("change", (event) => {
      populateBarangays(event.target.value);
      updateCheckoutSummary();
    });

  $$('input[name="payment_method"]').forEach((input) => {
    input.addEventListener("change", () => {
      $$(".payment-option").forEach((option) => {
        option.classList.toggle("is-selected", option.contains(input) && input.checked);
      });
    });
  });

  $("#checkoutCloseButton") && $("#checkoutCloseButton").addEventListener("click", closeCheckout);
  $("#checkoutModal") &&
    $("#checkoutModal").addEventListener("click", (event) => {
      if (event.target === $("#checkoutModal")) closeCheckout();
    });
  $("#successCloseButton") &&
    $("#successCloseButton").addEventListener("click", () => {
      closeCheckout();
      sectionForScroll("menu");
    });
  $("#successTrackButton") &&
    $("#successTrackButton").addEventListener("click", () => {
      const orderId = state.lastOrderId;
      closeCheckout();
      if (orderId) openOrderModal(orderId, true);
    });

  $$(".category-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      state.activeCategory = tab.dataset.category || "All";
      renderMenu();
    });
  });

  const menuSearch = $("#menuSearch");
  menuSearch &&
    menuSearch.addEventListener(
      "input",
      debounce((event) => {
        state.search = event.target.value;
        renderMenu();
      }, 150)
    );

  $("#municipalityFilter") &&
    $("#municipalityFilter").addEventListener("change", (event) => {
      state.municipality = event.target.value;
      renderMenu();
    });

  $("#clearFiltersButton") &&
    $("#clearFiltersButton").addEventListener("click", () => {
      state.activeCategory = "All";
      state.search = "";
      state.municipality = "All";
      if (menuSearch) menuSearch.value = "";
      const municipalityFilter = $("#municipalityFilter");
      if (municipalityFilter) municipalityFilter.value = "All";
      const heroSearch = $("#heroSearchInput");
      if (heroSearch) heroSearch.value = "";
      renderMenu();
    });

  $("#heroSearchForm") &&
    $("#heroSearchForm").addEventListener("submit", (event) => {
      event.preventDefault();
      const value = $("#heroSearchInput").value.trim();
      state.search = value;
      if (menuSearch) menuSearch.value = value;
      state.activeCategory = "All";
      renderMenu();
      sectionForScroll("menu");
    });

  $$("[data-category-jump]").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeCategory = button.dataset.categoryJump;
      state.search = "";
      if (menuSearch) menuSearch.value = "";
      renderMenu();
      sectionForScroll("menu");
    });
  });

  $("#heroTraceButton") && $("#heroTraceButton").addEventListener("click", () => sectionForScroll("integration"));
  $("#demoFilterButton") && $("#demoFilterButton").addEventListener("click", runFilterDemo);
  $("#refreshOrdersButton") &&
    $("#refreshOrdersButton").addEventListener("click", () => {
      loadOrders();
      toast("Orders refreshed", "Your latest hatod history is ready.", "info");
    });

  $("#ordersList") &&
    $("#ordersList").addEventListener("click", (event) => {
      const view = event.target.closest("[data-order-view]");
      const trace = event.target.closest("[data-order-trace]");
      const browse = event.target.closest("[data-browse-menu]");
      const retry = event.target.closest("#retryOrdersButton");
      if (view) openOrderModal(Number(view.dataset.orderView));
      else if (trace) openOrderModal(Number(trace.dataset.orderTrace), true);
      else if (browse) sectionForScroll("menu");
      else if (retry) loadOrders();
    });

  $("#orderModalCloseButton") && $("#orderModalCloseButton").addEventListener("click", closeOrderModal);
  $("#orderModal") &&
    $("#orderModal").addEventListener("click", (event) => {
      if (event.target === $("#orderModal")) closeOrderModal();
      if (event.target.closest("[data-close-order]")) closeOrderModal();
      const reorder = event.target.closest("[data-reorder]");
      if (reorder) {
        const order = state.orders.find((entry) => entry.id === Number(reorder.dataset.reorder));
        if (!order) {
          toast("Could not re-order", "Refresh your orders and try again.", "error");
          return;
        }
        let added = 0;
        order.items.forEach((item) => {
          const menuItem = state.menu.find((entry) => entry.id === item.menu_item_id);
          if (menuItem && menuItem.is_available && menuItem.stock_qty > 0) {
            const current = state.cart.get(menuItem.id) || 0;
            const next = Math.min(current + item.quantity, menuItem.stock_qty, 20);
            if (next > current) {
              state.cart.set(menuItem.id, next);
              added += next - current;
            }
          }
        });
        persistCart();
        renderCart();
        renderMenu();
        if (added > 0) {
          closeOrderModal();
          openCart();
          toast("Bag refilled", added + " item(s) added from " + order.reference + ".", "success");
        } else {
          toast("Nothing available", "Those dishes are out of stock right now.", "error");
        }
      }
    });

  // Dish modal delegated close for dynamically created content
  document.addEventListener("click", (event) => {
    if (event.target.closest("[data-dish-close]")) closeDishModal();
  });

  const userButton = $("#userButton");
  userButton &&
    userButton.addEventListener("click", (event) => {
      event.stopPropagation();
      const menu = $("#userMenu");
      const willOpen = menu.hidden;
      menu.hidden = !willOpen;
      userButton.setAttribute("aria-expanded", String(willOpen));
    });

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".user-wrap")) closeUserMenu();
    if (!event.target.closest(".mobile-nav") && !event.target.closest("#mobileMenuButton")) closeMobileNav();
  });

  $("#profileButton") && $("#profileButton").addEventListener("click", openProfile);
  $("#profileCloseButton") && $("#profileCloseButton").addEventListener("click", closeProfile);
  $("#profileModal") &&
    $("#profileModal").addEventListener("click", (event) => {
      if (event.target === $("#profileModal")) closeProfile();
    });

  $("#profileForm") &&
    $("#profileForm").addEventListener("submit", async (event) => {
      event.preventDefault();
      const select = $("#profileMunicipality");
      const errorEl = $("#profileError");
      errorEl.hidden = true;
      const button = $("#profileSaveButton");
      const label = button.querySelector("span");
      const original = label ? label.textContent : "";
      button.disabled = true;
      button.classList.add("is-busy");
      if (label) label.textContent = "Saving…";
      try {
        const payload = await api("/api/auth/me", {
          method: "PATCH",
          body: JSON.stringify({ municipality: select.value }),
        });
        state.user = payload.user;
        const headerMunicipality = $("#headerMunicipality");
        if (headerMunicipality) headerMunicipality.textContent = payload.user.municipality;
        const checkoutMunicipality = $("#checkoutMunicipality");
        if (checkoutMunicipality && state.zones[payload.user.municipality]) {
          checkoutMunicipality.value = payload.user.municipality;
        }
        closeProfile();
        toast("Preference saved", "We'll default to " + payload.user.municipality + " for delivery.", "success");
      } catch (error) {
        errorEl.textContent = error.message;
        errorEl.hidden = false;
      } finally {
        button.disabled = false;
        button.classList.remove("is-busy");
        if (label) label.textContent = original;
      }
    });

  $("#logoutButton") && $("#logoutButton").addEventListener("click", logout);
  $("#mobileLogoutButton") && $("#mobileLogoutButton").addEventListener("click", logout);

  $("#mobileMenuButton") &&
    $("#mobileMenuButton").addEventListener("click", (event) => {
      event.stopPropagation();
      const nav = $("#mobileNav");
      const willOpen = nav.hidden;
      nav.hidden = !willOpen;
      event.currentTarget.setAttribute("aria-expanded", String(willOpen));
      event.currentTarget.setAttribute("aria-label", willOpen ? "Close navigation" : "Open navigation");
    });

  $$("[data-mobile-link]").forEach((link) => {
    link.addEventListener("click", () => closeMobileNav());
  });

  $$(".video-card").forEach((card) => {
    card.addEventListener("click", () => openVideo(card));
  });
  $("#videoCloseButton") && $("#videoCloseButton").addEventListener("click", closeVideo);
  videoModal &&
    videoModal.addEventListener("click", (event) => {
      if (event.target === videoModal) closeVideo();
    });

  $("#footerHelpButton") && $("#footerHelpButton").addEventListener("click", openHelpModal);
  $("#helpCloseButton") && $("#helpCloseButton").addEventListener("click", closeHelpModal);
  $("#helpModal") &&
    $("#helpModal").addEventListener("click", (event) => {
      if (event.target === $("#helpModal")) closeHelpModal();
    });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const openOrder = $("#orderModal");
    if (openOrder && !openOrder.hidden) return closeOrderModal();
    if (videoModal && !videoModal.hidden) return closeVideo();
    if (dishModal && !dishModal.hidden) return closeDishModal();
    const profile = $("#profileModal");
    if (profile && !profile.hidden) return closeProfile();
    const help = $("#helpModal");
    if (help && !help.hidden) return closeHelpModal();
    const checkout = $("#checkoutModal");
    if (checkout && !checkout.hidden) return closeCheckout();
    if (cartDrawer && cartDrawer.classList.contains("is-open")) return closeCart();
    closeUserMenu();
    closeMobileNav();
  });

  // Scroll spy + sticky header shadow
  const sections = $$(".app-section");
  const navLinks = $$(".app-nav-link");
  function onScroll() {
    const header = $("#appHeader");
    if (header) header.classList.toggle("is-scrolled", window.scrollY > 8);
    let active = "discover";
    sections.forEach((section) => {
      if (section.getBoundingClientRect().top <= 160) active = section.id;
    });
    navLinks.forEach((link) => {
      link.classList.toggle("is-active", link.dataset.sectionLink === active);
    });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ------------------------------------------------------------------ */
  /* Boot                                                                */
  /* ------------------------------------------------------------------ */
  async function boot() {
    await loadMenu();
    hydrateCart();
    renderMenu();
    renderCart();
    await loadZones();
    loadOrders();
    loadIntegrationLogs();
    connectStream();
  }

  boot();
})();
