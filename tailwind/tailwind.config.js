const colors = require("tailwindcss/colors");

module.exports = {
  // Make Tailwind and Bootstrap 4 cohabitate for now.
  corePlugins: { preflight: false },
  prefix: "tw-",

  content: [
    /**
     * HTML. Paths to Flask template files that may contain Tailwind CSS classes.
     */
    "../src/**/templates/**/*.html",
    "../src/**/templates/**/*.j2",

    /**
     * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
     * patterns match your project structure.
     */
    /* JS 1: Ignore any JavaScript in node_modules folder. */
    // '!../../**/node_modules',
    /* JS 2: Process all JavaScript files in the project. */
    // '../../**/*.js',

    /**
     * Python: If you use Tailwind CSS classes in Python, uncomment the following line
     * and make sure the pattern below matches your project structure.
     */
    "../src/**/*.py",
  ],

  darkMode: "media", // or 'media' or 'class'

  important: true,

  theme: {
    extend: {
      colors: {
        rose: colors.rose,
        // a17t colors
        neutral: colors.slate,
        positive: colors.green,
        urge: colors.violet,
        warning: colors.yellow,
        info: colors.blue,
        critical: colors.red,
      },
      minHeight: {
        "24": "6rem",
      }
    },
    fontFamily: {
      primary:
          'var(--family-primary, "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji")',
      secondary:
          'var(--family-secondary, "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji")',
      sans: [
        "Inter",
        "system-ui",
        "-apple-system",
        "BlinkMacSystemFont",
        '"Segoe UI"',
        "Roboto",
        '"Helvetica Neue"',
        "Arial",
        '"Noto Sans"',
        "sans-serif",
        '"Apple Color Emoji"',
        '"Segoe UI Emoji"',
        '"Segoe UI Symbol"',
        '"Noto Color Emoji"',
      ],
      serif: ["Georgia", "Cambria", '"Times New Roman"', "Times", "serif"],
      mono: [
        "Menlo",
        "Monaco",
        "Consolas",
        '"Liberation Mono"',
        '"Courier New"',
        "monospace",
      ],
    },
  },

  plugins: [
    /**
     * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
     * for forms. If you don't like it or have own styling for forms,
     * comment the line below to disable '@tailwindcss/forms'.
     */
    require('daisyui'),
    // require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
    require("@tailwindcss/line-clamp"),
    require("@tailwindcss/aspect-ratio"),
  ],

  daisyui: {
    // prefix: "dui-",
    // daisyUI config (optional)
    styled: true,
    base: true,
    utils: true,
    logs: true,
    rtl: false,
    prefix: "",
    darkTheme: "dark",
    themes: [
      {
        'abilian': {                          /* your theme name */
          'primary': colors.sky[400],           /* Primary color */
          'primary-focus': colors.sky[600],     /* Primary color - focused */
          'primary-content': '#ffffff',   /* Foreground content color to use on primary color */

          'secondary': colors.amber[400],         /* Secondary color */
          'secondary-focus': colors.amber[600],   /* Secondary color - focused */
          'secondary-content': '#ffffff', /* Foreground content color to use on secondary color */

          'accent': colors.teal[500],            /* Accent color */
          'accent-focus': colors.teal[700],      /* Accent color - focused */
          'accent-content': '#ffffff',    /* Foreground content color to use on accent color */

          'neutral': colors.zinc[500],           /* Neutral color */
          'neutral-focus': colors.zinc[700],     /* Neutral color - focused */
          'neutral-content': '#ffffff',   /* Foreground content color to use on neutral color */

          'base-100': '#ffffff',          /* Base color of page, used for blank backgrounds */
          'base-200': '#f9fafb',          /* Base color, a little darker */
          'base-300': '#d1d5db',          /* Base color, even more darker */
          'base-content': '#1f2937',      /* Foreground content color to use on base color */

          // 'info': '#2094f3',              /* Info */
          // 'success': '#009485',           /* Success */
          // 'warning': '#ff9900',           /* Warning */
          // 'error': '#ff5724',             /* Error */

          'info': colors.blue[600],
          'success': colors.green[600],
          'warning': colors.orange[600],
          'error': colors.red[600],
        },
      },
    ],
  },

};
