# Copyright (c) 2012-2024, Abilian SAS

""""""

from __future__ import annotations

from wtforms import TextAreaField

from abilian.core.models.comment import Comment
from abilian.i18n import _l
from abilian.web.forms import Form
from abilian.web.forms.filters import strip
from abilian.web.forms.validators import required
from abilian.web.forms.widgets import TextArea


class CommentForm(Form):
    body = TextAreaField(
        label=_l("Comment"),
        validators=[required()],
        filters=(strip,),
        widget=TextArea(rows=5, resizeable="vertical"),
    )

    class Meta:
        model = Comment
        include_primary_keys = True
        assign_required = False  # for 'id': allow None, for new records
