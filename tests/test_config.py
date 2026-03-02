import tempfile
import unittest
from pathlib import Path

from contracts_scraper.utils.config import AppConfig


class AppConfigTests(unittest.TestCase):
    def test_loads_properties(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "app.properties"
            config_path.write_text(
                """[portal]\ncontract_url = https://example.com\nheadless = false\ntimeout_ms = 12345\n""",
                encoding="utf-8",
            )

            cfg = AppConfig(str(config_path))

            self.assertEqual(cfg.contract_url, "https://example.com")
            self.assertFalse(cfg.headless)
            self.assertEqual(cfg.timeout_ms, 12345)

    def test_raises_for_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            AppConfig("/tmp/does-not-exist.properties")


if __name__ == "__main__":
    unittest.main()
