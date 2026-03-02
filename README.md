# WebScrap Test - Contratos Públicos (Portal e-Pública)

Aplicação Python para extrair dados de contratos no Portal da Transparência e-Pública, incluindo:

- Valor total do contrato
- Município
- Unidade gestora
- Responsáveis jurídicos
- Gestores
- Fiscais
- Itens do contrato com paginação

## Estrutura do projeto

```text
src/contracts_scraper/
  domain/models.py             # Entidades de domínio (ContractData, ContractItem, ResponsiblePerson)
  services/contract_scraper.py # Lógica de scraping e paginação
  utils/config.py              # Leitura de app.properties
  main.py                      # Ponto de entrada
tests/
  test_config.py               # Testes unitários de configuração
  test_models.py               # Testes de serialização de domínio
  test_service_unit.py         # Testes unitários da lógica do scraper (sem browser)
app.properties                 # Configuração da URL e parâmetros da execução
```

## Configuração

Edite `app.properties`:

```ini
[portal]
contract_url = https://transparencia.e-publica.net/epublica-portal/#/palmeira/portal/compras/contratoView?params=%7B%22id%22:%22MV8yMDMy%22,%22mode%22:%22INFO%22%7D
headless = true
timeout_ms = 90000
```

## Como testar

### 1) Testes unitários (não dependem de Playwright)

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

### 2) Teste de execução real do scraper (integração)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
PYTHONPATH=src python -m contracts_scraper.main
```

A execução imprime JSON no terminal com os dados extraídos do contrato.

## Observações

- O portal é renderizado com JavaScript, por isso o scraper usa Playwright.
- A paginação dos itens é tratada buscando o botão de próxima página na seção "Itens".
- Caso o portal altere o HTML/seletores, ajuste os seletores em `services/contract_scraper.py`.
