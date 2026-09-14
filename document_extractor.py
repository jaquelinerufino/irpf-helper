import io
import logging
import re
from typing import Any, Dict, List, Optional

from pypdf import PdfReader
from pypdf.errors import PdfReadError

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB por arquivo
MAX_FILES_PER_REQUEST = 5

# Valor monetário em formato brasileiro (1.234,56), aceito logo após o rótulo —
# tolera "R$" opcional e até ~60 caracteres de separação (cobre rótulo em uma
# linha e valor em outra, comum em PDFs tabulares).
# Exige vírgula com exatamente 2 casas decimais: informes de rendimentos sempre
# mostram os centavos, e sem essa exigência o gap pode "engolir" a numeração de
# item de lista (ex.: "01.") e o valor casar como se fosse um R$ 1,00 falso.
_GAP = r"[^\d]{0,60}"
_MONEY_NUMBER = r"\d{1,3}(?:\.\d{3})*,\d{2}"
_MONEY = rf"(R\$\s*)?({_MONEY_NUMBER})"

# Regras de extração por categoria: cada regra tenta casar um rótulo textual
# (tolerante a variações de acentuação/maiúsculas/abreviações/quebras de linha)
# seguido de um valor monetário. Cada regra pode ter mais de um padrão
# alternativo para o mesmo campo — o primeiro que casar é usado.
CATEGORY_FIELD_PATTERNS: Dict[str, List[Dict[str, Any]]] = {
    "informe_empregador": [
        {
            "field": "salary_annual",
            "form_field": "salary",
            "label": "Rendimentos tributáveis",
            "patterns": [
                rf"rendimentos?\s+tribut[aá]veis{_GAP}{_MONEY}",
                rf"total\s+dos\s+rendimentos{_GAP}{_MONEY}",
            ],
        },
        {
            "field": "inss",
            "form_field": "inss",
            "label": "Contribuição previdenciária",
            "patterns": [
                rf"contribui[cç][aã]o\s+previdenci[aá]ria(?:\s+oficial)?{_GAP}{_MONEY}",
                rf"previd[eê]ncia\s+(?:social|oficial){_GAP}{_MONEY}",
                rf"\bINSS\b{_GAP}{_MONEY}",
            ],
        },
        {
            "field": "irrf",
            "form_field": None,
            "label": "Imposto Retido na Fonte",
            "patterns": [
                rf"imposto\s+(?:de\s+renda\s+)?retido\s+na\s+fonte{_GAP}{_MONEY}",
                rf"\bIRRF\b{_GAP}{_MONEY}",
                rf"\bIR\s+Fonte\b{_GAP}{_MONEY}",
            ],
        },
    ],
    "informe_bancos": [
        {
            "field": "rendimentos_tributaveis",
            "form_field": "extraIncome",
            "label": "Rendimentos tributáveis",
            "patterns": [
                rf"rendimentos?\s+tribut[aá]veis{_GAP}{_MONEY}",
            ],
        },
        {
            "field": "irrf",
            "form_field": None,
            "label": "IRRF sobre aplicações",
            "patterns": [
                rf"imposto\s+(?:de\s+renda\s+)?retido\s+na\s+fonte{_GAP}{_MONEY}",
                rf"\bIRRF\b{_GAP}{_MONEY}",
            ],
        },
    ],
    "recibos_saude": [
        {
            "field": "valor_pago",
            "form_field": "deductions",
            "label": "Valor pago (recibo)",
            "patterns": [
                rf"valor\s+(?:total\s+)?pago{_GAP}{_MONEY}",
                rf"valor\s+l[ií]quido{_GAP}{_MONEY}",
                rf"total\s+geral{_GAP}{_MONEY}",
            ],
        },
    ],
    "previdencia_privada": [
        {
            "field": "contribuicao_pgbl",
            "form_field": "deductions",
            "label": "Contribuição PGBL",
            "patterns": [
                rf"contribui[cç][aã]o(?:\s+pgbl)?{_GAP}{_MONEY}",
                rf"total\s+pago(?:\s+no\s+ano)?{_GAP}{_MONEY}",
            ],
        },
    ],
    # demais categorias (carne_leao, comprovantes_educacao, aluguel_pago, aluguel_recebido,
    # doacoes, dependentes_docs): sem regra numérica na v1, só guidance textual.
}


# Informes de rendimentos financeiros (bancos/corretoras) não seguem o padrão
# "rótulo perto do valor": são tabelas com uma linha por fonte pagadora/produto,
# às vezes com uma linha de "Total:" por fonte pagadora, às vezes só com os
# valores da linha. Cada instituição usa um layout diferente, então tentamos
# alguns extratores especializados em ordem até um deles encontrar algo.
_MONEY_PLAIN = rf"({_MONEY_NUMBER})"


def _find_section(text: str, start_pattern: str) -> Optional[str]:
    """Retorna o texto entre o primeiro título que casa com start_pattern e o
    próximo título de seção (outra "Ficha da Declaração:" ou um item numerado
    tipo "3. Dívidas..."), ou None se start_pattern não for encontrado."""
    start_match = re.search(start_pattern, text, re.IGNORECASE)
    if not start_match:
        return None
    start = start_match.end()
    end_match = re.search(
        r"Ficha da Declara[çc][ãa]o:|\n\s*\d+\.\s+[A-ZÀ-Ú]", text[start:]
    )
    end = start + end_match.start() if end_match else len(text)
    return text[start:end]


def _extract_bank_totals_table(text: str) -> Optional[Dict[str, float]]:
    """Layout com uma linha "Total:" por fonte pagadora contendo Rendimento
    Bruto, Imposto Retido e Valor a declarar (padrão usado pelo Itaú e por
    diversos outros bancos/corretoras que seguem o modelo CBLC/B3)."""
    section = _find_section(
        text, r"Rendimentos?\s+Sujeitos?\s+[àa]\s+Tributa[çc][ãa]o\s+Exclusiva"
    )
    if not section:
        return None

    bruto_total = 0.0
    retido_total = 0.0
    found = False
    for match in re.finditer(
        rf"Total:\s*{_MONEY_PLAIN}\s+{_MONEY_PLAIN}\s+{_MONEY_PLAIN}", section
    ):
        bruto = parse_brl_number(match.group(1))
        retido = parse_brl_number(match.group(2))
        if bruto is None or retido is None:
            continue
        bruto_total += bruto
        retido_total += retido
        found = True

    if not found:
        return None
    return {"rendimentos_tributaveis": bruto_total, "irrf": retido_total}


def _extract_bank_inline_rows(text: str) -> Optional[Dict[str, float]]:
    """Layout com uma linha por produto no formato
    "Fonte Pagadora ... R$ saldo2024 R$ saldo2025 R$ rendimento_líquido", sem
    linha de total (padrão usado por bancos digitais como o C6). Soma a
    última coluna (rendimento líquido) de cada linha da seção."""
    section = _find_section(
        text,
        r"\d+\.\s*Rendimentos?\s+Sujeitos?\s+[àa]?\s*Tributa[çc][ãa]o\s+Exclusiva",
    )
    if not section:
        return None

    total = 0.0
    found = False
    for match in re.finditer(
        rf"R\$\s*{_MONEY_NUMBER}\s*R\$\s*{_MONEY_NUMBER}\s*R\$\s*{_MONEY_PLAIN}", section
    ):
        value = parse_brl_number(match.group(1))
        if value is None:
            continue
        total += value
        found = True

    if not found:
        return None
    return {"rendimentos_tributaveis": total}


def _extract_bank_reversed_label(text: str) -> Optional[Dict[str, float]]:
    """Layout em que os valores aparecem no texto extraído ANTES do rótulo da
    coluna (comum em PDFs com campos posicionados de forma absoluta, ex.:
    Nubank). Procura o rótulo "Rendimento tributação exclusiva" e usa os 3
    valores em R$ mais próximos que aparecem antes dele na mesma linha."""
    total = 0.0
    found = False
    label_pattern = re.compile(
        r"Rendimento\s+tributa[çc][ãa]o\s+exclusiva", re.IGNORECASE
    )
    row_pattern = re.compile(
        rf"R\$\s*{_MONEY_NUMBER}\s*R\$\s*{_MONEY_NUMBER}\s*R\$\s*{_MONEY_PLAIN}"
    )
    for label_match in label_pattern.finditer(text):
        window = text[max(0, label_match.start() - 200) : label_match.start()]
        row_match = None
        for candidate in row_pattern.finditer(window):
            row_match = candidate  # fica com a ocorrência mais próxima do rótulo
        if row_match is None:
            continue
        value = parse_brl_number(row_match.group(1))
        if value is None:
            continue
        total += value
        found = True

    if not found:
        return None
    return {"rendimentos_tributaveis": total}


_BANK_TABLE_EXTRACTORS = (
    _extract_bank_totals_table,
    _extract_bank_inline_rows,
    _extract_bank_reversed_label,
)


def _extract_bank_table_fields(text: str, existing: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    already = {m["field"] for m in existing}
    field_meta = {rule["field"]: rule for rule in CATEGORY_FIELD_PATTERNS["informe_bancos"]}

    values: Dict[str, float] = {}
    for extractor in _BANK_TABLE_EXTRACTORS:
        values = extractor(text) or {}
        if values:
            break

    result = []
    for field, value in values.items():
        if field in already or field not in field_meta:
            continue
        rule = field_meta[field]
        rounded = round(value, 2)
        result.append(
            {
                "field": field,
                "form_field": rule["form_field"],
                "label": rule["label"],
                "value": rounded,
                "raw_match": f"{rounded:.2f}".replace(".", ","),
            }
        )
    return result


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
    rules = CATEGORY_FIELD_PATTERNS.get(category_id, [])
    matches: List[Dict[str, Any]] = []

    for rule in rules:
        best_match = None
        for pattern in rule["patterns"]:
            match = re.search(pattern, text, re.IGNORECASE)
            # Entre os padrões alternativos, usamos o que casa mais cedo no
            # documento — não o primeiro da lista. Formulários de rendimentos
            # costumam repetir o mesmo rótulo em seções posteriores (ex.:
            # "Rendimentos Recebidos Acumuladamente") com valor zerado, e a
            # ordem no texto é o sinal mais confiável de qual ocorrência é a
            # principal.
            if match and (best_match is None or match.start() < best_match.start()):
                best_match = match

        if best_match is None:
            continue

        raw_value = best_match.group(2)
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

    if category_id == "informe_bancos":
        matches.extend(_extract_bank_table_fields(text, matches))

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
