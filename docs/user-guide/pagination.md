# Pagination

There are times when you may need to paginate a query result response as the status returned contains partial content:

```json
{
    "status": "206 PARTIAL CONTENT",
    "time": "33.86 ms.",
    "hits": 479,
    "results_count": 100,
    "search on": {
        "parameter": "node",
        "river_name": "",
        "exact": "False",
        "page_number": 1,
        "page_size": 100
    },
    "results": []
}
```

Or if your request keeps returning a time out error message.

Sample request with a timeout:

```python
river_name = 'Ohio River'
query_url = f'{FTS_URL}/rivers/{river_name}'
params={'nodes': 'false', 'page_size': 100, 'page_number': 1}
response = requests.get(query_url, params=params)
```

Response:

```json
{
    "errorMessage": "2025-04-08T15:52:30.137Z c01772f8-c80b-497a-bbe9-7c77c6cdb5cf Task timed out after 5.01 seconds"
}
```

Modify the page size to 10 to return a response:

```python
river_name = 'Ohio River'
query_url = f'{FTS_URL}/rivers/{river_name}'
params={'nodes': 'false', 'page_size': 10, 'page_number': 1}
response = requests.get(query_url, params=params)
```

But that returns a status of `206 PARTIAL CONTENT`. So how do you retreive all results? See below for how to paginate results.

## paginate request

In order to retrieve all river data from FTS, you need to implement some sort of pagination. Here are two functions you can use. `paginate_fts` loops over pages of results while `query_fts` performs the actual query and return the results:

```python
def paginate_fts(query_url, page_size, page_number, exact="false", params={}):
    '''Paginate FTS query to retrieve all results.

    Parameters
    ----------
    query_url: str - URL to use to query FTS
    params: dict - Dictionary of parameters to pass to query

    Returns
    -------
    tuple: (dict of results, request URLs)
    '''

    hits = 1           # Set hits to intial value to start while loop
    results = []
    result_url = []
    while (page_size * page_number) != 0 and len(results) < hits:
        params.update({ 'page_size': page_size, 'page_number': page_number, 'exact': exact })
        response = query_fts(query_url, params)

        hits = response['hits']
        page_size = response['page_size']
        page_number = response['page_number'] + 1
        results.extend(response['results'])
        result_url.append(response['result_url'])

        print('\tpage_size: ', page_size, ', page_number: ', page_number - 1, ', hits: ', hits, ', # results: ', len(results))

    return results, result_url

def query_fts(query_url, params):
    '''Query Feature Translation Service (FTS) for reach identifers using the query_url parameter.

    Parameters
    ----------
    query_url: str - URL to use to query FTS
    params: dict - Dictionary of parameters to pass to query

    Returns
    -------
    dict of results: hits, page_size, page_number, results
    '''

    response = requests.get(query_url, params=params)
    response_json = response.json()

    if 'error' in response_json.keys() or 'hits' not in response_json.keys():
        page_size = 0
        page_number = 0
        response_json['hits'] = 0
        if 'error' in response_json.keys(): 
            response_json['status'] = response_json['error']
        else:
            response_json['status'] = response_json
        response_json['results'] = []

    hits = response_json['hits']
    if 'search on' in response_json.keys():
        page_size = response_json['search on']['page_size']
        page_number = response_json['search on']['page_number']
    else:
        page_size = 0
        page_number = 0

    return {
        'status': response_json['status'],
        'hits': hits,
        'page_size': page_size,
        'page_number': page_number,
        'results': response_json['results'],
        'result_url': response.request.url
    }
```

Sample use:

```python
# Search by basin identifier for nodes
BASIN_IDENTIFIER = '711817' # to search via basin ID, find within SWORD database
query_url = f'{FTS_URL}/rivers/node/{BASIN_IDENTIFIER}'
print(f'Searching for nodes by basin identifier ...{query_url}')

page_size = 100    # Set FTS to retrieve 100 results at a time
page_number = 1    # Set FTS to retrieve the first page of results
results, results_url = paginate_fts(query_url, page_size=page_size, page_number=page_number)

print(f'\tTotal nodes found for basin: {len(results)}')
print(f'\tRequest URL: {results_url}')
```

**Note you may need to adjust the `page_size` to reduce response time outs.**
