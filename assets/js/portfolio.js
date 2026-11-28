const root = document.documentElement;
const themeButton = document.querySelector(".theme");
const menuButton = document.querySelector(".menu");
const nav = document.querySelector("nav");

for (const gallery of document.querySelectorAll(".gallery")) {
  const filters = gallery.querySelector(".filters");
  const buttons = filters.querySelectorAll("button");
  const cards = gallery.querySelectorAll("[data-category]");
  filters.hidden = false;
  filters.addEventListener("click", (event) => {
    const selected = event.target.closest("button");
    if (!selected) return;
    const group = selected.dataset.filter;
    let visible = 0;
    for (const card of cards) {
      card.hidden = group !== "All" && card.dataset.category !== group;
      if (!card.hidden) visible++;
    }
    for (const button of buttons) button.setAttribute("aria-pressed", String(button === selected));
    gallery.querySelector('[role="status"]').textContent = visible + (visible === 1 ? " project shown" : " projects shown");
  });
}

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
matchMedia("(max-width: 900px)").addEventListener("change", () => setMenu(false));
document.querySelector("[data-year]").textContent = new Date().getFullYear();

if ("IntersectionObserver" in window) {
  const entryEdges = new WeakMap();
  const observer = new IntersectionObserver(entries => {
    const siblingsEntering = new Map();
    for (const entry of entries) {
      const item = entry.target;
      if (!entry.isIntersecting) {
        const above = entry.boundingClientRect.bottom <= (entry.rootBounds?.top ?? 0);
        entryEdges.set(item, above ? "above" : "below");
        continue;
      }

      // Leave the initial viewport in place, including on direct links to sections.
      const edge = entryEdges.get(item);
      entryEdges.delete(item);
      if (!edge || item.hasAttribute("data-scroll-entry")) continue;

      const position = siblingsEntering.get(item.parentElement) ?? 0;
      siblingsEntering.set(item.parentElement, position + 1);
      item.style.setProperty("--entry-delay", Math.min(position, 3) * 45 + "ms");
      item.dataset.scrollEntry = edge;
    }
  }, { rootMargin: "-12px 0px" });

  const items = document.querySelectorAll(
    ".highlights > div, .section-head, .about > div, #skills > h2, .skill, .project, " +
    ".career > div:first-child, .job, .article-card, .contact > div, " +
    ".detail > img, .detail > .cover, .detail > h2, .detail > h2 + p"
  );
  const preference = matchMedia("(prefers-reduced-motion: reduce)");
  function syncScrollMotion() {
    observer.disconnect();
    for (const item of items) {
      entryEdges.delete(item);
      item.removeAttribute("data-scroll-entry");
      if (!preference.matches) observer.observe(item);
    }
  }
  function clearScrollEntry(event) {
    if (event.animationName === "scroll-entry") event.target.removeAttribute("data-scroll-entry");
  }
  document.addEventListener("animationend", clearScrollEntry);
  document.addEventListener("animationcancel", clearScrollEntry);
  preference.addEventListener("change", syncScrollMotion);
  syncScrollMotion();
}

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
