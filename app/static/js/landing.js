/* ==========================================================================
   Hatod Akean — landing page interactions
   Auth tabs, registration / sign-in, demo access, language & help, toasts.
   ========================================================================== */

(function () {
  "use strict";

  const config = window.HATOD || {};
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
  const toastStack = $("#toastStack");

  /* ------------------------------------------------------------------ */
  /* Utilities                                                           */
  /* ------------------------------------------------------------------ */
  function toast(title, message, type = "info") {
    if (!toastStack) return;
    const el = document.createElement("div");
    el.className = `toast is-${type}`;
    el.innerHTML = `
      <span class="toast-icon" aria-hidden="true">${type === "error" ? "!" : type === "success" ? "✓" : "✦"}</span>
      <div class="toast-copy"><strong></strong><p></p></div>
    `;
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
          ? payload.detail.map((item) => item.msg || item.message || "").filter(Boolean).join(" ")
          : payload.detail;
      }
      const error = new Error(message);
      error.status = response.status;
      throw error;
    }
    return payload;
  }

  function setBusy(button, busy, label) {
    if (!button) return;
    button.disabled = busy;
    button.classList.toggle("is-busy", busy);
    if (label) {
      const span = button.querySelector("span");
      if (span) span.textContent = busy ? label : span.dataset.label || label;
    }
  }

  function showError(element, message) {
    if (!element) return;
    element.textContent = message;
    element.hidden = false;
  }

  function clearError(element) {
    if (!element) return;
    element.hidden = true;
    element.textContent = "";
  }

  /* ------------------------------------------------------------------ */
  /* Auth tabs                                                           */
  /* ------------------------------------------------------------------ */
  const loginTab = $("#loginTab");
  const signupTab = $("#signupTab");
  const loginPanel = $("#loginPanel");
  const signupPanel = $("#signupPanel");
  const authTitle = $("#authTitle");
  const authSubtitle = $("#authSubtitle");

  const COPY = {
    login: {
      title: "Welcome back",
      subtitle: "Your Aklanon favorites are waiting, {{name}}.",
      plain: "Sign in to track orders and revisit your favorite kitchens.",
    },
    signup: {
      title: "Create your account",
      subtitle: "One account for Aklan's most loved kitchens.",
    },
  };

  function selectTab(tab) {
    const isLogin = tab === "login";
    if (loginTab) {
      loginTab.classList.toggle("is-active", isLogin);
      loginTab.setAttribute("aria-selected", String(isLogin));
    }
    if (signupTab) {
      signupTab.classList.toggle("is-active", !isLogin);
      signupTab.setAttribute("aria-selected", String(!isLogin));
    }
    if (loginPanel) loginPanel.hidden = !isLogin;
    if (signupPanel) signupPanel.hidden = isLogin;
    if (authTitle) authTitle.textContent = isLogin ? COPY.login.title : COPY.signup.title;
    if (authSubtitle) authSubtitle.textContent = isLogin ? COPY.login.plain : COPY.signup.subtitle;
    clearError($("#loginError"));
    clearError($("#signupError"));
  }

  loginTab && loginTab.addEventListener("click", () => selectTab("login"));
  signupTab && signupTab.addEventListener("click", () => selectTab("signup"));

  $$(".auth-tab").forEach((tab) => {
    tab.addEventListener("keydown", (event) => {
      if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
        event.preventDefault();
        selectTab(tab === loginTab ? "signup" : "login");
        (tab === loginTab ? signupTab : loginTab).focus();
      }
    });
  });

  /* ------------------------------------------------------------------ */
  /* Password visibility                                                 */
  /* ------------------------------------------------------------------ */
  $$("[data-password-toggle]").forEach((button) => {
    const input = document.getElementById(button.dataset.passwordToggle);
    if (!input) return;
    button.addEventListener("click", () => {
      const reveal = input.type === "password";
      input.type = reveal ? "text" : "password";
      button.classList.toggle("is-revealed", reveal);
      button.setAttribute("aria-label", reveal ? "Hide password" : "Show password");
    });
  });

  /* ------------------------------------------------------------------ */
  /* Sign in                                                             */
  /* ------------------------------------------------------------------ */
  const loginForm = $("#loginPanel");
  const loginEmail = $("#loginEmail");
  const loginPassword = $("#loginPassword");
  const loginError = $("#loginError");
  const loginButton = $("#loginButton");

  loginForm &&
    loginForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      clearError(loginError);
      const email = loginEmail.value.trim().toLowerCase();
      const password = loginPassword.value;

      if (!EMAIL_RE.test(email)) {
        showError(loginError, "Enter a valid email address.");
        loginEmail.focus();
        return;
      }
      if (!password) {
        showError(loginError, "Enter your password to continue.");
        loginPassword.focus();
        return;
      }

      const label = loginButton.querySelector("span");
      const original = label ? label.textContent : "";
      setBusy(loginButton, true, "Signing in…");
      try {
        await api("/api/auth/login", {
          method: "POST",
          body: JSON.stringify({ email, password }),
        });
        if (label) label.textContent = "Welcome back!";
        toast("Maayong pag-abot!", "Opening your Aklanon kitchen…", "success");
        window.setTimeout(() => window.location.assign("/app"), 500);
      } catch (error) {
        setBusy(loginButton, false);
        if (label) label.textContent = original;
        showError(loginError, error.message);
      }
    });

  /* ------------------------------------------------------------------ */
  /* Sign up                                                             */
  /* ------------------------------------------------------------------ */
  const signupForm = $("#signupPanel");
  const signupName = $("#signupName");
  const signupEmail = $("#signupEmail");
  const signupMunicipality = $("#signupMunicipality");
  const signupPassword = $("#signupPassword");
  const signupConfirm = $("#signupConfirm");
  const signupError = $("#signupError");
  const signupButton = $("#signupButton");

  signupForm &&
    signupForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      clearError(signupError);

      const full_name = signupName.value.trim().replace(/\s+/g, " ");
      const email = signupEmail.value.trim().toLowerCase();
      const municipality = signupMunicipality.value;
      const password = signupPassword.value;
      const confirm_password = signupConfirm.value;

      if (full_name.length < 2) {
        showError(signupError, "Tell us your full name so riders can find you.");
        signupName.focus();
        return;
      }
      if (!EMAIL_RE.test(email)) {
        showError(signupError, "Enter a valid email address.");
        signupEmail.focus();
        return;
      }
      if (!municipality) {
        showError(signupError, "Choose your Aklan municipality.");
        signupMunicipality.focus();
        return;
      }
      if (password.length < 8) {
        showError(signupError, "Use at least 8 characters for your password.");
        signupPassword.focus();
        return;
      }
      if (password !== confirm_password) {
        showError(signupError, "Your passwords do not match yet.");
        signupConfirm.focus();
        return;
      }

      const label = signupButton.querySelector("span");
      const original = label ? label.textContent : "";
      setBusy(signupButton, true, "Creating account…");
      try {
        await api("/api/auth/register", {
          method: "POST",
          body: JSON.stringify({ full_name, email, municipality, password, confirm_password }),
        });
        if (label) label.textContent = "Account ready!";
        toast("Salamat, " + full_name.split(" ")[0] + "!", "Your Hatod Akean account is ready.", "success");
        window.setTimeout(() => window.location.assign("/app"), 600);
      } catch (error) {
        setBusy(signupButton, false);
        if (label) label.textContent = original;
        showError(signupError, error.message);
        if (error.status === 409) selectTab("login");
      }
    });

  [loginEmail, loginPassword].forEach((input) => {
    input && input.addEventListener("input", () => clearError(loginError));
  });
  [signupName, signupEmail, signupMunicipality, signupPassword, signupConfirm].forEach((input) => {
    input && input.addEventListener("input", () => clearError(signupError));
  });

  /* ------------------------------------------------------------------ */
  /* Demo account                                                        */
  /* ------------------------------------------------------------------ */
  const demoButton = $("#demoButton");
  demoButton &&
    demoButton.addEventListener("click", async () => {
      if (!config.demoEmail || !config.demoPassword) return;
      loginEmail.value = config.demoEmail;
      loginPassword.value = config.demoPassword;
      selectTab("login");
      const label = loginButton.querySelector("span");
      const original = label ? label.textContent : "";
      setBusy(loginButton, true, "Opening demo…");
      demoButton.disabled = true;
      try {
        await api("/api/auth/login", {
          method: "POST",
          body: JSON.stringify({ email: config.demoEmail, password: config.demoPassword }),
        });
        toast("Demo kitchen open", "Signing you in as Nene Aklanon.", "success");
        window.setTimeout(() => window.location.assign("/app"), 500);
      } catch (error) {
        demoButton.disabled = false;
        setBusy(loginButton, false);
        if (label) label.textContent = original;
        showError(loginError, "Demo sign-in failed. " + error.message);
        selectTab("login");
      }
    });

  /* ------------------------------------------------------------------ */
  /* Language switcher                                                   */
  /* ------------------------------------------------------------------ */
  const COPY_I18N = {
    en: {
      tagline: "Aklanon's Famous Cuisine",
      help: "Help",
      eyebrow: "A taste of Aklan, delivered",
      lede: "Create your account to order your favorite dishes, save favorites, and track orders from local restaurants and fast food partners.",
      badge1: "Heritage recipes",
      badge2: "30-minute local delivery",
      badge3: "Made in Aklan",
      rating: "from local food lovers",
      loved: "Loved by 2,400+ food lovers",
      lovedSub: "across Panay Island",
      openNow: "Kitchens open now",
      secure: "Secure local ordering",
    },
    akl: {
      tagline: "Sikat nga Pagkaon ka Akean",
      help: "Bulig",
      eyebrow: "Panamit ka Aklan, ginadara",
      lede: "Maghimo ka account agud maka-order ka ka paborito nga pagkaon, maka-save ka favorites, kag maka-track ka orders halin sa lokal nga restawran kag fast food partners.",
      badge1: "Heritage nga resipe",
      badge2: "30-minuto nga delivery",
      badge3: "Gin-himo sa Aklan",
      rating: "halin sa lokal nga food lovers",
      loved: "Ginmahal ka 2,400+ nga food lovers",
      lovedSub: "sa bug-os nga Panay",
      openNow: "Bukas ang mga kusina",
      secure: "Secure nga order lokal",
    },
    fil: {
      tagline: "Sikat na Pagkain ng Aklan",
      help: "Tulong",
      eyebrow: "Sarap ng Aklan, hatid sa iyo",
      lede: "Gumawa ng account para makapag-order ng paborito mong pagkain, makapag-save ng favorites, at makapag-track ng orders mula sa local na restawran at fast food partners.",
      badge1: "Heritage recipes",
      badge2: "30-minutong lokal na delivery",
      badge3: "Gawa sa Aklan",
      rating: "mula sa lokal na food lovers",
      loved: "Minamahal ng 2,400+ food lovers",
      lovedSub: "sa buong Panay Island",
      openNow: "Bukas ang mga kusina",
      secure: "Secure na lokal na ordering",
    },
  };

  const LANGUAGE_NAMES = { en: "English", akl: "Akeanon", fil: "Filipino" };
  const languageButton = $("#languageButton");
  const languageMenu = $("#languageMenu");
  const languageLabel = $("#languageLabel");

  function setLanguage(lang) {
    const dictionary = COPY_I18N[lang] || COPY_I18N.en;
    $$("[data-i18n]").forEach((node) => {
      const key = node.dataset.i18n;
      if (dictionary[key]) node.textContent = dictionary[key];
    });
    if (languageLabel) languageLabel.textContent = LANGUAGE_NAMES[lang] || "Language";
    $$("[data-language]", languageMenu).forEach((button) => {
      button.classList.toggle("is-selected", button.dataset.language === lang);
    });
    document.body.dataset.lang = lang;
    document.documentElement.lang = lang === "fil" ? "fil" : lang === "akl" ? "en" : "en";
    try {
      window.localStorage.setItem("hatod_language", lang);
    } catch (error) {
      /* storage may be unavailable */
    }
  }

  function closeLanguageMenu() {
    if (!languageMenu || !languageButton) return;
    languageMenu.hidden = true;
    languageButton.setAttribute("aria-expanded", "false");
  }

  languageButton &&
    languageButton.addEventListener("click", (event) => {
      event.stopPropagation();
      const willOpen = languageMenu.hidden;
      languageMenu.hidden = !willOpen;
      languageButton.setAttribute("aria-expanded", String(willOpen));
    });

  $$("[data-language]", languageMenu).forEach((button) => {
    button.addEventListener("click", () => {
      setLanguage(button.dataset.language);
      closeLanguageMenu();
      toast("Language updated", LANGUAGE_NAMES[button.dataset.language] + " is now active.", "success");
    });
  });

  document.addEventListener("click", (event) => {
    if (languageMenu && !languageMenu.hidden && !event.target.closest(".language-wrap")) {
      closeLanguageMenu();
    }
  });

  try {
    const storedLanguage = window.localStorage.getItem("hatod_language");
    if (storedLanguage && COPY_I18N[storedLanguage]) setLanguage(storedLanguage);
  } catch (error) {
    /* storage may be unavailable */
  }

  /* ------------------------------------------------------------------ */
  /* Help modal                                                          */
  /* ------------------------------------------------------------------ */
  const helpModal = $("#helpModal");

  function openHelp() {
    if (!helpModal) return;
    helpModal.hidden = false;
    document.body.classList.add("no-scroll");
    const close = helpModal.querySelector("[data-help-close]");
    close && close.focus({ preventScroll: true });
  }

  function closeHelp() {
    if (!helpModal) return;
    helpModal.hidden = true;
    document.body.classList.remove("no-scroll");
  }

  $$("[data-help-open]").forEach((button) => {
    button.addEventListener("click", openHelp);
  });
  $$("[data-help-close]").forEach((button) => {
    button.addEventListener("click", closeHelp);
  });
  helpModal &&
    helpModal.addEventListener("click", (event) => {
      if (event.target === helpModal) closeHelp();
    });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    if (helpModal && !helpModal.hidden) {
      closeHelp();
      return;
    }
    if (languageMenu && !languageMenu.hidden) closeLanguageMenu();
  });

  /* ------------------------------------------------------------------ */
  /* Small conveniences                                                  */
  /* ------------------------------------------------------------------ */
  $$("input").forEach((input) => {
    input.addEventListener("invalid", (event) => event.preventDefault());
  });

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    document.documentElement.style.scrollBehavior = "auto";
  }
})();
