from document_extractor import extract_fields_for_category, parse_brl_number


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
