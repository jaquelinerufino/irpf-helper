# IRPF Helper

Aplicação web de apoio ao planejamento da declaração do Imposto de Renda de Pessoa Física (IRPF). Ela compara os modelos de declaração, organiza documentos, sugere valores a partir de PDFs com texto e exporta um resumo em PDF ou Excel.

> **Aviso importante:** este projeto é uma estimativa para planejamento. Não substitui um contador, a legislação vigente, nem o preenchimento e a transmissão da declaração no programa oficial da Receita Federal.

## Documentação técnica

- [Modelo C4 da arquitetura](docs/c4-model.md)
- [Fluxos de processo](docs/processos.md)
- [Dados e privacidade](docs/dados.md)
- [Guia do agente de desenvolvimento](docs/agente.md)

## O que a aplicação faz

- Compara o desconto simplificado com as deduções legais informadas e recomenda o menor imposto estimado.
- Mantém um checklist de documentos comuns, com orientação de onde declarar cada item.
- Extrai sugestões de valores de informes e recibos em PDF com texto nativo.
- Permite confirmar cada sugestão antes de preencher o formulário.
- Gera um resumo do cálculo e do checklist em PDF ou `.xlsx`.

Os arquivos enviados para extração são processados somente quando o botão **Extrair dados** é usado. O conteúdo é lido em memória e não é persistido pela aplicação.

## Limitações e premissas do cálculo

As constantes em [`irpf_helper/irpf_calc.py`](irpf_helper/irpf_calc.py) foram definidas para o **ano-calendário de 2024** e incluem faixas, teto do desconto simplificado e dedução anual por dependente. Atualize-as antes de usar o projeto para outro ano-calendário.

O cálculo considera:

- salário bruto mensal, multiplicado por 12;
- rendimentos extras anuais;
- INSS, pensão, deduções gerais e dependentes declarados;
- imposto progressivo sobre a base calculada.

Ele não modela todas as situações tributárias, como rendimentos isentos ou sujeitos à tributação exclusiva, ganho de capital, renda variável, imposto retido/antecipações, limites específicos de deduções e regras particulares do contribuinte.

## Requisitos

- Python 3.12 (versão configurada para o runtime de produção)
- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
- `pip`

Para publicar no Azure, também são necessários Azure CLI e uma Function App já criada.

### Classificação opcional com Azure OpenAI

Para classificar itens complementares de informes que não foram reconhecidos pelas regras locais, configure `AZURE_OPENAI_ENDPOINT` e `AZURE_OPENAI_DEPLOYMENT`. A aplicação usa `DefaultAzureCredential`; em produção, atribua à identidade gerenciada da Function App uma permissão compatível no recurso Azure OpenAI. Sem essas variáveis ou em caso de falha, a classificação é ignorada e o usuário escolhe a categoria manualmente.

## Executar localmente

Crie e ative um ambiente virtual, instale as dependências e inicie a Function App:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
func start
```

Abra [http://localhost:7071/home](http://localhost:7071/home).

No Windows PowerShell, ative o ambiente com:

```powershell
.venv\Scripts\Activate.ps1
```

## Qualidade

As dependências de desenvolvimento já incluem `pytest` e `ruff`.

```bash
pytest
ruff check .
```

Os testes cobrem a progressividade do imposto, a comparação entre modelos e os principais formatos de texto extraído de PDFs.

## API HTTP

Como [`host.json`](host.json) define um prefixo de rota vazio, os endpoints ficam diretamente na raiz.

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/home` | Interface web da aplicação. |
| `POST` | `/api/calculate` | Calcula e compara os modelos. |
| `GET` | `/api/checklist` | Retorna as categorias do checklist e as orientações. |
| `POST` | `/api/extract` | Extrai sugestões de valores de PDFs enviados por `multipart/form-data`. |
| `POST` | `/api/report` | Gera o resumo em PDF ou Excel. |

### `POST /api/calculate`

Envie JSON com valores não negativos. `salary` é mensal; `extraIncome` e os demais valores monetários são anuais.

```json
{
  "salary": 7000,
  "extraIncome": 0,
  "deductions": 1200,
  "inss": 8000,
  "pension": 0,
  "dependents": 1
}
```

Resposta resumida:

```json
{
  "annual_income": 84000.0,
  "simplified": {
    "discount_applied": 16754.34,
    "taxable_base": 59245.66,
    "tax_amount": 5860.24,
    "effective_rate": 6.98
  },
  "complete": {
    "deduction_total": 11475.08,
    "taxable_base": 72524.92,
    "tax_amount": 9512.03,
    "effective_rate": 11.32
  },
  "recommended": "simplified",
  "difference": 3651.79
}
```

`recommended` pode ser `simplified`, `complete` ou `equal`. Valores inválidos, corpo vazio ou números negativos retornam HTTP 400 com `{ "error": "..." }`.

### `POST /api/extract`

Envie `multipart/form-data` com `categoryId` e um ou mais campos `files`. São aceitos no máximo cinco arquivos por requisição, cada um com até 10 MB. A extração suporta somente PDFs com camada de texto; PDFs escaneados, protegidos por senha ou sem texto exigem preenchimento manual.

As categorias com extração de valores na versão atual são:

- `informe_empregador`: rendimentos tributáveis, INSS e IRRF;
- `informe_bancos`: rendimentos e IRRF em alguns layouts de bancos/corretoras;
- `recibos_saude`: valor pago;
- `previdencia_privada`: contribuição PGBL.

Os valores devolvidos são sugestões. A aplicação cliente decide se irá aplicá-los ao formulário.

### `POST /api/report`

Envie o formato desejado, o mesmo objeto usado no cálculo e o estado do checklist:

```json
{
  "format": "pdf",
  "calculation": {
    "salary": 7000,
    "extraIncome": 0,
    "deductions": 1200,
    "inss": 8000,
    "pension": 0,
    "dependents": 1
  },
  "checklist": [
    {
      "id": "informe_empregador",
      "checked": true,
      "fileNames": ["informe.pdf"]
    }
  ]
}
```

Use `"pdf"` ou `"xlsx"` em `format`. A resposta é um download com o tipo MIME correspondente.

## Estrutura do projeto

| Arquivo | Responsabilidade |
| --- | --- |
| [`function_app.py`](function_app.py) | Ponto de entrada do Azure Functions e rotas HTTP. |
| [`irpf_helper/`](irpf_helper) | Pacote da aplicação: cálculo, checklist, extração, relatórios e interface. |
| [`irpf_helper/irpf_calc.py`](irpf_helper/irpf_calc.py) | Faixas, deduções e comparação dos modelos. |
| [`irpf_helper/document_extractor.py`](irpf_helper/document_extractor.py) | Leitura de PDFs, reconhecimento de valores e classificação opcional com Azure OpenAI. |
| [`tests/`](tests) | Testes automatizados do pacote da aplicação. |

## Deploy no Azure

O ambiente atual utiliza Azure Functions em plano Consumption, na região Brazil South:

- Resource group: `rg-irpf-helper`
- Function App: `irpf-helper-bb340c`
- URL: <https://irpf-helper-bb340c.azurewebsites.net/home>
- Runtime de produção: Python 3.12

Para publicar uma nova versão:

```bash
func azure functionapp publish irpf-helper-bb340c --build remote
```

Para outro ambiente, crie uma Function App com uma versão de Python suportada pelo Azure Functions e então publique com:

```bash
func azure functionapp publish <nome-da-function-app> --build remote
```

Consulte a [matriz de linguagens suportadas pelo Azure Functions](https://learn.microsoft.com/azure/azure-functions/supported-languages) antes de escolher o runtime.
