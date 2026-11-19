(() => {
  const backdrop = document.querySelector("[data-modal]");
  const openButton = document.querySelector("[data-modal-open]");
  const closeButton = document.querySelector("[data-modal-close]");
  if (!backdrop || !openButton || !closeButton) return;

  const open = () => {
    backdrop.classList.add("is-open");
    backdrop.setAttribute("aria-hidden", "false");
    closeButton.focus();
  };
  const close = () => {
    backdrop.classList.remove("is-open");
    backdrop.setAttribute("aria-hidden", "true");
    openButton.focus();
  };

  openButton.addEventListener("click", open);
  closeButton.addEventListener("click", close);
  backdrop.addEventListener("click", (event) => {
    if (event.target === backdrop) close();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && backdrop.classList.contains("is-open"))
      close();
  });
})();
