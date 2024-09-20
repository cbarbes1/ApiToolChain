# tests/test_module1.py
import unittest
from ApiToolChain.Wos_Api import WOS_Api_Starter
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY_S")

class TestWrapper(unittest.TestCase):

    def test_query_json(self):
        client = WOS_Api_Starter(api_key=api_key)

        print(client.query_json())

    # def test_query_params(self):
    #     client = WOS_Api_Starter(api_key=api_key)

    #     client.get_year_range()
        

if __name__ == "__main__":
    unittest.main()