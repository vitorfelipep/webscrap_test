import unittest

from contracts_scraper.domain.models import ContractData, ContractItem, ResponsiblePerson


class ModelsTests(unittest.TestCase):
    def test_contract_to_dict(self):
        contract = ContractData(
            contract_number="Contrato 1/2026",
            total_value_brl="R$ 1,00",
            municipality="Palmeira",
            management_unit="Prefeitura",
            object_description="Teste",
            legal_representatives=[
                ResponsiblePerson("Responsáveis Jurídicos", "000", "Nome A", "01/01/2026", "")
            ],
            managers=[ResponsiblePerson("Gestores", "111", "Nome B", "01/01/2026", "")],
            inspectors=[ResponsiblePerson("Fiscais", "222", "Nome C", "01/01/2026", "")],
            items=[ContractItem("1", "Item", "1", "UN", "1,00", "1,00")],
        )

        data = contract.to_dict()

        self.assertEqual(data["municipality"], "Palmeira")
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["description"], "Item")


if __name__ == "__main__":
    unittest.main()
