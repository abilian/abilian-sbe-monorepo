from __future__ import annotations

from types import FunctionType

import dramatiq


class LazyActor:
    # Intermediate object that register actor on broker an call.

    fn: FunctionType
    crontab: str | None
    kw: dict
    actor: dramatiq.Actor | None = None

    def __init__(self, fn, **kw):
        self.fn = fn
        self.crontab = kw.pop("crontab", None)
        self.kw = kw
        # self.actor = None

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.fn.__module__}.{self.fn.__name__}>"

    def __call__(self, *a, **kw):
        return self.fn(*a, **kw)

    def __getattr__(self, name):
        if not self.actor:
            raise AttributeError(name)
        return getattr(self.actor, name)

    def register(self, broker):
        self.actor = dramatiq.actor(broker=broker, **self.kw)(self.fn)

    # Next is regular actor API.

    def send(self, *a, **kw):
        assert self.actor
        return self.actor.send(*a, **kw)

    def send_with_options(self, *a, **kw):
        assert self.actor
        return self.actor.send_with_options(*a, **kw)
