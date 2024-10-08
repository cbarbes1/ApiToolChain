import os
import asyncio
import json
from dotenv import load_dotenv
from langchain_community.document_loaders import FireCrawlLoader
from langchain_openai import OpenAI


load_dotenv()

firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(
    model="gpt-3.5-turbo-instruct",
    temperature=0,
    max_retries=2,
    api_key=openai_api_key
)

def load_data(scrape_endpoint: str = 'academic-offices/science-and-technology/computer-science/faculty-and-staff.aspx'):
    params = {
        "formats": ['markdown', 'html']
    }

    loader = FireCrawlLoader(url=f"https://www.salisbury.edu/{scrape_endpoint}", mode="scrape", params=params)

    try: 
        docs = loader.load()
        return docs[0].page_content
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

def get_schools_dict():
    doc = load_data(scrape_endpoint="explore-academics/colleges-schools-and-departments.aspx")

    return doc


def get_llm_output(message: list[tuple]):
    output = llm.invoke(message)

    return output


if __name__ == "__main__":
    # messages = [
    #     ("system", "You are a helpful translator. Translate the user sentence to French."),
    #     ("human", "I love programming."),
    # ]
    # print(get_llm_output(messages))

    school_markdown = get_schools_dict()

    messages = [
        ("system", "You are a text analyzer to help a salisbury university scraper do its job. Take the input text and extract everything under the 'Majors To Meet Your Needs' section of the markdown given to you. Take that section and make each section of text an element in a list. Make sure to give me the links that are with it as well."),
        ("human", school_markdown)
    ]

    print(get_llm_output(messages))


    