/* ======================= */
/* Back to top button */
/* ======================= */
window.addEventListener("scroll", () => {
  const btn = document.getElementById("back-to-top");
  if (!btn) return;
  btn.style.display = window.scrollY > 200 ? "block" : "none";
});

/* ======================= */
/* Dark / Light toggle */
/* ======================= */
const toggleBtn = document.getElementById("theme-toggle");
const root = document.documentElement;

/* SVG icons */
const sunIcon = `
  <svg class="theme-icon" viewBox="0 0 24 24" aria-hidden="true">
    <circle cx="12" cy="12" r="5"/>
    <line x1="12" y1="1" x2="12" y2="3"/>
    <line x1="12" y1="21" x2="12" y2="23"/>
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
    <line x1="1" y1="12" x2="3" y2="12"/>
    <line x1="21" y1="12" x2="23" y2="12"/>
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
  </svg>
`;

const moonIcon = `
  <svg class="theme-icon" viewBox="0 0 24 24" aria-hidden="true">
    <path d="M21 12.79A9 9 0 1111.21 3
             7 7 0 0021 12.79z"/>
  </svg>
`;

function updateToggle(theme) {
  toggleBtn.innerHTML =
    theme === "dark"
      ? `${sunIcon}<span>Light mode</span>`
      : `${moonIcon}<span>Dark mode</span>`;
}

if (toggleBtn) {
  // Restore the saved theme
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    root.setAttribute("data-theme", savedTheme);
    updateToggle(savedTheme);
  }

  // Change theme
  toggleBtn.addEventListener("click", () => {
    const current = root.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";

    root.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
    updateToggle(next);
  });
}
