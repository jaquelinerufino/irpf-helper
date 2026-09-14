from typing import Any, Dict, List

DOCUMENT_CATEGORIES: List[Dict[str, Any]] = [
    {
        "id": "informe_empregador",
        "label": "Informe de Rendimentos do Empregador",
        "group": "Rendimentos",
        "target_form_fields": ["salary", "inss"],
        "guidance": (
            "Lance o total de rendimentos tributáveis na Ficha "
            "\"Rendimentos Tributáveis Recebidos de Pessoas Jurídicas\", "
            "informando o CNPJ da fonte pagadora. A contribuição previdenciária "
            "oficial entra como dedução na mesma ficha. O Imposto Retido na "
            "Fonte (IRRF) vai no campo específico dessa ficha."
        ),
    },
    {
        "id": "informe_bancos",
        "label": "Informe de Rendimentos de Bancos/Corretoras",
        "group": "Rendimentos",
        "target_form_fields": ["extraIncome"],
        "guidance": (
            "Rendimentos tributáveis (ex.: alguns fundos, renda variável) "
            "geralmente vão na Ficha \"Rendimentos Sujeitos à Tributação "
            "Exclusiva/Definitiva\" ou \"Rendimentos Isentos e Não "
            "Tributáveis\", dependendo do tipo de aplicação — confira "
            "no informe qual a natureza de cada rendimento."
        ),
    },
    {
        "id": "carne_leao",
        "label": "Carnê-Leão (se aplicável)",
        "group": "Rendimentos",
        "target_form_fields": ["extraIncome"],
        "guidance": (
            "Os recolhimentos mensais informados no programa Carnê-Leão "
            "Web são importados automaticamente para a Ficha "
            "\"Rendimentos Tributáveis Recebidos de Pessoas Físicas/Exterior\"."
        ),
    },
    {
        "id": "recibos_saude",
        "label": "Recibos Médicos/Odontológicos",
        "group": "Saúde",
        "target_form_fields": ["deductions"],
        "guidance": (
            "Lance cada recibo na Ficha \"Pagamentos Efetuados\", código "
            "referente a despesas médicas (sem limite de dedução, mas "
            "exige CPF/CNPJ do prestador)."
        ),
    },
    {
        "id": "comprovantes_educacao",
        "label": "Comprovantes de Educação",
        "group": "Educação",
        "target_form_fields": ["deductions"],
        "guidance": (
            "Lance na Ficha \"Pagamentos Efetuados\", código de despesas "
            "com instrução — respeitando o limite anual de dedução por "
            "dependente/titular definido pela Receita Federal."
        ),
    },
    {
        "id": "aluguel_pago",
        "label": "Comprovante de Aluguel Pago",
        "group": "Moradia",
        "target_form_fields": [],
        "guidance": (
            "Aluguel pago não é dedutível na declaração de pessoa física, "
            "mas deve constar na Ficha \"Pagamentos Efetuados\" quando "
            "houver repasse a terceiros a informar."
        ),
    },
    {
        "id": "aluguel_recebido",
        "label": "Comprovante de Aluguel Recebido",
        "group": "Moradia",
        "target_form_fields": ["extraIncome"],
        "guidance": (
            "Lance na Ficha \"Rendimentos Tributáveis Recebidos de "
            "Pessoas Físicas/Exterior\" (aluguel recebido de pessoa "
            "física) ou na ficha de rendimentos de pessoa jurídica, "
            "conforme o pagador."
        ),
    },
    {
        "id": "doacoes",
        "label": "Doações (dedutíveis ou incentivadas)",
        "group": "Doações",
        "target_form_fields": ["deductions"],
        "guidance": (
            "Doações incentivadas (Fundos da Criança e do Adolescente, "
            "Lei Rouanet, etc.) entram na Ficha \"Doações Efetuadas\", "
            "respeitando os limites percentuais legais."
        ),
    },
    {
        "id": "previdencia_privada",
        "label": "Previdência Privada (PGBL/VGBL)",
        "group": "Previdência",
        "target_form_fields": ["deductions"],
        "guidance": (
            "Contribuições PGBL entram na Ficha \"Pagamentos Efetuados\" "
            "e só são dedutíveis (até 12% da renda tributável) na "
            "declaração completa. VGBL não é dedutível."
        ),
    },
    {
        "id": "dependentes_docs",
        "label": "Documentos de Dependentes",
        "group": "Dependentes",
        "target_form_fields": ["dependents"],
        "guidance": (
            "Cadastre cada dependente na Ficha \"Dependentes\", "
            "informando CPF (obrigatório a partir de determinada idade). "
            "O número total de dependentes afeta a dedução simplificada."
        ),
    },
]


def get_checklist_definition() -> List[Dict[str, Any]]:
    return DOCUMENT_CATEGORIES
