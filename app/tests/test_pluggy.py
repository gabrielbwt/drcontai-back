from fastapi.testclient import TestClient
from app.main import app
import unittest

class TestPluggy(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.id_item = ''

    def test_categories_pluggy(self):
        response = self.client.get("/pluggy/categories")
        self.assertEqual(response.status_code, 200)

    def test_connect_pluggy(self):
        response = self.client.get("/pluggy/connect")
        self.assertEqual(response.status_code, 200)

    def test_transactions_pluggy(self):
        response = self.client.get(f"/pluggy/transactions/{self.id_item}")
        self.assertEqual(response.status_code, 200)

    def test_informations_pluggy(self):
        response = self.client.get(
            f"/pluggy/informations/{self.id_item}?from=2024-01-01&to=2024-10-15"
        )
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
