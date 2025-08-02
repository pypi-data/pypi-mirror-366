# aws-http-auth

[![PyPI - Version](https://img.shields.io/pypi/v/aws-http-auth.svg)](https://pypi.org/project/aws-http-auth)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aws-http-auth.svg)](https://pypi.org/project/aws-http-auth)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/FlavioAmurrioCS/aws-http-auth/main.svg)](https://results.pre-commit.ci/latest/github/FlavioAmurrioCS/aws-http-auth/main)

Lightweight AWS SigV4 signing and HTTP authentication for httpx, requests, and raw HTTP clients—without the weight of boto3.

-----

## Features

- 🚀 **Lightweight**: No heavy dependencies like boto3—just pure AWS SigV4 signing
- 🔗 **Universal**: Works with `requests`, `httpx`, and any HTTP client that supports auth handlers
- 🔑 **Flexible credentials**: Load from AWS credentials file, environment variables, or provide directly
- 🎯 **Zero config**: Automatically detects AWS regions and services from URLs
- 🌐 **Pyodide compatible**: Works in browser environments with WebAssembly
- 📦 **Type safe**: Full type hints for better development experience

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
  - [Using requests](#using-requests)
  - [Using httpx](#using-httpx)
  - [Different credential sources](#different-credential-sources)
- [Credential Loading](#credential-loading)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Installation

```console
pip install aws-http-auth
```

## Usage Examples

### Using requests

```python
from aws_http_auth.credentials import AWSCredentials
from aws_http_auth.http_auth import AWSV4SignerAuth
import requests

creds = AWSCredentials.from_ini_file("~/.aws/credentials")
auth = AWSV4SignerAuth(credentials=creds)

session = requests.Session()
session.auth = auth

response = session.request(
    method="POST",
    url="https://secretsmanager.us-east-1.amazonaws.com/",
    json={
        "SecretId": "MyTestDatabaseSecret",
    },
    headers={
        "Content-Type": "application/x-amz-json-1.1",
        "X-Amz-Target": "secretsmanager.GetSecretValue",
    },
)
```

### Using httpx

```python
from aws_http_auth.credentials import AWSCredentials
from aws_http_auth.http_auth import AWSV4SignerAuth
import httpx

creds = AWSCredentials.from_ini_file()
auth = AWSV4SignerAuth(credentials=creds)

async with httpx.AsyncClient(auth=auth) as client:
    response = await client.post(
        "https://secretsmanager.us-east-1.amazonaws.com/",
        json={
            "SecretId": "MyTestDatabaseSecret",
        },
        headers={
            "Content-Type": "application/x-amz-json-1.1",
            "X-Amz-Target": "secretsmanager.GetSecretValue",
        },
    )
```

### Profile Selection

- If no profile is specified, the library uses the `AWS_PROFILE` environment variable
- If only one profile exists in the credentials file, it's used automatically
- If multiple profiles exist and none is specified, an error is raised

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

`aws-http-auth` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
