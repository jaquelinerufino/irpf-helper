# Guia do agente de desenvolvimento

## Escopo

Este projeto **não possui um agente de IA como componente de produção**. A palavra “agente”, neste documento, significa o assistente de desenvolvimento (humano ou automatizado) que altera, revisa ou opera o repositório.

O agente deve preservar o papel do IRPF Helper: apoio ao planejamento, sem se apresentar como fonte oficial, contador, sistema de transmissão ou aconselhamento tributário definitivo.

## Responsabilidades

- Manter o cálculo separado da camada HTTP e da interface.
- Atualizar faixas e deduções somente com fonte oficial, registrando o ano-calendário, a fonte e os testes alterados.
- Tratar documentos e valores fiscais como dados confidenciais.
- Manter a extração como sugestão confirmável, sem preenchimento silencioso.
- Atualizar README e documentação técnica quando modificar contratos, arquitetura, limites ou deploy.

## Regras de alteração

| Área | Procedimento obrigatório |
| --- | --- |
| `irpf_calc.py` | Alterar constantes e testes juntos; validar casos de faixa, teto e recomendação. |
| `function_app.py` | Documentar novas rotas, payloads, respostas e erros no README. |
| `document_extractor.py` | Adicionar testes com texto sintético representativo; não adicionar PDFs reais de usuários ao repositório. |
| `report_generator.py` | Verificar que PDF/XLSX é gerado em memória e que os campos refletem o contrato da API. |
| `templates.py` | Manter confirmação explícita para qualquer valor sugerido por extração. |
| Infraestrutura | Não colocar credenciais, connection strings ou dados fiscais no controle de versão. |

## Rotina de trabalho

1. Leia `README.md` e os documentos relevantes em `docs/`.
2. Inspecione alterações existentes com `git status` e preserve trabalho que não pertence à tarefa.
3. Faça a menor alteração que resolva o objetivo.
4. Execute `pytest` e `ruff check .` no ambiente com as dependências de desenvolvimento instaladas.
5. Revise payloads e mensagens de erro se houver impacto em API ou interface.
6. Atualize testes e documentação; informe limitações ou validações que não puderam ser executadas.

## Regras de segurança e privacidade

- Nunca exponha conteúdo de PDFs, valores fiscais ou nomes de arquivos em logs, commits, exemplos públicos ou tickets.
- Não adicione armazenamento persistente, OCR ou integração de terceiros sem decisão explícita de produto e análise de privacidade.
- Não trate valores extraídos como verdade; preserve a confirmação do usuário.
- Não altere regras tributárias com base em memória. Use fontes oficiais e registre o ano de vigência.

## Definição de pronto

Uma mudança está pronta quando:

- o comportamento é coberto ou ajustado por teste automatizado;
- `pytest` e `ruff check .` passam;
- não há dados reais ou segredos no diff;
- contratos e documentos afetados foram atualizados;
- o texto da interface continua deixando claro o caráter estimativo da aplicação.
