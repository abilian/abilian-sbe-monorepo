// vite/src/main.js

// --- Core Libraries ---
// Import Alpine.js FIRST and start it immediately
import Alpine from "alpinejs";

// Make Alpine available globally
window.Alpine = Alpine;

// Start Alpine IMMEDIATELY before any other code runs
// This allows Alpine to set up its mutation observer and process directives
Alpine.start();

console.log("Alpine.js started");
console.log("Alpine version:", Alpine.version);

// --- Legacy Libraries (for backward compatibility) ---
// jQuery is loaded globally in abilian_base.html before this module loads
// We don't import it here to avoid loading it twice
const jQuery = window.jQuery || window.$;
if (!jQuery) {
  console.error("jQuery not found! Legacy scripts may not work.");
}

// DataTables and Select2 are already loaded via legacy scripts in the HTML
// We don't need to import them here since they're available globally
// and were loaded before this module executes

// Import vanilla JS component implementations AFTER Alpine is started
import "./alpine-components.js";

console.log("Vite JS bundle loaded successfully.");
console.log("jQuery version:", jQuery.fn.jquery);
console.log("All components initialized.");
