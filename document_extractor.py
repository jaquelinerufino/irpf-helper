import io
import logging
import re
from typing import Any, Dict, List, Optional

from pypdf import PdfReader
from pypdf.errors import PdfReadError

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB por arquivo
MAX_FILES_PER_REQUEST = 5

# Regras de extração por categoria: cada regra tenta casar um rótulo textual
# (tolerante a variações de acentuação/maiúsculas/quebras de linha) seguido
# de um valor monetário em formato brasileiro (1.234,56).
CATEGORY_FIELD_PATTERNS: Dict[str, List[Dict[str, Optional[str]]]] = {
    "informe_empregador": [
        {
            "field": "salary_annual",
            "form_field": "salary",
            "label": "Rendimentos tributáveis",
            "pattern": r"rendimentos?\s+tribut[aá]veis[^\d]{0,40}([\d.,]+\d)",
        },
        {
            "field": "inss",
            "form_field": "inss",
            "label": "Contribuição previdenciária oficial",
            "pattern": r"contribui[cç][aã]o\s+previdenci[aá]ria\s+oficial[^\d]{0,40}([\d.,]+\d)",
        },
        {
            "field": "irrf",
            "form_field": None,
            "label": "Imposto Retido na Fonte",
            "pattern": r"imposto\s+(?:de\s+renda\s+)?retido\s+na\s+fonte[^\d]{0,40}([\d.,]+\d)",
        },
    ],
    "informe_bancos": [
        {
            "field": "rendimentos_tributaveis",
            "form_field": "extraIncome",
            "label": "Rendimentos tributáveis",
            "pattern": r"rendimentos?\s+tribut[aá]veis[^\d]{0,40}([\d.,]+\d)",
        },
        {
            "field": "irrf",
            "form_field": None,
            "label": "IRRF sobre aplicações",
            "pattern": r"imposto\s+(?:de\s+renda\s+)?retido\s+na\s+fonte[^\d]{0,40}([\d.,]+\d)",
        },
    ],
    "recibos_saude": [
        {
            "field": "valor_pago",
            "form_field": "deductions",
            "label": "Valor pago (recibo)",
            "pattern": r"valor\s+(?:total\s+)?pago[^\d]{0,40}([\d.,]+\d)",
        },
    ],
    "previdencia_privada": [
        {
            "field": "contribuicao_pgbl",
            "form_field": "deductions",
            "label": "Contribuição PGBL",
            "pattern": r"(?:contribui[cç][aã]o|total\s+pago)\s+(?:pgbl)?[^\d]{0,40}([\d.,]+\d)",
        },
    ],
    # demais categorias (carne_leao, comprovantes_educacao, aluguel_pago, aluguel_recebido,
    # doacoes, dependentes_docs): sem regra numérica na v1, só guidance textual.
}


class PdfExtractionError(Exception):
    """Erro tratável: PDF corrompido, protegido por senha, ou excede tamanho máximo."""


def parse_brl_number(raw: str) -> Optional[float]:
    cleaned = raw.strip().replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_text_from_pdf(file_bytes: bytes) -> Dict[str, Any]:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except PdfReadError as exc:
        raise PdfExtractionError("Não foi possível ler este PDF — arquivo corrompido.") from exc

    if reader.is_encrypted:
        raise PdfExtractionError("PDF protegido por senha — remova a senha e tente novamente.")

    text_parts = []
    for page in reader.pages:
        try:
            text_parts.append(page.extract_text() or "")
        except Exception:
            logging.exception("Falha ao extrair texto de uma página do PDF.")
            continue

    return {"text": "\n".join(text_parts), "pages": len(reader.pages)}


def extract_fields_for_category(category_id: str, text: str) -> List[Dict[str, Any]]:
    patterns = CATEGORY_FIELD_PATTERNS.get(category_id, [])
    matches: List[Dict[str, Any]] = []

    for rule in patterns:
        match = re.search(rule["pattern"], text, re.IGNORECASE)
        if not match:
            continue
        raw_value = match.group(1)
        value = parse_brl_number(raw_value)
        if value is None:
            continue
        matches.append(
            {
                "field": rule["field"],
                "form_field": rule["form_field"],
                "label": rule["label"],
                "value": value,
                "raw_match": raw_value,
            }
        )

    return matches


def extract_from_files(category_id: str, files: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = []
    has_any_match = False

    for file_info in files:
        filename = file_info.get("filename") or "arquivo"
        content = file_info.get("content", b"")

        try:
            extracted = extract_text_from_pdf(content)
        except PdfExtractionError as exc:
            results.append(
                {"filename": filename, "status": "error", "message": str(exc), "matches": []}
            )
            continue
        except Exception:
            logging.exception("Erro inesperado ao processar '%s'.", filename)
            results.append(
                {
                    "filename": filename,
                    "status": "error",
                    "message": "Não foi possível processar este arquivo.",
                    "matches": [],
                }
            )
            continue

        text = extracted["text"]
        if not text.strip():
            results.append(
                {
                    "filename": filename,
                    "status": "no_text",
                    "message": (
                        "Não foi possível extrair texto deste arquivo — provavelmente é um "
                        "PDF escaneado (imagem). Preencha os campos manualmente."
                    ),
                    "matches": [],
                }
            )
            continue

        matches = extract_fields_for_category(category_id, text)
        if matches:
            has_any_match = True

        results.append(
            {
                "filename": filename,
                "status": "ok",
                "message": None if matches else "Nenhum valor reconhecido automaticamente neste arquivo.",
                "matches": matches,
            }
        )

    return {"category_id": category_id, "results": results, "has_any_match": has_any_match}
