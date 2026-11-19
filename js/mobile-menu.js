(() => {
  const menu = document.querySelector("[data-menu]");
  const openButton = document.querySelector("[data-menu-open]");
  const closeButton = document.querySelector("[data-menu-close]");
  if (!menu || !openButton || !closeButton) return;
  const close = () => {
    menu.classList.remove("is-open");
    menu.setAttribute("aria-hidden", "true");
  };
  openButton.addEventListener("click", () => {
    menu.classList.add("is-open");
    menu.setAttribute("aria-hidden", "false");
    closeButton.focus();
  });
  closeButton.addEventListener("click", () => {
    close();
    openButton.focus();
  });
  menu.querySelectorAll(".mobile-navigation-link").forEach((link) => {
    link.addEventListener("click", close);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menu.classList.contains("is-open")) {
      close();
      openButton.focus();
    }
  });
})();
