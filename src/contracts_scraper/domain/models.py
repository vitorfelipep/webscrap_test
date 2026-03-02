from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any


@dataclass
class ResponsiblePerson:
    role: str
    cpf: str
    name: str
    start_date: str
    end_date: str


@dataclass
class ContractItem:
    number: str
    description: str
    quantity: str
    unit: str
    unit_value_brl: str
    total_value_brl: str


@dataclass
class ContractData:
    contract_number: str = ""
    total_value_brl: str = ""
    municipality: str = ""
    management_unit: str = ""
    object_description: str = ""
    legal_representatives: List[ResponsiblePerson] = field(default_factory=list)
    managers: List[ResponsiblePerson] = field(default_factory=list)
    inspectors: List[ResponsiblePerson] = field(default_factory=list)
    items: List[ContractItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["legal_representatives"] = [asdict(x) for x in self.legal_representatives]
        data["managers"] = [asdict(x) for x in self.managers]
        data["inspectors"] = [asdict(x) for x in self.inspectors]
        data["items"] = [asdict(x) for x in self.items]
        return data
