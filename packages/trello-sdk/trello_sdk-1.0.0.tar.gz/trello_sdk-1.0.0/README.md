
# Getting Started with Trello

## Introduction

This document describes the REST API of Trello as published by Trello.com.

- <a href='https://trello.com/docs/index.html' target='_blank'>Official Documentation</a>
- <a href='https://trello.com/docs/api' target='_blank'>The HTML pages that were scraped in order to generate this specification.</a>

Find out more here: [https://developers.trello.com](https://developers.trello.com)

## Install the Package

The package is compatible with Python versions `3.7+`.
Install the package from PyPi using the following pip command:

```bash
pip install trello-sdk==1.0.0
```

You can also view the package at:
https://pypi.python.org/pypi/trello-sdk/1.0.0

## Initialize the API Client

**_Note:_** Documentation for the client can be found [here.](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/client.md)

The following parameters are configurable for the API Client:

| Parameter | Type | Description |
|  --- | --- | --- |
| http_client_instance | `HttpClient` | The Http Client passed from the sdk user for making requests |
| override_http_client_configuration | `bool` | The value which determines to override properties of the passed Http Client from the sdk user |
| http_call_back | `HttpCallBack` | The callback value that is invoked before and after an HTTP call is made to an endpoint |
| timeout | `float` | The value to use for connection timeout. <br> **Default: 60** |
| max_retries | `int` | The number of times to retry an endpoint call if it fails. <br> **Default: 0** |
| backoff_factor | `float` | A backoff factor to apply between attempts after the second try. <br> **Default: 2** |
| retry_statuses | `Array of int` | The http statuses on which retry is to be done. <br> **Default: [408, 413, 429, 500, 502, 503, 504, 521, 522, 524]** |
| retry_methods | `Array of string` | The http methods on which retry is to be done. <br> **Default: ['GET', 'PUT']** |
| api_key_credentials | [`ApiKeyCredentials`](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/auth/custom-query-parameter.md) | The credential object for Custom Query Parameter |
| api_token_credentials | [`ApiTokenCredentials`](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/auth/custom-query-parameter-1.md) | The credential object for Custom Query Parameter |

The API client can be initialized as follows:

```python
from trello.configuration import Environment
from trello.http.auth.api_key import ApiKeyCredentials
from trello.http.auth.api_token import ApiTokenCredentials
from trello.trello_client import TrelloClient

client = TrelloClient(
    api_key_credentials=ApiKeyCredentials(
        key='key'
    ),
    api_token_credentials=ApiTokenCredentials(
        token='token'
    ),
    environment=Environment.PRODUCTION
)
```

## Authorization

This API uses the following authentication schemes.

* [`api_key (Custom Query Parameter)`](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/auth/custom-query-parameter.md)
* [`api_token (Custom Query Parameter)`](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/auth/custom-query-parameter-1.md)

## List of APIs

* [Action](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/controllers/action.md)
* [Batch](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/controllers/batch.md)
* [Board](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/controllers/board.md)
* [Card](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/controllers/card.md)
* [Checklist](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/controllers/checklist.md)
* [Label](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/controllers/label.md)
* [List](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/controllers/list.md)
* [Member](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/controllers/member.md)
* [Notification](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/controllers/notification.md)
* [Organization](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/controllers/organization.md)
* [Search](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/controllers/search.md)
* [Session](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/controllers/session.md)
* [Token](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/controllers/token.md)
* [Type](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/controllers/type.md)
* [Webhook](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/controllers/webhook.md)

## SDK Infrastructure

### HTTP

* [HttpResponse](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/http-response.md)
* [HttpRequest](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/http-request.md)

### Utilities

* [ApiHelper](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/api-helper.md)
* [HttpDateTime](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/http-date-time.md)
* [RFC3339DateTime](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/rfc3339-date-time.md)
* [UnixDateTime](https://www.github.com/MuHamza30/trello-python-sdk/tree/1.0.0/doc/unix-date-time.md)

