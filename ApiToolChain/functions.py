import time
import requests
import json
import os

def Crf_dict_cursor(base_url: str = 'https://api.crossref.org/works', 
             affiliation: str = 'Salisbury University', 
             from_date: str = '2019-01-01',
             to_date: str = '2024-09-19',
             n_element: str = '1000', 
             sort_type: str = 'relevance',
             sort_ord: str = 'desc',
             cursor: str = '*',
             page_limit: int = 10
             ):
    """
    Purpose:
        Query the crossref api and cursor through the specified 
    Parameters:
        base_url : the base url for the api we are to query
        affiliation : The organization that the data is associated with
        from_date : The start date to collect
        n_element : number of elements per page
    """
    item_list: list = []
    processed_papers: int = 0
    filtered_data: list = []
    
    # create the query url
    req_url = base_url+'?'+f"query.affiliation={affiliation}&filter=from-pub-date:{from_date}&sort={sort_type}&order={sort_ord}&rows={n_element}&cursor=*"
    # request from the api
    data = requests.get(req_url)
    data = data.json()['message']
    
    # get the total results
    total_docs = data['total-results']
    i = 1
    print("Processing API Pages.........")
    
    # loop until specified end or processed papers reaches the total docs
    while(processed_papers != total_docs and i <= page_limit):
        i+=1
        # set the next query the next-cursor moves to the next page
        req_url = base_url+'?'+f"query.affiliation={affiliation}&filter=from-pub-date:{from_date},until-pub-date:{to_date}&sort={sort_type}&order={sort_ord}&rows={n_element}&cursor={cursor}"
        data = requests.get(req_url)
        data = data.json()['message']
        
        # get the number of papers in this page
        processed_papers += len(data['items'])
        
        # loop through the items
        # if the published date is less than 2019 we have processed all papers in our range
        for item in data['items']:
            count = 0
            if item['published']['date-parts'][0][0] >= 2019:
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
                
        # add the filtered items to the list
        item_list.extend(filtered_data)
        # shift the cursor to the next page
        cursor = data['next-cursor']
        # space out the queries to avoid overloading the api
        time.sleep(3)
    print("Processing Complete")
    # return the item list and the cursor so the process can be continued this function
    return {"items": item_list,
            "next-cursor": cursor
        }


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

def Crf_Analysis(title_list = None):
    """
    Use the crossref api to pull down specified query then check if titles the user passed in are in the queried data
    Parameters:
        base_url (str) : the specific url with the endpoint needed
        query (str) : the exact query to the api
        title_list (List of titles) : *required* The list of titles the user would like to check if they exist in the exact query dataset
    """
    # the title list is required 
    if title_list is not None:
        
        data = Crf_dict()

        found_titles = []
        item_titles = [item.get('title', [''])[0] for item in data.get('items', [])]

        for title in title_list:
           if title in item_titles:
               found_titles.append(title)
            

        if found_titles == []:
            return None
        return {
            'FOUND':found_titles,
            'found_count': len(found_titles)
        }

    else:
        print('No titles Given, Please enter list of titles!')