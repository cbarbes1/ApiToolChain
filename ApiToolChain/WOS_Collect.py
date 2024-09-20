from Wos_Api import WOS_Api_Starter
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY_S")

client = WOS_Api_Starter(api_key=api_key)

years = client.get_year_range(end=2020)

with open('DOI_list.txt', 'w') as file:
    for key, value in years.items():
        for item in value:
            if item['identifiers'].get('doi', 'ERROR') != 'ERROR':
                print(item['identifiers']['doi'], '\n', file=file)
                print(item['title'], '\n', file=file)
            elif item['identifiers'].get('uid', 'ERROR') != 'ERROR':
                print(item['identifiers']['uid'], '\n', file=file)
                print(item['title'], '\n', file=file)