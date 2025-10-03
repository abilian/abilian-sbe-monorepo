// vite/src/main.js

// --- Core Libraries ---
// Import Alpine.js FIRST and start it immediately
import Alpine from "alpinejs";

// Make Alpine available globally
window.Alpine = Alpine;

// Start Alpine IMMEDIATELY before any other code runs
// This allows Alpine to set up its mutation observer and process directives
Alpine.start();

// --- Legacy Libraries (for backward compatibility) ---
// jQuery is loaded globally in abilian_base.html before this module loads
// We don't import it here to avoid loading it twice
// DataTables and Select2 are already loaded via legacy scripts in the HTML

// Import vanilla JS component implementations AFTER Alpine is started
import "./alpine-components.js";
