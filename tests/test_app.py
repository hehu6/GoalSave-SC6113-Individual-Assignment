import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app import create_app


class GoalSaveAppTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_home_and_health(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["service"], "GoalSave")

    def test_config_includes_abi_and_sepolia(self):
        response = self.client.get("/api/config")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["chainId"], 11155111)
        self.assertIsInstance(data["abi"], list)

    def test_goal_validation_accepts_valid_input(self):
        deadline = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        response = self.client.post(
            "/api/validate/goal",
            json={"name": "Laptop", "targetEth": "0.75", "deadline": deadline},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["value"]["targetEth"], "0.75")

    def test_goal_validation_rejects_bad_input(self):
        response = self.client.post(
            "/api/validate/goal",
            json={"name": "", "targetEth": "-1", "deadline": "yesterday"},
        )
        self.assertEqual(response.status_code, 400)

    def test_deposit_validation_rejects_zero_and_too_many_decimals(self):
        self.assertEqual(
            self.client.post("/api/validate/deposit", json={"amountEth": "0"}).status_code,
            400,
        )
        self.assertEqual(
            self.client.post(
                "/api/validate/deposit", json={"amountEth": "0.0000000000000000001"}
            ).status_code,
            400,
        )

    def test_transaction_hash_validation_and_unconfigured_rpc(self):
        self.assertEqual(self.client.get("/api/transaction/not-a-hash").status_code, 400)
        good_hash = "0x" + "a" * 64
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.get(f"/api/transaction/{good_hash}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "unavailable")


if __name__ == "__main__":
    unittest.main()
