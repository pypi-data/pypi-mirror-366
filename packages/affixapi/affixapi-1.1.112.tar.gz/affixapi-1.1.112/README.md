# openapi-client
The affixapi.com API documentation.

# Introduction
Affix API is an OAuth 2.1 application that allows developers to access
customer data, without developers needing to manage or maintain
integrations; or collect login credentials or API keys from users for these
third party systems.

# OAuth 2.1
Affix API follows the [OAuth 2.1 spec](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-08).

As an OAuth application, Affix API handles not only both the collection of
sensitive user credentials or API keys, but also builds and maintains the
integrations with the providers, so you don't have to.

# How to obtain an access token
in order to get started, you must:
  - register a `client_id`
  - direct your user to the sign in flow  (`https://connect.affixapi.com`
    [with the appropriate query
    parameters](https://github.com/affixapi/starter-kit/tree/master/connect))
  - capture `authorization_code` we will send to your redirect URI after
    the sign in flow is complete and exchange that `authorization_code` for
    a Bearer token

# Sandbox keys (xhr mode)
### dev
```
eyJhbGciOiJFUzI1NiIsImtpZCI6Ims5RmxwSFR1YklmZWNsUU5QRVZzeFcxazFZZ0Zfbk1BWllOSGVuOFQxdGciLCJ0eXAiOiJKV1MifQ.eyJwcm92aWRlciI6InNhbmRib3giLCJzY29wZXMiOlsiLzIwMjMtMDMtMDEveGhyL2NvbXBhbnkiLCIvMjAyMy0wMy0wMS94aHIvZW1wbG95ZWUiLCIvMjAyMy0wMy0wMS94aHIvZW1wbG95ZWVzIiwiLzIwMjMtMDMtMDEveGhyL2dyb3VwcyIsIi8yMDIzLTAzLTAxL3hoci9pZGVudGl0eSIsIi8yMDIzLTAzLTAxL3hoci9wYXlydW5zIiwiLzIwMjMtMDMtMDEveGhyL3BheXJ1bnMvOnBheXJ1bl9pZCIsIi8yMDIzLTAzLTAxL3hoci90aW1lLW9mZi1iYWxhbmNlcyIsIi8yMDIzLTAzLTAxL3hoci90aW1lLW9mZi1lbnRyaWVzIiwiLzIwMjMtMDMtMDEveGhyL3RpbWVzaGVldHMiLCIvMjAyMy0wMy0wMS94aHIvd29yay1sb2NhdGlvbnMiXSwidG9rZW4iOiIzODIzNTNlMi05N2ZiLTRmMWEtOTYxYy0zZDI5OTViNzYxMTUiLCJpYXQiOjE3MTE4MTA3MTQsImlzcyI6InB1YmxpY2FwaS1pbnRlcm1lZGlhdGUuZGV2LmVuZ2luZWVyaW5nLmFmZml4YXBpLmNvbSIsInN1YiI6InhociIsImF1ZCI6IjNGREFFREY5LTFEQ0E0RjU0LTg3OTQ5RjZBLTQxMDI3NjQzIn0.zUJPaT6IxcIdr8b9iO6u-Rr5I-ohTHPYTrQGrgOFghbEbovItiwr9Wk479GnJVJc3WR8bxAwUMAE4Ul6Okdk6Q
```

#### `employees` endpoint sample:
```
curl --fail \\
  -X GET \\
  -H 'Authorization: Bearer eyJhbGciOiJFUzI1NiIsImtpZCI6Ims5RmxwSFR1YklmZWNsUU5QRVZzeFcxazFZZ0Zfbk1BWllOSGVuOFQxdGciLCJ0eXAiOiJKV1MifQ.eyJwcm92aWRlciI6InNhbmRib3giLCJzY29wZXMiOlsiLzIwMjMtMDMtMDEveGhyL2NvbXBhbnkiLCIvMjAyMy0wMy0wMS94aHIvZW1wbG95ZWUiLCIvMjAyMy0wMy0wMS94aHIvZW1wbG95ZWVzIiwiLzIwMjMtMDMtMDEveGhyL2dyb3VwcyIsIi8yMDIzLTAzLTAxL3hoci9pZGVudGl0eSIsIi8yMDIzLTAzLTAxL3hoci9wYXlydW5zIiwiLzIwMjMtMDMtMDEveGhyL3BheXJ1bnMvOnBheXJ1bl9pZCIsIi8yMDIzLTAzLTAxL3hoci90aW1lLW9mZi1iYWxhbmNlcyIsIi8yMDIzLTAzLTAxL3hoci90aW1lLW9mZi1lbnRyaWVzIiwiLzIwMjMtMDMtMDEveGhyL3RpbWVzaGVldHMiLCIvMjAyMy0wMy0wMS94aHIvd29yay1sb2NhdGlvbnMiXSwidG9rZW4iOiIzODIzNTNlMi05N2ZiLTRmMWEtOTYxYy0zZDI5OTViNzYxMTUiLCJpYXQiOjE3MTE4MTA3MTQsImlzcyI6InB1YmxpY2FwaS1pbnRlcm1lZGlhdGUuZGV2LmVuZ2luZWVyaW5nLmFmZml4YXBpLmNvbSIsInN1YiI6InhociIsImF1ZCI6IjNGREFFREY5LTFEQ0E0RjU0LTg3OTQ5RjZBLTQxMDI3NjQzIn0.zUJPaT6IxcIdr8b9iO6u-Rr5I-ohTHPYTrQGrgOFghbEbovItiwr9Wk479GnJVJc3WR8bxAwUMAE4Ul6Okdk6Q' \\
  'https://dev.api.affixapi.com/2023-03-01/xhr/employees'
```

### prod
```
eyJhbGciOiJFUzI1NiIsImtpZCI6Ims5RmxwSFR1YklmZWNsUU5QRVZzeFcxazFZZ0Zfbk1BWllOSGVuOFQxdGciLCJ0eXAiOiJKV1MifQ.eyJwcm92aWRlciI6InNhbmRib3giLCJzY29wZXMiOlsiLzIwMjMtMDMtMDEveGhyL2NvbXBhbnkiLCIvMjAyMy0wMy0wMS94aHIvZW1wbG95ZWUiLCIvMjAyMy0wMy0wMS94aHIvZW1wbG95ZWVzIiwiLzIwMjMtMDMtMDEveGhyL2dyb3VwcyIsIi8yMDIzLTAzLTAxL3hoci9pZGVudGl0eSIsIi8yMDIzLTAzLTAxL3hoci9wYXlydW5zIiwiLzIwMjMtMDMtMDEveGhyL3BheXJ1bnMvOnBheXJ1bl9pZCIsIi8yMDIzLTAzLTAxL3hoci90aW1lLW9mZi1iYWxhbmNlcyIsIi8yMDIzLTAzLTAxL3hoci90aW1lLW9mZi1lbnRyaWVzIiwiLzIwMjMtMDMtMDEveGhyL3RpbWVzaGVldHMiLCIvMjAyMy0wMy0wMS94aHIvd29yay1sb2NhdGlvbnMiXSwidG9rZW4iOiIzYjg4MDc2NC1kMGFmLTQ5ZDAtOGM5OS00YzIwYjE2MTJjOTMiLCJpYXQiOjE3MTE4MTA4NTgsImlzcyI6InB1YmxpY2FwaS1pbnRlcm1lZGlhdGUucHJvZC5lbmdpbmVlcmluZy5hZmZpeGFwaS5jb20iLCJzdWIiOiJ4aHIiLCJhdWQiOiIwOEJCMDgxRS1EOUFCNEQxNC04REY5OTIzMy02NjYxNUNFOSJ9.n3pJmmfegU21Tko_TyUyCHi4ITvfd75T8NFFTHmf1r8AI8yCUYTWdfNjyZZWcZD6z50I3Wsk2rAd8GDWXn4vlg
```

#### `employees` endpoint sample:
```
curl --fail \\
  -X GET \\
  -H 'Authorization: Bearer eyJhbGciOiJFUzI1NiIsImtpZCI6Ims5RmxwSFR1YklmZWNsUU5QRVZzeFcxazFZZ0Zfbk1BWllOSGVuOFQxdGciLCJ0eXAiOiJKV1MifQ.eyJwcm92aWRlciI6InNhbmRib3giLCJzY29wZXMiOlsiLzIwMjMtMDMtMDEveGhyL2NvbXBhbnkiLCIvMjAyMy0wMy0wMS94aHIvZW1wbG95ZWUiLCIvMjAyMy0wMy0wMS94aHIvZW1wbG95ZWVzIiwiLzIwMjMtMDMtMDEveGhyL2dyb3VwcyIsIi8yMDIzLTAzLTAxL3hoci9pZGVudGl0eSIsIi8yMDIzLTAzLTAxL3hoci9wYXlydW5zIiwiLzIwMjMtMDMtMDEveGhyL3BheXJ1bnMvOnBheXJ1bl9pZCIsIi8yMDIzLTAzLTAxL3hoci90aW1lLW9mZi1iYWxhbmNlcyIsIi8yMDIzLTAzLTAxL3hoci90aW1lLW9mZi1lbnRyaWVzIiwiLzIwMjMtMDMtMDEveGhyL3RpbWVzaGVldHMiLCIvMjAyMy0wMy0wMS94aHIvd29yay1sb2NhdGlvbnMiXSwidG9rZW4iOiIzYjg4MDc2NC1kMGFmLTQ5ZDAtOGM5OS00YzIwYjE2MTJjOTMiLCJpYXQiOjE3MTE4MTA4NTgsImlzcyI6InB1YmxpY2FwaS1pbnRlcm1lZGlhdGUucHJvZC5lbmdpbmVlcmluZy5hZmZpeGFwaS5jb20iLCJzdWIiOiJ4aHIiLCJhdWQiOiIwOEJCMDgxRS1EOUFCNEQxNC04REY5OTIzMy02NjYxNUNFOSJ9.n3pJmmfegU21Tko_TyUyCHi4ITvfd75T8NFFTHmf1r8AI8yCUYTWdfNjyZZWcZD6z50I3Wsk2rAd8GDWXn4vlg' \\
  'https://api.affixapi.com/2023-03-01/xhr/employees'
```

# Compression
We support `brotli`, `gzip`, and `deflate` compression algorithms.

To enable, pass the `Accept-Encoding` header with one or all of the values:
`br`, `gzip`, `deflate`, or `identity` (no compression)

In the response, you will receive the `Content-Encoding` response header
indicating the compression algorithm used in the data payload to enable you
to decompress the result. If the `Accept-Encoding: identity` header was
passed, no `Content-Encoding` response header is sent back, as no
compression algorithm was used.

# Webhooks
An exciting feature for HR/Payroll modes are webhooks.

If enabled, your `webhook_uri` is set on your `client_id` for the
respective environment: `dev | prod`

Webhooks are configured to make live requests to the underlying integration
1x/hr, and if a difference is detected since the last request, we will send a
request to your `webhook_uri` with this shape:

```
{

  added: <api.v20230301.Employees>[
    <api.v20230301.Employee>{
      ...,
      date_of_birth: '2010-08-06',
      display_full_name: 'Daija Rogahn',
      employee_number: '57993',
      employment_status: 'pending',
      employment_type: 'other',
      employments: [
        {
          currency: 'eur',
          effective_date: '2022-02-25',
          employment_type: 'other',
          job_title: 'Dynamic Implementation Manager',
          pay_frequency: 'semimonthly',
          pay_period: 'YEAR',
          pay_rate: 96000,
        },
      ],
      first_name: 'Daija',
      ...
    }
  ],
  removed: [],
  updated: [
    <api.v20230301.Employee>{
      ...,
      date_of_birth: '2009-11-09',
      display_full_name: 'Lourdes Stiedemann',
      employee_number: '63189',
      employment_status: 'leave',
      employment_type: 'full_time',
      employments: [
        {
          currency: 'gbp',
          effective_date: '2023-01-16',
          employment_type: 'full_time',
          job_title: 'Forward Brand Planner',
          pay_frequency: 'semimonthly',
          pay_period: 'YEAR',
          pay_rate: 86000,
        },
      ],
      first_name: 'Lourdes',
    }
  ]
}
```

the following headers will be sent with webhook requests:

```
x-affix-api-signature: ab8474e609db95d5df3adc39ea3add7a7544bd215c5c520a30a650ae93a2fba7

x-affix-api-origin:  webhooks-employees-webhook

user-agent:  affixapi.com
```

Before trusting the payload, you should sign the payload and verify the
signature matches the signature sent by the `affixapi.com` service.

This secures that the data sent to your `webhook_uri` is from the
`affixapi.com` server.

The signature is created by combining the signing secret (your
`client_secret`) with the body of the request sent using a standard
HMAC-SHA256 keyed hash.

The signature can be created via:
  - create an `HMAC` with your `client_secret`
  - update the `HMAC` with the payload
  - get the hex digest -> this is the signature

Sample `typescript` code that follows this recipe:

```
import { createHmac } from 'crypto';

export const computeSignature = ({
  str,
  signingSecret,
}: {
  signingSecret: string;
  str: string;
}): string => {
  const hmac = createHmac('sha256', signingSecret);
  hmac.update(str);
  const signature = hmac.digest('hex');

  return signature;
};
```

While verifying the Affix API signature header should be your primary
method of confirming validity, you can also whitelist our outbound webhook
static IP addresses.

```
dev:
  - 52.210.169.82
  - 52.210.38.77
  - 3.248.135.204

prod:
  - 52.51.160.102
  - 54.220.83.244
  - 3.254.213.171
```

## Rate limits
Open endpoints (not gated by an API key) (applied at endpoint level):
  - 15 requests every 1 minute (by IP address)
  - 25 requests every 5 minutes (by IP address)

Gated endpoints (require an API key) (applied at endpoint level):
  - 40 requests every 1 minute (by IP address)
  - 40 requests every 5 minutes (by `client_id`)

Things to keep in mind:
  - Open endpoints (not gated by an API key) will likely be called by your
    users, not you, so rate limits generally would not apply to you.
  - As a developer, rate limits are applied at the endpoint granularity.
    - For example, say the rate limits below are 10 requests per minute by ip.
      from that same ip, within 1 minute, you get:
      - 10 requests per minute on `/orders`,
      - another 10 requests per minute on `/items`,
      - and another 10 requests per minute on `/identity`,
      - for a total of 30 requests per minute.


This Python package is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- API version: 2023-03-01
- Package version: 1.0.0
- Build package: org.openapitools.codegen.languages.PythonClientCodegen

## Requirements.

Python >= 3.6

## Installation & Usage
### pip install

If the python package is hosted on a repository, you can install directly using:

```sh
pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git`)

Then import the package:
```python
import openapi_client
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import openapi_client
```

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import time
import openapi_client
from pprint import pprint
from openapi_client.api import 2023_03_01_api
from openapi_client.model.companies20230301_response import Companies20230301Response
from openapi_client.model.employees20230301_response import Employees20230301Response
from openapi_client.model.employment_status_not_null_not_nullable import EmploymentStatusNotNullNotNullable
from openapi_client.model.groups20230301_response import Groups20230301Response
from openapi_client.model.identity_response import IdentityResponse
from openapi_client.model.inline_response401 import InlineResponse401
from openapi_client.model.message_response import MessageResponse
from openapi_client.model.payruns20230301_response import Payruns20230301Response
from openapi_client.model.payslips20230301_response import Payslips20230301Response
from openapi_client.model.time_off_balances20230301_response import TimeOffBalances20230301Response
from openapi_client.model.time_off_entries20230301_response import TimeOffEntries20230301Response
from openapi_client.model.timesheets20230301_response import Timesheets20230301Response
from openapi_client.model.work_locations20230301_response import WorkLocations20230301Response
# Defining the host is optional and defaults to https://api.affixapi.com
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://api.affixapi.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: access-token
configuration.api_key['access-token'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['access-token'] = 'Bearer'


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = 2023_03_01_api.20230301Api(api_client)
    
    try:
        # Company
        api_response = api_instance.xhr_companies20230301()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling 20230301Api->xhr_companies20230301: %s\n" % e)
```

## Documentation for API Endpoints

All URIs are relative to *https://api.affixapi.com*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*20230301Api* | [**xhr_companies20230301**](docs/20230301Api.md#xhr_companies20230301) | **GET** /2023-03-01/xhr/company | Company
*20230301Api* | [**xhr_employees20230301**](docs/20230301Api.md#xhr_employees20230301) | **GET** /2023-03-01/xhr/employees | Employees
*20230301Api* | [**xhr_groups20230301**](docs/20230301Api.md#xhr_groups20230301) | **GET** /2023-03-01/xhr/groups | Groups
*20230301Api* | [**xhr_identity20230301**](docs/20230301Api.md#xhr_identity20230301) | **GET** /2023-03-01/xhr/identity | Identity
*20230301Api* | [**xhr_payruns20230301**](docs/20230301Api.md#xhr_payruns20230301) | **GET** /2023-03-01/xhr/payruns | Payruns
*20230301Api* | [**xhr_payslips20230301**](docs/20230301Api.md#xhr_payslips20230301) | **GET** /2023-03-01/xhr/payruns/{payrun_id} | Payslips
*20230301Api* | [**xhr_time_off_balances20230301**](docs/20230301Api.md#xhr_time_off_balances20230301) | **GET** /2023-03-01/xhr/time-off-balances | Time off balances
*20230301Api* | [**xhr_time_off_entries20230301**](docs/20230301Api.md#xhr_time_off_entries20230301) | **GET** /2023-03-01/xhr/time-off-entries | Time off entries
*20230301Api* | [**xhr_timesheets20230301**](docs/20230301Api.md#xhr_timesheets20230301) | **GET** /2023-03-01/xhr/timesheets | Timesheets
*20230301Api* | [**xhr_work_locations20230301**](docs/20230301Api.md#xhr_work_locations20230301) | **GET** /2023-03-01/xhr/work-locations | Work locations
*CoreApi* | [**providers**](docs/CoreApi.md#providers) | **GET** /providers | Providers
*ManagementApi* | [**client**](docs/ManagementApi.md#client) | **GET** /2023-03-01/management/client | Client
*ManagementApi* | [**disconnect**](docs/ManagementApi.md#disconnect) | **POST** /2023-03-01/management/disconnect | Disconnect token
*ManagementApi* | [**introspect**](docs/ManagementApi.md#introspect) | **GET** /2023-03-01/management/introspect | Inspect token
*ManagementApi* | [**token**](docs/ManagementApi.md#token) | **POST** /2023-03-01/management/token | Create token
*ManagementApi* | [**tokens**](docs/ManagementApi.md#tokens) | **GET** /2023-03-01/management/tokens | Tokens
*ManagementApi* | [**update_client**](docs/ManagementApi.md#update_client) | **POST** /2023-03-01/management/client | Update client
*XHRVerticallyIntegratedApi* | [**xhr_companies20230301**](docs/XHRVerticallyIntegratedApi.md#xhr_companies20230301) | **GET** /2023-03-01/xhr/company | Company
*XHRVerticallyIntegratedApi* | [**xhr_employees20230301**](docs/XHRVerticallyIntegratedApi.md#xhr_employees20230301) | **GET** /2023-03-01/xhr/employees | Employees
*XHRVerticallyIntegratedApi* | [**xhr_groups20230301**](docs/XHRVerticallyIntegratedApi.md#xhr_groups20230301) | **GET** /2023-03-01/xhr/groups | Groups
*XHRVerticallyIntegratedApi* | [**xhr_identity20230301**](docs/XHRVerticallyIntegratedApi.md#xhr_identity20230301) | **GET** /2023-03-01/xhr/identity | Identity
*XHRVerticallyIntegratedApi* | [**xhr_payruns20230301**](docs/XHRVerticallyIntegratedApi.md#xhr_payruns20230301) | **GET** /2023-03-01/xhr/payruns | Payruns
*XHRVerticallyIntegratedApi* | [**xhr_payslips20230301**](docs/XHRVerticallyIntegratedApi.md#xhr_payslips20230301) | **GET** /2023-03-01/xhr/payruns/{payrun_id} | Payslips
*XHRVerticallyIntegratedApi* | [**xhr_time_off_balances20230301**](docs/XHRVerticallyIntegratedApi.md#xhr_time_off_balances20230301) | **GET** /2023-03-01/xhr/time-off-balances | Time off balances
*XHRVerticallyIntegratedApi* | [**xhr_time_off_entries20230301**](docs/XHRVerticallyIntegratedApi.md#xhr_time_off_entries20230301) | **GET** /2023-03-01/xhr/time-off-entries | Time off entries
*XHRVerticallyIntegratedApi* | [**xhr_timesheets20230301**](docs/XHRVerticallyIntegratedApi.md#xhr_timesheets20230301) | **GET** /2023-03-01/xhr/timesheets | Timesheets
*XHRVerticallyIntegratedApi* | [**xhr_work_locations20230301**](docs/XHRVerticallyIntegratedApi.md#xhr_work_locations20230301) | **GET** /2023-03-01/xhr/work-locations | Work locations


## Documentation For Models

 - [AddressNoNonNullRequest](docs/AddressNoNonNullRequest.md)
 - [AddressResponse](docs/AddressResponse.md)
 - [ClientRequest](docs/ClientRequest.md)
 - [ClientResponse](docs/ClientResponse.md)
 - [Companies20230301Response](docs/Companies20230301Response.md)
 - [CompanyResponse](docs/CompanyResponse.md)
 - [CompensationHistoryNoNonNullRequest](docs/CompensationHistoryNoNonNullRequest.md)
 - [CompensationHistoryResponse](docs/CompensationHistoryResponse.md)
 - [CreateEmployeeRequest](docs/CreateEmployeeRequest.md)
 - [CreateEmployeeRequestBankAccount](docs/CreateEmployeeRequestBankAccount.md)
 - [CreateEmployeeRequestDependents](docs/CreateEmployeeRequestDependents.md)
 - [CreateEmployeeRequestEmergencyContacts](docs/CreateEmployeeRequestEmergencyContacts.md)
 - [CreateEmployeeRequestManager](docs/CreateEmployeeRequestManager.md)
 - [CurrencyNotNullRequest](docs/CurrencyNotNullRequest.md)
 - [CurrencyNotNullResponse](docs/CurrencyNotNullResponse.md)
 - [CurrencyResponse](docs/CurrencyResponse.md)
 - [DisconnectResponse](docs/DisconnectResponse.md)
 - [EmployeeResponse](docs/EmployeeResponse.md)
 - [EmployeeResponseManager](docs/EmployeeResponseManager.md)
 - [Employees20230301Response](docs/Employees20230301Response.md)
 - [EmploymentHistoryNoNonNullRequest](docs/EmploymentHistoryNoNonNullRequest.md)
 - [EmploymentHistoryResponse](docs/EmploymentHistoryResponse.md)
 - [EmploymentStatusNotNullNotNullable](docs/EmploymentStatusNotNullNotNullable.md)
 - [EmploymentStatusNotNullRequest](docs/EmploymentStatusNotNullRequest.md)
 - [EmploymentStatusResponse](docs/EmploymentStatusResponse.md)
 - [GroupNoNullEnumRequest](docs/GroupNoNullEnumRequest.md)
 - [GroupResponse](docs/GroupResponse.md)
 - [Groups20230301Response](docs/Groups20230301Response.md)
 - [GroupsNoNullEnumRequest](docs/GroupsNoNullEnumRequest.md)
 - [IdAndMessageResponse](docs/IdAndMessageResponse.md)
 - [IdentityResponse](docs/IdentityResponse.md)
 - [InlineResponse400](docs/InlineResponse400.md)
 - [InlineResponse401](docs/InlineResponse401.md)
 - [InlineResponse409](docs/InlineResponse409.md)
 - [IntrospectResponse](docs/IntrospectResponse.md)
 - [LocationNoNonNullRequest](docs/LocationNoNonNullRequest.md)
 - [LocationResponse](docs/LocationResponse.md)
 - [MessageResponse](docs/MessageResponse.md)
 - [ModeRequest](docs/ModeRequest.md)
 - [ModeResponse](docs/ModeResponse.md)
 - [PayrunResponse](docs/PayrunResponse.md)
 - [PayrunTypeResponse](docs/PayrunTypeResponse.md)
 - [Payruns20230301Response](docs/Payruns20230301Response.md)
 - [PayslipResponse](docs/PayslipResponse.md)
 - [PayslipResponseContributions](docs/PayslipResponseContributions.md)
 - [PayslipResponseDeductions](docs/PayslipResponseDeductions.md)
 - [PayslipResponseEarnings](docs/PayslipResponseEarnings.md)
 - [PayslipResponseReimbursements](docs/PayslipResponseReimbursements.md)
 - [PayslipResponseTaxes](docs/PayslipResponseTaxes.md)
 - [Payslips20230301Response](docs/Payslips20230301Response.md)
 - [PolicyTypeResponse](docs/PolicyTypeResponse.md)
 - [ProviderRequest](docs/ProviderRequest.md)
 - [ProviderResponse](docs/ProviderResponse.md)
 - [ProvidersResponse](docs/ProvidersResponse.md)
 - [ScopesRequest](docs/ScopesRequest.md)
 - [ScopesResponse](docs/ScopesResponse.md)
 - [TimeOffBalanceResponse](docs/TimeOffBalanceResponse.md)
 - [TimeOffBalances20230301Response](docs/TimeOffBalances20230301Response.md)
 - [TimeOffEntries20230301Response](docs/TimeOffEntries20230301Response.md)
 - [TimeOffEntryResponse](docs/TimeOffEntryResponse.md)
 - [TimesheetResponse](docs/TimesheetResponse.md)
 - [Timesheets20230301Response](docs/Timesheets20230301Response.md)
 - [TokenRequest](docs/TokenRequest.md)
 - [TokenResponse](docs/TokenResponse.md)
 - [TokensResponse](docs/TokensResponse.md)
 - [WorkLocations20230301Response](docs/WorkLocations20230301Response.md)


## Documentation For Authorization


## access-token

- **Type**: API key
- **API key parameter name**: Authorization
- **Location**: HTTP header


## basic

- **Type**: API key
- **API key parameter name**: Authorization
- **Location**: HTTP header


## Author

developers@affixapi.com


## Notes for Large OpenAPI documents
If the OpenAPI document is large, imports in openapi_client.apis and openapi_client.models may fail with a
RecursionError indicating the maximum recursion limit has been exceeded. In that case, there are a couple of solutions:

Solution 1:
Use specific imports for apis and models like:
- `from openapi_client.api.default_api import DefaultApi`
- `from openapi_client.model.pet import Pet`

Solution 2:
Before importing the package, adjust the maximum recursion limit as shown below:
```
import sys
sys.setrecursionlimit(1500)
import openapi_client
from openapi_client.apis import *
from openapi_client.models import *
```

