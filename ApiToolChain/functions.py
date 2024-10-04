import time
import requests
import json
import os
import logging

import asyncio
import aiohttp


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Maximum number of concurrent requests allowed
MAX_CONCURRENT_REQUESTS = 2  # Limit to 2 concurrent tasks at a ti

# Semaphore to control the rate of concurrent requests
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


def Crf_dict(base_url: str = 'https://api.crossref.org/works', 
             affiliation: str = 'Salisbury University', 
             from_date: str = '2024-01-01',
             n_element: str = '1000',
             offset: str = None, 
             ):
    """
    Purpose:
        Query the crossref api with a basic query the user passes in
    Parameters:
        base_url (str) : the url with the specific endpoint
        query (str) : the exact query for the crossref api call
    """
    query=f"query.affiliation={affiliation}&rows={n_element}"

    if offset is not None:
        query+=f"&offset={offset}"
    req_url = base_url+'?'+query

    data = requests.get(req_url)

    data = data.json()

    return data['message']


def Crf_dict_cursor(base_url: str = 'https://api.crossref.org/works', 
             affiliation: str = 'Salisbury University', 
             from_date: str = '2018-01-01',
             to_date: str = '2024-09-19',
             n_element: str = '1000', 
             sort_type: str = 'relevance',
             sort_ord: str = 'desc',
             cursor: str = '*'
             ):
    """
    Purpose:
        Query the crossref api and cursor through the specified 
    Parameters:
        base_url : the base url for the api we are to query
        affiliation : The organization that the data is associated with
        from_date : The start date range to collect
        to_data : the end of the data renge
        n_element : number of elements per page
        sort_type : the type of sort to use
        sort_ord : the order of the sort
        cursor : the cursor to start at
        page_limit : the number of pages to query
    """
    logger.info("Starting Crf_dict_cursor function")
    item_list: list = []
    processed_papers: int = 0
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Rommel Center",
        "mailto": "cbarbes1@gulls.salisbury.edu",
    }
    
    # create the query url
    req_url = base_url+'?'+f"query.affiliation={affiliation}&filter=from-pub-date:{from_date},until-pub-date:{to_date}&sort={sort_type}&order={sort_ord}&rows={n_element}&cursor=*"
    logger.debug(f"Request URL: {req_url}")
    # request from the api
    try:
        data = requests.get(req_url, headers=headers)
        if data.status_code == 429:
            retry_after = int(data.headers.get("Retry-After", 60))  # Get 'Retry-After' or default to 60 seconds
            logging.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
    
    data = data.json()['message']
    
    # get the total results
    total_docs = data['total-results']
    i = 1
    logger.info(f"Processing API Pages from {from_date} to {to_date}")
    
    # loop until specified end or processed papers reaches the total docs
    while(processed_papers != total_docs):
        i+=1
        filtered_data: list = []
        # set the next query the next-cursor moves to the next page
        req_url = base_url+'?'+f"query.affiliation={affiliation}&filter=from-pub-date:{from_date},until-pub-date:{to_date}&sort={sort_type}&order={sort_ord}&rows={n_element}&cursor={cursor}"
        try:
            data = requests.get(req_url, headers=headers)

            if data.status_code == 429:
                retry_after = int(data.headers.get("Retry-After", 60))  # Get 'Retry-After' or default to 60 seconds
                logging.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                continue  # Retry after the specified time
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return 
        data = data.json()['message']
        
        # get the number of papers in this page
        processed_papers += len(data['items'])
        
        # loop through the items
        # if the published date is less than 2019 we have processed all papers in our range
        for item in data['items']:
            count = 0
            if item['published']['date-parts'][0][0] >= int(from_date.split('-')[0]):
                # go through each author
                for author in item.get('author', []):
                    # check if affiliation exists
                    if author.get('affiliation', 'ERROR') != 'ERROR':
                        for affil in author['affiliation']:
                            # check if name exists
                            if affil.get('name', 'ERROR') != 'ERROR':
                                # see if salisbury univ is included in the name string
                                if "salisbury univ" in affil.get('name').lower():
                                    count += 1
                # when there is atleast 1 affiliation save the paper
                if count != 0:
                    filtered_data.append(item)
        if filtered_data == []:
            print("No more papers to process")
            break    
        # add the filtered items to the list
        item_list.extend(filtered_data)
        # shift the cursor to the next page
        cursor = data['next-cursor']
        # space out the queries to avoid overloading the api
        time.sleep(3)
    logger.info("Processing Complete")
    # return the item list and the cursor so the process can be continued this function
    return {"items": item_list,
            "next-cursor": cursor
        }



async def Crf_dict_cursor_async(
            session: aiohttp.ClientSession,
            base_url: str = 'https://api.crossref.org/works', 
            affiliation: str = 'Salisbury University', 
            from_date: str = '2018-01-01',
            to_date: str = '2024-09-19',
            n_element: str = '1000', 
            sort_type: str = 'relevance',
            sort_ord: str = 'desc',
            cursor: str = '*',
            retries: int = 5,
            retry_delay: int = 3
            ):
    """
    Purpose:
        Query the crossref api and cursor through the specified 
    Parameters:
        base_url : the base url for the api we are to query
        affiliation : The organization that the data is associated with
        from_date : The start date range to collect
        to_data : the end of the data renge
        n_element : number of elements per page
        sort_type : the type of sort to use
        sort_ord : the order of the sort
        cursor : the cursor to start at
        page_limit : the number of pages to query
    """
    logger.info("Starting Crf_dict_cursor function")
    item_list: list = []
    processed_papers: int = 0
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Rommel Center",
        "mailto": "cbarbes1@gulls.salisbury.edu",
    }
    
    
    # run this segment asyncronously with a semaphore to avoid hitting limit
    async with semaphore:
        # create the query url
        req_url = base_url+'?'+f"query.affiliation={affiliation}&filter=from-pub-date:{from_date},until-pub-date:{to_date}&sort={sort_type}&order={sort_ord}&rows={n_element}&cursor=*"
        logger.debug(f"Request URL: {req_url}")
        num_iter = 0
        # request from the api
        # only keep requesting if the iterations is less than the number of retries
        while num_iter < retries:
            try:
                # attempt the request asyncronously
                async with session.get(req_url, headers=headers) as response:
                    # if rate limit is reached then we have some extra work to do
                    if response.status == 429:
                        # if still valid to continue then sleep and continure to next iter
                        if num_iter < retries:
                            retry_after = retry_delay
                            logger.debug(f"Hit request limit for {from_date}, retrying in {retry_after} seconds...")
                            await asyncio.sleep(retry_after)
                            num_iter+=1
                            continue
                        else: # reach limit so fail and exit
                            logging.warning(f"Exceeded max retries for {from_date}.")
                            return None
                    elif response.status == 200: # if the response is VALID
                        logging.info(f"getting data from response...... ")
                        data = await response.json()
                        break
                    else: # falal error meaning some undefined behavior
                        logging.fatal("Error: Receivee unexpected status {response.status} for {from_date}")
                        return None
            except aiohttp.ClientError as e: # actual exception thrown from aiohttp
                logger.debug(f"Nework error for {from_date}: {e}")
                return None
        else: # exceed retry
            return None  # Exceeded retries
        
    
    data = data['message'] # get the data
    
    # get the total results
    total_docs = data['total-results']
    i = 1
    logger.info(f"Processing API Pages from {from_date} to {to_date}")
    
    # loop until specified end or processed papers reaches the total docs
    while(processed_papers != total_docs):
        i+=1
        filtered_data: list = []
        # set the next query the next-cursor moves to the next page
        req_url = base_url+'?'+f"query.affiliation={affiliation}&filter=from-pub-date:{from_date},until-pub-date:{to_date}&sort={sort_type}&order={sort_ord}&rows={n_element}&cursor={cursor}"
        
        while num_iter < retries:
            try:
                async with session.get(req_url, headers=headers) as response:
                    
                    if response.status == 429:
                        if num_iter < retries:
                            retry_after = retry_delay
                            logger.debug(f"Hit request limit for {from_date}, retrying in {retry_after} seconds...")
                            await asyncio.sleep(retry_after)
                        else:
                            logging.warning(f"Exceeded max retries for {from_date}.")
                            return None
                    elif response.status == 200:
                        logging.info(f"getting data from response...... ")
                        data = await response.json()
                        break
                    else:
                        logging.fatal("Error: Receivee unexpected status {response.status} for {from_date}")
                        return None
            except aiohttp.ClientError as e:
                logger.debug(f"Nework error for {from_date}: {e}")
                return None
            num_iter+=1
            await asyncio.sleep(1)
        
        data = data['message']
        
        # get the number of papers in this page
        processed_papers += len(data['items'])
        
        # loop through the items
        # if the published date is less than 2019 we have processed all papers in our range
        for item in data['items']:
            count = 0
            if item['published']['date-parts'][0][0] >= int(from_date.split('-')[0]):
                # go through each author
                for author in item.get('author', []):
                    # check if affiliation exists
                    if author.get('affiliation', 'ERROR') != 'ERROR':
                        for affil in author['affiliation']:
                            # check if name exists
                            if affil.get('name', 'ERROR') != 'ERROR':
                                # see if salisbury univ is included in the name string
                                if "salisbury univ" in affil.get('name').lower():
                                    count += 1
                # when there is atleast 1 affiliation save the paper
                if count != 0:
                    filtered_data.append(item)
        if filtered_data == []:
            print("No more papers to process")
            break    
        # add the filtered items to the list
        item_list.extend(filtered_data)
        # shift the cursor to the next page
        cursor = data['next-cursor']
        # space out the queries to avoid overloading the api
        time.sleep(3)
    logger.info("Processing Complete")
    # return the item list and the cursor so the process can be continued this function
    return {"items": item_list,
            "next-cursor": cursor
        }

async def fetch_data_for_multiple_years():
    years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    async with aiohttp.ClientSession() as session:
        tasks = [Crf_dict_cursor_async(session, from_date=f"{year}-01-01", to_date=f"{year}-12-12") for year in years]

        results = await asyncio.gather(*tasks)

        print("All data fetched.")
        return results

def get_year(year):


    with open(f"sub-essential-data-{year}.json", 'w') as file:
        data = Crf_dict_cursor(from_date=f"{year}-01-01", to_date=f"{year}-12-12")['items']
        data_list = []
        for item in data:
            data_list.append( {
                "DOI": item.get('DOI', []), 
                "ISSN": item.get('ISSN', []), 
                "TITLE":item.get('title', []), 
                "AU": item.get('author', []), 
                "published": item.get('published', []), 
                "reference-count": item.get('reference-count', []), 
                "container-title": item.get('container-title', []), 
                "is-referenced-by-count":item.get('is-referenced-by-count', []), 
                "journal-issue":item.get('journal-issue', [])
            })
        json.dump(data_list, file, indent=4)
    print(f"Data for year {year} has been saved in essential-data-{year}.json")


if __name__ == "__main__":
    result_list = asyncio.run(fetch_data_for_multiple_years())
    with open("test.json", 'w') as file:
        json.dump(result_list, fp=file,indent=4)
    