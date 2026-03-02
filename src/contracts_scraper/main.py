import json

from contracts_scraper.services.contract_scraper import ContractScraperService
from contracts_scraper.utils.config import AppConfig


def main() -> None:
    config = AppConfig("app.properties")
    scraper = ContractScraperService(timeout_ms=config.timeout_ms)
    contract_data = scraper.scrape_contract(config.contract_url, headless=config.headless)
    print(json.dumps(contract_data.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
