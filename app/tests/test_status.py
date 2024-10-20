from fastapi.testclient import TestClient
from app.main import app
import unittest

client = TestClient(app)

class TestStatus(unittest.TestCase):

    def test_if_server_is_running(self):
        response = client.get("/status")
        self.assertEqual(response.status_code, 200)