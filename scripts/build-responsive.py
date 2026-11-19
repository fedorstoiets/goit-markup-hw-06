from pathlib import Path
import re

root = Path(".")
html_file = root / "index.html"
html = html_file.read_text(encoding="utf-8")

# All content images have explicit src plus 1x/2x srcset; never picture/source.
for prefix, count in (("team", 4), ("portfolio", 6)):
    for index in range(1, count + 1):
        old = 'src="./images/%s-%s.jpg"' % (prefix, index)
        new = ('src="./images/%s-%s-1x.jpg"\n'
               '                srcset="./images/%s-%s-1x.jpg 1x, ./images/%s-%s-2x.jpg 2x"'
               ) % (prefix, index, prefix, index, prefix, index)
        assert old in html, old
        html = html.replace(old, new)

# Mobile menu is a distinct post-footer component.
menu = """
    <div class="mobile-menu" data-menu aria-hidden="true">
      <div class="mobile-menu-inner">
        <button class="mobile-menu-close" data-menu-close type="button" aria-label="Close mobile menu">
          <svg width="8" height="8" fill="#2e2f42" aria-hidden="true">
            <use href="./images/icons.svg#icon-close"></use>
          </svg>
        </button>
        <ul class="mobile-navigation-list">
          <li><a class="mobile-navigation-link" href="#features">Features</a></li>
          <li><a class="mobile-navigation-link" href="#team">Team</a></li>
          <li><a class="mobile-navigation-link" href="#portfolio">Portfolio</a></li>
        </ul>
        <div class="mobile-menu-bottom">
          <address class="mobile-contact-details">
            <ul class="mobile-contact-list">
              <li><a class="mobile-phone" href="tel:+110001111111">+11 (000) 111-11-11</a></li>
              <li><a class="mobile-email" href="mailto:info@devstudio.com">info@devstudio.com</a></li>
            </ul>
          </address>
          <ul class="mobile-social-list">
            <li><a class="mobile-social-link" aria-label="Instagram" href="./images/icons.svg#icon-instagram"><svg width="24" height="24" fill="#f4f4fd" aria-hidden="true"><use href="./images/icons.svg#icon-instagram"></use></svg></a></li>
            <li><a class="mobile-social-link" aria-label="Twitter" href="./images/icons.svg#icon-twitter"><svg width="24" height="24" fill="#f4f4fd" aria-hidden="true"><use href="./images/icons.svg#icon-twitter"></use></svg></a></li>
            <li><a class="mobile-social-link" aria-label="Facebook" href="./images/icons.svg#icon-facebook"><svg width="24" height="24" fill="#f4f4fd" aria-hidden="true"><use href="./images/icons.svg#icon-facebook"></use></svg></a></li>
            <li><a class="mobile-social-link" aria-label="LinkedIn" href="./images/icons.svg#icon-linkedin"><svg width="24" height="24" fill="#f4f4fd" aria-hidden="true"><use href="./images/icons.svg#icon-linkedin"></use></svg></a></li>
          </ul>
        </div>
      </div>
    </div>
"""
assert "</footer>" in html
html = html.replace("</footer>", "</footer>\n"+menu, 1)

# Hamburger button follows logo on mobile, with explicit SVG dimensions/fill.
hamburger = """
        <button class="mobile-menu-open" type="button" data-menu-open aria-label="Open mobile menu">
          <svg width="24" height="24" fill="#2e2f42" aria-hidden="true">
            <use href="./images/icons.svg#icon-menu"></use>
          </svg>
        </button>
"""
assert '<nav class="primary-navigation">' in html
html = html.replace('<nav class="primary-navigation">', hamburger+'\n        <nav class="primary-navigation">', 1)
assert 'src="./js/modal.js" defer' in html
html = html.replace('<script src="./js/modal.js" defer></script>', '<script src="./js/modal.js" defer></script>\n    <script src="./js/mobile-menu.js" defer></script>')
html_file.write_text(html, encoding="utf-8")

sprite = root / "images/icons.svg"
icons = sprite.read_text(encoding="utf-8")
assert '</defs>' in icons
icons=icons.replace("</defs>",'<symbol id="icon-menu" viewBox="0 0 24 24"><path d="M3 6h18v2H3zM3 11h18v2H3zM3 16h18v2H3z"/></symbol></defs>',1)
sprite.write_text(icons,encoding="utf-8")

js_dir=root/"js"
js_dir.mkdir(exist_ok=True)
(js_dir/"mobile-menu.js").write_text('''(() => {
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
''',encoding="utf-8")

# Responsive CSS is authored mobile-first; shared modules are kept in their corresponding CSS files.
def append(path, extra):
    file = root / "css" / path
    file.write_text(file.read_text(encoding="utf-8").rstrip()+"\n\n"+extra.strip()+"\n",encoding="utf-8")

append("common.css", """
/* Mobile-first container and section geometry (320 / 768 / 1158). */
.container {
  width: 100%;
  max-width: 320px;
  padding-right: 16px;
  padding-left: 16px;
}
.section { padding-top: 96px; padding-bottom: 96px; }
@media screen and (min-width: 768px) {
  .container { max-width: 768px; }
}
@media screen and (min-width: 1158px) {
  .container { max-width: 1158px; padding-right: 15px; padding-left: 15px; }
  .section { padding-top: 120px; padding-bottom: 120px; }
}
""")

append("header.css", """
/* Mobile first: header height comes from the logo's vertical padding. */
.header-container { justify-content: space-between; }
.logo { padding: 16px 0; margin-right: 0; }
.primary-navigation, .contact-details { display: none; }
.mobile-menu-open {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  border: 0;
  background-color: transparent;
  cursor: pointer;
}
@media screen and (min-width: 768px) {
  .header-container { justify-content: flex-start; }
  .logo { padding: 0; margin-right: 76px; }
  .primary-navigation, .contact-details { display: block; }
  .mobile-menu-open { display: none; }
  .address-list { flex-direction: column; gap: 4px; }
  .address-link { padding: 0; font-size: 12px; line-height: 1.17; }
}
@media screen and (min-width: 1158px) {
  .address-list { flex-direction: row; gap: 40px; }
  .address-link { padding: 24px 0; font-size: 16px; line-height: 1.5; }
}
""")

append("hero.css", """
/* Mobile hero (1x & 2x), mobile first. */
.hero {
  padding: 72px 0;
  background-image: linear-gradient(rgba(46, 47, 66, 0.7), rgba(46, 47, 66, 0.7)),
    url("../images/hero-mobile-1x.jpg");
}
.hero-title { max-width: 288px; font-size: 36px; line-height: 1.11; }
@media screen and (min-resolution: 192dpi), screen and (min-resolution: 2dppx) {
  .hero {
    background-image: linear-gradient(rgba(46, 47, 66, 0.7), rgba(46, 47, 66, 0.7)),
      url("../images/hero-mobile-2x.jpg");
  }
}
@media screen and (min-width: 768px) {
  .hero {
    padding: 112px 0;
    background-image: linear-gradient(rgba(46, 47, 66, 0.7), rgba(46, 47, 66, 0.7)),
      url("../images/hero-tablet-1x.jpg");
  }
  .hero-title { max-width: 496px; font-size: 56px; line-height: 1.07; }
}
@media screen and (min-width: 768px) and (min-resolution: 2dppx) {
  .hero {
    background-image: linear-gradient(rgba(46, 47, 66, 0.7), rgba(46, 47, 66, 0.7)),
      url("../images/hero-tablet-2x.jpg");
  }
}
@media screen and (min-width: 1158px) {
  .hero {
    padding: 188px 0;
    max-width: 1440px;
    background-image: linear-gradient(rgba(46, 47, 66, 0.7), rgba(46, 47, 66, 0.7)),
      url("../images/hero-desktop-1x.jpg");
  }
}
@media screen and (min-width: 1158px) and (min-resolution: 2dppx) {
  .hero {
    background-image: linear-gradient(rgba(46, 47, 66, 0.7), rgba(46, 47, 66, 0.7)),
      url("../images/hero-desktop-2x.jpg");
  }
}
""")

append("features.css", """
.features-list { flex-direction: column; gap: 72px; }
.features-item { width: 100%; }
.features-subtitle { text-align: center; }
.feature-icon-box { display: none; }
@media screen and (min-width: 768px) {
  .features-list { flex-direction: row; flex-wrap: wrap; gap: 72px 24px; }
  .features-item { width: calc((100% - 24px) / 2); }
  .features-subtitle { text-align: left; }
}
@media screen and (min-width: 1158px) {
  .features-list { flex-wrap: nowrap; gap: 24px; }
  .features-item { width: calc((100% - 72px) / 4); }
  .feature-icon-box { display: flex; }
}
""")

append("team.css", """
.team-list { flex-wrap: wrap; justify-content: center; gap: 72px; }
.team-item { width: 264px; flex-shrink: 0; }
@media screen and (min-width: 768px) {
  .team-list { gap: 64px 24px; }
}
@media screen and (min-width: 1158px) {
  .team-list { gap: 24px; }
}
""")

append("portfolio.css", """
.portfolio-list { justify-content: center; gap: 48px; }
.portfolio-item { width: 100%; max-width: 360px; }
.portfolio-image-wrap img { width: 100%; }
@media screen and (min-width: 768px) {
  .portfolio-list { justify-content: flex-start; gap: 72px 24px; }
  .portfolio-item { width: calc((100% - 24px) / 2); }
}
@media screen and (min-width: 1158px) {
  .portfolio-list { gap: 48px 24px; }
  .portfolio-item { width: calc((100% - 48px) / 3); }
}
""")

append("footer.css", """
.footer-container { flex-direction: column; align-items: center; }
.footer-brand { margin: 0 0 72px; }
.footer-social { margin-bottom: 72px; }
.footer-subscribe { width: 100%; margin-left: 0; }
.footer-subscribe-form { flex-direction: column; align-items: center; gap: 16px; }
.footer-subscribe-title { text-align: center; }
@media screen and (min-width: 768px) {
  .footer-container { flex-direction: row; flex-wrap: wrap; align-items: flex-start; justify-content: flex-start; }
  .footer-brand { margin: 0 24px 72px 108px; }
  .footer-social { margin-bottom: 72px; }
  .footer-subscribe { margin-left: 108px; }
  .footer-subscribe-form { flex-direction: row; align-items: center; gap: 24px; }
  .footer-subscribe-title { text-align: left; }
}
@media screen and (min-width: 1158px) {
  .footer-container { flex-wrap: nowrap; }
  .footer-brand { margin: 0 120px 0 0; }
  .footer-social { margin: 0; }
  .footer-subscribe { width: auto; margin-left: auto; }
}
""")

append("modal.css", """
@media screen and (max-width: 767px) {
  .modal {
    max-height: calc(100vh - 32px);
    overflow-y: auto;
  }
}
""")

(root/"css/mobile-menu.css").write_text("""/* Standalone viewport-covering mobile menu. */
.mobile-menu {
  position: fixed;
  inset: 0;
  z-index: 900;
  width: 100%;
  height: 100%;
  background-color: #ffffff;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transition: opacity 250ms cubic-bezier(0.4, 0, 0.2, 1),
    visibility 250ms cubic-bezier(0.4, 0, 0.2, 1);
}
.mobile-menu.is-open {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}
.mobile-menu-inner {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 100%;
  height: 100%;
  max-width: 320px;
  padding: 72px 16px 40px;
  margin: 0 auto;
  overflow-y: auto;
}
.mobile-menu-close {
  position: absolute;
  top: 24px;
  right: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: 1px solid #e7e9fc;
  border-radius: 50%;
  background-color: #e7e9fc;
  cursor: pointer;
}
.mobile-navigation-list { display: flex; flex-direction: column; gap: 40px; }
.mobile-navigation-link {
  font-weight: 700;
  font-size: 36px;
  line-height: 1.11;
  letter-spacing: 0.02em;
  color: #2e2f42;
  transition: color 250ms cubic-bezier(0.4, 0, 0.2, 1);
}
.mobile-navigation-link:hover,
.mobile-navigation-link:focus { color: #404bbf; }
.mobile-contact-details { font-style: normal; margin-bottom: 48px; }
.mobile-contact-list { display: flex; flex-direction: column; gap: 24px; }
.mobile-phone { color: #4d5ae5; font-size: 24px; font-weight: 500; line-height: 1.2; }
.mobile-email { color: #434455; font-size: 20px; line-height: 1.2; }
.mobile-social-list { display: flex; gap: 16px; justify-content: space-between; }
.mobile-social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #4d5ae5;
  transition: background-color 250ms cubic-bezier(0.4, 0, 0.2, 1);
}
.mobile-social-link:hover, .mobile-social-link:focus { background-color: #404bbf; }
@media screen and (min-width: 768px) {
  .mobile-menu { display: none; }
}
""", encoding="utf-8")

main = root/"css/main.css"
existing=main.read_text(encoding="utf-8")
assert 'modal.css' in existing
main.write_text(existing.rstrip()+'\n@import "./mobile-menu.css";\n',encoding="utf-8")
print("Responsive HTML, CSS, menu and srcset updated.")
