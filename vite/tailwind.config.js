const colors = require("tailwindcss/colors");

module.exports = {
  // DISABLE preflight until Bootstrap is fully removed (safe migration)
  corePlugins: { preflight: false },
  // RE-ENABLE prefix for coexistence with Bootstrap
  prefix: "tw-",

  content: [
    /**
     * HTML. Paths to Flask template files that may contain Tailwind CSS classes.
     */
    "../src/**/templates/**/*.html",
    "../src/**/templates/**/*.j2",

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
    // require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
    require("@tailwindcss/line-clamp"),
    require("@tailwindcss/aspect-ratio"),
  ],

};
