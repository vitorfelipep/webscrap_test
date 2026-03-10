import unittest

from contracts_scraper.services.contract_scraper import ContractScraperService


class _FakeCell:
    def __init__(self, text):
        self._text = text

    def inner_text(self):
        return self._text


class _FakeRow:
    def __init__(self, cols):
        self._cols = cols

    def locator(self, selector):
        if selector == "td":
            return _FakeCollection([_FakeCell(v) for v in self._cols])
        raise ValueError(selector)


class _FakeCollection:
    def __init__(self, data):
        self._data = data

    def all(self):
        return self._data


class _FakeButton:
    def __init__(self, cls="", disabled=None):
        self.cls = cls
        self.disabled = disabled
        self.clicked = False

    def get_attribute(self, name):
        if name == "class":
            return self.cls
        if name == "disabled":
            return self.disabled
        return None

    def click(self):
        self.clicked = True


class _FakeLocator:
    def __init__(self, rows=None, button=None, count=0):
        self._rows = rows or []
        self._button = button
        self._count = count

    @property
    def first(self):
        return self._button

    def count(self):
        return self._count

    def locator(self, selector):
        if selector == "tbody tr":
            return _FakeCollection(self._rows)
        raise ValueError(selector)


class _FakePage:
    def __init__(self, body_text="", table_rows=None, button_locator=None):
        self.body_text = body_text
        self.table_rows = table_rows or []
        self.button_locator = button_locator

    def locator(self, selector):
        if selector == "body":
            return type("Body", (), {"inner_text": lambda _self: self.body_text})()
        if "following::table[1]" in selector:
            return _FakeLocator(rows=self.table_rows, count=1 if self.table_rows else 0)
        if "following::button" in selector:
            return self.button_locator or _FakeLocator(count=0)
        return _FakeLocator(count=0)


class ContractScraperUnitTests(unittest.TestCase):
    def setUp(self):
        self.service = ContractScraperService()

    def test_read_field_value(self):
        page = _FakePage(body_text="Valor total\nR$ 99,99\nOutro campo")
        value = self.service._read_field_value(page, "Valor total")
        self.assertEqual(value, "R$ 99,99")

    def test_read_current_items_page(self):
        rows = [
            _FakeRow(["1", "Serviço", "2", "MÊS", "10,00", "20,00"]),
            _FakeRow(["total", "", "", "", "", ""]),
        ]
        page = _FakePage(table_rows=rows)
        items = self.service._read_current_items_page(page)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].description, "Serviço")

    def test_go_to_next_items_page_clicks_enabled_button(self):
        button = _FakeButton(cls="btn")
        page = _FakePage(button_locator=_FakeLocator(button=button, count=1))
        self.assertTrue(self.service._go_to_next_items_page(page))
        self.assertTrue(button.clicked)

    def test_go_to_next_items_page_stops_when_disabled(self):
        button = _FakeButton(cls="btn disabled", disabled="disabled")
        page = _FakePage(button_locator=_FakeLocator(button=button, count=1))
        self.assertFalse(self.service._go_to_next_items_page(page))


if __name__ == "__main__":
    unittest.main()
