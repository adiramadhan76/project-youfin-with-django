//  JavaScript untuk menutup navbar dan scroll ke section
// Menangani click event untuk menu item
document.querySelectorAll("#navbarNav .nav-link").forEach((item) => {
  item.addEventListener("click", function () {
    const targetId = this.getAttribute("href"); // Mendapatkan ID dari link
    const targetElement = document.querySelector(targetId);
    if (targetElement) {
      targetElement.scrollIntoView({
        behavior: "smooth",
      }); // Scroll ke section
    }
    const collapseElement = document.getElementById("navbarNav");
    const collapseInstance = bootstrap.Collapse.getInstance(collapseElement);
    if (collapseInstance) {
      collapseInstance.hide(); // Menutup navbar
    }
  });
});

// Memastikan tombol navbar berfungsi dengan baik saat beralih tampilan
const navbarCollapse = document.getElementById("navbarNav");
const navbarToggleButton = document.querySelector(
  '[data-bs-target="#navbarNav"]'
);

// Menyembunyikan menu saat berpindah ke tampilan desktop
window.addEventListener("resize", function () {
  if (window.innerWidth >= 768) {
    // Jika lebih dari 768px (tampilan desktop)
    navbarCollapse.classList.remove("show"); // Menyembunyikan navbar
  }
});

// Login & Sign Up
// Toggle visibility of the password fields
document.addEventListener("DOMContentLoaded", function () {
  const togglePassword = document.querySelector("#togglePassword");
  const toggleConfirmPassword = document.querySelector(
    "#toggleConfirmPassword"
  );
  const password = document.querySelector("#password");
  const confirmPassword = document.querySelector("#confirm-password");

  if (togglePassword) {
    togglePassword.addEventListener("click", function () {
      const type =
        password.getAttribute("type") === "password" ? "text" : "password";
      password.setAttribute("type", type);
      this.classList.toggle("bi-eye");
    });
  }

  if (toggleConfirmPassword) {
    toggleConfirmPassword.addEventListener("click", function () {
      const type =
        confirmPassword.getAttribute("type") === "password"
          ? "text"
          : "password";
      confirmPassword.setAttribute("type", type);
      this.classList.toggle("bi-eye");
    });
  }
});
