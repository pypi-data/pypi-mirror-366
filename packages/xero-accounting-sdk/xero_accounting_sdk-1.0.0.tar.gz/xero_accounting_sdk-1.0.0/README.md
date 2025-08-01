
# Getting Started with Xero

## Introduction

All the endpoints on the Accounting API.

To make requests you'll need a valid access_token and xero-tenant-id in your environment variables. These can be set by following the steps in the `Xero OAuth2.0` collection.

Note: access tokens expire after 30 minutes but can be refreshed using the POST Refresh token request in the `Xero OAuth2.0` collection.

## Install the Package

The package is compatible with Python versions `3.7+`.
Install the package from PyPi using the following pip command:

```bash
pip install xero-accounting-sdk==1.0.0
```

You can also view the package at:
https://pypi.python.org/pypi/xero-accounting-sdk/1.0.0

## Test the SDK

You can test the generated SDK and the server with test cases. `unittest` is used as the testing framework and `pytest` is used as the test runner. You can run the tests as follows:

Navigate to the root directory of the SDK and run the following commands

```
pip install -r test-requirements.txt
pytest
```

## Initialize the API Client

**_Note:_** Documentation for the client can be found [here.](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/client.md)

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
| implicit_auth_credentials | [`ImplicitAuthCredentials`](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/auth/oauth-2-implicit-grant.md) | The credential object for OAuth 2 Implicit Grant |

The API client can be initialized as follows:

```python
from xero.configuration import Environment
from xero.http.auth.o_auth_2 import ImplicitAuthCredentials
from xero.xero_client import XeroClient

client = XeroClient(
    implicit_auth_credentials=ImplicitAuthCredentials(
        o_auth_client_id='OAuthClientId',
        o_auth_redirect_uri='OAuthRedirectUri'
    ),
    environment=Environment.PRODUCTION
)
```

## Authorization

This API uses the following authentication schemes.

* [`oauth2 (OAuth 2 Implicit Grant)`](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/auth/oauth-2-implicit-grant.md)

## List of APIs

* [File Name](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/file-name.md)
* [Account ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/account-id.md)
* [Batch Payment ID History](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/batch-payment-id-history.md)
* [Batch Payments](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/batch-payments.md)
* [Bank Transaction ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/bank-transaction-id.md)
* [Bank Transactions](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/bank-transactions.md)
* [Bank Transfer ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/bank-transfer-id.md)
* [Bank Transfers](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/bank-transfers.md)
* [Payment Services](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/payment-services.md)
* [Branding Theme ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/branding-theme-id.md)
* [Branding Themes](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/branding-themes.md)
* [Contact ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/contact-id.md)
* [Contact Group ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/contact-group-id.md)
* [Contact Groups](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/contact-groups.md)
* [Credit Note ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/credit-note-id.md)
* [Credit Notes](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/credit-notes.md)
* [Expense Claim ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/expense-claim-id.md)
* [Expense Claims](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/expense-claims.md)
* [Invoice ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/invoice-id.md)
* [Item ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/item-id.md)
* [Linked Transaction ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/linked-transaction-id.md)
* [Linked Transactions](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/linked-transactions.md)
* [Manual Journal ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/manual-journal-id.md)
* [Manual Journals](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/manual-journals.md)
* [Overpayment ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/overpayment-id.md)
* [Payment ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/payment-id.md)
* [Prepayment ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/prepayment-id.md)
* [Purchase Order ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/purchase-order-id.md)
* [Purchase Orders](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/purchase-orders.md)
* [Quote ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/quote-id.md)
* [Receipt ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/receipt-id.md)
* [Repeating Invoice ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/repeating-invoice-id.md)
* [Repeating Invoices](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/repeating-invoices.md)
* [Tax Rates](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/tax-rates.md)
* [Tracking Option ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/tracking-option-id.md)
* [Tracking Category ID](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/tracking-category-id.md)
* [Tracking Categories](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/tracking-categories.md)
* [Attachments](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/attachments.md)
* [Accounts](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/accounts.md)
* [History](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/history.md)
* [Contacts](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/contacts.md)
* [Currencies](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/currencies.md)
* [Employees](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/employees.md)
* [Invoices](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/invoices.md)
* [Items](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/items.md)
* [Journals](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/journals.md)
* [Organisation](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/organisation.md)
* [Overpayments](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/overpayments.md)
* [Payments](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/payments.md)
* [Prepayments](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/prepayments.md)
* [Quotes](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/quotes.md)
* [Receipts](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/receipts.md)
* [Reports](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/reports.md)
* [Options](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/options.md)
* [Users](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/users.md)
* [Misc](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/controllers/misc.md)

## SDK Infrastructure

### HTTP

* [HttpResponse](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/http-response.md)
* [HttpRequest](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/http-request.md)

### Utilities

* [ApiHelper](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/api-helper.md)
* [HttpDateTime](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/http-date-time.md)
* [RFC3339DateTime](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/rfc3339-date-time.md)
* [UnixDateTime](https://www.github.com/MuHamza30/xero-accounting-python-sdk/tree/1.0.0/doc/unix-date-time.md)

