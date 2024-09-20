import requests
import json
import math
import logging
import time
from pydantic import BaseModel, Field
from typing import Optional, Dict, List

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from requests.exceptions import RequestException, Timeout

class Meta(BaseModel):
    """
    Metadata information for the query results.
    """
    total: int = Field(..., description="Total number of results")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of results per page")

class Document(BaseModel):
    """
    Represents a single document in the query results.
    """
    uid: str = Field(..., description="Unique identifier for the document")
    title: str = Field(..., description="Title of the document")
    types: Optional[List[str]] = Field(None, description="List of types associated with the document")
    sourceType: Optional[List[str]] = Field(None, description="List of source types")
    source: Optional[Dict[str, Any]] = Field(None, description="Source information as a dictionary")
    names: Optional[Dict[str, List[Dict[str, Any]]]] = Field(
        None, description="Names associated with the document"
    )
    links: Optional[Dict[str, str]] = Field(None, description="Links related to the document")
    citations: Optional[List[Dict[str, Any]]] = Field(
        None, description="List of citations for the document"
    )
    identifiers: Optional[Dict[str, str]] = Field(
        None, description="Identifiers for the document"
    )
    keywords: Optional[Dict[str, Any]] = Field(
        None, description="Keywords associated with the document"
    )

class WosQuery(BaseModel):
    """
    Represents the complete query response containing metadata and a list of documents.
    """
    metadata: Meta = Field(..., description="Metadata of the query results")
    hits: List[Document] = Field(..., description="List of documents returned by the query")


class SearchParams(BaseModel):
    database: str = Field(...,alias="db", description="Choose the database to search from")
    query: str = Field(...,alias="q", 
                       description= ("See docs for full description, Parameters include title, identification numbers, author, doc type, etc.."))    
    limit: int = Field(default=None,alias="limit", description="The limit is how many results per page youd like to request. eg. limit = 10 and page = 1 is 10 papers per page and page 1 is the results you are requesting")
    page: int = Field(default=None,alias="page", description="The page is the page in which you want to request.")
    sortField: str = Field(default=None,alias="sortField", description="Parameters: LD - Load Date, PY - Publication Year, RS - Relevance, TC - Times Cited. Adding +D like PY+D or +A PY+A D meaning Descending, and A meaning Ascending")
    modifiedTimeSpan: str = Field(default=None,alias="modifiedTimeSpan")
    tcModifiedTimeSpan: str = Field(default=None,alias="tcModifiedTimeSpan")
    detail: str = Field(default=None,alias="detail")
    edition: str = Field(default=None,alias="edition")

class WOS_Api_Starter():
    def __init__(self, 
                 api_key: str, 
                 base_url: str = 'https://api.clarivate.com/apis/wos-starter/v1/documents', 
                 timeout: int = 30, 
                 db: str ='WOS', 
                 q: str ='OG="Salisbury University" AND DT="Article" AND PY=2021', 
                 limit: int = 10, 
                 page: int = 1, 
                 sortField: str = None, 
                 modifiedTimeSpan: str = None, 
                 tcModifiedTimeSpan: str = None, 
                 detail: str = None, 
                 edition: str = None
                 ):
        """
        Initialize the Web of Science API starter wrapper
        :param 
        Parameters:
            api_key(str): Your API key for authentication
            base_url(str): The API endpoint URL
            timeout(str): Timeout for API requests
            db (str): The database to query, default is 'WOS' (Web of Science).
            q (str): The query string used to filter the search. 
                Example: 'OG="Salisbury University" AND DT="Article" AND PY=2021', 
                where 'OG' is organization, 'DT' is document type, and 'PY' is publication year.
            limit (int): The maximum number of results per page, default is 10.
            page (int): The page number for paginated results, default is 1.
            sortField (str): Optional. The field by which to sort results, if needed.
            modifiedTimeSpan (str): Optional. Filters results by modification date range (e.g., '2020-01-01 TO 2020-12-31').
            tcModifiedTimeSpan (str): Optional. Filters results by citation count modification time span.
            detail (str): Optional. Specifies the level of detail for the response (e.g., 'full').
            edition (str): Optional. Specifies the edition of the database to query, if applicable

        """
        logging.basicConfig(filename='wos_api.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info('Initializing Web of Science API wrapper')
        self.url = base_url

        # set the api key into the header
        # set to accept json
        self.headers = {
            "X-ApiKey": api_key,
            "Accept": "application/json"
        }

        # set the base query so user can change parameters as needed basis, param query builder function will assit the user in creating a prompt
        # query parameters
        # in the OG is organization where you can input a organization to search for in affiliations
        # The DT is document type, article is what we needed
        # PY you can do a specific data or a date range ex. PY=2019-2024
        self.params = self.set_params(db=db, q=q, limit=limit, page=page, sortField=sortField, modifiedTimeSpan=modifiedTimeSpan, tcModifiedTimeSpan=tcModifiedTimeSpan, detail=detail, edition=edition)
        self.timeout = timeout

        
    
    def query_json(self):
        """
        Simple query function to use requests get function to pull needed data based on the self.params dictionary which holds all query parameters
        """
        retries = 3  # Number of retry attempts
        for attempt in range(retries):
            try:
                #print(self.params.dict())
                logging.info(f"Attempting request with params: {self.params.dict(by_alias=True, exclude_none=True)}")
                r = requests.get(self.url, headers=self.headers, params=self.params.dict(by_alias=True, exclude_none=True), timeout=self.timeout)


                # Handle rate-limiting (429 Too Many Requests)
                if r.status_code == 429:
                    retry_after = int(r.headers.get("Retry-After", 60))  # Get 'Retry-After' or default to 60 seconds
                    logging.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue  # Retry after the specified time
                if r.status_code == 200:
                    try:
                        # Try parsing the JSON response
                        doc_data = r.json()
                        logging.info("JSON parsed successfully!")
                        return WosQuery(**doc_data)
                    except json.JSONDecodeError as e:
                        print("Error parsing JSON:", e)
                        print("Raw response:", r.text)
                else:
                    logging.error(f"Error parsing JSON: {e}")
                    logging.error(f"Raw response: {r.text}")
            except (RequestException, Timeout) as e:
                logging.error(f"Request failed on attempt {attempt + 1}/{retries}: {e}")
        
            # Retry delay if not a rate-limiting issue
            time.sleep(2)
        # If all retries fail, log and return None
        logging.error(f"Failed to get a valid response after {retries} attempts.")
        return None

    def set_params(self, 
                     db: str ='WOS', 
                     q: str ='OG="OR" Salisbury University AND DT=Article AND PY=2021', 
                     limit: int = 10, 
                     page: int = 1, 
                     sortField: str = None, 
                     modifiedTimeSpan: str = None, 
                     tcModifiedTimeSpan: str = None, 
                     detail: str = None, 
                     edition: str = None):
        """
        This function sets the parameters for the api query 
        The actual query is set on each needed case since we need only a subset of what is actually here
        """
        params = {}
        params['db'] = db
        params['q'] = q
        params['limit'] = limit
        params['page'] = page
        if sortField is not None:
            params['sortField'] = sortField
        if modifiedTimeSpan is not None:
            params['modifiedTimeSpan'] = modifiedTimeSpan
        if tcModifiedTimeSpan is not None:
            params['tcModifiedTimeSpan'] = tcModifiedTimeSpan
        if detail is not None:
            params['detail'] = detail
        if edition is not None:
            params['edition'] = edition
            
        # Using the pydantic model SearchParams we verify that all query params are correctly set
        return SearchParams(**params)
    

    def get_year_range(self, 
                       start: int = 2020, 
                       end: int = 2024, 
                       author: str = None, 
                       author_id: str = None, 
                       doc_type: str = 'Article', 
                       org: str = 'Salisbury University', 
                       topic_search: str = None):
        """
        Iterates through each year and paginates through results to retrieve data for the specified year range.
        
        Parameters:
            start (int): The start year for the query.
            end (int): The end year for the query.
            author (str): Optional. Author name to filter the results.
            author_id (str): Optional. Author ID to filter the results.
            doc_type (str): Document type filter (default is 'Article').
            org (str): Organization name filter (default is 'Salisbury University').
            topic_search (str): Optional. Topic search term to filter the results.
        
        Returns:
            None. Saves the result dictionary to 'doc_dict_test.json'.
        """
        doc_dict = {}
        year_pages = {}
        total_per_page = {}
        for year in range(start, end+1):
            query = self.build_query(year=year, doc_type=doc_type, org=org)
            logging.info(f"Fetching results for year {year}...")

            # First page request
            self.params = self.set_params(db='WOS', q=query, limit=50, page=1)
            result = self.query_json()

            if not result or not result.hits:
                logging.warning(f"No results for year {year}")
                continue

            # Initialize list to hold results for the year
            doc_dict[str(year)] = [n.dict() for n in result.hits]

            # Calculate total pages
            total_pages = int(math.ceil(result.metadata.total / 50))

            year_pages[str(year)] = total_pages

            total_per_page[str(year)] = result.metadata.total
            # Fetch additional pages
            for page in range(2, total_pages + 1):
                logging.info(f"Fetching page {page} for year {year}")
                self.params = self.set_params(db='WOS', q=query, limit=50, page=page)
                result = self.query_json()

                if result and result.hits:
                    doc_dict[str(year)].extend([n.model_dump() for n in result.hits])
                    print(str(year))
                else:
                    logging.warning(f"No results for page {page} in year {year}")
            
            logging.info(f"Completed fetching results for year {year}. Total records: {len(doc_dict[str(year)])}")
        logging.info(f"Completed Setting the summary for all year.")
       
        return doc_dict
        
    def build_query(self, year: int = None, author: str = None, author_id: str = None, doc_type: str = None, org: str = None, topic_search: str = None):
        """
        Helper function to build the query string for a given year and optional filters.
        
        Parameters:
            year (int): The publication year to query.
            author (str): Optional. Author name to include in the query.
            author_id (str): Optional. Author ID to include in the query.
            doc_type (str): The type of document to query (e.g., 'Article').
            org (str): The organization to query (e.g., 'Salisbury University').
            topic_search (str): Optional. A topic search filter.
        
        Returns:
            str: A properly formatted query string.
        """
        if year is not None:
            query = f"PY={year}"
        
        if author is not None:
            query += f" AND AU={author}"

        if author_id is not None:
            query += f" AND AI={author_id}"

        if doc_type is not None:
            query += f" AND DT={doc_type}"
        
        if org is not None:
            query += f" AND OG={org}"

        if topic_search is not None:
            query += f" AND TS={topic_search}"

        logging.info(f"Generated query: {query}")
        return query
            
            
        