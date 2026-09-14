# Fluxos de processo

## 1. Comparação dos modelos de declaração

```mermaid
sequenceDiagram
    actor U as Usuário
    participant B as Navegador
    participant A as POST /api/calculate
    participant C as irpf_calc.compare_models

    U->>B: Informa renda, deduções e dependentes
    B->>A: JSON com os valores
    A->>A: Valida JSON e corpo
    A->>C: Encaminha payload
    C->>C: Valida valores não negativos
    C->>C: Calcula renda anual
    C->>C: Calcula imposto simplificado e completo
    C->>C: Seleciona o menor imposto estimado
    C-->>A: Comparação e recomendação
    A-->>B: HTTP 200 + JSON
    B-->>U: Exibe resultado
```

Regras operacionais:

- `salary` representa a renda bruta mensal e é multiplicado por 12.
- `extraIncome`, `deductions`, `inss` e `pension` são valores anuais.
- entradas negativas ou não numéricas retornam HTTP 400;
- as constantes tributárias são centralizadas em `irpf_calc.py` e estão marcadas como ano-calendário 2024.

## 2. Extração de dados de documentos

```mermaid
sequenceDiagram
    actor U as Usuário
    participant B as Navegador
    participant A as POST /api/extract
    participant E as document_extractor
    participant M as Memória da requisição

    U->>B: Seleciona PDF(s) e solicita extração
    B->>A: multipart/form-data: categoryId + files
    A->>A: Valida categoria, quantidade e tamanho
    A->>M: Lê bytes dos arquivos
    A->>E: extract_from_files(categoryId, arquivos)
    E->>E: Abre PDF e extrai camada de texto
    E->>E: Aplica padrões por categoria
    E-->>A: Sugestões, avisos ou erros por arquivo
    A-->>B: HTTP 200 + JSON
    B-->>U: Mostra sugestões para confirmação
    U->>B: Confirma ou ignora cada sugestão
```

Tratamento esperado:

| Situação | Resultado |
| --- | --- |
| Mais de 5 arquivos | HTTP 400. |
| Arquivo acima de 10 MB | HTTP 400. |
| PDF protegido ou corrompido | Resultado do arquivo com `status: error`. |
| PDF escaneado/sem texto | Resultado com `status: no_text`; preenchimento manual. |
| Texto sem padrão reconhecido | Resultado `ok`, sem sugestões. |

O extrator não faz OCR e não garante que um valor reconhecido esteja correto. A confirmação humana é obrigatória no fluxo de interface.

## 3. Geração de relatório

```mermaid
sequenceDiagram
    actor U as Usuário
    participant B as Navegador
    participant A as POST /api/report
    participant C as irpf_calc
    participant R as report_generator

    U->>B: Escolhe PDF ou Excel
    B->>A: formato + cálculo + checklist
    A->>A: Valida formato
    A->>C: Recalcula a comparação a partir da entrada
    C-->>A: Resultado do cálculo
    A->>R: Gera arquivo em memória
    R-->>A: Bytes do PDF/XLSX
    A-->>B: Download com Content-Disposition
    B-->>U: Salva o arquivo localmente
```

O backend recalcula o resultado em vez de confiar no cálculo apresentado pelo navegador. O relatório contém estimativas e o estado do checklist recebido na requisição.
