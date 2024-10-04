import unittest
from unittest.mock import patch, MagicMock
from functions import Crf_dict_cursor, Crf_dict

class TestApiToolChainFunctions(unittest.TestCase):

    @patch('functions.requests.get')
    def test_Crf_dict_cursor(self, mock_get):
        # Mock response for the initial request
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'message': {
                'total-results': 2,
                'items': [
                    {
                        'published': {'date-parts': [[2019]]},
                        'author': [
                            {'affiliation': [{'name': 'Salisbury University'}]}
                        ]
                    }
                ],
                'next-cursor': 'next-cursor-value'
            }
        }
        mock_get.return_value = mock_response

        result = Crf_dict_cursor(page_limit=1)

        self.assertEqual(len(result['items']), 1)
        self.assertEqual(result['next-cursor'], 'next-cursor-value')
        self.assertEqual(result['items'][0]['author'][0]['affiliation'][0]['name'], 'Salisbury University')

    @patch('functions.requests.get')
    def test_Crf_dict(self, mock_get):
        # Mock response for the request
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'message': {
                'items': [
                    {
                        'published': {'date-parts': [[2024]]},
                        'author': [
                            {'affiliation': [{'name': 'Salisbury University'}]}
                        ]
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        result = Crf_dict()

        self.assertEqual(len(result['items']), 1)
        self.assertEqual(result['items'][0]['author'][0]['affiliation'][0]['name'], 'Salisbury University')

if __name__ == '__main__':
    unittest.main()