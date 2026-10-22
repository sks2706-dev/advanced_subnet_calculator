/**
 * script.js — Tab navigation & animations for IPv4 Subnet Toolkit
 * Vanilla JS only. No external libraries.
 */

(function () {
  "use strict";

  const navItems = document.querySelectorAll(".sidebar-nav-item");
  const sections = document.querySelectorAll(".tool-section");
  const landing = document.getElementById("landing");

  /**
   * Show the tool section matching the given id, hide everything else.
   * Applies a fade-in / slide-up animation via CSS class swap.
   */
  function showSection(id) {
    // Hide landing
    if (landing) {
      landing.classList.add("hidden");
    }

    // Hide all sections, reset their animation class
    sections.forEach((sec) => {
      sec.classList.remove("active", "fade-in");
    });

    // Activate target section and trigger animation
    const target = document.getElementById(id);
    if (target) {
      target.classList.add("active");
      // Force reflow so the animation restarts cleanly
      void target.offsetWidth;
      target.classList.add("fade-in");
    }

    // Update active nav state
    navItems.forEach((item) => {
      item.classList.toggle("active", item.dataset.target === id);
    });
  }

  /**
   * Attach click listeners to sidebar nav items.
   */
  function initNav() {
    navItems.forEach((item) => {
      item.addEventListener("click", () => {
        const target = item.dataset.target;
        if (target) {
          showSection(target);
        }
      });
    });
  }

  /**
   * On page load, if the server returned results for a specific tool
   * (indicated by the data-active-section attribute on <body>),
   * auto-navigate to that tool so the user sees their results.
   */
  function handleServerResult() {
    const body = document.body;
    const activeSection = body.dataset.activeSection;
    if (activeSection) {
      showSection(activeSection);
    }
  }

  /**
   * Staggered entrance animation for sidebar nav items on initial load.
   */
  function initPageLoadAnimation() {
    navItems.forEach((item, i) => {
      item.style.animationDelay = `${0.1 + i * 0.07}s`;
      item.classList.add("nav-enter");
    });

    // Animate landing title words
    const heroWords = document.querySelectorAll(".hero-word");
    heroWords.forEach((word, i) => {
      word.style.animationDelay = `${0.2 + i * 0.1}s`;
      word.classList.add("hero-enter");
    });
  }

  // Boot
  document.addEventListener("DOMContentLoaded", () => {
    initNav();
    initPageLoadAnimation();
    handleServerResult();
  });
})();
