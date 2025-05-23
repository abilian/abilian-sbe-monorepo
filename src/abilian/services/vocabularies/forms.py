# Copyright (c) 2012-2024, Abilian SAS

""""""

from __future__ import annotations

import bleach
from wtforms import BooleanField, IntegerField, StringField
from wtforms.widgets import HiddenInput

from abilian.i18n import _l
from abilian.web.forms import ModelForm
from abilian.web.forms.filters import strip
from abilian.web.forms.validators import required

ALLOWED_TAGS = {"b", "i", "del", "s", "u", "small", "strong", "em"}
ALLOWED_ATTRIBUTES: dict[str, list[str]] = {}


class EditForm(ModelForm):
    label = StringField(
        _l("Label"),
        description=_l("allowed tags: %(tags)s", tags=", ".join(ALLOWED_TAGS)),
        filters=(strip,),
        validators=[required()],
    )
    default = BooleanField(_l("Default"), default=False)
    active = BooleanField(_l("Active"), default=True)

    def validate_label(self, field) -> None:
        field.data = bleach.clean(
            field.data, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True
        )


class ListEditForm(EditForm):
    id = IntegerField(widget=HiddenInput())
    position = IntegerField(widget=HiddenInput())
