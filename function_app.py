import json

import azure.functions as func

from document_checklist import get_checklist_definition
from document_extractor import MAX_FILES_PER_REQUEST, MAX_FILE_SIZE_BYTES, extract_from_files
from irpf_calc import compare_models
from report_generator import generate_excel_report, generate_pdf_report
from templates import HTML_PAGE

app = func.FunctionApp()


@app.route(route="home", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def home(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(HTML_PAGE, mimetype="text/html")


@app.route(route="api/calculate", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def calculate(req: func.HttpRequest) -> func.HttpResponse:
    try:
        payload = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "JSON inválido."}),
            mimetype="application/json",
            status_code=400,
        )

    if not payload:
        return func.HttpResponse(
            json.dumps({"error": "Body vazio."}),
            mimetype="application/json",
            status_code=400,
        )

    try:
        result = compare_models(payload)
    except ValueError as exc:
        return func.HttpResponse(
            json.dumps({"error": str(exc)}),
            mimetype="application/json",
            status_code=400,
        )

    return func.HttpResponse(
        json.dumps(result),
        mimetype="application/json",
        status_code=200,
    )


@app.route(route="api/checklist", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def checklist(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(get_checklist_definition()),
        mimetype="application/json",
        status_code=200,
    )


@app.route(route="api/report", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def report(req: func.HttpRequest) -> func.HttpResponse:
    try:
        payload = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "JSON inválido."}),
            mimetype="application/json",
            status_code=400,
        )

    fmt = (payload or {}).get("format")
    if fmt not in ("pdf", "xlsx"):
        return func.HttpResponse(
            json.dumps({"error": "Formato inválido. Use 'pdf' ou 'xlsx'."}),
            mimetype="application/json",
            status_code=400,
        )

    try:
        calc_result = compare_models(payload.get("calculation", {}))
    except ValueError as exc:
        return func.HttpResponse(
            json.dumps({"error": str(exc)}),
            mimetype="application/json",
            status_code=400,
        )

    checklist_state = payload.get("checklist", [])

    if fmt == "pdf":
        content = generate_pdf_report(calc_result, checklist_state)
        mimetype = "application/pdf"
        filename = "resumo-irpf.pdf"
    else:
        content = generate_excel_report(calc_result, checklist_state)
        mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "resumo-irpf.xlsx"

    return func.HttpResponse(
        content,
        mimetype=mimetype,
        status_code=200,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.route(route="api/extract", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def extract(req: func.HttpRequest) -> func.HttpResponse:
    category_id = req.form.get("categoryId") if req.form else None
    if not category_id:
        return func.HttpResponse(
            json.dumps({"error": "categoryId é obrigatório."}),
            mimetype="application/json",
            status_code=400,
        )

    uploaded = req.files.getlist("files")
    if not uploaded:
        return func.HttpResponse(
            json.dumps({"error": "Nenhum arquivo enviado."}),
            mimetype="application/json",
            status_code=400,
        )

    if len(uploaded) > MAX_FILES_PER_REQUEST:
        return func.HttpResponse(
            json.dumps({"error": f"Máximo de {MAX_FILES_PER_REQUEST} arquivos por vez."}),
            mimetype="application/json",
            status_code=400,
        )

    files_payload = []
    for uploaded_file in uploaded:
        content = uploaded_file.stream.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            return func.HttpResponse(
                json.dumps({"error": f"Arquivo '{uploaded_file.filename}' excede o tamanho máximo permitido."}),
                mimetype="application/json",
                status_code=400,
            )
        files_payload.append({"filename": uploaded_file.filename, "content": content})

    result = extract_from_files(category_id, files_payload)
    return func.HttpResponse(
        json.dumps(result),
        mimetype="application/json",
        status_code=200,
    )
