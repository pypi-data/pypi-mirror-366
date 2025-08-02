from __future__ import annotations

import datetime
import hashlib
import hmac
from typing import TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from collections.abc import Mapping

    from aws_http_auth.credentials import AWSCredentials


def get_signature_key(
    secret_access_key: str, date_stamp: str, region_name: str, service_name: str
) -> bytes:
    k_date = hmac.new(
        ("AWS4" + secret_access_key).encode("utf-8"), date_stamp.encode("utf-8"), hashlib.sha256
    ).digest()
    k_region = hmac.new(k_date, region_name.encode("utf-8"), hashlib.sha256).digest()
    k_service = hmac.new(k_region, service_name.encode("utf-8"), hashlib.sha256).digest()
    return hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()


def sign_requests(
    *,
    creds: AWSCredentials,
    method: str,
    url: str,
    body: bytes,
    headers: Mapping[str, str],
) -> dict[str, str]:
    x_amz_target = headers.get("X-Amz-Target")
    if x_amz_target is None:
        msg = "X-Amz-Target header is required for signing requests"
        raise ValueError(msg)
    content_type = headers.get("Content-Type") or "application/x-amz-json-1.1"
    t = datetime.datetime.now(tz=datetime.timezone.utc)
    x_amz_date = t.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = t.strftime("%Y%m%d")

    parsed_url = urlparse(url)
    host = parsed_url.netloc
    service, region, *_ = host.split(".")
    canonical_uri = parsed_url.path or "/"
    canonical_querystring = str(parsed_url.query)

    canonnical_headers = (
        f"content-type:{content_type}\n"
        f"host:{host}\n"
        f"x-amz-date:{x_amz_date}\n"
        f"x-amz-target:{x_amz_target}\n"
    )

    signed_headers = "content-type;host;x-amz-date;x-amz-target"

    payload_hash = hashlib.sha256(body).hexdigest()

    canonical_request = (
        f"{method}\n"
        f"{canonical_uri}\n"
        f"{canonical_querystring}\n"
        f"{canonnical_headers}\n"
        f"{signed_headers}\n"
        f"{payload_hash}"
    )

    algorithm = "AWS4-HMAC-SHA256"
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"

    string_to_sign = (
        f"{algorithm}\n"
        f"{x_amz_date}\n"
        f"{credential_scope}\n"
        f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    )

    signing_key = get_signature_key(creds.aws_secret_access_key, date_stamp, region, service)

    signature = hmac.new(signing_key, (string_to_sign).encode("utf-8"), hashlib.sha256).hexdigest()

    authorization_header = (
        f"{algorithm} "
        f"Credential={creds.aws_access_key_id}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )

    return {
        "Content-Type": content_type,
        "X-Amz-Date": x_amz_date,
        "X-Amz-Target": x_amz_target,
        "Authorization": authorization_header,
        "X-Amz-Security-Token": creds.aws_session_token,
    }
