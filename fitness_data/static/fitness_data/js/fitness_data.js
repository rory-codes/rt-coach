(function () {
    const $ = (id) => document.getElementById(id);
    const LS_KEY = "tenrm_state_v1";

    /* ====== HR ZONES / BMI / WHR ====== */
    const ZONES = [
        { name: "Zone 1", low: 0.50, high: 0.60 },
        { name: "Zone 2", low: 0.60, high: 0.70 },
        { name: "Zone 3", low: 0.70, high: 0.80 },
        { name: "Zone 4", low: 0.80, high: 0.90 },
        { name: "Zone 5", low: 0.90, high: 1.00 }
    ];
    function toNum(v) { const n = parseFloat(v); return Number.isFinite(n) ? n : null; }
    function clamp(n, min, max) { if (!Number.isFinite(n)) return null; return Math.min(Math.max(n, min), max); }
    function calcBMI(w, h) { w = clamp(w, 0, 500); h = clamp(h, 30, 300); if (!Number.isFinite(w) || !Number.isFinite(h)) return null; const m = h / 100; return w / (m * m); }
    function bmiCategory(b) { if (b == null) return ""; if (b < 18.5) return "Underweight"; if (b < 25) return "Normal"; if (b < 30) return "Overweight"; return "Obese"; }
    function calcWHR(w, h) { w = clamp(w, 20, 300); h = clamp(h, 20, 300); if (!Number.isFinite(w) || !Number.isFinite(h) || h <= 0) return null; return w / h; }
    function calcMaxHR(a) { a = clamp(a, 1, 120); if (!Number.isFinite(a)) return null; return 220 - a; }
    function calcZones(a, r) {
        a = clamp(a, 1, 120); r = clamp(r, 20, 150);
        const m = calcMaxHR(a);
        if (!Number.isFinite(m) || !Number.isFinite(r) || r >= m) return { max: m ?? null, hrr: null, zones: [] };
        const hrr = m - r;
        const zones = ZONES.map(z => ({ ...z, lowBpm: Math.round(r + hrr * z.low), highBpm: Math.round(r + hrr * z.high) }));
        return { max: m, hrr, zones };
    }
    function renderBMI() {
        const b = calcBMI(toNum($("weightKg")?.value), toNum($("heightCm")?.value));
        if ($("bmiValue")) $("bmiValue").textContent = b ? b.toFixed(1) : "—";
        if ($("bmiNote")) $("bmiNote").textContent = b ? `(${bmiCategory(b)})` : "";
    }
    function renderWHR() {
        const v = calcWHR(toNum($("waistCm")?.value), toNum($("hipCm")?.value));
        if ($("whrValue")) $("whrValue").textContent = v ? v.toFixed(2) : "—";
    }
    function renderHRZones() {
        const { max, hrr, zones } = calcZones(toNum($("age")?.value), toNum($("rhr")?.value));
        if ($("maxHr")) $("maxHr").textContent = Number.isFinite(max) ? Math.round(max) : "—";
        if ($("hrr")) $("hrr").textContent = Number.isFinite(hrr) ? Math.round(hrr) : "—";
        const tb = $("zonesBody"); if (!tb) return;
        tb.innerHTML = "";
        if (!zones.length) {
            tb.innerHTML = `<tr><td colspan="3" class="text-muted">Enter valid age and resting heart rate (RHR &lt; Max HR) to see zones.</td></tr>`;
            return;
        }
        zones.forEach(z => {
            const tr = document.createElement("tr");
            tr.innerHTML = `<td>${z.name}</td><td>${Math.round(z.low * 100)}–${Math.round(z.high * 100)}%</td><td class="text-end">${z.lowBpm}–${z.highBpm} bpm</td>`;
            tb.appendChild(tr);
        });
    }

    /* ====== 10RM SECTION ====== */
    const EXERCISES = ["Chest Press", "Shoulder Press", "Lat Pull Down", "Seated Row", "Leg Press", "Deadlift", "Squat", "Upright Row", "Bicep Curl", "Tricep Pushdown"];
    const PHASES = { endurance: 0.60, hypertrophy: 0.72, strength: 0.85, power: 0.65 };
    function kgToLb(kg) { return kg * 2.2046226218; }
    function lbToKg(lb) { return lb / 2.2046226218; }
    function roundToIncrement(val, inc) { if (!Number.isFinite(val) || !Number.isFinite(inc) || inc <= 0) return null; return Math.round(val / inc) * inc; }
    function fmt(v, units) { if (!Number.isFinite(v)) return "—"; return (units === "lb" ? kgToLb(v) : v).toFixed(1); }

    function renderTenRmInputs() {
        const wrap = $("tenRmInputs"); if (!wrap) return;
        wrap.innerHTML = "";
        EXERCISES.forEach((name, idx) => {
            const id = `tenrm_${idx}`;
            const col = document.createElement("div");
            col.className = "col-sm-6 col-md-4 col-lg-3";
            col.innerHTML = `
        <div class="form-check form-switch mb-1">
          <input class="form-check-input include-switch" type="checkbox" id="inc_${id}" checked>
          <label class="form-check-label small" for="inc_${id}">Include</label>
        </div>
        <label class="form-label">${name} (10RM, kg)</label>
        <input type="number" min="0" step="0.5" class="form-control tenrm-input" id="${id}" placeholder="e.g. 40">
        <div class="form-text">Optional: leave blank to skip.</div>`;
            wrap.appendChild(col);
        });
    }

    function estimate1RMfrom10RM(tenrm) { if (!Number.isFinite(tenrm) || tenrm <= 0) return null; return tenrm * (1 + 10 / 30); }

    function readTenRmEntries() {
        return EXERCISES.map((name, idx) => {
            const v = parseFloat(($(`tenrm_${idx}`) || {}).value);
            const include = ($(`inc_tenrm_${idx}`) || $(`inc_${`tenrm_${idx}`}`))?.checked ?? true;
            return { name, tenrm: Number.isFinite(v) ? v : null, include };
        });
    }

    function computePhaseWeights(oneRm, incKg, units = "kg") {
        if (!Number.isFinite(oneRm)) return { endurance: null, hypertrophy: null, strength: null, power: null };
        const incDisplay = units === "lb" ? kgToLb(incKg) : incKg;
        const roundDisp = (kg) => {
            const disp = units === "lb" ? kgToLb(kg) : kg;
            const r = roundToIncrement(disp, incDisplay);
            return units === "lb" ? lbToKg(r) : r;
        };
        return {
            endurance: roundDisp(oneRm * PHASES.endurance),
            hypertrophy: roundDisp(oneRm * PHASES.hypertrophy),
            strength: roundDisp(oneRm * PHASES.strength),
            power: roundDisp(oneRm * PHASES.power)
        };
    }

    function updateTenRmHeaderUnits(units) {
        const ths = document.querySelectorAll("#tenrmTable thead th");
        if (ths.length >= 3) {
            ths[1].innerHTML = `10RM (${units})`;
            ths[2].innerHTML = `Est. 1RM (${units})`;
        }
    }

    function renderTenRmTable() {
        const rows = readTenRmEntries();
        const inc = parseFloat(($("incrementSelect") || {}).value) || 2.5;
        const units = (($("unitsSelect") || {}).value) || "kg";
        updateTenRmHeaderUnits(units);

        const tbody = $("tenrmTableBody"); if (!tbody) return;
        tbody.innerHTML = "";
        let any = false;

        rows.forEach(({ name, tenrm, include }) => {
            if (!include || !Number.isFinite(tenrm) || tenrm <= 0) return;
            any = true;
            const oneRm = estimate1RMfrom10RM(tenrm);
            const t = computePhaseWeights(oneRm, inc, units);
            const tr = document.createElement("tr");
            tr.innerHTML = `
        <td>${name}</td>
        <td class="text-end">${fmt(tenrm, units)}</td>
        <td class="text-end">${fmt(oneRm, units)}</td>
        <td class="text-end">${fmt(t.endurance, units)}</td>
        <td class="text-end">${fmt(t.hypertrophy, units)}</td>
        <td class="text-end">${fmt(t.strength, units)}</td>
        <td class="text-end">${fmt(t.power, units)}</td>`;
            tbody.appendChild(tr);
        });

        if (!any) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-muted">Enter any 10RM above and click Calculate.</td></tr>`;
        }
    }

    // persistence
    function saveState() {
        const inc = ($("incrementSelect") || {}).value;
        const units = ($("unitsSelect") || {}).value;
        const rows = EXERCISES.map((_, idx) => ({
            v: parseFloat(($(`tenrm_${idx}`) || {}).value),
            inc: ($(`inc_${`tenrm_${idx}`}`) || {}).checked
        }));
        try { localStorage.setItem(LS_KEY, JSON.stringify({ inc, units, rows })); } catch (_) { }
    }
    function loadState() {
        try {
            const raw = localStorage.getItem(LS_KEY);
            if (!raw) return;
            const data = JSON.parse(raw);
            if (data.inc && $("incrementSelect")) $("incrementSelect").value = data.inc;
            if (data.units && $("unitsSelect")) $("unitsSelect").value = data.units;
            data.rows?.forEach((r, idx) => {
                const input = $(`tenrm_${idx}`);
                const sw = $(`inc_${`tenrm_${idx}`}`);
                if (input && Number.isFinite(r.v)) input.value = r.v;
                if (sw != null && typeof r.inc === "boolean") sw.checked = r.inc;
            });
        } catch (e) { }
    }

    // CSV export
    function buildCsv() {
        const inc = parseFloat(($("incrementSelect") || {}).value) || 2.5;
        const units = (($("unitsSelect") || {}).value) || "kg";
        const rows = readTenRmEntries().filter(r => r.include && Number.isFinite(r.tenrm) && r.tenrm > 0);
        const header = ["Exercise", `10RM (${units})`, `Est 1RM (${units})`, `Endurance (${units})`, `Hypertrophy (${units})`, `Strength (${units})`, `Power (${units})`];
        const lines = [header.join(",")];
        rows.forEach(({ name, tenrm }) => {
            const oneRm = estimate1RMfrom10RM(tenrm);
            const t = computePhaseWeights(oneRm, inc, units);
            lines.push([name, fmt(tenrm, units), fmt(oneRm, units), fmt(t.endurance, units), fmt(t.hypertrophy, units), fmt(t.strength, units), fmt(t.power, units)].join(","));
        });
        return lines.join("\n");
    }

    /* ====== INIT + EVENTS ====== */
    function renderAllMetrics() { renderBMI(); renderWHR(); renderHRZones(); }

    // On DOM ready (defer in template ensures elements exist)
    renderTenRmInputs();
    loadState();

    // 10RM listeners
    document.addEventListener("input", (e) => {
        if (e.target.closest(".tenrm-input") || e.target.classList.contains("include-switch") || e.target.id === "incrementSelect" || e.target.id === "unitsSelect") {
            saveState();
            renderTenRmTable();
        }
    });
    document.addEventListener("change", (e) => {
        if (e.target.closest(".tenrm-input") || e.target.classList.contains("include-switch") || e.target.id === "incrementSelect" || e.target.id === "unitsSelect") {
            saveState();
            renderTenRmTable();
        }
    });

    $("calc10rmBtn")?.addEventListener("click", renderTenRmTable);
    $("clear10rmBtn")?.addEventListener("click", () => {
        localStorage.removeItem(LS_KEY);
        document.querySelectorAll(".tenrm-input").forEach(el => el.value = "");
        document.querySelectorAll(".include-switch").forEach(el => el.checked = true);
        if ($("incrementSelect")) $("incrementSelect").value = "2.5";
        if ($("unitsSelect")) $("unitsSelect").value = "kg";
        renderTenRmTable();
    });

    $("sample10rmBtn")?.addEventListener("click", () => {
        const samples = [40, 30, 45, 40, 140, 90, 80, 25, 15, 20]; // example kg values
        samples.forEach((v, i) => { const el = $(`tenrm_${i}`); if (el) el.value = v; });
        document.querySelectorAll(".include-switch").forEach(chk => chk.checked = true);
        saveState();
        renderTenRmTable();
    });
    $("reset10rmBtn")?.addEventListener("click", () => {
        localStorage.removeItem(LS_KEY);
        document.querySelectorAll(".tenrm-input").forEach(el => el.value = "");
        document.querySelectorAll(".include-switch").forEach(el => el.checked = true);
        if ($("incrementSelect")) $("incrementSelect").value = "2.5";
        if ($("unitsSelect")) $("unitsSelect").value = "kg";
        renderTenRmTable();
    });

    // CSV export
    $("downloadCsvBtn")?.addEventListener("click", () => {
        const csv = buildCsv();
        const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "training_weights.csv";
        document.body.appendChild(a); a.click(); a.remove();
    });

    // Personal metrics listeners
    $("calcBtn")?.addEventListener("click", renderAllMetrics);
    ["weightKg", "heightCm", "waistCm", "hipCm", "age", "rhr"].forEach(id => $(id)?.addEventListener("input", renderAllMetrics));
    $("clearBtn")?.addEventListener("click", () => { ["weightKg", "heightCm", "waistCm", "hipCm", "age", "rhr"].forEach(id => $(id).value = ""); renderAllMetrics(); });

    // Initial paints
    renderAllMetrics();
    renderTenRmTable();
})();
