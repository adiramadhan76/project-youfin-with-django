//backend
document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.querySelector(".sidebar-container");
  const mainContent = document.querySelector(".main-content");
  const overlay = document.querySelector(".overlay");
  const menuToggles = document.querySelectorAll(".menu-toggle");
  const sidebarToggle = document.createElement("button");

  // Create and add sidebar toggle button
  sidebarToggle.className = "btn btn-light position-fixed";
  sidebarToggle.style.cssText = "top: 15px; left: 15px; z-index: 1029;";
  sidebarToggle.innerHTML = '<i class="bi bi-list"></i>';
  document.body.appendChild(sidebarToggle);

  // Toggle sidebar
  function toggleSidebar() {
    if (window.innerWidth <= 992) {
      sidebar.classList.toggle("mobile-active");
      overlay.classList.toggle("active");
    } else {
      sidebar.classList.toggle("collapsed");
      mainContent.classList.toggle("expanded");
    }
  }

  // Event listeners
  sidebarToggle.addEventListener("click", toggleSidebar);
  overlay.addEventListener("click", toggleSidebar);
  menuToggles.forEach((toggle) => {
    toggle.addEventListener("click", toggleSidebar);
  });

  // Handle window resize
  let timeoutId;
  window.addEventListener("resize", () => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      if (window.innerWidth > 992) {
        sidebar.classList.remove("mobile-active");
        overlay.classList.remove("active");
      }
    }, 250);
  });

  // Active menu item
  const menuLinks = document.querySelectorAll(".menu-link");
  menuLinks.forEach((link) => {
    if (link.href === window.location.href) {
      link.classList.add("active");
    }
  });
});
