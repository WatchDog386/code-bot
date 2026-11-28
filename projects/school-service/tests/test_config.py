"""Configuration checks for the School Records API."""

import unittest

from school_service.config import Settings


class SettingsTests(unittest.TestCase):
    def test_defaults(self):
        self.assertEqual(Settings.from_env({}), Settings())

    def test_environment_values(self):
        settings = Settings.from_env({
            "SCHOOL_HOST": "0.0.0.0",
            "SCHOOL_PORT": "8124",
            "SCHOOL_SEED_SIZE": "0",
        })
        self.assertEqual((settings.host, settings.port, settings.seed_size), ("0.0.0.0", 8124, 0))

    def test_invalid_port_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "SCHOOL_PORT"):
            Settings.from_env({"SCHOOL_PORT": "70000"})

    def test_invalid_seed_size_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "SCHOOL_SEED_SIZE"):
            Settings.from_env({"SCHOOL_SEED_SIZE": "many"})


if __name__ == "__main__":
    unittest.main()
