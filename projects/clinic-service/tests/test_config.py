"""Configuration checks for the Clinic Scheduling API."""

import unittest

from clinic_service.config import Settings


class SettingsTests(unittest.TestCase):
    def test_defaults(self):
        self.assertEqual(Settings.from_env({}), Settings())

    def test_environment_values(self):
        settings = Settings.from_env({
            "CLINIC_HOST": "0.0.0.0",
            "CLINIC_PORT": "8123",
            "CLINIC_SEED_SIZE": "0",
        })
        self.assertEqual((settings.host, settings.port, settings.seed_size), ("0.0.0.0", 8123, 0))

    def test_invalid_port_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "CLINIC_PORT"):
            Settings.from_env({"CLINIC_PORT": "70000"})

    def test_invalid_seed_size_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "CLINIC_SEED_SIZE"):
            Settings.from_env({"CLINIC_SEED_SIZE": "many"})


if __name__ == "__main__":
    unittest.main()
