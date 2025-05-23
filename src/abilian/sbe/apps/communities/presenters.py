# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from flask_babel import lazy_gettext as _l

from abilian.core.util import BasePresenter


class CommunityPresenter(BasePresenter):
    @property
    def breadcrumbs(self):
        return [
            {"label": _l("Communities"), "path": "/communities/"},
            {"label": self._model.name},
        ]
