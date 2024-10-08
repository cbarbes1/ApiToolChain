import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
import json 

load_dotenv()

firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")

app = FirecrawlApp(api_key=firecrawl_api_key)

# Crawl a website:
crawl_status = app.async_crawl_url(
  'https://www.salisbury.edu/faculty-and-staff/', 
  params={
    'limit': 64, 
    'scrapeOptions': {'formats': ['markdown', 'html']}
  },
  poll_interval=30
)

crawl_data = crawl_status['data'][0]

crawl_data_markdown = crawl_data['markdown']

with open('test.md', 'w') as mdf:
  print(crawl_data_markdown, file=mdf)



