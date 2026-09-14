# irpf-helper

Site de apoio à declaração do IRPF, rodando como Azure Function App (Python).

Funcionalidades:
- Comparação do desconto simplificado x deduções completas, com recomendação de qual compensa mais.
- Organizador de documentos: checklist de comprovantes comuns, com anexo de múltiplos arquivos por categoria e orientação de onde preencher cada tipo de documento no programa da Receita.
- Extração automática de valores a partir do texto de PDFs de informes (ex.: rendimentos tributáveis, INSS, IRRF) — sob demanda, ao clicar em "Extrair dados". O conteúdo do arquivo só é enviado ao servidor nesse momento, é lido em memória e descartado imediatamente após o processamento; nada fica armazenado. Cobre PDFs com texto nativo — PDFs escaneados (imagem) não são suportados nesta versão e pedem preenchimento manual. Os valores extraídos são sempre uma sugestão, aplicada apenas com confirmação do usuário.
- Guia passo a passo de como declarar no programa oficial da Receita Federal.
- Download do resumo em PDF ou Excel.

Este é um cálculo técnico simplificado para apoio de planejamento. Não substitui a orientação de um contador ou a declaração oficial do IRPF.

## Rodando localmente

```bash
pip install -r requirements.txt
func start
```

A página fica disponível em `http://localhost:7071/home`.

## Estrutura

- `function_app.py` — rotas HTTP (`/home`, `/api/calculate`, `/api/checklist`, `/api/report`, `/api/extract`).
- `irpf_calc.py` — lógica de cálculo (faixas do IRPF, desconto simplificado, deduções completas).
- `document_checklist.py` — categorias do organizador de documentos, com orientação de preenchimento por categoria.
- `document_extractor.py` — extração de texto de PDF (pypdf) e reconhecimento de valores por regex, em memória.
- `report_generator.py` — geração de PDF (reportlab) e Excel (openpyxl) em memória.
- `templates.py` — página HTML/CSS/JS.

## Deploy no Azure

Recursos atuais (Consumption plan, Brazil South):
- Resource group: `rg-irpf-helper`
- Function App: `irpf-helper-bb340c` — https://irpf-helper-bb340c.azurewebsites.net/home
- Runtime: Python 3.12 (o ambiente local usa 3.14, mas o Linux Consumption ainda não tinha o pipeline de deploy pronto para 3.14 no momento do deploy — reavaliar quando quiser atualizar)

Para publicar uma nova versão do código:

```bash
func azure functionapp publish irpf-helper-bb340c --build remote
```

Para recriar do zero em outro ambiente:

1. `az login`
2. Crie (ou use) um Function App: `az functionapp create ...` — confira a versão de Python suportada em produção (https://learn.microsoft.com/azure/azure-functions/supported-languages), já que o desenvolvimento local pode usar uma versão mais recente.
3. Publique: `func azure functionapp publish <nome-do-app> --build remote`
