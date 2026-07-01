/* ==========================================
   Portfolio JavaScript
   Inventory Management System
========================================== */

document.addEventListener("DOMContentLoaded", () => {

    console.log("Portfolio initialized.");

    initializePortfolio();

});

/* ==========================================
   Initialize
========================================== */

function initializePortfolio() {

    animatePortfolioBanner();
    initializeTooltips();

}

/* ==========================================
   Banner Animation
========================================== */

function animatePortfolioBanner() {

    const banner = document.querySelector(".portfolio-banner");

    if (!banner) return;

    banner.style.opacity = "0";
    banner.style.transform = "translateY(20px)";

    setTimeout(() => {

        banner.style.transition = "all 0.6s ease";
        banner.style.opacity = "1";
        banner.style.transform = "translateY(0)";

    }, 150);

}

/* ==========================================
   Bootstrap Tooltips
========================================== */

function initializeTooltips() {

    if (typeof bootstrap === "undefined") return;

    const tooltipTriggerList = document.querySelectorAll(
        '[data-bs-toggle="tooltip"]'
    );

    [...tooltipTriggerList].forEach(element => {

        new bootstrap.Tooltip(element);

    });

}

/* ==========================================
   Future Features
========================================== */

// Portfolio Statistics
function loadPortfolioStats() {

    console.log("Portfolio stats loaded.");

}

// GitHub API
function loadGithubProjects() {

    console.log("GitHub projects ready.");

}

// Resume Download
function downloadResume() {

    console.log("Resume download.");

}

// Contact Button
function openPortfolioContact() {

    console.log("Portfolio contact.");

}