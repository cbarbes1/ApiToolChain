# Functions Documentation

This document provides an overview and usage instructions for the functions defined in `functions.py`.

## Functions

### `Crf_dict_cursor`

```python
def Crf_dict_cursor(base_url: str = 'https://api.crossref.org/works', 
             affiliation: str = 'Salisbury University', 
             from_date: str = '2018-01-01',
             to_date: str = '2024-09-19',
             n_element: str = '1000', 
             sort_type: str = 'relevance',
             sort_ord: str = 'desc',
             cursor: str = '*',
             page_limit: int = 10
             ):
```

#### Purpose
Query the CrossRef API and cursor through the specified pages to collect data.

#### Parameters
- `base_url` (str): The base URL for the API to query.
- `affiliation` (str): The organization that the data is associated with.
- `from_date` (str): The start date range to collect data from.
- `to_date` (str): The end date range to collect data until.
- `n_element` (str): Number of elements per page.
- `sort_type` (str): The type of sort to use.
- `sort_ord` (str): The order of the sort.
- `cursor` (str): The cursor to start at.
- `page_limit` (int): The number of pages to query.

#### Returns
A dictionary containing:
- `items` (list): A list of filtered items.
- `next-cursor` (str): The cursor for the next page.

#### Example Usage
```python
result = Crf_dict_cursor(
    base_url='https://api.crossref.org/works',
    affiliation='Salisbury University',
    from_date='2018-01-01',
    to_date='2024-09-19',
    n_element='1000',
    sort_type='relevance',
    sort_ord='desc',
    cursor='*',
    page_limit=10
)
```

### `Crf_dict`

```python
def Crf_dict(base_url: str = 'https://api.crossref.org/works', 
             affiliation: str = 'Salisbury University', 
             from_date: str = '2024-01-01',
             n_element: str = '1000',
             offset: str = None, 
             ):
```

#### Purpose
Query the CrossRef API with a basic query provided by the user.

#### Parameters
- `base_url` (str): The URL with the specific endpoint.
- `affiliation` (str): The organization that the data is associated with.
- `from_date` (str): The start date range to collect data from.
- `n_element` (str): Number of elements per page.
- `offset` (str, optional): The offset for pagination.

#### Returns
A dictionary containing the API response message.

#### Example Usage
```python
result = Crf_dict(
    base_url='https://api.crossref.org/works',
    affiliation='Salisbury University',
    from_date='2024-01-01',
    n_element='1000',
    offset=None
)
```