# Modernizing Front-End Architecture with Flask-Vite, Tailwind CSS, and Lightweight Interaction Frameworks

Status: Draft

## Introduction

This ADR outlines the plan for modernizing the front-end architecture of **Abilian SBE**. The goal is to adopt a modern development toolchain, replace legacy dependencies, and introduce lightweight frameworks for client-side interactivity. This effort aims to improve developer productivity, ensure long-term maintainability, and enhance the user experience by leveraging more efficient and flexible technologies.

The modernization will focus on introducing **Flask-Vite** for managing assets, **Tailwind CSS** for styling, and lightweight JavaScript frameworks like **HTMX**, **Alpine.js**, or **Hyperscript** to replace older, heavier frameworks like **jQuery** and **flask-assets**.

## Summary

This ADR covers the introduction of **Flask-Vite** for front-end asset management, **Tailwind CSS** for a modern, utility-first design system, and a lightweight front-end interaction framework like **HTMX** or **Alpine.js**. Additionally, it addresses the deprecation and removal of legacy dependencies such as **jQuery**, **closure**, and **flask-assets**.

## Status

Proposed

## Context and Goals

### Context

The current front-end architecture of Abilian SBE relies on legacy technologies such as **jQuery**, **flask-assets**, and **closure**, which have become difficult to maintain and extend. These tools do not align with modern web development practices and impose a significant overhead on both developers and the platform’s performance.

- **jQuery**: Although widely used in the past, it is no longer necessary for most modern front-end development tasks.
- **flask-assets**: This package was previously used to manage and bundle front-end assets, but it lacks flexibility and integration with modern front-end workflows.
- **closure**: Used as a plugin system for front-end code, it is now outdated and difficult to extend.

### Goals

- **Modernize the front-end architecture** by adopting a more scalable and maintainable toolchain.
- **Improve developer productivity** by streamlining asset management and reducing the complexity of the front-end stack.
- **Enhance the user experience** through faster load times and more efficient interactivity.
- **Deprecate and replace legacy dependencies** with modern, lightweight alternatives that align with current best practices.

## Tenets

- **Simplicity**: The new front-end stack should be easy to understand, maintain, and extend.
- **Performance**: Reduce the size of front-end assets and improve page load times by adopting modern, lightweight frameworks.
- **Modularity**: Ensure the front-end architecture is modular and pluggable, allowing for easier customization and future enhancements.
- **Responsiveness**: Design a front-end that is mobile-friendly and adaptable to various screen sizes using modern responsive design techniques.

## Decision

### Key Technologies and Tools

1. **Flask-Vite**:
   - **Asset Management**: We will use **Flask-Vite** to manage and bundle front-end assets. Vite is a fast build tool optimized for modern JavaScript and CSS workflows.
   - **Benefits**: It supports ES modules, faster builds, hot module replacement (HMR), and better integration with modern JavaScript ecosystems like React, Vue, or Svelte (if required in the future).

2. **Tailwind CSS**:
   - **Design System**: We will use **Tailwind CSS** to provide a utility-first CSS framework. Tailwind allows for highly customizable and maintainable design without relying on monolithic CSS files.
   - **Benefits**: Tailwind promotes reusability, modularity, and a clean design approach while reducing the need for custom CSS.

3. **Lightweight Front-End Interaction Framework**:
   - **HTMX** or **Alpine.js**: These frameworks offer a lightweight alternative to traditional client-side JavaScript. They allow for interactivity without the overhead of larger frameworks.
   - **Benefits**:
     - **HTMX** allows for server-driven UI updates with minimal JavaScript.
     - **Alpine.js** (or **Hyperscript**) provides lightweight JavaScript interactivity, closer to the feel of Vue.js, but without the complexity.
   - These frameworks will help us reduce the reliance on AJAX calls and heavy JavaScript logic, moving towards a more declarative model of front-end interactivity.

### Deprecation and Removal of Legacy Dependencies

1. **Deprecation of jQuery**:
   - jQuery will be replaced with native JavaScript and lightweight frameworks such as HTMX or Alpine.js.
   - Where necessary (e.g., for complex data tables), we will phase out jQuery plugins, opting for modern libraries or components.

2. **Closure and flask-assets**:
   - **flask-assets** will be replaced by **Flask-Vite** to manage front-end assets more effectively.
   - The **closure-based plugin system** will be refactored, replaced by a modular system that integrates directly with Vite and Flask-Vite. This might include using **Flask-Vite plugins** or a custom front-end architecture that leverages Vite’s modern capabilities.

3. **Refactoring Legacy AJAX/JavaScript**:
   - We will replace complex jQuery-based AJAX logic with **HTMX** or **Alpine.js**, simplifying the interaction model to rely more on declarative HTML and server-driven UI updates.
   - **AJAX-heavy pages** will be refactored to use HTMX to trigger partial page updates from the server, reducing the amount of JavaScript required on the client.

## Detailed Design

1. **Front-End Asset Management with Flask-Vite**:
   - Migrate from **flask-assets** to **Flask-Vite**.
   - Vite will handle all JavaScript and CSS bundling, and the integration with Flask will allow for easy management of assets in both development and production environments.
   - The setup will include hot module replacement for development and optimized builds for production, significantly improving the developer experience.

2. **Introduction of Tailwind CSS**:
   - Tailwind CSS will be integrated into the front-end stack, replacing custom and legacy CSS with a utility-first design system.
   - The design system will include components and layout utilities for rapid UI development, including responsiveness and accessibility.

3. **Lightweight Front-End Interactivity**:
   - **HTMX** will be introduced to handle declarative, server-driven interactivity, such as form submissions, page updates, and content replacement without the need for custom JavaScript.
   - **Alpine.js** or **Hyperscript** will be used for lightweight client-side interactivity where needed, providing state management and event handling without the overhead of a full framework like Vue or React.
   - Use cases include interactive widgets, form validation, modals, and tabs.

4. **Migration Path for Legacy Dependencies**:
   - **Phased removal** of jQuery and other legacy dependencies:
     - First, identify and replace jQuery uses with native JavaScript, HTMX, or Alpine.js equivalents.
     - Gradually remove **flask-assets** and **closure**-based plugins in favor of Flask-Vite.

## Examples and Interactions

1. **Asset Bundling with Flask-Vite**:
   - During development, Vite will bundle assets with hot module replacement enabled, speeding up the feedback loop for front-end development.
   - In production, Vite will minify and optimize assets for fast page loads.

2. **Tailwind CSS for Utility-First Design**:
   - Layouts and components will be styled using Tailwind CSS classes, allowing for rapid UI development without writing custom CSS.
   - Example:
     ```html
     <div class="p-4 bg-gray-200 rounded-lg">
       <h1 class="text-xl font-bold">Welcome to Abilian SBE</h1>
     </div>
     ```

3. **HTMX for Interactive Pages**:
   - Use **HTMX** to enable partial page updates without full page reloads.
   - Example:
     ```html
     <button hx-get="/update" hx-target="#result">Click Me</button>
     <div id="result"></div>
     ```

## Consequences

### Benefits

- **Modernization**: By using Flask-Vite and Tailwind CSS, the front-end will be modern, modular, and easier to maintain.
- **Developer Productivity**: The new stack will simplify development, improve build speeds, and provide a better developer experience.
- **Performance**: Switching to lightweight frameworks like HTMX and Alpine.js will reduce the amount of JavaScript on the client, leading to faster page loads and better performance.
- **Consistency**: Tailwind CSS will provide a consistent design system across the application, reducing the need for custom styling.

### Drawbacks

- **Migration Effort**: The migration of legacy dependencies like jQuery and flask-assets will require significant refactoring and testing.
- **Learning Curve**: Developers will need to familiarize themselves with the new tools, particularly Flask-Vite and Tailwind CSS.

## Lessons Learned

In previous refactoring efforts, we've seen that removing legacy dependencies piecemeal without a clear migration strategy leads to inconsistencies and technical debt. A well-planned, phased approach is critical to ensure the new front-end architecture is properly integrated without breaking existing functionality.

## Action Items

### Strategic Priorities

1. Integrate Flask-Vite into the build pipeline.
2. Introduce Tailwind CSS and define reusable components for the design system.
3. Replace jQuery and AJAX with HTMX and Alpine.js.
4. Remove flask-assets and closure, replacing them with modern, modular front-end tools.
5. Test the entire front-end stack for DX and UX improvements and compatibility across mobile, tablet, and desktop platforms.

## Alternatives

- **Full Front-End Framework (Vue, React)**: A full front-end framework like Vue.js or React could be considered, but this would increase the complexity and lead to a heavier JavaScript bundle.
- **Sticking with Legacy Tools**: Continuing to use jQuery and flask-assets would avoid the migration effort, but would also hinder future development and modernization.

## Prior Art

- Many modern web applications have moved to **Vite** as a replacement for older bundling tools like Webpack or Gulp, particularly in environments where fast iteration is required.
- **Tailwind CSS** has been widely adopted for building scalable, maintainable UIs without the complexity of traditional CSS frameworks.

## Unresolved Questions

- Should we use **Alpine.js** or **HTMX** for interactive features requiring more client-side logic?
- How will we manage the transition for existing users and developers accustomed to the legacy stack?

## Future Work

- Explore the integration of a full design system based on Tailwind components.
- Add support for **dark mode** or other accessibility features as part of the design overhaul.

## Related

- ADR TODO: Deprecation of Legacy JavaScript Libraries
- ADR TODO: Front-End Modularization with Flask-Vite
- ADR TODO: Design System Implementation with Tailwind CSS
- ADR TODO: Lightweight Front-End Interactivity with HTMX and Alpine.js

## References

- **Flask-Vite**: https://pypi.org/project/Flask-Vite/
- **Tailwind CSS**: https://tailwindcss.com/
- **HTMX**: https://htmx.org/
