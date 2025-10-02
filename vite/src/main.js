// vite/src/main.js

// --- Core Libraries ---
// Import Alpine.js and start it
import Alpine from 'alpinejs';

// Import Alpine.js component implementations
import './alpine-components.js';

window.Alpine = Alpine;
Alpine.start();

// --- Legacy Libraries (for backward compatibility) ---
// Import jQuery for DataTables and legacy code
import jQuery from 'jquery';
window.jQuery = window.$ = jQuery;

// Import other legacy libraries
import 'datatables.net';
import 'select2';

console.log("Vite JS bundle loaded successfully.");
console.log("jQuery version:", jQuery.fn.jquery);
console.log("Alpine.js started with custom components.");
