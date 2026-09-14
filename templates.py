HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>IRPF Helper</title>
  <style>
    :root {
      --bg: #f4f7fb;
      --panel: #ffffff;
      --primary: #0f5bd9;
      --primary-dark: #0b3e93;
      --accent: #1ba97f;
      --text: #1e293b;
      --muted: #64748b;
      --border: #dfe7f1;
      --danger: #c92a2a;
      --shadow: 0 18px 38px rgba(15, 91, 217, 0.12);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: Arial, sans-serif;
      background: linear-gradient(180deg, #edf5ff 0%, var(--bg) 100%);
      color: var(--text);
    }

    .container {
      max-width: 1100px;
      margin: 0 auto;
      padding: 32px 20px 60px;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 28px;
      gap: 16px;
      flex-wrap: wrap;
    }

    h1 {
      margin: 0;
      font-size: clamp(2rem, 4vw, 3rem);
    }

    .badge {
      background: rgba(15, 91, 217, 0.08);
      color: var(--primary-dark);
      border: 1px solid rgba(15, 91, 217, 0.18);
      padding: 10px 14px;
      border-radius: 999px;
      font-weight: 700;
      font-size: 0.85rem;
    }

    .grid {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 28px;
      margin-bottom: 28px;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      box-shadow: var(--shadow);
      padding: 24px;
      margin-bottom: 28px;
    }

    .panel h2 {
      margin-top: 0;
      margin-bottom: 18px;
      font-size: 1.35rem;
    }

    .row {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 12px;
    }

    label {
      display: block;
      font-weight: 700;
      font-size: 0.9rem;
      margin-bottom: 6px;
      color: var(--text);
    }

    input {
      width: 100%;
      padding: 12px 14px;
      border: 1px solid var(--border);
      border-radius: 12px;
      font-size: 1rem;
      background: #f8fbff;
    }

    input:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(15, 91, 217, 0.12);
    }

    .button-wrap {
      margin-top: 18px;
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }

    button {
      background: var(--primary);
      color: white;
      border: none;
      border-radius: 12px;
      padding: 12px 18px;
      font-size: 1rem;
      font-weight: 700;
      cursor: pointer;
      transition: 0.2s ease;
    }

    button:hover {
      background: var(--primary-dark);
    }

    button:disabled {
      background: #b7c6dd;
      cursor: not-allowed;
    }

    .secondary {
      background: #eef6f3;
      color: #0f6d54;
    }

    .secondary:hover {
      background: #e1f5ee;
    }

    .comparison-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }

    .card {
      background: #f8fbff;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 12px;
    }

    .card strong {
      display: block;
      font-size: 0.75rem;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 8px;
    }

    .value {
      font-size: clamp(1.1rem, 2vw, 1.6rem);
      font-weight: 800;
      color: var(--text);
    }

    .value.negative {
      color: var(--danger);
    }

    .model-column h3 {
      margin: 0 0 12px;
      font-size: 1.05rem;
    }

    #comparison-banner {
      margin-top: 18px;
      padding: 14px 18px;
      border-radius: 12px;
      font-weight: 700;
      background: rgba(27, 169, 127, 0.12);
      color: #0f6d54;
      border: 1px solid rgba(27, 169, 127, 0.3);
    }

    .note {
      margin-top: 18px;
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.5;
    }

    .checklist-group {
      margin-bottom: 18px;
    }

    .checklist-group h3 {
      font-size: 0.95rem;
      color: var(--primary-dark);
      margin-bottom: 10px;
    }

    .checklist-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 12px;
      border: 1px solid var(--border);
      border-radius: 10px;
      margin-bottom: 8px;
      background: #f8fbff;
      flex-wrap: wrap;
    }

    .checklist-item input[type="checkbox"] {
      width: auto;
    }

    .checklist-item label {
      margin-bottom: 0;
      flex: 1;
      min-width: 200px;
      font-weight: 600;
    }

    .checklist-item input[type="file"] {
      flex: 1;
      min-width: 180px;
      padding: 6px;
      background: white;
    }

    .checklist-item .file-list {
      flex-basis: 100%;
      font-size: 0.82rem;
      color: var(--muted);
      margin-top: 4px;
    }

    .privacy-note {
      background: rgba(15, 91, 217, 0.06);
      border: 1px dashed rgba(15, 91, 217, 0.3);
      border-radius: 12px;
      padding: 14px;
      font-size: 0.88rem;
      color: var(--primary-dark);
      margin-bottom: 18px;
    }

    .guide-list {
      padding-left: 22px;
      line-height: 1.8;
    }

    .hidden {
      display: none;
    }

    @media (max-width: 820px) {
      .grid, .row, .comparison-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>IRPF Helper</h1>
      <div class="badge">Estimativa simplificada</div>
    </div>

    <div class="grid">
      <section class="panel" style="margin-bottom: 0;">
        <h2>Dados do ano</h2>
        <form id="irpf-form">
          <div class="row">
            <div>
              <label for="salary">Salário bruto mensal</label>
              <input id="salary" name="salary" type="number" min="0" step="0.01" value="7000" required />
            </div>
            <div>
              <label for="extraIncome">Rendimentos extras anuais</label>
              <input id="extraIncome" name="extraIncome" type="number" min="0" step="0.01" value="0" />
            </div>
          </div>

          <div class="row">
            <div>
              <label for="deductions">Deduções gerais</label>
              <input id="deductions" name="deductions" type="number" min="0" step="0.01" value="0" />
            </div>
            <div>
              <label for="inss">Contribuição INSS</label>
              <input id="inss" name="inss" type="number" min="0" step="0.01" value="0" />
            </div>
          </div>

          <div class="row">
            <div>
              <label for="dependents">Número de dependentes</label>
              <input id="dependents" name="dependents" type="number" min="0" step="1" value="0" />
            </div>
            <div>
              <label for="pension">Pensão alimentícia / outros descontos</label>
              <input id="pension" name="pension" type="number" min="0" step="0.01" value="0" />
            </div>
          </div>

          <div class="button-wrap">
            <button type="submit">Calcular IRPF</button>
            <button type="button" class="secondary" id="fill-example">Usar exemplo</button>
          </div>
        </form>

        <div class="note">
          Este é um cálculo técnico simplificado para apoio de planejamento. Não substitui a orientação de um contador ou a declaração oficial do IRPF.
        </div>
      </section>

      <aside class="panel" style="margin-bottom: 0;">
        <h2>Comparação de modelos</h2>
        <div class="comparison-grid">
          <div class="model-column">
            <h3>Desconto Simplificado</h3>
            <div class="card">
              <strong>Base tributável</strong>
              <div class="value" id="simplified-base">R$ 0,00</div>
            </div>
            <div class="card">
              <strong>Imposto estimado</strong>
              <div class="value negative" id="simplified-tax">R$ 0,00</div>
            </div>
            <div class="card">
              <strong>Alíquota efetiva</strong>
              <div class="value" id="simplified-rate">0,00%</div>
            </div>
          </div>
          <div class="model-column">
            <h3>Deduções Completas</h3>
            <div class="card">
              <strong>Base tributável</strong>
              <div class="value" id="complete-base">R$ 0,00</div>
            </div>
            <div class="card">
              <strong>Imposto estimado</strong>
              <div class="value negative" id="complete-tax">R$ 0,00</div>
            </div>
            <div class="card">
              <strong>Alíquota efetiva</strong>
              <div class="value" id="complete-rate">0,00%</div>
            </div>
          </div>
        </div>
        <div id="comparison-banner" class="hidden"></div>

        <div class="button-wrap">
          <button type="button" id="download-pdf" disabled>Baixar PDF</button>
          <button type="button" class="secondary" id="download-xlsx" disabled>Baixar Excel</button>
        </div>
      </aside>
    </div>

    <section class="panel" id="checklist-panel">
      <h2>Organizador de Documentos</h2>
      <div class="privacy-note">
        Você pode anexar mais de um arquivo por categoria. Os arquivos ficam apenas no seu navegador durante esta sessão — nada é enviado nem armazenado no servidor. Apenas os nomes dos arquivos são incluídos no relatório final.
      </div>
      <div id="checklist-container"></div>
    </section>

    <section class="panel" id="guide-panel">
      <h2>Guia Passo a Passo — Programa da Receita</h2>
      <ol class="guide-list">
        <li>Baixe o programa do Imposto de Renda mais recente no site oficial da Receita Federal.</li>
        <li>Se já declarou antes, importe a declaração do ano anterior para agilizar o preenchimento.</li>
        <li>Preencha seus dados pessoais e informe os dependentes na ficha correspondente.</li>
        <li>Lance os rendimentos tributáveis com base nos informes de rendimentos do empregador, bancos e corretoras.</li>
        <li>Informe pagamentos e recebimentos de aluguel, se houver.</li>
        <li>Preencha as deduções (saúde, educação, previdência privada, pensão) na ficha de pagamentos efetuados.</li>
        <li>Use a comparação acima para decidir entre o desconto simplificado e as deduções completas.</li>
        <li>Preencha a ficha de bens e direitos com a posição em 31/12 do ano anterior e do ano corrente.</li>
        <li>Revise o resumo da declaração e confira se não há pendências indicadas pelo programa.</li>
        <li>Transmita a declaração e guarde o recibo de entrega.</li>
      </ol>
    </section>
  </div>

  <script>
    const form = document.getElementById('irpf-form');
    const fillExampleBtn = document.getElementById('fill-example');
    const downloadPdfBtn = document.getElementById('download-pdf');
    const downloadXlsxBtn = document.getElementById('download-xlsx');
    const checklistContainer = document.getElementById('checklist-container');

    let lastCalculationInputs = null;
    let checklistCategories = [];

    function formatMoney(value) {
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      }).format(value);
    }

    const RECOMMENDED_LABELS = {
      simplified: 'Desconto Simplificado',
      complete: 'Deduções Completas',
      equal: 'Empate entre os modelos'
    };

    function setComparison(data) {
      document.getElementById('simplified-base').textContent = formatMoney(data.simplified.taxable_base);
      document.getElementById('simplified-tax').textContent = formatMoney(data.simplified.tax_amount);
      document.getElementById('simplified-rate').textContent = `${Number(data.simplified.effective_rate).toFixed(2)}%`;

      document.getElementById('complete-base').textContent = formatMoney(data.complete.taxable_base);
      document.getElementById('complete-tax').textContent = formatMoney(data.complete.tax_amount);
      document.getElementById('complete-rate').textContent = `${Number(data.complete.effective_rate).toFixed(2)}%`;

      const banner = document.getElementById('comparison-banner');
      banner.classList.remove('hidden');
      if (data.recommended === 'equal') {
        banner.textContent = 'Os dois modelos resultam no mesmo imposto estimado.';
      } else {
        const label = RECOMMENDED_LABELS[data.recommended];
        banner.textContent = `${label} compensa mais e economiza ${formatMoney(data.difference)}.`;
      }

      downloadPdfBtn.disabled = false;
      downloadXlsxBtn.disabled = false;
    }

    function currentFormValues() {
      return {
        salary: Number(document.getElementById('salary').value || 0),
        extraIncome: Number(document.getElementById('extraIncome').value || 0),
        deductions: Number(document.getElementById('deductions').value || 0),
        inss: Number(document.getElementById('inss').value || 0),
        dependents: Number(document.getElementById('dependents').value || 0),
        pension: Number(document.getElementById('pension').value || 0),
      };
    }

    form.addEventListener('submit', async (event) => {
      event.preventDefault();

      const payload = currentFormValues();

      const response = await fetch('/api/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (!response.ok) {
        alert(data.error || 'Erro ao calcular.');
        return;
      }

      lastCalculationInputs = payload;
      setComparison(data);
    });

    fillExampleBtn.addEventListener('click', () => {
      document.getElementById('salary').value = 8500;
      document.getElementById('extraIncome').value = 15000;
      document.getElementById('deductions').value = 1200;
      document.getElementById('inss').value = 1800;
      document.getElementById('dependents').value = 1;
      document.getElementById('pension').value = 0;
      form.requestSubmit();
    });

    function renderChecklist(categories) {
      const groups = {};
      categories.forEach((category) => {
        if (!groups[category.group]) {
          groups[category.group] = [];
        }
        groups[category.group].push(category);
      });

      checklistContainer.innerHTML = '';
      Object.keys(groups).forEach((groupName) => {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'checklist-group';

        const heading = document.createElement('h3');
        heading.textContent = groupName;
        groupDiv.appendChild(heading);

        groups[groupName].forEach((category) => {
          const item = document.createElement('div');
          item.className = 'checklist-item';

          const checkbox = document.createElement('input');
          checkbox.type = 'checkbox';
          checkbox.id = `check-${category.id}`;
          checkbox.dataset.categoryId = category.id;

          const label = document.createElement('label');
          label.setAttribute('for', checkbox.id);
          label.textContent = category.label;

          const fileInput = document.createElement('input');
          fileInput.type = 'file';
          fileInput.multiple = true;
          fileInput.dataset.categoryId = category.id;

          const fileList = document.createElement('div');
          fileList.className = 'file-list';
          fileList.dataset.categoryId = category.id;

          fileInput.addEventListener('change', () => {
            const names = Array.from(fileInput.files).map((file) => file.name);
            fileList.textContent = names.length > 0 ? names.join(', ') : '';
          });

          item.appendChild(checkbox);
          item.appendChild(label);
          item.appendChild(fileInput);
          item.appendChild(fileList);
          groupDiv.appendChild(item);
        });

        checklistContainer.appendChild(groupDiv);
      });
    }

    function collectChecklistState() {
      return checklistCategories.map((category) => {
        const checkbox = document.querySelector(`input[type="checkbox"][data-category-id="${category.id}"]`);
        const fileInput = document.querySelector(`input[type="file"][data-category-id="${category.id}"]`);
        return {
          id: category.id,
          checked: checkbox ? checkbox.checked : false,
          fileNames: fileInput ? Array.from(fileInput.files).map((file) => file.name) : [],
        };
      });
    }

    async function loadChecklist() {
      const response = await fetch('/api/checklist');
      checklistCategories = await response.json();
      renderChecklist(checklistCategories);
    }

    async function downloadReport(format) {
      if (!lastCalculationInputs) {
        alert('Calcule o IRPF antes de baixar o relatório.');
        return;
      }

      const payload = {
        calculation: lastCalculationInputs,
        checklist: collectChecklistState(),
        format,
      };

      const response = await fetch('/api/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json();
        alert(data.error || 'Erro ao gerar relatório.');
        return;
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = format === 'pdf' ? 'resumo-irpf.pdf' : 'resumo-irpf.xlsx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }

    downloadPdfBtn.addEventListener('click', () => downloadReport('pdf'));
    downloadXlsxBtn.addEventListener('click', () => downloadReport('xlsx'));

    loadChecklist();
  </script>
</body>
</html>
"""
