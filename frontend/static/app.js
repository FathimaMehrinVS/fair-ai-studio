/* ═══════════════════════════════════════════
   FairAI Studio — Dashboard JavaScript
   Member 4: Platform Architect
   ═══════════════════════════════════════════ */

const API = '';  // same origin
let summaryData = null;
let gaugesLoaded = false;
let generator = null;

/* ── Utility ── */
const $ = id => document.getElementById(id);
const pct = v => (v * 100).toFixed(1) + '%';
const fmt4 = v => (typeof v === 'number' ? v.toFixed(4) : '—');
const img = (b64) => `<img src="data:image/png;base64,${b64}" alt="chart" style="width:100%;border-radius:8px;" />`;

/* ══════════════════════
   1. NAVIGATION
══════════════════════ */
const sections = ['overview', 'audit', 'mitigation', 'explainability', 'data', 'predict'];

function activateSection(id) {
  sections.forEach(s => {
    const sec = document.getElementById(s);
    const nav = document.getElementById('nav-' + s);
    if (s === id) {
      sec.classList.add('active-section');
      nav && nav.classList.add('active');
    } else {
      sec.classList.remove('active-section');
      nav && nav.classList.remove('active');
    }
  });
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

document.querySelectorAll('.nav-item').forEach(el => {
  el.addEventListener('click', e => {
    e.preventDefault();
    const target = el.getAttribute('href').replace('#', '');
    activateSection(target);
    if (target === 'data') loadDataSection();
    if (target === 'audit') loadAuditSection();
    if (target === 'mitigation') loadMitigationSection();
    if (target === 'explainability') loadExplainabilitySection();
  });
});

/* ══════════════════════
   2. FETCH HELPERS
══════════════════════ */
async function fetchJSON(url) {
  const res = await fetch(API + url);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

/* ══════════════════════
   3. OVERVIEW / SUMMARY
══════════════════════ */
async function loadOverview() {
  try {
    summaryData = await fetchJSON('/api/summary');
    const { comparison, audit } = summaryData;
    const fm = comparison.fair_model;
    const bm = comparison.biased_model;

    // KPI Cards
    $('kv-improvement').textContent = comparison.improvement_score_pct.toFixed(1) + '%';
    $('kv-accuracy').textContent = pct(fm.accuracy);
    $('kv-accuracy-biased').textContent = pct(bm.accuracy);
    $('kv-di').textContent = fmt4(fm.fairness_metrics.disparate_impact);
    $('kv-di-biased').textContent = fmt4(audit.disparate_impact);
    $('kv-spd').textContent = fmt4(fm.fairness_metrics.statistical_parity_difference);
    $('kv-spd-biased').textContent = fmt4(audit.statistical_parity_difference);

    ['kpi-improvement', 'kpi-accuracy', 'kpi-di', 'kpi-spd'].forEach(id => {
      document.getElementById(id).classList.remove('loading');
    });

    loadGauges();
  } catch (err) {
    console.error('loadOverview:', err);
  }
}

async function loadGauges() {
  if (gaugesLoaded) return;
  try {
    const gauges = await fetchJSON('/api/charts/gauges');
    $('gauge-di-biased').innerHTML = img(gauges.di_biased);
    $('gauge-di-fair').innerHTML = img(gauges.di_fair);
    $('gauge-spd-biased').innerHTML = img(gauges.spd_biased);
    $('gauge-spd-fair').innerHTML = img(gauges.spd_fair);
    gaugesLoaded = true;
  } catch (err) {
    console.error('loadGauges:', err);
    ['gauge-di-biased', 'gauge-di-fair', 'gauge-spd-biased', 'gauge-spd-fair'].forEach(id => {
      $(id).innerHTML = '<span style="color:var(--text2);font-size:12px;">Chart unavailable</span>';
    });
  }
}

/* ══════════════════════
   4. AUDIT SECTION
══════════════════════ */
let auditLoaded = false;
async function loadAuditSection() {
  if (auditLoaded) return;
  try {
    if (!summaryData) summaryData = await fetchJSON('/api/summary');
    const { comparison, audit } = summaryData;
    const fm = comparison.fair_model.fairness_metrics;
    const bm = comparison.biased_model.fairness_metrics;

    // Build metrics table
    const rows = [
      {
        label: 'Disparate Impact',
        biased: bm.disparate_impact,
        fair: fm.disparate_impact,
        ideal: 1.0,
        better: Math.abs(fm.disparate_impact - 1) < Math.abs(bm.disparate_impact - 1),
      },
      {
        label: 'Statistical Parity Difference',
        biased: bm.statistical_parity_difference,
        fair: fm.statistical_parity_difference,
        ideal: 0.0,
        better: Math.abs(fm.statistical_parity_difference) < Math.abs(bm.statistical_parity_difference),
      },
      {
        label: 'Equal Opportunity Difference',
        biased: bm.equal_opportunity_difference,
        fair: fm.equal_opportunity_difference,
        ideal: 0.0,
        better: Math.abs(fm.equal_opportunity_difference) < Math.abs(bm.equal_opportunity_difference),
      },
      {
        label: 'Selection Rate — Male (Privileged)',
        biasedPct: bm.selection_rate_privileged,
        fairPct: fm.selection_rate_privileged,
        isRate: true,
      },
      {
        label: 'Selection Rate — Female (Unprivileged)',
        biasedPct: bm.selection_rate_unprivileged,
        fairPct: fm.selection_rate_unprivileged,
        isRate: true,
      },
    ];

    const tbody = $('metrics-tbody');
    tbody.innerHTML = rows.map(r => {
      // ── Selection rate rows (special rendering) ──
      if (r.isRate) {
        const bPct = (r.biasedPct * 100).toFixed(1) + '%';
        const fPct = (r.fairPct * 100).toFixed(1) + '%';
        const delta = ((r.fairPct - r.biasedPct) * 100).toFixed(2);
        const deltaColor = Math.abs(parseFloat(delta)) < 0.5 ? 'var(--green)' : 'var(--yellow)';
        const deltaStr = parseFloat(delta) >= 0 ? `+${delta}%` : `${delta}%`;
        const fillW = (r.fairPct * 100).toFixed(1);
        return `<tr>
          <td style="font-family:'Inter',sans-serif;font-weight:600">${r.label}</td>
          <td><span style="font-family:'JetBrains Mono',monospace">${bPct}</span></td>
          <td>
            <div style="display:flex;align-items:center;gap:8px">
              <div style="flex:1;height:6px;background:var(--bg3);border-radius:3px;overflow:hidden;min-width:60px">
                <div style="width:${fillW}%;height:100%;background:var(--green);border-radius:3px;transition:width .6s"></div>
              </div>
              <strong style="color:var(--green);font-family:'JetBrains Mono',monospace;white-space:nowrap">${fPct}</strong>
            </div>
          </td>
          <td style="color:var(--accent)">Equal</td>
          <td><span class="badge badge-yellow">📊 Base Stat</span></td>
          <td><span style="color:${deltaColor};font-family:'JetBrains Mono',monospace">${deltaStr}</span></td>
        </tr>`;
      }

      // ── Standard fairness metric rows ──
      const change = typeof r.ideal === 'number'
        ? (Math.abs(r.fair - r.ideal) - Math.abs(r.biased - r.ideal)).toFixed(4)
        : '—';
      const changeStr = change !== '—'
        ? (parseFloat(change) < 0
          ? `<span style="color:var(--green)">${change}</span>`
          : `<span style="color:var(--orange)">+${change}</span>`)
        : '—';

      let statusBadge = '—';
      if (r.better === true) statusBadge = '<span class="badge badge-green">✓ Improved</span>';
      if (r.better === false) statusBadge = '<span class="badge badge-red">✗ Regressed</span>';

      return `<tr>
        <td style="font-family:'Inter',sans-serif;font-weight:600">${r.label}</td>
        <td>${fmt4(r.biased)}</td>
        <td><strong style="color:var(--green)">${fmt4(r.fair)}</strong></td>
        <td style="color:var(--accent)">${r.ideal}</td>
        <td>${statusBadge}</td>
        <td>${changeStr}</td>
      </tr>`;
    }).join('');

    // Selection rate chart
    const sr = await fetchJSON('/api/charts/selection-rates');
    $('chart-selection-rates').innerHTML = img(sr.chart);

    auditLoaded = true;
  } catch (err) {
    console.error('loadAuditSection:', err);
  }
}

/* ══════════════════════
   5. MITIGATION SECTION
══════════════════════ */
let mitigationLoaded = false;
async function loadMitigationSection() {
  if (mitigationLoaded) return;
  try {
    if (!summaryData) summaryData = await fetchJSON('/api/summary');
    const { comparison } = summaryData;
    const fm = comparison.fair_model;
    const bm = comparison.biased_model;

    // Banner
    $('ib-score').textContent = comparison.improvement_score_pct.toFixed(2) + '%';

    // Stats
    $('biased-acc').textContent = pct(bm.accuracy);
    $('biased-f1').textContent = fmt4(bm.f1_score);
    $('biased-di').textContent = fmt4(bm.fairness_metrics.disparate_impact);
    $('biased-spd').textContent = fmt4(bm.fairness_metrics.statistical_parity_difference);
    $('biased-eod').textContent = fmt4(bm.fairness_metrics.equal_opportunity_difference);

    $('fair-acc').textContent = pct(fm.accuracy);
    $('fair-f1').textContent = fmt4(fm.f1_score);
    $('fair-di').textContent = fmt4(fm.fairness_metrics.disparate_impact);
    $('fair-spd').textContent = fmt4(fm.fairness_metrics.statistical_parity_difference);
    $('fair-eod').textContent = fmt4(fm.fairness_metrics.equal_opportunity_difference);

    // Chart
    const chart = await fetchJSON('/api/charts/metrics-comparison');
    $('chart-metrics-comparison').innerHTML = img(chart.chart);

    mitigationLoaded = true;
  } catch (err) {
    console.error('loadMitigationSection:', err);
  }
}

/* ══════════════════════
   6. EXPLAINABILITY
══════════════════════ */
let xaiLoaded = false;
async function loadExplainabilitySection() {
  if (xaiLoaded) return;
  try {
    const [shap, fi] = await Promise.all([
      fetchJSON('/api/charts/shap'),
      fetchJSON('/api/charts/feature-importance'),
    ]);
    $('chart-shap').innerHTML = img(shap.chart);
    $('chart-feature-importance').innerHTML = img(fi.chart);
    xaiLoaded = true;
  } catch (err) {
    console.error('loadExplainabilitySection:', err);
    $('chart-shap').innerHTML = '<p style="color:var(--text2);font-size:12px;padding:20px;">Run <code>python bias_auditor.py</code> first to generate SHAP plots.</p>';
  }
}

/* ══════════════════════
   7. DATASET SECTION
══════════════════════ */
let dataLoaded = false;
async function loadDataSection() {
  if (dataLoaded) return;
  try {
    const stats = await fetchJSON('/api/dataset/stats');

    $('ds-total').textContent = stats.total.toLocaleString();
    $('ds-male').textContent = stats.gender_distribution['Male (1)'].toLocaleString();
    $('ds-female').textContent = stats.gender_distribution['Female (0)'].toLocaleString();
    $('ds-male-rate').textContent = pct(stats.shortlisted_rate_by_gender.Male);
    $('ds-female-rate').textContent = pct(stats.shortlisted_rate_by_gender.Female);

    // Feature stats table
    const feats = [
      { name: 'Age', s: stats.age },
      { name: 'Experience Yrs', s: stats.experience_years },
      { name: 'Screening Score', s: stats.screening_score },
    ];
    $('feat-stats-body').innerHTML = feats.map(f => `<tr>
      <td style="font-family:'Inter',sans-serif">${f.name}</td>
      <td>${f.s.mean}</td><td>${f.s.min}</td><td>${f.s.max}</td>
    </tr>`).join('');

    // Education bar chart
    const eduLabels = {
      '0': 'Level 0 – Basic',
      '1': 'Level 1 – Diploma',
      '2': 'Level 2 – Bachelor\'s',
      '3': 'Level 3 – Master\'s',
      '4': 'Level 4 – PhD',
    };
    const edu = stats.education_distribution;
    const maxEdu = Math.max(...Object.values(edu));
    $('edu-bars').innerHTML = Object.entries(edu).sort((a, b) => a[0] - b[0]).map(([k, v]) => `
      <div class="edu-bar-row">
        <div class="edu-bar-label">
          <span>${eduLabels[k] || 'Level ' + k}</span>
          <span style="font-family:'JetBrains Mono',monospace;font-size:11px">${v}</span>
        </div>
        <div class="edu-bar-track">
          <div class="edu-bar-fill" style="width:${(v / maxEdu * 100).toFixed(1)}%"></div>
        </div>
      </div>
    `).join('');

    // Load feature distributions chart
    const distChart = await fetchJSON('/api/charts/distributions');
    $('chart-distributions').innerHTML = img(distChart.chart);

    dataLoaded = true;
  } catch (err) {
    console.error('loadDataSection:', err);
  }
}

/* ══════════════════════
   8. LIVE PREDICTOR
══════════════════════ */
// Range live values
const rangeMap = { 'input-age': 'age-val', 'input-exp': 'exp-val', 'input-score': 'score-val' };
Object.entries(rangeMap).forEach(([id, labelId]) => {
  const el = $(id);
  el.addEventListener('input', () => {
    $(labelId).textContent = id === 'input-score'
      ? parseFloat(el.value).toFixed(1)
      : el.value;
  });
});

$('predict-form').addEventListener('submit', async e => {
  e.preventDefault();
  const btn = $('btn-predict');
  btn.disabled = true;
  btn.textContent = '⏳ Predicting...';

  const data = {
    gender: parseInt($('input-gender').value),
    age: parseInt($('input-age').value),
    education_level: parseInt($('input-edu').value),
    experience_years: parseInt($('input-exp').value),
    screening_score: parseFloat($('input-score').value),
  };

  try {
    const res = await fetch(API + '/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    const result = await res.json();
    displayPrediction(result);
  } catch (err) {
    alert('Prediction failed: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = '⚡ Run Prediction';
  }
});

function displayPrediction(result) {
  $('predict-placeholder').classList.add('hidden');
  $('predict-output').classList.remove('hidden');

  const agree = result.biased_model.prediction === result.fair_model.prediction;

  // Verdict
  const verdict = $('predict-verdict');
  verdict.textContent = result.verdict;
  verdict.style.background = agree ? 'rgba(63,185,80,.1)' : 'rgba(247,129,102,.1)';
  verdict.style.color = agree ? 'var(--green)' : 'var(--orange)';

  // Biased
  const bPred = result.biased_model.prediction;
  const bProb = result.biased_model.probability;
  $('mc-biased-pred').textContent = bPred === 1 ? '✅ SELECTED' : '❌ REJECTED';
  $('mc-biased-pred').className = 'mc-pred ' + (bPred === 1 ? 'selected' : 'rejected');
  $('mc-biased-bar').style.width = (bProb * 100).toFixed(1) + '%';
  $('mc-biased-prob').textContent = (bProb * 100).toFixed(1) + '%';

  // Fair
  const fPred = result.fair_model.prediction;
  const fProb = result.fair_model.probability;
  $('mc-fair-pred').textContent = fPred === 1 ? '✅ SELECTED' : '❌ REJECTED';
  $('mc-fair-pred').className = 'mc-pred ' + (fPred === 1 ? 'selected' : 'rejected');
  $('mc-fair-bar').style.width = (fProb * 100).toFixed(1) + '%';
  $('mc-fair-prob').textContent = (fProb * 100).toFixed(1) + '%';

  // Alert
  const alert = $('bias-alert');
  alert.classList.add('show');
  if (!agree) {
    alert.className = 'bias-alert show disagree';
    alert.textContent = '⚠️ Models disagree! The biased model may be discriminating on this candidate.';
  } else {
    alert.className = 'bias-alert show agree';
    alert.textContent = '✓ Both models agree on this candidate.';
  }
}

// Quick scenarios
function loadScenario(gender, age, edu, exp, score) {
  $('input-gender').value = gender;
  $('input-age').value = age;
  $('age-val').textContent = age;
  $('input-edu').value = edu;
  $('input-exp').value = exp;
  $('exp-val').textContent = exp;
  $('input-score').value = score;
  $('score-val').textContent = score + '.0';
  $('predict-form').dispatchEvent(new Event('submit'));
}

/* ══════════════════════
   INIT
══════════════════════ */
window.addEventListener('DOMContentLoaded', () => {
  loadOverview();
});

/* ══════════════════════
   9. GEMINI POWERED AUDITOR (STABLE)
   ══════════════════════ */
async function generateSmartReport() {
  const btn = $('btn-ai');
  const content = $('ai-content');

  if (!summaryData) {
    content.innerHTML = '⚠️ Data not loaded yet. Please refresh the dashboard.';
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<div class="spinner" style="width:14px;height:14px;margin:0 auto;border-top-color:var(--accent)"></div> Consulting Gemini...';

  try {
    const fm = summaryData.comparison.fair_model;
    const audit = summaryData.comparison.biased_model;

    const payload = {
      di: fm.fairness_metrics.disparate_impact.toFixed(3),
      improvement: summaryData.comparison.improvement_score_pct.toFixed(1),
      initial_di: audit.disparate_impact.toFixed(3)
    };

    const res = await fetch('/api/ai/insight', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const result = await res.json();

    if (result.error) {
      content.innerHTML = `<span style="color:var(--orange)">⚠️ ${result.error}. Verify <code>GEMINI_API_KEY</code> in .env.</span>`;
      btn.textContent = '📊 Retry Audit';
      btn.disabled = false;
    } else {
      const text = result.insight;
      content.innerHTML = '';
      let i = 0;
      const type = () => {
        if (i < text.length) {
          content.innerHTML += text.charAt(i);
          i++;
          setTimeout(type, 20);
        } else {
          btn.textContent = '🔄 Regenerate (Gemini 1.5)';
          btn.disabled = false;
        }
      };
      type();
    }
  } catch (err) {
    console.error('Gemini error:', err);
    content.innerHTML = '⚠️ Connection failed. Check server logs.';
    btn.disabled = false;
    btn.textContent = '📊 Retry Audit';
  }
}
