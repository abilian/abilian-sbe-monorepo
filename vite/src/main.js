// vite/src/main.js

// --- Core Libraries ---
// Import Alpine.js and start it. This is ESSENTIAL for the navbar.
import Alpine from 'alpinejs';
window.Alpine = Alpine;
Alpine.start();

// --- Legacy Libraries (for backward compatibility) ---
// Import libraries and attach them to the `window` object so that old,
// non-module scripts can still find them.
import jQuery from 'jquery';
window.jQuery = window.$ = jQuery;

import 'datatables.net';
import 'select2';
// Note: You may need to import other legacy plugins here as well,
// e.g., bootbox, datepicker, etc. Add them as needed.

// --- Abilian's Legacy Scripts ---
// Import your application's own scripts. The order might be important.
// You will need to find these files in your old asset structure and
// ensure they are accessible. For now, we assume they are in static folders.
// This is a temporary measure; ideally, these would be refactored.
//
// Example (you will need to verify paths):
// import '/path/to/static/js/abilian-namespace.js';
// import '/path/to/static/js/abilian.js';
// import '/path/to/static/js/widgets/base.js';

console.log("Vite JS bundle loaded successfully. Alpine.js started.");
