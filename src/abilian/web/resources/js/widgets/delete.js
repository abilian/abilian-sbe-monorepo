/**
 Allow to setup a delete button for urls managed by abilian.web.views.object.ObjectDelete.
 */
require(["AbilianWidget", "jquery", "AbilianConfirm"], (Abilian, $, confirmDialog) => {
  "use strict";

  const defaults = {
    title: "La suppression est irréversible",
    message: "Do you really want to delete this entity ?",
    label: "Delete",
    cancelLabel: "Cancel",
  };

  function ConfirmDialog(elt, options) {
    "use strict";

    const self = this;
    this.elt = elt;
    this.options = $.extend({}, defaults, options);
    this.url = elt.attr("href");
    elt.on("click", (e) => {
      e.preventDefault();
      self.openModal();
    });
  }

  ConfirmDialog.prototype.openModal = function () {
    const self = this;
    const title = `<span class="text-red-600"><i class="fa fa-exclamation-triangle"></i> ${this.options.title}</span>`;

    confirmDialog({
      title: title,
      message: `<p class="text-xl font-light text-gray-600">${this.options.message}</p>`,
      okLabel: this.options.label,
      cancelLabel: this.options.cancelLabel,
      onConfirm() {
        self.onConfirm();
      },
    });
  };

  ConfirmDialog.prototype.onConfirm = function () {
    // Hack to provoke a POST instead of a GET.
    const form = document.createElement("form");
    form.setAttribute("method", "POST");
    form.setAttribute("action", this.url);
    form.setAttribute("enctype", "multipart/form-data");

    // csrf
    const input1 = document.createElement("input");
    input1.setAttribute("type", "hidden");
    input1.setAttribute("name", Abilian.csrf_fieldname);
    input1.setAttribute("value", Abilian.csrf_token);
    form.appendChild(input1);

    // action value
    const input2 = document.createElement("input");
    input2.setAttribute("type", "hidden");
    input2.setAttribute("name", "__action");
    input2.setAttribute("value", "delete");
    form.appendChild(input2);

    document.body.appendChild(form);
    form.submit();
  };

  function setupDeleteConfirm(params) {
    return new ConfirmDialog($(this), params);
  }

  Abilian.registerWidgetCreator("deleteConfirm", setupDeleteConfirm);
});
