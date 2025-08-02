
# Getting Started with Notion API

## Introduction

Hello and welcome!

To make use of this API collection collection as it's written, please duplicate [this database template](https://www.notion.so/8e2c2b769e1d47d287b9ed3035d607ae?v=dc1b92875fb94f10834ba8d36549bd2a).

﻿Under the `Variables` tab, add your environment variables to start making requests. You will need to [create an integration](https://www.notion.so/my-integrations) to retrieve an API token. You will also need additional values, such as a database ID and page ID, which can be found in your Notion workspace or from the database template mentioned above.

For our full documentation, including sample integrations and guides, visit [developers.notion.com](https://developers.notion.com/)﻿.

Please note: Pages that are parented by a database _must_ have the same properties as the parent database. If you are not using the database template provided, the request `body` for the page endpoints included in this collection should be updated to match the properties in the parent database being used. See documentation for [Creating a page](https://developers.notion.com/reference/post-page) for more information.

To learn more about creating an access token, see our [official documentation](https://developers.notion.com/reference/create-a-token) and read our [Authorization](https://developers.notion.com/docs/authorization#step-3-send-the-code-in-a-post-request-to-the-notion-api) guide.

Need more help? Join our [developer community on Slack](https://join.slack.com/t/notiondevs/shared_invite/zt-20b5996xv-DzJdLiympy6jP0GGzu3AMg)﻿.

## Install the Package

The package is compatible with Python versions `3.7+`.
Install the package from PyPi using the following pip command:

```bash
pip install notion-pypi==1.0.0
```

You can also view the package at:
https://pypi.python.org/pypi/notion-pypi/1.0.0

## Test the SDK

You can test the generated SDK and the server with test cases. `unittest` is used as the testing framework and `pytest` is used as the test runner. You can run the tests as follows:

Navigate to the root directory of the SDK and run the following commands

```
pip install -r test-requirements.txt
pytest
```

## Initialize the API Client

**_Note:_** Documentation for the client can be found [here.](https://www.github.com/MuHamza30/notion-python-sdk-pypi/tree/1.0.0/doc/client.md)

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
| bearer_auth_credentials | [`BearerAuthCredentials`](https://www.github.com/MuHamza30/notion-python-sdk-pypi/tree/1.0.0/doc/auth/oauth-2-bearer-token.md) | The credential object for OAuth 2 Bearer token |

The API client can be initialized as follows:

```python
from notionapi.configuration import Environment
from notionapi.http.auth.o_auth_2 import BearerAuthCredentials
from notionapi.notionapi_client import NotionapiClient

client = NotionapiClient(
    bearer_auth_credentials=BearerAuthCredentials(
        access_token='AccessToken'
    ),
    environment=Environment.PRODUCTION
)
```

## Authorization

This API uses the following authentication schemes.

* [`bearerAuth (OAuth 2 Bearer token)`](https://www.github.com/MuHamza30/notion-python-sdk-pypi/tree/1.0.0/doc/auth/oauth-2-bearer-token.md)

## List of APIs

* [Users](https://www.github.com/MuHamza30/notion-python-sdk-pypi/tree/1.0.0/doc/controllers/users.md)
* [Databases](https://www.github.com/MuHamza30/notion-python-sdk-pypi/tree/1.0.0/doc/controllers/databases.md)
* [Pages](https://www.github.com/MuHamza30/notion-python-sdk-pypi/tree/1.0.0/doc/controllers/pages.md)
* [Blocks](https://www.github.com/MuHamza30/notion-python-sdk-pypi/tree/1.0.0/doc/controllers/blocks.md)
* [Search](https://www.github.com/MuHamza30/notion-python-sdk-pypi/tree/1.0.0/doc/controllers/search.md)
* [Comments](https://www.github.com/MuHamza30/notion-python-sdk-pypi/tree/1.0.0/doc/controllers/comments.md)

## SDK Infrastructure

### HTTP

* [HttpResponse](https://www.github.com/MuHamza30/notion-python-sdk-pypi/tree/1.0.0/doc/http-response.md)
* [HttpRequest](https://www.github.com/MuHamza30/notion-python-sdk-pypi/tree/1.0.0/doc/http-request.md)

### Utilities

* [ApiHelper](https://www.github.com/MuHamza30/notion-python-sdk-pypi/tree/1.0.0/doc/api-helper.md)
* [HttpDateTime](https://www.github.com/MuHamza30/notion-python-sdk-pypi/tree/1.0.0/doc/http-date-time.md)
* [RFC3339DateTime](https://www.github.com/MuHamza30/notion-python-sdk-pypi/tree/1.0.0/doc/rfc3339-date-time.md)
* [UnixDateTime](https://www.github.com/MuHamza30/notion-python-sdk-pypi/tree/1.0.0/doc/unix-date-time.md)

