# Arquitetura — modelo C4

Este documento descreve a arquitetura existente, não uma arquitetura-alvo. O IRPF Helper é uma aplicação web monolítica hospedada como Azure Function App. Não há banco de dados, fila ou armazenamento de arquivos. A classificação de itens ambíguos pode usar Azure OpenAI quando configurada.

## Nível 1 — Contexto do sistema

```mermaid
flowchart LR
    contribuinte["Contribuinte\nUsuário da aplicação"]
    contador["Contador\nOrientação profissional externa"]
    receita["Programa e regras da Receita Federal\nSistema externo"]
    openai["Azure OpenAI\nClassificação opcional de itens"]
    sistema["IRPF Helper\nPlanejamento e organização da declaração"]

    contribuinte -->|"informa valores, anexa PDFs e baixa relatórios"| sistema
    sistema -->|"estimativas, checklist e orientação"| contribuinte
    contribuinte -->|"preenche e transmite a declaração oficial"| receita
    contador <-->|"orientação tributária"| contribuinte
    sistema -. "classifica itens ambíguos quando configurado" .-> openai
```

O IRPF Helper apoia o planejamento. Ele não transmite declarações, não autentica no Gov.br/Receita e não consulta sistemas externos.

## Nível 2 — Contêineres

```mermaid
flowchart TB
    browser["Navegador\nHTML, CSS e JavaScript"]
    function["Azure Function App\nPython 3.12 / HTTP"]
    calc["Motor de cálculo\nirpf_calc.py"]
    checklist["Catálogo de checklist\ndocument_checklist.py"]
    extract["Extrator de PDFs\ndocument_extractor.py + pypdf"]
    reports["Gerador de relatórios\nreport_generator.py"]
    openai["Azure OpenAI\nClassificação opcional"]
    memory[("Memória efêmera\nda requisição")]

    browser -->|"HTTPS: /home e /api/*"| function
    function --> calc
    function --> checklist
    function --> extract
    function --> reports
    extract -. "item complementar ambíguo" .-> openai
    extract -->|"lê bytes do PDF"| memory
    reports -->|"mantém PDF/XLSX durante a resposta"| memory
    function -->|"HTML, JSON ou arquivo para download"| browser
```

| Contêiner | Tecnologia | Responsabilidade |
| --- | --- | --- |
| Cliente web | HTML, CSS e JavaScript em `irpf_helper/templates.py` | Entrada dos dados, apresentação, confirmação de sugestões e download. |
| API | Azure Functions Python em `function_app.py` | Expõe as rotas HTTP, interpreta as requisições e compõe os módulos. |
| Cálculo | Python puro em `irpf_helper/irpf_calc.py` | Compara modelos simplificado e completo. |
| Extração | `pypdf`, expressões regulares e Azure OpenAI opcional | Lê PDFs com texto nativo, reconhece valores e pode classificar itens ambíguos. |
| Relatórios | ReportLab e openpyxl | Produz PDF e Excel em memória. |

## Nível 3 — Componentes da Function App

```mermaid
flowchart LR
    routes["function_app.py\nRotas HTTP"]
    home["home\nGET /home"]
    calculate["calculate\nPOST /api/calculate"]
    check["checklist\nGET /api/checklist"]
    extraction["extract\nPOST /api/extract"]
    report["report\nPOST /api/report"]
    html["irpf_helper/templates.py\nHTML_PAGE"]
    tax["irpf_helper/irpf_calc.py\ncompare_models"]
    docs["irpf_helper/document_checklist.py\nget_checklist_definition"]
    pdf["irpf_helper/document_extractor.py\nextract_from_files"]
    output["irpf_helper/report_generator.py\ngenerate_*_report"]

    routes --> home --> html
    routes --> calculate --> tax
    routes --> check --> docs
    routes --> extraction --> pdf
    routes --> report --> tax
    report --> output
```

### Responsabilidades e fronteiras

- `function_app.py` é a fronteira HTTP: faz parsing e validação básica, mas não contém regras tributárias ou lógica de extração.
- `irpf_helper/irpf_calc.py` é determinístico e não possui I/O; por isso é diretamente testável.
- `irpf_helper/document_extractor.py` trata o PDF como entrada não confiável e retorna sugestões, nunca altera valores persistidos. A chamada opcional ao Azure OpenAI só classifica itens complementares sem categoria reconhecida.
- `irpf_helper/report_generator.py` recebe o cálculo pronto e um estado de checklist; não recalcula regras próprias.
- Não existe persistência de estado no servidor. O estado da interface reside no navegador durante a sessão.

## Infraestrutura e implantação

```mermaid
flowchart LR
    dev["Desenvolvedor"] -->|"func azure functionapp publish --build remote"| azure["Azure Functions\nConsumption / Brazil South"]
    azure --> app["Function App\nirpf-helper-bb340c"]
    user["Navegador do usuário"] -->|"HTTPS"| app
```

O runtime e o nome da Function App atual estão documentados no [README principal](../README.md#deploy-no-azure). O modelo não pressupõe recursos adicionais do Azure.
