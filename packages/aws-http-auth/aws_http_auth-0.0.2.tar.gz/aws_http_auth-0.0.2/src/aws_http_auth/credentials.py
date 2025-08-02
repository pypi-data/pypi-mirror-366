from __future__ import annotations

import datetime
import logging
import os
from typing import TYPE_CHECKING
from typing import NamedTuple

if TYPE_CHECKING:
    from typing_extensions import Self

logger = logging.getLogger(__name__)


class AWSCredentials(NamedTuple):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_session_token: str

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(f'{k}=***' for k in self._asdict())})"

    @classmethod
    def from_ini_file(cls, path: str | None = None, aws_profile: str | None = None) -> Self:
        path = (
            path
            or os.getenv("AWS_SHARED_CREDENTIALS_FILE")
            or os.path.expanduser("~/.aws/credentials")
        )
        with open(path) as f:
            return cls.from_ini_file_like_string(f.read(), aws_profile=aws_profile)

    @classmethod
    def from_ini_file_like_string(cls, s: str, aws_profile: str | None = None) -> Self:
        import configparser

        config = configparser.ConfigParser()
        config.read_string(s)

        sections = config.sections()

        if not sections:
            msg = "No AWS profiles found in the provided configuration."
            raise ValueError(msg)

        aws_profile = aws_profile or os.getenv("AWS_PROFILE")

        if aws_profile in sections:
            profile = config[aws_profile or ""]

        elif aws_profile is None and len(sections) == 1:
            profile = config[sections[0]]

        else:
            msg = (
                f"No AWS profile specified and multiple profiles found: {sections}. "
                "Please specify a profile using the 'aws_profile' parameter or set the 'AWS_PROFILE' environment variable."  # noqa: E501
            )
            raise ValueError(msg)

        expiration = profile.get("token_expiration")

        if expiration:
            expiration_datetime = datetime.datetime.fromisoformat(
                expiration.replace("Z", "+00:00")
            ).replace(tzinfo=datetime.timezone.utc)
            current_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
            time_remaining = expiration_datetime - current_datetime

            if time_remaining > datetime.timedelta(minutes=1):
                logger.info(
                    "AWS Token for %s is still valid for %s minutes.",
                    aws_profile,
                    int(time_remaining.total_seconds() / 60),
                )
            else:
                logger.warning(
                    "The AWS credentiials are expired. Please refresh them for profile '%s'.",
                    aws_profile,
                )
        return cls(
            aws_access_key_id=profile.get("aws_access_key_id", ""),
            aws_secret_access_key=profile.get("aws_secret_access_key", ""),
            aws_session_token=profile.get("aws_session_token", ""),
        )
