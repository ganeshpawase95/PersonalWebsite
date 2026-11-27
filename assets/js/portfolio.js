const root = document.documentElement;
const themeButton = document.querySelector(".theme");
const menuButton = document.querySelector(".menu");
const nav = document.querySelector("nav");

function syncThemeLabel() {
  const dark = root.dataset.theme === "dark";
  const label = dark ? "Switch to light theme" : "Switch to dark theme";
  themeButton.setAttribute("aria-label", label);
  themeButton.title = label;
  document.querySelector('meta[name="theme-color"]').content = dark ? "#080d19" : "#f7faff";
}

syncThemeLabel();
themeButton.addEventListener("click", () => {
  root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
  syncThemeLabel();
  try {
    localStorage.setItem("gp-theme", root.dataset.theme);
  } catch {
    // The current page can still switch themes without storage.
  }
});

function setMenu(open) {
  nav.classList.toggle("open", open);
  menuButton.setAttribute("aria-expanded", String(open));
  menuButton.setAttribute("aria-label", open ? "Close menu" : "Open menu");
}
menuButton.addEventListener("click", () => {
  const opening = menuButton.getAttribute("aria-expanded") === "false";
  setMenu(opening);
  if (opening) nav.querySelector("a").focus();
});
nav.addEventListener("click", (event) => {
  const link = event.target.closest("a");
  if (!link || menuButton.getAttribute("aria-expanded") !== "true") return;
  setMenu(false);
  const section = document.getElementById(link.hash.slice(1));
  if (section) {
    section.setAttribute("tabindex", "-1");
    section.focus({ preventScroll: true });
  }
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && nav.classList.contains("open")) {
    setMenu(false);
    menuButton.focus();
  }
});
document.addEventListener("pointerdown", (event) => {
  if (!event.target.closest(".site-header")) setMenu(false);
});
document.querySelector(".site-header").addEventListener("focusout", (event) => {
  if (!event.currentTarget.contains(event.relatedTarget)) setMenu(false);
});
matchMedia("(max-width: 760px)").addEventListener("change", () => setMenu(false));
document.querySelector("[data-year]").textContent = new Date().getFullYear();

const sections = Array.from(document.querySelectorAll("main section[id]"));
if (sections.length) {
  let scheduled = false;
  function highlightSection() {
    const atEnd = Math.ceil(scrollY + innerHeight) >= document.documentElement.scrollHeight;
    const current = atEnd ? sections.at(-1) :
      sections.filter(section => section.getBoundingClientRect().top <= 125).at(-1) || sections[0];
    for (const link of nav.querySelectorAll("a")) {
      if (link.hash === "#" + current.id) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    }
    scheduled = false;
  }
  addEventListener("scroll", () => {
    if (!scheduled) requestAnimationFrame(highlightSection);
    scheduled = true;
  }, { passive: true });
  highlightSection();
}
