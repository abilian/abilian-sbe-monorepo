/* Title-uniqueness check for the folder/document create and rename modals.
 *
 * Vanilla JS. The old version used $.ajax({async: false}) -- a synchronous XHR,
 * deprecated and main-thread-blocking -- so it could decide inside the click
 * handler whether to preventDefault(). fetch() cannot do that, so instead the
 * first click is always cancelled and the button re-clicked once the check comes
 * back clean. Re-clicking rather than form.submit() keeps the button's
 * name="action" value, which the server handler reads.
 */
define("SBEFolderEditSetup", ["Abilian"], () => {
  "use strict";

  function setupModalFolderInputnameCheck(target, objectId, action) {
    // A CSS selector, or the container element itself: the Alpine document
    // modal has no stable id and computes its own.
    const modal =
      typeof target === "string" ? document.querySelector(target) : target;
    if (!modal) return;

    // Was `button.btn-primary`, which stopped matching anything when the modals
    // were converted to Tailwind -- the check has been inert since.
    const submit = modal.querySelector('button[type="submit"]');
    const input = modal.querySelector('input[name="title"]');
    if (!submit || !input) return;

    const checkUrl = input.dataset.checkUrl;
    const help = modal.querySelector("span.help-block");
    let checked = false;

    function setError(message) {
      input.classList.toggle("border-red-500", Boolean(message));
      if (!help) return;
      help.textContent = message || "";
      // The markup hides this with Tailwind's `hidden`; the old code toggled
      // `hide`, a Bootstrap class that no longer exists, so nothing showed.
      help.classList.toggle("hidden", !message);
      help.classList.toggle("text-red-600", Boolean(message));
    }

    submit.addEventListener("click", (event) => {
      if (checked) {
        checked = false;
        return; // Let the real submit through.
      }
      event.preventDefault();

      const params = new URLSearchParams({
        object_id: objectId,
        title: input.value,
        action,
      });

      fetch(`${checkUrl}?${params}`, { credentials: "same-origin" })
        .then((response) => response.json())
        .then((data) => {
          if (data.valid) {
            setError(null);
            checked = true;
            submit.click();
          } else {
            setError(data.help_text);
          }
        });
    });
  }

  return setupModalFolderInputnameCheck;
});
