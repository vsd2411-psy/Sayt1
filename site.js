(() => {
  const header = document.querySelector(".header");
  const primaryNav = header?.querySelector("nav:not(.language-switcher)");
  if (!header || !primaryNav) return;

  primaryNav.id ||= "primary-navigation";
  const toggle = document.createElement("button");
  toggle.className = "menu-toggle";
  toggle.type = "button";
  toggle.setAttribute("aria-controls", primaryNav.id);
  toggle.setAttribute("aria-expanded", "false");
  toggle.textContent = document.documentElement.lang === "uk" ? "Меню" : "Меню";
  header.insertBefore(toggle, primaryNav);

  const closeMenu = () => {
    toggle.setAttribute("aria-expanded", "false");
    primaryNav.removeAttribute("data-open");
  };

  toggle.addEventListener("click", () => {
    const isOpen = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!isOpen));
    primaryNav.toggleAttribute("data-open", !isOpen);
  });
  primaryNav.addEventListener("click", (event) => {
    if (event.target.closest("a")) closeMenu();
  });
  document.addEventListener("keydown", (event) => {
    const isOpen = toggle.getAttribute("aria-expanded") === "true";
    if (event.key === "Escape" && isOpen) {
      closeMenu();
      toggle.focus();
    }
  });
  window.matchMedia("(min-width: 761px)").addEventListener("change", closeMenu);
})();
