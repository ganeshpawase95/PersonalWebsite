(() => {
  try {
    const saved = localStorage.getItem("gp-theme");
    if (saved === "light" || saved === "dark") {
      document.documentElement.dataset.theme = saved;
    }
  } catch {
    // Storage can be unavailable in private browsing.
  }
})();
