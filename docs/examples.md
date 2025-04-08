# Examples

Top-level URL to query FTS: `FTS_URL=https://fts.podaac.earthdata.nasa.gov/v1`

## SWORD

### Reaches

```python
reach_identifier = '66120000013'
query_url = f'{FTS_URL}/rivers/reach/{reach_identifier}'
response = requests.get(query_url)
```

### Nodes

```python
node_identifier = '77199000010025'
query_url = f'{FTS_URL}/rivers/node/{node_identifier}'
response = requests.get(query_url)
```

### River Name

```python
river_name = 'Ohio River'
query_url = f'{FTS_URL}/rivers/{river_name}' #if searching via river name instead
response = requests.get(query_url)
```

## USGS

### Region Partial

```python
region = 'California'
query_url = f'{FTS_URL}/region/{region}'
response = requests.get(query_url)
```

### Region Exact

```python
region = 'Woods Creek-Skykomish River'
query_url = f'{FTS_URL}/region/{region}'
params={'exact': 'true'}
response = requests.get(query_url, params=params
```

### HUC Partial

```python
huc = '18050003'
query_url = f'{FTS_URL}/huc/{huc}'
response = requests.get(query_url)
```

### HUC Exact

```python
huc = '1805000301'
query_url = f'{FTS_URL}/huc/{huc}'
params={'exact': 'true'}
response = requests.get(query_url, params=params)
```

## Paginate results

In order to retrieve all river data from FTS, you need to implement some sort of pagination. Here are two functions you can use. `paginate_fts` loops over pages of results while `query_fts` performs the actual query and return the results:

```python
def paginate_fts(query_url, exact="false", params={}):
    '''Paginate FTS query to retrieve all results.

    Parameters
    ----------
    query_url: str - URL to use to query FTS
    params: dict - Dictionary of parameters to pass to query

    Returns
    -------
    tuple: (dict of results, request URLs)
    '''

    page_size = 100    # Set FTS to retrieve 100 results at a time
    page_number = 1    # Set FTS to retrieve the first page of results
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

Example usage:

```python
FTS_URL=https://fts.podaac.earthdata.nasa.gov/v1

# Search by basin identifier for nodes
basin_identifier = '711817' # to search via basin ID, find within SWORD database
query_url = f'{FTS_URL}/rivers/node/{basin_identifier}'

print(f'Searching for nodes by basin identifier ...{query_url}')

results, results_url = paginate_fts(query_url)

print(f'\tTotal nodes found for basin: {len(results)}')
print(f'\tRequest URL: {results_url}')
```
