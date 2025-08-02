
# Getting Started with PandaScore REST API for All Videogames

## Introduction

### Introduction

Whether you're looking to build an official Pandascore integration for your service, or you just want to build something awesome, [we can help you get started](/home).

The API works over the HTTPS protocol, and is accessed from the `api.pandascore.co` domain.

- The current endpoint is [https://api.pandascore.co](https://api.pandascore.co).
- All data is sent and received as JSON by default.
- Blank fields are included with `null` values instead of being omitted.
- All timestamps are returned in ISO-8601 format

#### About this documentation

Clicking on a query parameter like `filter` or `search` will show you the available options: ![filter](/doc/images/query_param_details.jpg)

You can also click on a response to see the detailed response schema: ![response](/doc/images/response_schema.jpg)

#### Events hierarchy

The PandaScore API allows you to access data about eSports events by using a certain structure detailed below.

**Leagues**

Leagues are the top level events. They don't have a date and represent a regular competition. A League is composed of one or several series.  
Some League of Legends leagues are: _EU LCS, NA LCS, LCK, etc._  
Some Dota 2 leagues are: _ESL One, GESC, The International, PGL, etc._

**Series**

A Serie represents an occurrence of a league event.  
The EU LCS league has two series per year: _spring 2017, summer 2017, spring 2016, summer 2016 etc._  
Some Dota2 Series examples would be: _Changsha Major, Open Bucharest, Frankfurt, i-League Invitational etc._

**Tournaments**

Tournaments groups all the matches of a serie under "stages" and "groups".  
The tournaments of the EU LCS of summer 2017 are: _Group A, Group B, Playoffs, etc._  
Some Dota 2 tournaments are: _Group A, Group B, Playoffs, etc._

**Matches**

Finally we have matches which have two players or teams (depending on the played videogame) and several games (the rounds of the match).  
Matches of the group A in the EU LCS of summer 2017 are: _G2 vs FNC, MSF vs NIP, etc._  
Matches of the group A in the ESL One, Genting tournamnet are: _Lower Round 1, Quarterfinal, Upper Final, etc._

**Please note that some matches may be listed as "TBD vs TBD" if the matchup is not announced yet, for example the date of the Final match is known but the quarterfinal is still being played.**  
![Structure](/doc/images/structure.png)

#### Formats

&lt;!-- The API currently supports the JSON format by default, as well as the XML format. Add the desired extension to your request URL in order to get that format. --&gt;
The API currently supports the JSON format by default.

Other formats may be added depending on user needs.

#### Pagination

The Pandascore API paginates all resources on the index method.

Requests that return multiple items will be paginated to 50 items by default. You can specify further pages with the `page[number]` parameter. You can also set a custom page size (up to 100) with the `page[size]` parameter.

The `Link` HTTP response header contains pagination data with `first`, `previous`, `next` and `last` raw page links when available, under the format

```
Link: &lt;https://api.pandascore.co/{Resource}?page=X+1&gt;; rel="next", &lt;https://api.pandascore.co/{Resource}?page=X-1&gt;; rel="prev", &lt;https://api.pandascore.co/{Resource}?page=1&gt;; rel="first", &lt;https://api.pandascore.co/{Resource}?page=X+n&gt;; rel="last"
```

There is also:

* A `X-Page` header field, which contains the current page.
* A `X-Per-Page` header field, which contains the current pagination length.
* A `X-Total` header field, which contains the total count of items across all pages.

#### Filtering

The `filter` query parameter can be used to filter a collection by one or several fields for one or several values. The `filter` parameter takes the field to filter as a key, and the values to filter as the value. Multiples values must be comma-separated (`,`).

For example, the following is a request for all the champions with a name matching Twitch or Brand exactly, but only with 21 armor:

```
GET /lol/champions?filter[name]=Brand,Twitch&amp;filter[armor]=21&amp;token=YOUR_ACCESS_TOKEN
```

#### Range

The `range` parameter is a hash that allows filtering fields by an interval.
Only values between the given two comma-separated bounds will be returned. The bounds are inclusive.

For example, the following is a request for all the champions with `hp` within 500 and 1000:

```
GET /lol/champions?range[hp]=500,1000&amp;token=YOUR_ACCESS_TOKEN
```

#### Search

The `search` parameter is a bit like the `filter` parameter, but it will return all results where the values **contain** the given parameter.

Note: this only works on strings.
Searching with integer values is not supported and `filter` or `range` parameters may be better suited for your needs here.

For example, to get all the champions with a name containing `"twi"`:

```
$ curl -sg -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' 'https://api.pandascore.co/lol/champions?search[name]=twi' | jq -S '.[].name'
"Twitch"
"Twisted Fate"
```

#### Sorting

All index endpoints support multiple sort fields with comma-separation (`,`); the fields are applied in the order specified.

The sort order for each field is ascending unless it is prefixed with a minus (U+002D HYPHEN-MINUS, “-“), in which case it is descending.

For example, `GET /lol/champions?sort=attackdamage,-name&amp;token=YOUR_ACCESS_TOKEN` will return all the champions sorted by attack damage.
Any champions with the same attack damage will then be sorted by their names in descending alphabetical order.

#### Rate limiting

Depending on your current plan, you will have a different rate limit. Your plan and your current request count [are available on your dashboard](https://pandascore.co/settings).

With the **free plan**, you have a limit of 1000 requests per hour, others plans have a limit of 4000 requests per hour. The number of remaining requests is available in the `X-Rate-Limit-Remaining` response header.

Your API key is included in all the examples on this page, so you can test any example right away. **Only you can see this value.**

### Authentication

The authentication on the Pandascore API works with access tokens.

All developers need to [create an account](https://pandascore.co/users/sign_in) before getting started, in order to get an access token. The access token should not be shared.

**Your token can be found and regenerated from [your dashboard](https://pandascore.co/settings).**

The access token can be passed in the URL with the `token` query string parameter, or in the `Authorization: Bearer` header field.

&lt;!-- ReDoc-Inject: &lt;security-definitions&gt; --&gt;

## Install the Package

The package is compatible with Python versions `3.7+`.
Install the package from PyPi using the following pip command:

```bash
pip install panda-score-sdk==1.0.0
```

You can also view the package at:
https://pypi.python.org/pypi/panda-score-sdk/1.0.0

## Test the SDK

You can test the generated SDK and the server with test cases. `unittest` is used as the testing framework and `pytest` is used as the test runner. You can run the tests as follows:

Navigate to the root directory of the SDK and run the following commands

```
pip install -r test-requirements.txt
pytest
```

## Initialize the API Client

**_Note:_** Documentation for the client can be found [here.](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/client.md)

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
| bearer_token_credentials | [`BearerTokenCredentials`](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/auth/oauth-2-bearer-token.md) | The credential object for OAuth 2 Bearer token |
| query_token_credentials | [`QueryTokenCredentials`](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/auth/custom-query-parameter.md) | The credential object for Custom Query Parameter |

The API client can be initialized as follows:

```python
from pandascorerestapiforallvideogames.configuration import Environment
from pandascorerestapiforallvideogames.http.auth.bearer_token import BearerTokenCredentials
from pandascorerestapiforallvideogames.http.auth.query_token import QueryTokenCredentials
from pandascorerestapiforallvideogames.pandascorerestapiforallvideogames_client import PandascorerestapiforallvideogamesClient

client = PandascorerestapiforallvideogamesClient(
    bearer_token_credentials=BearerTokenCredentials(
        access_token='AccessToken'
    ),
    query_token_credentials=QueryTokenCredentials(
        token='token'
    ),
    environment=Environment.PRODUCTION
)
```

## Authorization

This API uses the following authentication schemes.

* [`BearerToken (OAuth 2 Bearer token)`](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/auth/oauth-2-bearer-token.md)
* [`QueryToken (Custom Query Parameter)`](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/auth/custom-query-parameter.md)

## List of APIs

* [Incidents](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/controllers/incidents.md)
* [Leagues](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/controllers/leagues.md)
* [Matches](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/controllers/matches.md)
* [Players](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/controllers/players.md)
* [Series](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/controllers/series.md)
* [Teams](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/controllers/teams.md)
* [Tournaments](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/controllers/tournaments.md)
* [Videogames](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/controllers/videogames.md)

## SDK Infrastructure

### HTTP

* [HttpResponse](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/http-response.md)
* [HttpRequest](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/http-request.md)

### Utilities

* [ApiHelper](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/api-helper.md)
* [HttpDateTime](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/http-date-time.md)
* [RFC3339DateTime](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/rfc3339-date-time.md)
* [UnixDateTime](https://www.github.com/MuHamza30/panda-score-python-sdk/tree/1.0.0/doc/unix-date-time.md)

