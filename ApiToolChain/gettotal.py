

import json
from functions import Crf_dict_cursor



def get_total():
    
    data = Crf_dict_cursor(page_limit=12)['items']
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
    return data_list
get_total()