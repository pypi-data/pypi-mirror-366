from __future__ import annotations

import sys

if sys.platform == "emscripten":
    try:
        import pyodide_http

        pyodide_http.patch_all()

    except ImportError:
        msg = (
            "pyodide_http is required for AWSV4SignerAuth to work in Pyodide. "
            "Please install it using 'micropip.install(\"pyodide-http\")'."
        )
        raise ImportError(msg) from None


from typing import TYPE_CHECKING
from typing import cast

from aws_http_auth.signer import sign_requests

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import TypeVar

    import httpx
    import requests
    from typing_extensions import TypeIs

    from aws_http_auth.credentials import AWSCredentials

    T = TypeVar("T", bound="httpx.Request | requests.PreparedRequest")

try:
    from requests.auth import AuthBase
except ImportError:
    AuthBase = object  # type: ignore[misc,assignment]


def is_prepared_request(
    obj: httpx.Request | requests.PreparedRequest,
) -> TypeIs[requests.PreparedRequest]:
    return obj.__class__.__name__ == "PreparedRequest"


class AWSV4SignerAuth(AuthBase):  # pyright: ignore[reportGeneralTypeIssues] # pyrefly: ignore[invalid-inheritance]
    def __init__(self, credentials: AWSCredentials) -> None:
        self.credentials = credentials

    def __call__(self, r: T) -> T:
        creds = self.credentials
        method = r.method or "GET"
        url = str(r.url)
        body: bytes
        if is_prepared_request(r):  # noqa: SIM108
            body = r.body  # type: ignore[assignment]
        else:
            body = cast("httpx.Request", r).content
        headers: Mapping[str, str] = r.headers  # pyrefly: ignore[bad-assignment]
        signed_headers = sign_requests(
            creds=creds,
            method=method,
            url=url,
            body=body,
            headers=headers,
        )

        for key, value in signed_headers.items():
            r.headers[key] = value  # pyrefly: ignore[missing-attribute]

        return r
