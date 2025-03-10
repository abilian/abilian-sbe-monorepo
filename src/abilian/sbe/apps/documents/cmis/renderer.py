# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flask import render_template

if TYPE_CHECKING:
    from abilian.sbe.apps.documents.models import Document, Folder

# TEMP
ROOT = "http://localhost:5000/cmis/atompub"
XML_HEADER = "<?xml version='1.0' encoding='UTF-8'?>\n"


class Feed:
    def __init__(self, object: Folder, collection: list[Document]) -> None:
        self.object = object
        self.collection = collection

    def to_xml(self, **options: Any) -> str:
        ctx = {
            "ROOT": ROOT,
            "object": self.object,
            "collection": self.collection,
            "to_xml": to_xml,
        }
        return render_template("cmis/feed.xml", **ctx)


class Entry:
    def __init__(self, obj: Document | Folder) -> None:
        self.obj = obj

    def to_xml(self, **options: Any) -> str:
        ctx = {
            "ROOT": ROOT,
            "folder": self.obj,
            "document": self.obj,
            "options": options,
            "to_xml": to_xml,
        }

        if self.obj.sbe_type == "cmis:folder":
            result = render_template("cmis/folder.xml", **ctx)
        elif self.obj.sbe_type == "cmis:document":
            result = render_template("cmis/document.xml", **ctx)
        else:
            msg = f"Unknown base object type: {self.obj.sbe_type}"
            raise Exception(msg)

        if "no_xml_header" not in options:
            result = XML_HEADER + result

        return result


def to_xml(obj: Document | Folder, **options: Any) -> str:
    entry = Entry(obj)
    return entry.to_xml(**options)
