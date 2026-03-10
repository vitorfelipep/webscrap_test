from __future__ import annotations

import re
from typing import List, Set
from urllib.parse import urlparse


from typing import TYPE_CHECKING

from contracts_scraper.domain.models import ContractData, ContractItem, ResponsiblePerson

if TYPE_CHECKING:
    from playwright.sync_api import Page


from playwright.sync_api import Page, sync_playwright



class ContractScraperService:
    def __init__(self, timeout_ms: int = 90000) -> None:
        self.timeout_ms = timeout_ms

    def scrape_contract(self, url: str, headless: bool = True) -> ContractData:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=headless)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=self.timeout_ms)
            page.wait_for_timeout(1500)

            data = ContractData(
                contract_number=self._read_contract_number(page),
                total_value_brl=self._read_field_value(page, "Valor total"),
                municipality=self._infer_municipality(page, url),
                management_unit=self._read_field_value(page, "Unidade gestora:"),
                object_description=self._read_field_value(page, "Objeto:"),
                legal_representatives=self._read_responsibles(page, "Responsáveis Jurídicos"),
                managers=self._read_responsibles(page, "Gestores"),
                inspectors=self._read_responsibles(page, "Fiscais"),
                items=self._read_items_with_pagination(page),
            )

            browser.close()
            return data

    def _read_contract_number(self, page: Page) -> str:
        text = page.locator("text=/Contrato\s+\d+/i").first.inner_text(timeout=5000)
        return text.strip()

    def _read_field_value(self, page: Page, label: str) -> str:
        body = page.locator("body").inner_text()
        pattern = rf"{re.escape(label)}\s*\n([^\n]+)"
        match = re.search(pattern, body, flags=re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _infer_municipality(self, page: Page, url: str) -> str:
        title = page.locator("text=/Prefeitura Municipal de/i").first
        if title.count() > 0:
            return title.inner_text().replace("Prefeitura Municipal de", "").strip()
        try:
            parsed = urlparse(url)
            fragment = parsed.fragment
            parts = fragment.split("/")
            return parts[1].strip().capitalize() if len(parts) > 1 else ""
        except Exception:
            return ""

    def _read_responsibles(self, page: Page, section_title: str) -> List[ResponsiblePerson]:
        rows = []
        table = page.locator(f"xpath=//h3[contains(normalize-space(), '{section_title}')]/following::table[1]")
        if table.count() == 0:
            return rows

        for tr in table.locator("tbody tr").all():
            cols = [c.inner_text().strip() for c in tr.locator("td").all()]
            if len(cols) >= 4:
                rows.append(
                    ResponsiblePerson(
                        role=section_title,
                        cpf=cols[0],
                        name=cols[1],
                        start_date=cols[2],
                        end_date=cols[3],
                    )
                )
        return rows

    def _read_items_with_pagination(self, page: Page) -> List[ContractItem]:
        items: List[ContractItem] = []
        seen_keys: Set[str] = set()

        while True:
            current_rows = self._read_current_items_page(page)
            for item in current_rows:
                key = f"{item.number}-{item.description}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    items.append(item)

            if not self._go_to_next_items_page(page):
                break
            page.wait_for_timeout(800)

        return items

    def _read_current_items_page(self, page: Page) -> List[ContractItem]:
        table = page.locator("xpath=//h3[contains(normalize-space(), 'Itens')]/following::table[1]")
        if table.count() == 0:
            return []

        rows: List[ContractItem] = []
        for tr in table.locator("tbody tr").all():
            cols = [c.inner_text().strip() for c in tr.locator("td").all()]
            if len(cols) >= 6 and cols[0].isdigit():
                rows.append(
                    ContractItem(
                        number=cols[0],
                        description=cols[1],
                        quantity=cols[2],
                        unit=cols[3],
                        unit_value_brl=cols[4],
                        total_value_brl=cols[5],
                    )
                )
        return rows

    def _go_to_next_items_page(self, page: Page) -> bool:
        candidates = [
            "xpath=//h3[contains(normalize-space(), 'Itens')]/following::button[contains(@aria-label, 'Próxima')][1]",
            "xpath=//h3[contains(normalize-space(), 'Itens')]/following::button[contains(@ng-click, 'next')][1]",
            "xpath=//h3[contains(normalize-space(), 'Itens')]/following::button[.//i[contains(@class,'fa-chevron-right')]][1]",
        ]

        for selector in candidates:
            button = page.locator(selector)
            if button.count() == 0:
                continue
            class_attr = button.first.get_attribute("class") or ""
            disabled_attr = button.first.get_attribute("disabled")
            is_disabled = ("disabled" in class_attr.lower()) or (disabled_attr is not None)
            if is_disabled:
                return False
            button.first.click()
            return True

        return False
