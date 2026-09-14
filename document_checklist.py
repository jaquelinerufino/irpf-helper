from typing import Any, Dict, List

DOCUMENT_CATEGORIES: List[Dict[str, str]] = [
    {"id": "informe_empregador", "label": "Informe de Rendimentos do Empregador", "group": "Rendimentos"},
    {"id": "informe_bancos", "label": "Informe de Rendimentos de Bancos/Corretoras", "group": "Rendimentos"},
    {"id": "carne_leao", "label": "Carnê-Leão (se aplicável)", "group": "Rendimentos"},
    {"id": "recibos_saude", "label": "Recibos Médicos/Odontológicos", "group": "Saúde"},
    {"id": "comprovantes_educacao", "label": "Comprovantes de Educação", "group": "Educação"},
    {"id": "aluguel_pago", "label": "Comprovante de Aluguel Pago", "group": "Moradia"},
    {"id": "aluguel_recebido", "label": "Comprovante de Aluguel Recebido", "group": "Moradia"},
    {"id": "doacoes", "label": "Doações (dedutíveis ou incentivadas)", "group": "Doações"},
    {"id": "previdencia_privada", "label": "Previdência Privada (PGBL/VGBL)", "group": "Previdência"},
    {"id": "dependentes_docs", "label": "Documentos de Dependentes", "group": "Dependentes"},
]


def get_checklist_definition() -> List[Dict[str, Any]]:
    return DOCUMENT_CATEGORIES
