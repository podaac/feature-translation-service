# response

All responses have common data attributes returned and are discussed here. Please see the API Endpoint documentation for the different requests and corresponding response details.

Common response attributes:

```json
{
    "status": "200 OK",
    "time": "19.034 ms.",
    "hits": 1,
    "search on": {
        "parameter": "reach",
        "river_name": "",
        "exact": "False",
        "page_number": 1,
        "page_size": 100
    },
    "results": ["..."]
}
```

- `status`: The status of the HTTP response
- `time`: The time it took to query FTS with the request and return a response
- `hits`: The number of results returned in the response from the FTS query
- `search on`: The request and pagination details
  - `parameter`: The identifier type used in the FTS query
  - `river_name`: The river name associated with the data (if it is available)
  - `exact`: Whether an exact query was performed. FTS will be queried for the exact string defined in the request.
  - `page_number`: The page number of the results returned
  - `page_size`: The page size of the result returned
- `results`: The result returned for each request query type
