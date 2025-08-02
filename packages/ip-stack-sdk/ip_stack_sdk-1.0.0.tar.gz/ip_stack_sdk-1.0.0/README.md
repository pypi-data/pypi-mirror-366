
# Getting Started with IPstack

## Introduction

### **Quickstart Guide**

<video src="https://youtube.com/embed/cjP8lsqc1Y0" width="620" height="310"></video>

#### Step 1: Fork the collection

To get started quickly, you need to fork the IP Stack Postman Collection. Simply click the button below to fork it.

[<img src="https://run.pstmn.io/button.svg">](https://god.gw.postman.com/run-collection/10131015-55145132-244c-448c-8e6f-8780866e4862?action=collection/fork)

#### Step 2: Get your API Access Key

1. Go to the [IP Stack](https://ipstack.com/?utm_source=Postman&utm_medium=Referral) website and choose the right subscription plan for your particular project.
2. Get your personal API Access Key on the [Dashboard](https://ipstack.com/dashboard) to authenticate with the API. Keep it safe! You can reset it at any time in your Account Dashboard.

### Step 3: Make your first API call

IP Stack Postman collection contains all the three endpoint supported by IP Stack API.

1. Standard IP Lookup
2. Bulk IP Lookup
3. Requester Lookup

We recommend you to start with the Standard IP Lookup endpoint as it's primary endpoint. It is used to look up single IPv4 or IPv6 addresses. To call this endpoint, simply attach any IPv4 or IPv6 address to the API's base URL.

Check out all the widely used API calls with the necessary parameters in the [Standard IP Lookup folder](https://apilayer.postman.co/workspace/APILayer~2b7498b6-6d91-4fa8-817f-608441fe42a8/folder/10131015-594322f8-abae-4135-80d1-2cf544caa60b?action=share&creator=10131015&ctx=documentation).

## Install the Package

The package is compatible with Python versions `3.7+`.
Install the package from PyPi using the following pip command:

```bash
pip install ip-stack-sdk==1.0.0
```

You can also view the package at:
https://pypi.python.org/pypi/ip-stack-sdk/1.0.0

## Test the SDK

You can test the generated SDK and the server with test cases. `unittest` is used as the testing framework and `pytest` is used as the test runner. You can run the tests as follows:

Navigate to the root directory of the SDK and run the following commands

```
pip install -r test-requirements.txt
pytest
```

## Initialize the API Client

**_Note:_** Documentation for the client can be found [here.](https://www.github.com/MuHamza30/ip-stack-python-sdk/tree/1.0.0/doc/client.md)

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
| custom_query_authentication_credentials | [`CustomQueryAuthenticationCredentials`](https://www.github.com/MuHamza30/ip-stack-python-sdk/tree/1.0.0/doc/auth/custom-query-parameter.md) | The credential object for Custom Query Parameter |

The API client can be initialized as follows:

```python
from ipstack.configuration import Environment
from ipstack.http.auth.custom_query_authentication import CustomQueryAuthenticationCredentials
from ipstack.ipstack_client import IpstackClient

client = IpstackClient(
    custom_query_authentication_credentials=CustomQueryAuthenticationCredentials(
        access_key='access_key'
    ),
    environment=Environment.PRODUCTION
)
```

## Authorization

This API uses the following authentication schemes.

* [`apiKey (Custom Query Parameter)`](https://www.github.com/MuHamza30/ip-stack-python-sdk/tree/1.0.0/doc/auth/custom-query-parameter.md)

## List of APIs

* [Standard IP Lookup](https://www.github.com/MuHamza30/ip-stack-python-sdk/tree/1.0.0/doc/controllers/standard-ip-lookup.md)
* [Bulk IP Lookup](https://www.github.com/MuHamza30/ip-stack-python-sdk/tree/1.0.0/doc/controllers/bulk-ip-lookup.md)
* [Requester IP Lookup](https://www.github.com/MuHamza30/ip-stack-python-sdk/tree/1.0.0/doc/controllers/requester-ip-lookup.md)

## SDK Infrastructure

### HTTP

* [HttpResponse](https://www.github.com/MuHamza30/ip-stack-python-sdk/tree/1.0.0/doc/http-response.md)
* [HttpRequest](https://www.github.com/MuHamza30/ip-stack-python-sdk/tree/1.0.0/doc/http-request.md)

### Utilities

* [ApiHelper](https://www.github.com/MuHamza30/ip-stack-python-sdk/tree/1.0.0/doc/api-helper.md)
* [HttpDateTime](https://www.github.com/MuHamza30/ip-stack-python-sdk/tree/1.0.0/doc/http-date-time.md)
* [RFC3339DateTime](https://www.github.com/MuHamza30/ip-stack-python-sdk/tree/1.0.0/doc/rfc3339-date-time.md)
* [UnixDateTime](https://www.github.com/MuHamza30/ip-stack-python-sdk/tree/1.0.0/doc/unix-date-time.md)

