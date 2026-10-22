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
   */
  function showSection(id) {
    if (landing) {
      landing.classList.add("hidden");
    }

    sections.forEach((sec) => {
      sec.classList.remove("active", "fade-in");
    });

    const target = document.getElementById(id);
    if (target) {
      target.classList.add("active");
      void target.offsetWidth; // Force reflow
      target.classList.add("fade-in");
    }

    navItems.forEach((item) => {
      item.classList.toggle("active", item.dataset.target === id);
    });
  }

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

  function handleServerResult() {
    const body = document.body;
    const activeSection = body.dataset.activeSection;
    if (activeSection) {
      showSection(activeSection);
    }
  }

  function initPageLoadAnimation() {
    navItems.forEach((item, i) => {
      item.style.animationDelay = `${0.1 + i * 0.07}s`;
      item.classList.add("nav-enter");
    });

    const heroWords = document.querySelectorAll(".hero-word");
    heroWords.forEach((word, i) => {
      word.style.animationDelay = `${0.2 + i * 0.1}s`;
      word.classList.add("hero-enter");
    });
  }

  /**
   * CORRECTED: Binary Coloring based on Subnet Mask position
   */
  function colorBinaryBits() {
    const pres = document.querySelectorAll("#section-calc pre");
    
    pres.forEach((pre) => {
      const raw = pre.textContent;
      const lines = raw.split('\n');
      
      let maskBits = "";
      // 1. Find the subnet mask to know where the network ends
      for (let line of lines) {
        if (line.includes("Subnet Mask:")) {
          maskBits = line.split(':')[1].replace(/\./g, '').replace(/\s/g, '');
          break;
        }
      }

      if (!maskBits) return; // If no mask found, stop

      let html = "";
      let bitIndex = 0;

      // 2. Loop through the text and color based on the mask
      for (let i = 0; i < raw.length; i++) {
        const ch = raw[i];
        
        // Keep spaces and newlines as-is
        if (ch === '\n' || ch === ' ' || ch === '\t') {
            html += ch;
        } else if (ch === '.') {
            html += ch;
        } else if (ch === '0' || ch === '1') {
            // Check if the corresponding bit in the mask is 1 or 0
            if (maskBits[bitIndex] === '1') {
                html += `<span class="net-bit">${ch}</span>`;
            } else {
                html += `<span class="host-bit">${ch}</span>`;
            }
            bitIndex++;
        } else {
            // Keep text labels like "IP:" as normal text
            if (ch === "&") html += "&amp;";
            else if (ch === "<") html += "&lt;";
            else if (ch === ">") html += "&gt;";
            else html += ch;
        }
        
        // Reset bitIndex at the end of a line so the next line starts fresh
        if (ch === '\n') {
            bitIndex = 0;
        }
      }
      pre.innerHTML = html;
    });
  }

  // Boot
  document.addEventListener("DOMContentLoaded", () => {
    initNav();
    initPageLoadAnimation();
    handleServerResult();
    colorBinaryBits();
  });
})();