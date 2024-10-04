from functions import Crf_dict_cursor
import json


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


get_year(2024)