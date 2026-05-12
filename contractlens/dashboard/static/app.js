(() => {
  const $ = (sel) => document.querySelector(sel);

  let reportLoadedForRun = "";

  function selectedRunId() {
    const sel = $("#run-select");
    if (!sel || !sel.value) return "latest";
    return sel.value;
  }

  function riskClass(r) {
    const x = String(r || "").toLowerCase();
    if (x === "high") return "risk-high";
    if (x === "medium") return "risk-medium";
    if (x === "low") return "risk-low";
    return "";
  }

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function qRun(runId) {
    const r = encodeURIComponent(runId || "latest");
    return `run_id=${r}`;
  }

  async function fetchRunsList() {
    const res = await fetch("/api/runs?limit=100");
    if (!res.ok) throw new Error("runs list failed");
    return res.json();
  }

  async function loadSnapshot(runId) {
    const res = await fetch(`/api/snapshot?${qRun(runId)}`);
    if (!res.ok) throw new Error("snapshot failed");
    return res.json();
  }

  async function populateRunSelect() {
    const sel = $("#run-select");
    if (!sel) return;
    sel.innerHTML = "";
    let meta = { latest_run_id: "", runs: [] };
    try {
      meta = await fetchRunsList();
    } catch (_) {
      /* ignore */
    }
    const optLatest = document.createElement("option");
    optLatest.value = "latest";
    optLatest.textContent = meta.latest_run_id
      ? `latest (${meta.latest_run_id})`
      : "latest";
    sel.appendChild(optLatest);
    (meta.runs || []).forEach((row) => {
      if (!row || !row.run_id) return;
      const o = document.createElement("option");
      o.value = row.run_id;
      const mc = row.mismatch_count != null ? ` · ${row.mismatch_count} mm` : "";
      let probe = "";
      if (row.runtime_probe_configured) probe = row.runtime_probe_ok ? " · probe ✓" : " · probe ✗";
      o.textContent = `${row.run_id}${mc}${probe}`;
      sel.appendChild(o);
    });
  }

  function wireTabs() {
    document.querySelectorAll(".tab").forEach((btn) => {
      btn.addEventListener("click", () => {
        const name = btn.getAttribute("data-tab");
        document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("active", b === btn));
        document.querySelectorAll(".panel").forEach((p) => {
          p.classList.toggle("active", p.id === "panel-" + name);
        });
      });
    });
  }

  function renderOverview(data) {
    const sum = data.run_summary || {};
    const empty = $("#overview-empty");
    const grid = $("#overview-grid");
    const links = $("#overview-links");
    grid.innerHTML = "";
    links.innerHTML = "";

    if (!data.has_run_summary) {
      empty.classList.remove("hidden");
      return;
    }
    empty.classList.add("hidden");

    const probeMeta = sum.runtime_probe && typeof sum.runtime_probe === "object" ? sum.runtime_probe : {};
    let probeOverview = "—";
    if (probeMeta.configured) {
      const st = probeMeta.status_code != null ? `HTTP ${probeMeta.status_code}` : "no status";
      const ms = probeMeta.elapsed_ms != null ? `${probeMeta.elapsed_ms} ms` : "—";
      if (probeMeta.ok) probeOverview = `ok · ${st} · ${ms}`;
      else {
        const err = probeMeta.error ? String(probeMeta.error).slice(0, 160) : "";
        probeOverview = `fail · ${st} · ${ms}${err ? ` · ${err}` : ""}`;
      }
    } else if ((sum.runtime_probe_base_url || "").trim()) {
      probeOverview = "(configured URL missing from summary — re-run audit)";
    } else {
      probeOverview = "off (set probe_base_url or CONTRACTLENS_PROBE_BASE_URL)";
    }

    const rows = [
      ["Snapshot", data.snapshot_dir || data.latest_dir || ""],
      ["Run ID", sum.run_id || data.run_id],
      ["Feature", sum.feature_name || data.feature_name_fallback],
      ["Root", sum.root_path],
      ["Completed", sum.completed_at],
      ["Duration (ms)", sum.duration_ms],
      ["Mismatch count", sum.mismatch_count],
      ["High-risk count", sum.high_risk_count],
      ["Frontend contracts", sum.frontend_contract_count],
      ["Backend routes", sum.backend_route_count],
      ["Runtime probe", probeOverview],
    ];
    rows.forEach(([k, v]) => {
      const dt = document.createElement("dt");
      dt.textContent = k;
      const dd = document.createElement("dd");
      dd.textContent = v !== undefined && v !== null ? String(v) : "—";
      grid.appendChild(dt);
      grid.appendChild(dd);
    });

    const rid = selectedRunId();
    const rp = data.report_paths || {};
    if (rp.markdown_abs) {
      const a = document.createElement("a");
      a.href = `/api/report/markdown?${qRun(rid)}`;
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = "Open Markdown (raw)";
      links.appendChild(a);
      const b = document.createElement("a");
      b.href = "#";
      b.textContent = "View rendered (this UI)";
      b.addEventListener("click", (e) => {
        e.preventDefault();
        document.querySelector('.tab[data-tab="report"]').click();
        loadReportHtml(true);
      });
      links.appendChild(b);
    }
    if (rp.html_abs) {
      const a = document.createElement("a");
      a.href = `/open/html-report?${qRun(rid)}`;
      a.textContent = "Open HTML report";
      a.target = "_blank";
      a.rel = "noopener";
      links.appendChild(a);
    }
  }

  function renderTrace(data) {
    const ol = $("#exec-list");
    ol.innerHTML = "";
    (data.execution_trace || []).forEach((line) => {
      const li = document.createElement("li");
      li.textContent = String(line);
      ol.appendChild(li);
    });
    if (!ol.children.length) {
      const li = document.createElement("li");
      li.className = "muted";
      li.textContent = "No execution trace.";
      ol.appendChild(li);
    }
  }

  function renderAudit(data) {
    const tb = $("#audit-table").querySelector("tbody");
    tb.innerHTML = "";
    (data.tool_audit || []).forEach((e) => {
      if (!e || typeof e !== "object") return;
      const tr = document.createElement("tr");
      tr.innerHTML =
        "<td><code>" +
        esc(String(e.tool || "")) +
        "</code></td><td>" +
        esc(String(e.status || "")) +
        "</td><td>" +
        esc(String(e.duration_ms ?? "")) +
        "</td><td>" +
        esc(String(e.input_summary || "").slice(0, 120)) +
        "</td><td>" +
        esc(String(e.output_summary || "—").slice(0, 120)) +
        "</td>";
      tb.appendChild(tr);
    });
    if (!tb.children.length) {
      const tr = document.createElement("tr");
      tr.innerHTML = '<td colspan="5">No audit entries.</td>';
      tb.appendChild(tr);
    }
  }

  function renderAgents(data) {
    const wrap = $("#agent-groups");
    wrap.innerHTML = "";
    const g = data.agent_trace_grouped || {};
    const order = ["Frontend Analyst", "Backend Analyst", "Contract Reviewer", "Report Writer", "Other"];
    order.forEach((name) => {
      const lines = g[name] || [];
      const block = document.createElement("div");
      block.className = "agent-block";
      const h4 = document.createElement("h4");
      h4.textContent = name + " (" + lines.length + ")";
      block.appendChild(h4);
      const ul = document.createElement("ul");
      lines.forEach((line) => {
        const li = document.createElement("li");
        li.textContent = String(line);
        ul.appendChild(li);
      });
      if (!lines.length) {
        const li = document.createElement("li");
        li.style.color = "var(--muted)";
        li.textContent = "—";
        ul.appendChild(li);
      }
      block.appendChild(ul);
      wrap.appendChild(block);
    });
  }

  function renderFindings(data) {
    $("#fe-json").textContent = JSON.stringify(data.frontend_contracts || [], null, 2);
    $("#be-json").textContent = JSON.stringify(data.backend_contracts || [], null, 2);
    const tb = $("#mm-table").querySelector("tbody");
    tb.innerHTML = "";
    (data.mismatches || []).forEach((m) => {
      if (!m || typeof m !== "object") return;
      const tr = document.createElement("tr");
      const rk = esc(String(m.risk || ""));
      const rc = riskClass(m.risk);
      tr.innerHTML =
        "<td><code>" +
        esc(String(m.area || "")) +
        "</code></td><td class=\"" +
        rc +
        "\">" +
        rk +
        "</td><td>" +
        esc(String(m.frontend_expects || "")) +
        "</td><td>" +
        esc(String(m.backend_provides || "")) +
        "</td><td>" +
        esc(String(m.suggestion || "")) +
        "</td>";
      tb.appendChild(tr);
    });
    if (!tb.children.length) {
      const tr = document.createElement("tr");
      tr.innerHTML = '<td colspan="5">No mismatches.</td>';
      tb.appendChild(tr);
    }
  }

  async function loadReportHtml(force) {
    const el = $("#report-html");
    const rid = selectedRunId();
    if (!force && reportLoadedForRun === rid && el.dataset.loaded === "1") return;
    el.innerHTML = "<p class='hint'>Loading…</p>";
    el.dataset.loaded = "1";
    reportLoadedForRun = rid;
    const res = await fetch(`/api/report/markdown-html?${qRun(rid)}`);
    if (!res.ok) {
      el.innerHTML = "<p>No report to display for this snapshot.</p>";
      return;
    }
    el.innerHTML = await res.text();
  }

  function renderReportActions(data) {
    const actions = $("#report-actions");
    actions.innerHTML = "";
    const rp = data.report_paths || {};
    const rid = selectedRunId();
    if (rp.html_abs) {
      const a = document.createElement("a");
      a.href = `/open/html-report?${qRun(rid)}`;
      a.className = "link-btn";
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = "Open standalone HTML report";
      actions.appendChild(a);
    } else {
      const p = document.createElement("span");
      p.className = "hint";
      p.textContent = "No HTML report on disk — generate with --html or the generate_html_report tool.";
      actions.appendChild(p);
    }
  }

  async function loadAndRenderAll() {
    const rid = selectedRunId();
    $("#latest-hint").textContent = `Loading snapshot (${rid})…`;
    const data = await loadSnapshot(rid);
    $("#latest-hint").textContent =
      `Selected: ${rid} · artifacts: ${data.snapshot_dir || data.latest_dir || "—"}`;
    renderOverview(data);
    renderTrace(data);
    renderAudit(data);
    renderAgents(data);
    renderFindings(data);
    renderReportActions(data);
    const el = $("#report-html");
    if (el) {
      el.dataset.loaded = "0";
      reportLoadedForRun = "";
    }
  }

  async function fillDiffSelects() {
    const meta = await fetchRunsList();
    const left = $("#diff-left");
    const right = $("#diff-right");
    if (!left || !right) return;
    [left, right].forEach((sel) => {
      sel.innerHTML = "";
      const o0 = document.createElement("option");
      o0.value = "latest";
      o0.textContent = "latest";
      sel.appendChild(o0);
      (meta.runs || []).forEach((row) => {
        if (!row.run_id) return;
        const o = document.createElement("option");
        o.value = row.run_id;
        o.textContent = row.run_id;
        sel.appendChild(o);
      });
    });
    if (meta.runs && meta.runs.length >= 2) {
      right.selectedIndex = 1;
    }
  }

  async function runDiff() {
    const out = $("#diff-out");
    if (!out) return;
    const left = $("#diff-left").value || "latest";
    const right = $("#diff-right").value || "latest";
    out.innerHTML = "<p class='hint'>Loading…</p>";
    const res = await fetch(
      `/api/diff?left=${encodeURIComponent(left)}&right=${encodeURIComponent(right)}`
    );
    if (!res.ok) {
      out.textContent = "Diff request failed.";
      return;
    }
    const d = await res.json();
    if (d.error) {
      out.textContent = `Error: ${d.error}`;
      return;
    }
    const ol = d.only_in_left || [];
    const or = d.only_in_right || [];
    out.innerHTML =
      `<p><strong>Left</strong> (${left}): ${d.left_total} mismatches · ` +
      `<strong>Right</strong> (${right}): ${d.right_total} · ` +
      `<strong>Both</strong>: ${d.in_both}</p>` +
      `<h4>Only in left (${ol.length})</h4><pre class="json-block">${esc(JSON.stringify(ol, null, 2))}</pre>` +
      `<h4>Only in right (${or.length})</h4><pre class="json-block">${esc(JSON.stringify(or, null, 2))}</pre>`;
  }

  async function init() {
    wireTabs();
    await populateRunSelect();
    await fillDiffSelects();
    $("#reload-btn")?.addEventListener("click", () => loadAndRenderAll().catch(showErr));
    $("#run-select")?.addEventListener("change", () => loadAndRenderAll().catch(showErr));
    $("#diff-run-btn")?.addEventListener("click", () => runDiff().catch(showErr));

    try {
      await loadAndRenderAll();
    } catch (e) {
      showErr(e);
    }

    document.querySelector('.tab[data-tab="report"]').addEventListener("click", () => {
      loadReportHtml(false).catch(() => {
        $("#report-html").innerHTML = "<p>Could not load report.</p>";
      });
    });
  }

  function showErr(e) {
    $("#latest-hint").textContent = "Error: " + (e && e.message ? e.message : String(e));
  }

  init();
})();
