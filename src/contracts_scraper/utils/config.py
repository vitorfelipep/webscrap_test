from configparser import ConfigParser
from pathlib import Path


class AppConfig:
    def __init__(self, path: str = "app.properties") -> None:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        parser = ConfigParser()
        parser.read(path, encoding="utf-8")
        self.contract_url = parser.get("portal", "contract_url")
        self.headless = parser.getboolean("portal", "headless", fallback=True)
        self.timeout_ms = parser.getint("portal", "timeout_ms", fallback=90000)
