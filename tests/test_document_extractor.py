from irpf_helper.document_extractor import extract_fields_for_category, parse_brl_number


def test_parse_brl_number():
    assert parse_brl_number("1.234,56") == 1234.56
    assert parse_brl_number("90.994,79") == 90994.79
    assert parse_brl_number("nao é um número") is None


def test_salary_annual_uses_earliest_match_in_document():
    # Comprovantes de rendimentos costumam repetir "rendimentos tributáveis" em
    # seções posteriores (ex.: Rendimentos Recebidos Acumuladamente) com valor
    # zerado. O valor correto é o que aparece primeiro no documento.
    text = """
    3. - Rendimentos Tributáveis, Deduções e Imposto sobre a Renda Retido na Fonte
    01. Total dos Rendimentos (inclusive Férias).      90.994,79
    02. Contribuição Previdenciária Oficial.      10.869,62
    05. Imposto sobre a Renda Retido na Fonte (IRRF).       9.337,08

    6. - Rendimentos Recebidos Acumuladamente
    01. Total dos rendimentos tributáveis (inclusive férias e décimo terceiro salário)          0,00
    """
    matches = {m["field"]: m["value"] for m in extract_fields_for_category("informe_empregador", text)}
    assert matches["salary_annual"] == 90994.79
    assert matches["inss"] == 10869.62
    assert matches["irrf"] == 9337.08


def test_informe_bancos_totals_table_sums_per_source():
    # Layout tipo Itaú: uma linha "Total:" por fonte pagadora com Rendimento
    # Bruto, Imposto Retido e Valor a declarar.
    text = """
    Ficha da Declaração: Rendimentos Sujeitos à Tributação Exclusiva/Definitiva
    Fonte Pagadora:
    Banco A
    Rendimento
     Bruto
    Imposto
     Retido
    Valor
    (a declarar)
    RDB/CDB
         0,28
         0,01
         0,27
    Total:


     0,28
     0,01
     0,27
    Fonte Pagadora:
    Banco B
    Rendimento
     Bruto
    Imposto
     Retido
    Valor
    (a declarar)
    TESOURO DIRETO
         4,73
         0,71
         4,02
    Total:


     4,73
     0,71
     4,02
    Ficha da Declaração: Bens e Direitos
    Total:



     473,89
     5.899,88
    """
    matches = {m["field"]: m["value"] for m in extract_fields_for_category("informe_bancos", text)}
    assert matches["rendimentos_tributaveis"] == 5.01
    assert matches["irrf"] == 0.72


def test_informe_bancos_inline_rows_sums_last_column():
    # Layout tipo C6: uma linha por produto com 3 valores em R$ (saldo inicial,
    # saldo final, rendimento líquido), sem linha de total.
    text = """
    1. Rendimentos Isentos
    Banco X Aplicações em Renda Fixa R$ 100,00 R$ 200,00 R$ 999,99
    2. Rendimentos Sujeitos a Tributação Exclusiva
    Banco X Rendimentos de Aplicações Financeiras R$ 0,00 R$ 0,00 R$ 123,45
    Banco Y Rendimentos de Aplicações Financeiras R$ 0,00 R$ 0,00 R$ 876,55
    3. Dívidas e Ônus Reais
    Banco X Crédito Pessoal R$ 0,00 R$ 0,00 R$ 555,55
    """
    matches = {m["field"]: m["value"] for m in extract_fields_for_category("informe_bancos", text)}
    assert matches["rendimentos_tributaveis"] == 1000.0
    assert "irrf" not in matches


def test_informe_bancos_reversed_label_uses_value_before_label():
    # Layout tipo Nubank: o rótulo da coluna aparece no texto extraído DEPOIS
    # dos valores da linha, por causa do posicionamento absoluto no PDF.
    text = """
    Grupo 04 - Aplicações e Investimentos
    0001 824459-0 R$ 0,01 R$ 0,00 R$ 1,26
    Agência
    Conta
    31/12/2024
    31/12/2025
    Rendimento tributação
    exclusiva
    """
    matches = {m["field"]: m["value"] for m in extract_fields_for_category("informe_bancos", text)}
    assert matches["rendimentos_tributaveis"] == 1.26


def test_unknown_category_returns_no_matches():
    assert extract_fields_for_category("categoria_inexistente", "qualquer texto") == []


_QUADRO_7_TEXT = """
  7. - Informações Complementares
01. ASS.ODONTO.COPARTICI           - TITULAR - ODONTOPREV S/A - CNPJ: 58.119.199/0001-51         52,74
02. KPMG PREV SOC. PREVID PRIVADA  / CONTRIBUIÇÃO À PREVIDÊNCIA PRIVADA / CNPJ:  03.898.918/000
1-98      4.231,50
03. ASSIST.MED.COPARTICI           - TITULAR - BRADESCO SAÚDE S/A - CNPJ: 92.693.118/0001-60      1.602,04
04. O total informado na linha 03 do Quadro 5 já inclui o  valor total pago a título de  PLR
correspondente a      1.389,20
  8. - Responsável Pelas Informações
Nome Data Assinatura
"""


def test_complementary_items_extracted_with_values_and_labels():
    matches = extract_fields_for_category("informe_empregador", _QUADRO_7_TEXT)
    complementary = {m["field"]: m for m in matches if m["field"].startswith("complementar_")}

    assert complementary["complementar_0"]["value"] == 52.74
    assert "ODONTOPREV" in complementary["complementar_0"]["label"]

    assert complementary["complementar_1"]["value"] == 4231.50
    assert "PREVIDÊNCIA PRIVADA" in complementary["complementar_1"]["label"]

    assert complementary["complementar_2"]["value"] == 1602.04
    assert "BRADESCO SAÚDE" in complementary["complementar_2"]["label"]

    assert complementary["complementar_3"]["value"] == 1389.20

    for match in complementary.values():
        assert match["form_field"] == "deductions"
        assert {opt["id"] for opt in match["category_options"]} == {
            "recibos_saude",
            "previdencia_privada",
            "outro",
        }


def test_complementary_items_classified_by_keyword():
    matches = extract_fields_for_category("informe_empregador", _QUADRO_7_TEXT)
    guesses = {m["field"]: m["category_guess"] for m in matches if m["field"].startswith("complementar_")}

    # item 01: ODONTOPREV contém "PREV" mas é uma empresa de odontologia —
    # não pode virar previdência por causa disso.
    assert guesses["complementar_0"] == "recibos_saude"
    assert guesses["complementar_1"] == "previdencia_privada"
    assert guesses["complementar_2"] == "recibos_saude"
    # item 04 (nota sobre PLR) não tem palavra-chave de saúde nem previdência,
    # e sem AZURE_OPENAI_ENDPOINT/DEPLOYMENT configurados a LLM não roda.
    assert guesses["complementar_3"] is None


def test_complementary_items_skip_zero_value():
    text = _QUADRO_7_TEXT.replace("52,74", "0,00")
    matches = extract_fields_for_category("informe_empregador", text)
    fields = {m["field"] for m in matches}
    assert "complementar_0" not in fields  # item zerado é descartado
    # os demais itens continuam presentes (índice não reaproveitado por causa disso)
    assert any(f.startswith("complementar_") for f in fields)


def test_complementary_section_boundary_does_not_leak_into_next_quadro():
    matches = extract_fields_for_category("informe_empregador", _QUADRO_7_TEXT)
    labels = " ".join(m["label"] for m in matches if m["field"].startswith("complementar_"))
    assert "Responsável" not in labels


def test_complementary_items_run_for_any_category():
    matches = extract_fields_for_category("recibos_saude", _QUADRO_7_TEXT)
    assert any(m["field"].startswith("complementar_") for m in matches)


def test_llm_classification_skipped_without_env_vars(monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)
    from irpf_helper.document_extractor import _classify_ambiguous_items_with_llm

    assert _classify_ambiguous_items_with_llm([{"field": "x", "label": "y"}]) == {}
