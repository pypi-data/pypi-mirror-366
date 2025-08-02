
# Getting Started with Bitly API

## Introduction

Bitly's Postman Collection was last updated 5/01/22. Please visit our Developer Docs for the most up-to-date information: [https://dev.bitly.com/](https://dev.bitly.com/)

Contact Support:  
[https://bitly.is/API-support](https://bitly.is/API-support)

## Install the Package

The package is compatible with Python versions `3.7+`.
Install the package from PyPi using the following pip command:

```bash
pip install bitly-api-sdk==1.0.0
```

You can also view the package at:
https://pypi.python.org/pypi/bitly-api-sdk/1.0.0

## Test the SDK

You can test the generated SDK and the server with test cases. `unittest` is used as the testing framework and `pytest` is used as the test runner. You can run the tests as follows:

Navigate to the root directory of the SDK and run the following commands

```
pip install -r test-requirements.txt
pytest
```

## Initialize the API Client

**_Note:_** Documentation for the client can be found [here.](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/client.md)

The following parameters are configurable for the API Client:

| Parameter | Type | Description |
|  --- | --- | --- |
| environment | `Environment` | The API environment. <br> **Default: `Environment.PRODUCTION`** |
| http_client_instance | `HttpClient` | The Http Client passed from the sdk user for making requests |
| override_http_client_configuration | `bool` | The value which determines to override properties of the passed Http Client from the sdk user |
| http_call_back | `HttpCallBack` | The callback value that is invoked before and after an HTTP call is made to an endpoint |
| timeout | `float` | The value to use for connection timeout. <br> **Default: 60** |
| max_retries | `int` | The number of times to retry an endpoint call if it fails. <br> **Default: 0** |
| backoff_factor | `float` | A backoff factor to apply between attempts after the second try. <br> **Default: 2** |
| retry_statuses | `Array of int` | The http statuses on which retry is to be done. <br> **Default: [408, 413, 429, 500, 502, 503, 504, 521, 522, 524]** |
| retry_methods | `Array of string` | The http methods on which retry is to be done. <br> **Default: ['GET', 'PUT']** |
| bearer_auth_credentials | [`BearerAuthCredentials`](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/auth/oauth-2-bearer-token.md) | The credential object for OAuth 2 Bearer token |

The API client can be initialized as follows:

```python
from bitlyapi.bitlyapi_client import BitlyapiClient
from bitlyapi.configuration import Environment
from bitlyapi.http.auth.o_auth_2 import BearerAuthCredentials

client = BitlyapiClient(
    bearer_auth_credentials=BearerAuthCredentials(
        access_token='AccessToken'
    ),
    environment=Environment.PRODUCTION
)
```

## Authorization

This API uses the following authentication schemes.

* [`bearer (OAuth 2 Bearer token)`](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/auth/oauth-2-bearer-token.md)

## List of APIs

* [Organizationguid](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/organizationguid.md)
* [Campaignguid](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/campaignguid.md)
* [Groupguid](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/groupguid.md)
* [Webhookguid](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/webhookguid.md)
* [Custombitlink](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/custombitlink.md)
* [Custombitlinks](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/custombitlinks.md)
* [Channelguid](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/channelguid.md)
* [Organizations](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/organizations.md)
* [Campaigns](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/campaigns.md)
* [Preferences](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/preferences.md)
* [Bitlinks](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/bitlinks.md)
* [Groups](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/groups.md)
* [Clicks](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/clicks.md)
* [Bitlink](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/bitlink.md)
* [Webhooks](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/webhooks.md)
* [User](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/user.md)
* [Channels](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/channels.md)
* [Misc](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/controllers/misc.md)

## SDK Infrastructure

### HTTP

* [HttpResponse](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/http-response.md)
* [HttpRequest](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/http-request.md)

### Utilities

* [ApiHelper](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/api-helper.md)
* [HttpDateTime](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/http-date-time.md)
* [RFC3339DateTime](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/rfc3339-date-time.md)
* [UnixDateTime](https://www.github.com/MuHamza30/bitly-api-python-sdk/tree/1.0.0/doc/unix-date-time.md)

