# Copyright (c) 2012-2024, Abilian SAS

from __future__ import annotations

DAV_PROPS = [
    "creationdate",
    "displayname",
    "getcontentlanguage",
    "getcontentlength",
    "getcontenttype",
    "getetag",
    "getlastmodified",
    "lockdiscovery",
    "resourcetype",
    "source",
    "supportedlock",
]

# DAV level 1
# OPTIONS = 'GET, HEAD, COPY, MOVE, POST, PUT, PROPFIND, PROPPATCH, OPTIONS, '\
#           'MKCOL, DELETE, TRACE, REPORT'
OPTIONS = (
    "GET, HEAD, POST, PUT, DELETE, OPTIONS, TRACE, PROPFIND, "
    "PROPPATCH, MKCOL, COPY, MOVE"
)  # + ', LOCK, UNLOCK'

HTTP_CONTINUE = 100
HTTP_SWITCHING_PROTOCOLS = 101
HTTP_PROCESSING = 102

HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NON_AUTHORITATIVE_INFO = 203
HTTP_NO_CONTENT = 204
HTTP_RESET_CONTENT = 205
HTTP_PARTIAL_CONTENT = 206
HTTP_MULTI_STATUS = 207
HTTP_IM_USED = 226

HTTP_MULTIPLE_CHOICES = 300
HTTP_MOVED = 301
HTTP_FOUND = 302
HTTP_SEE_OTHER = 303
HTTP_NOT_MODIFIED = 304
HTTP_USE_PROXY = 305
HTTP_TEMP_REDIRECT = 307
HTTP_BAD_REQUEST = 400
HTTP_PAYMENT_REQUIRED = 402
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_NOT_ACCEPTABLE = 406
HTTP_PROXY_AUTH_REQUIRED = 407
HTTP_REQUEST_TIMEOUT = 408
HTTP_CONFLICT = 409
HTTP_GONE = 410
HTTP_LENGTH_REQUIRED = 411
HTTP_PRECONDITION_FAILED = 412
HTTP_REQUEST_ENTITY_TOO_LARGE = 413
HTTP_REQUEST_URI_TOO_LONG = 414
HTTP_MEDIATYPE_NOT_SUPPORTED = 415
HTTP_RANGE_NOT_SATISFIABLE = 416
HTTP_EXPECTATION_FAILED = 417
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_LOCKED = 423
HTTP_FAILED_DEPENDENCY = 424
HTTP_UPGRADE_REQUIRED = 426

HTTP_INTERNAL_ERROR = 500
HTTP_NOT_IMPLEMENTED = 501
HTTP_BAD_GATEWAY = 502
HTTP_SERVICE_UNAVAILABLE = 503
HTTP_GATEWAY_TIMEOUT = 504
HTTP_VERSION_NOT_SUPPORTED = 505
HTTP_INSUFFICIENT_STORAGE = 507
HTTP_NOT_EXTENDED = 510
