import unittest
from unittest.mock import patch, MagicMock
from src import main

class TestApp(unittest.TestCase):

    @patch('src.main.HubConnectionBuilder')
    def test_setup_sensor_hub(self, mock_hub_connection_builder):
        app = main.App()
        app.setup_sensor_hub()
        mock_hub_connection_builder.assert_called_once()

    @patch('src.main.requests.get')
    def test_send_action_to_hvac(self, mock_requests_get):
        app = main.App()
        app.HOST = "http://dummy_host"
        app.TOKEN = "dummy_token"
        app.TICKS = 10

        # Set up the mock response
        mock_response = MagicMock()
        mock_response.text = '[{"date": "2024-03-10T01:11:15.1894024+00:00", "data": "98.11"}]'  # Example JSON string representing sensor data
        mock_requests_get.return_value = mock_response

        app.send_action_to_hvac("dummy_action")
        mock_requests_get.assert_called_once_with("http://dummy_host/api/hvac/dummy_token/dummy_action/10")

    @patch('src.main.psycopg2.connect')
    def test_save_event_to_database(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.execute.return_value = None
        mock_connect.return_value.cursor.return_value = mock_cursor
        app = main.App()
        app.save_event_to_database("2024-03-09", 25.5)
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_called()
        mock_cursor.commit.assert_called()

if __name__ == '__main__':
    unittest.main()
