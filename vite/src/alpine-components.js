/**
 * Alpine.js components for Bootstrap replacement
 * Provides dropdown, modal, collapse, and tab functionality
 *
 * This uses vanilla JS with minimal Alpine integration for maximum compatibility
 */

(function () {
  "use strict";

  console.log("Loading Alpine components...");

  // Initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  function init() {
    console.log("Initializing interactive components...");

    // Hide all modals and dropdowns initially
    hideAllModals();
    hideAllDropdowns();

    // Set up handlers
    initDropdowns();
    initModals();
    initCollapse();
    initTabs();
    initAlerts();

    console.log("Interactive components initialized");
  }

  /**
   * Hide all modals on page load
   */
  function hideAllModals() {
    document.querySelectorAll(".modal").forEach(function (modal) {
      modal.style.display = "none";
    });
  }

  /**
   * Hide all dropdown menus on page load
   */
  function hideAllDropdowns() {
    document.querySelectorAll(".dropdown-menu").forEach(function (menu) {
      menu.style.display = "none";
    });
  }

  /**
   * Dropdown functionality
   */
  function initDropdowns() {
    document
      .querySelectorAll('[data-toggle="dropdown"]')
      .forEach(function (trigger) {
        if (trigger.hasAttribute("data-dropdown-initialized")) return;
        trigger.setAttribute("data-dropdown-initialized", "true");

        const parent = trigger.closest(".dropdown") || trigger.parentElement;
        const menu = parent.querySelector(".dropdown-menu");

        if (!menu) return;

        // Ensure menu is hidden initially
        menu.style.display = "none";

        // Toggle on trigger click
        trigger.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();

          const isOpen = menu.style.display === "block";

          // Close all other dropdowns first
          document.querySelectorAll(".dropdown-menu").forEach(function (m) {
            m.style.display = "none";
            const p = m.closest(".dropdown");
            if (p) p.classList.remove("open");
          });

          if (!isOpen) {
            menu.style.display = "block";
            parent.classList.add("open");
          } else {
            menu.style.display = "none";
            parent.classList.remove("open");
          }
        });

        // Close on click outside
        document.addEventListener("click", function (e) {
          if (!parent.contains(e.target)) {
            menu.style.display = "none";
            parent.classList.remove("open");
          }
        });
      });
  }

  /**
   * Modal functionality
   */
  function initModals() {
    // Initialize modal triggers
    document
      .querySelectorAll('[data-toggle="modal"]')
      .forEach(function (trigger) {
        if (trigger.hasAttribute("data-modal-initialized")) return;
        trigger.setAttribute("data-modal-initialized", "true");

        const targetSelector =
          trigger.getAttribute("data-target") || trigger.getAttribute("href");
        if (!targetSelector) return;

        const modal = document.querySelector(targetSelector);
        if (!modal) return;

        // Ensure modal is hidden initially
        modal.style.display = "none";

        trigger.addEventListener("click", function (e) {
          e.preventDefault();
          showModal(modal);
        });
      });

    // Initialize dismiss buttons
    document
      .querySelectorAll('[data-dismiss="modal"]')
      .forEach(function (dismissBtn) {
        if (dismissBtn.hasAttribute("data-dismiss-initialized")) return;
        dismissBtn.setAttribute("data-dismiss-initialized", "true");

        dismissBtn.addEventListener("click", function (e) {
          e.preventDefault();
          const modal = dismissBtn.closest(".modal");
          if (modal) {
            hideModal(modal);
          }
        });
      });

    // Initialize all modals to handle backdrop clicks and ESC key
    document.querySelectorAll(".modal").forEach(function (modal) {
      if (modal.hasAttribute("data-modal-container-initialized")) return;
      modal.setAttribute("data-modal-container-initialized", "true");

      // Ensure hidden initially
      modal.style.display = "none";

      // Close on backdrop click
      modal.addEventListener("click", function (e) {
        if (e.target === modal) {
          hideModal(modal);
        }
      });

      // Close on ESC key
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && modal.style.display === "flex") {
          hideModal(modal);
        }
      });
    });
  }

  function showModal(modal) {
    modal.style.display = "flex";
    document.body.classList.add("modal-open");
  }

  function hideModal(modal) {
    modal.style.display = "none";
    document.body.classList.remove("modal-open");
  }

  /**
   * Collapse functionality
   */
  function initCollapse() {
    document
      .querySelectorAll('[data-toggle="collapse"]')
      .forEach(function (trigger) {
        if (trigger.hasAttribute("data-collapse-initialized")) return;
        trigger.setAttribute("data-collapse-initialized", "true");

        const targetSelector =
          trigger.getAttribute("data-target") || trigger.getAttribute("href");
        if (!targetSelector) return;

        const target = document.querySelector(targetSelector);
        if (!target) return;

        // Determine initial state from trigger
        const isCollapsed = trigger.classList.contains("collapsed");

        // Set initial display
        if (isCollapsed) {
          target.style.display = "none";
          target.classList.remove("in");
        } else {
          target.style.display = "block";
          target.classList.add("in");
        }

        trigger.addEventListener("click", function (e) {
          e.preventDefault();

          const isCurrentlyCollapsed = target.style.display === "none";

          if (isCurrentlyCollapsed) {
            target.style.display = "block";
            target.classList.add("in");
            trigger.classList.remove("collapsed");
          } else {
            target.style.display = "none";
            target.classList.remove("in");
            trigger.classList.add("collapsed");
          }
        });
      });
  }

  /**
   * Tab functionality
   */
  function initTabs() {
    document
      .querySelectorAll('[data-toggle="tab"]')
      .forEach(function (trigger) {
        if (trigger.hasAttribute("data-tab-initialized")) return;
        trigger.setAttribute("data-tab-initialized", "true");

        trigger.addEventListener("click", function (e) {
          e.preventDefault();

          const targetSelector = trigger.getAttribute("href");
          if (!targetSelector) return;

          const target = document.querySelector(targetSelector);
          if (!target) return;

          // Deactivate all tabs in the group
          const tabList =
            trigger.closest('[role="tablist"]') || trigger.closest(".nav-tabs");
          if (tabList) {
            tabList.querySelectorAll("li").forEach(function (li) {
              li.classList.remove("active");
            });
            tabList.querySelectorAll("a").forEach(function (a) {
              a.setAttribute("aria-selected", "false");
            });
          }

          // Activate this tab
          const parentLi = trigger.closest("li");
          if (parentLi) parentLi.classList.add("active");
          trigger.setAttribute("aria-selected", "true");

          // Hide all tab panes in the group
          const tabContent = target.closest(".tab-content");
          if (tabContent) {
            tabContent.querySelectorAll(".tab-pane").forEach(function (pane) {
              pane.classList.remove("active", "in");
            });
          }

          // Show target pane
          target.classList.add("active", "in");
        });
      });
  }

  /**
   * Alert dismiss functionality
   */
  function initAlerts() {
    document
      .querySelectorAll('[data-dismiss="alert"]')
      .forEach(function (dismissBtn) {
        if (dismissBtn.hasAttribute("data-alert-dismiss-initialized")) return;
        dismissBtn.setAttribute("data-alert-dismiss-initialized", "true");

        dismissBtn.addEventListener("click", function (e) {
          e.preventDefault();
          const alert = dismissBtn.closest(".alert");
          if (alert) {
            alert.style.transition = "opacity 0.15s linear";
            alert.style.opacity = "0";
            setTimeout(function () {
              alert.remove();
            }, 150);
          }
        });
      });
  }
})();
