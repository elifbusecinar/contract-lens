import { useCallback, useEffect, useMemo, useState } from "react";

type Tab =
  | "overview"
  | "trace"
  | "mcp"
  | "agents"
  | "findings"
  | "report"
  | "compare";

function qRun(id: string) {
  return `run_id=${encodeURIComponent(id || "latest")}`;
}

function esc(s: string): string {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function riskClass(r: unknown): string {
  const x = String(r || "").toLowerCase();
  if (x === "high") return "risk-high";
  if (x === "medium") return "risk-medium";
  if (x === "low") return "risk-low";
  return "";
}

type RunRow = {
  run_id: string;
  mismatch_count?: number;
  runtime_probe_configured?: boolean;
  runtime_probe_ok?: boolean | null;
};

export default function App() {
  const [tab, setTab] = useState<Tab>("overview");
  const [runId, setRunId] = useState("latest");
  const [hint, setHint] = useState("Loading…");
  const [runsMeta, setRunsMeta] = useState<{ runs: RunRow[]; latest_run_id?: string }>({ runs: [] });
  const [snapshot, setSnapshot] = useState<Record<string, unknown> | null>(null);
  const [reportHtml, setReportHtml] = useState("");
  const [diffLeft, setDiffLeft] = useState("latest");
  const [diffRight, setDiffRight] = useState("latest");
  const [diffHtml, setDiffHtml] = useState("");

  const fetchRunsList = useCallback(async () => {
    const res = await fetch("/api/runs?limit=100");
    if (!res.ok) throw new Error("runs list failed");
    return res.json() as Promise<{ runs: RunRow[]; latest_run_id?: string }>;
  }, []);

  const loadSnapshot = useCallback(async (rid: string) => {
    const res = await fetch(`/api/snapshot?${qRun(rid)}`);
    if (!res.ok) throw new Error("snapshot failed");
    return res.json() as Promise<Record<string, unknown>>;
  }, []);

  const reloadAll = useCallback(async () => {
    setHint(`Loading snapshot (${runId})…`);
    try {
      const data = await loadSnapshot(runId);
      setSnapshot(data);
      setHint(`Selected: ${runId} · artifacts: ${String(data.snapshot_dir || data.latest_dir || "—")}`);
      setReportHtml("");
    } catch (e) {
      setHint(`Error: ${e instanceof Error ? e.message : String(e)}`);
    }
  }, [loadSnapshot, runId]);

  useEffect(() => {
    (async () => {
      try {
        const meta = await fetchRunsList();
        setRunsMeta(meta);
      } catch {
        /* ignore */
      }
    })();
  }, [fetchRunsList]);

  useEffect(() => {
    void reloadAll();
  }, [reloadAll]);

  useEffect(() => {
    if (tab !== "report") return;
    let cancelled = false;
    void (async () => {
      setReportHtml("<p class='hint'>Loading…</p>");
      const res = await fetch(`/api/report/markdown-html?${qRun(runId)}`);
      const body = res.ok ? await res.text() : "<p>No report to display for this snapshot.</p>";
      if (!cancelled) setReportHtml(body);
    })();
    return () => {
      cancelled = true;
    };
  }, [tab, runId]);

  const sum = useMemo(
    () => (snapshot?.run_summary || {}) as Record<string, unknown>,
    [snapshot],
  );

  const overviewRows = useMemo(() => {
    const probeMeta =
      sum.runtime_probe && typeof sum.runtime_probe === "object"
        ? (sum.runtime_probe as Record<string, unknown>)
        : {};
    let probeOverview = "—";
    if (probeMeta.configured) {
      const st = probeMeta.status_code != null ? `HTTP ${probeMeta.status_code}` : "no status";
      const ms = probeMeta.elapsed_ms != null ? `${probeMeta.elapsed_ms} ms` : "—";
      if (probeMeta.ok) probeOverview = `ok · ${st} · ${ms}`;
      else {
        const err = probeMeta.error ? String(probeMeta.error).slice(0, 160) : "";
        probeOverview = `fail · ${st} · ${ms}${err ? ` · ${err}` : ""}`;
      }
    } else if (String(sum.runtime_probe_base_url || "").trim()) {
      probeOverview = "(configured URL missing from summary — re-run audit)";
    } else {
      probeOverview = "off (set probe_base_url or CONTRACTLENS_PROBE_BASE_URL)";
    }

    const rows: [string, unknown][] = [
      ["Snapshot", snapshot?.snapshot_dir || snapshot?.latest_dir || ""],
      ["Run ID", sum.run_id || snapshot?.run_id],
      ["Feature", sum.feature_name || snapshot?.feature_name_fallback],
      ["Root", sum.root_path],
      ["Completed", sum.completed_at],
      ["Duration (ms)", sum.duration_ms],
      ["Mismatch count", sum.mismatch_count],
      ["High-risk count", sum.high_risk_count],
      ["Frontend contracts", sum.frontend_contract_count],
      ["Backend routes", sum.backend_route_count],
      ["Runtime probe", probeOverview],
    ];
    return rows;
  }, [snapshot, sum]);

  const execLines = (snapshot?.execution_trace || []) as unknown[];
  const auditEntries = (snapshot?.tool_audit || []) as Record<string, unknown>[];
  const agentGrouped = (snapshot?.agent_trace_grouped || {}) as Record<string, string[]>;
  const fe = snapshot?.frontend_contracts || [];
  const be = snapshot?.backend_contracts || [];
  const mm = snapshot?.mismatches || [];
  const rp = (snapshot?.report_paths || {}) as Record<string, string | undefined>;

  async function runDiff() {
    setDiffHtml("<p class='hint'>Loading…</p>");
    const res = await fetch(
      `/api/diff?left=${encodeURIComponent(diffLeft)}&right=${encodeURIComponent(diffRight)}`,
    );
    if (!res.ok) {
      setDiffHtml("Diff request failed.");
      return;
    }
    const d = (await res.json()) as Record<string, unknown>;
    if (d.error) {
      setDiffHtml(`Error: ${String(d.error)}`);
      return;
    }
    const ol = (d.only_in_left || []) as unknown[];
    const or = (d.only_in_right || []) as unknown[];
    setDiffHtml(
      `<p><strong>Left</strong> (${String(d.left_run)}): ${Number(d.left_total)} mismatches · ` +
        `<strong>Right</strong> (${String(d.right_run)}): ${Number(d.right_total)} · ` +
        `<strong>Both</strong>: ${Number(d.in_both)}</p>` +
        `<h4>Only in left (${ol.length})</h4><pre class="json-block">${esc(JSON.stringify(ol, null, 2))}</pre>` +
        `<h4>Only in right (${or.length})</h4><pre class="json-block">${esc(JSON.stringify(or, null, 2))}</pre>`,
    );
  }

  useEffect(() => {
    const rs = runsMeta.runs || [];
    if (rs.length >= 2) {
      setDiffRight(rs[1].run_id);
    }
  }, [runsMeta]);

  const hasSummary = Boolean(snapshot?.has_run_summary);

  return (
    <>
      <header className="top">
        <h1>
          ContractLens <span className="badge">react</span>
        </h1>
        <p className="sub">
          Read-only view of run artifacts under <code>contractlens-runs/</code> (Vite build — falls back to legacy static
          when not built).
        </p>
      </header>

      <div className="toolbar">
        <label className="run-label">
          Snapshot{" "}
          <select
            value={runId}
            onChange={(e) => {
              setRunId(e.target.value);
            }}
          >
            <option value="latest">
              {runsMeta.latest_run_id ? `latest (${runsMeta.latest_run_id})` : "latest"}
            </option>
            {(runsMeta.runs || []).map((row) => {
              if (!row.run_id) return null;
              const mc = row.mismatch_count != null ? ` · ${row.mismatch_count} mm` : "";
              let probe = "";
              if (row.runtime_probe_configured) probe = row.runtime_probe_ok ? " · probe ✓" : " · probe ✗";
              return (
                <option key={row.run_id} value={row.run_id}>
                  {row.run_id}
                  {mc}
                  {probe}
                </option>
              );
            })}
          </select>
        </label>
        <button type="button" className="btn-secondary" onClick={() => void reloadAll()}>
          Reload
        </button>
      </div>

      <nav className="tabs">
        {(
          [
            ["overview", "Overview"],
            ["trace", "Workflow Trace"],
            ["mcp", "MCP Tool Calls"],
            ["agents", "Agent Trace"],
            ["findings", "Findings"],
            ["report", "Report Viewer"],
            ["compare", "Compare runs"],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={`tab${tab === id ? " active" : ""}`}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </nav>

      <main>
        <section className={`panel${tab === "overview" ? " active" : ""}`}>
          <h2>Overview</h2>
          <div className={`empty${hasSummary ? " hidden" : ""}`} role="status">
            No <code>run_summary.json</code> yet. Run:
            <pre>python -m contractlens.main --feature &quot;…&quot; --root &lt;repo&gt; --verbose</pre>
          </div>
          {hasSummary ? (
            <>
              <dl className="grid-dl">
                {overviewRows.map(([k, v]) => (
                  <FragmentRow key={k} k={k} v={v} />
                ))}
              </dl>
              <div className="links">
                {rp.markdown_abs ? (
                  <>
                    <a href={`/api/report/markdown?${qRun(runId)}`} target="_blank" rel="noopener noreferrer">
                      Open Markdown (raw)
                    </a>
                    <a
                      href="#"
                      onClick={(e) => {
                        e.preventDefault();
                        setTab("report");
                      }}
                    >
                      View rendered (this UI)
                    </a>
                  </>
                ) : null}
                {rp.html_abs ? (
                  <a href={`/open/html-report?${qRun(runId)}`} target="_blank" rel="noopener noreferrer">
                    Open HTML report
                  </a>
                ) : null}
              </div>
            </>
          ) : null}
        </section>

        <section className={`panel${tab === "trace" ? " active" : ""}`}>
          <h2>Workflow trace</h2>
          <p className="hint">LangGraph / sequential execution lines from execution_trace.json.</p>
          <ol className="mono-list">
            {execLines.length ? (
              execLines.map((line, i) => <li key={i}>{String(line)}</li>)
            ) : (
              <li className="muted">No execution trace.</li>
            )}
          </ol>
        </section>

        <section className={`panel${tab === "mcp" ? " active" : ""}`}>
          <h2>MCP tool calls</h2>
          <p className="hint">From tool_audit_log.json.</p>
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>Tool</th>
                  <th>Status</th>
                  <th>ms</th>
                  <th>Input</th>
                  <th>Output</th>
                </tr>
              </thead>
              <tbody>
                {auditEntries.length ? (
                  auditEntries.map((e, i) => (
                    <tr key={i}>
                      <td>
                        <code>{String(e.tool || "")}</code>
                      </td>
                      <td>{String(e.status || "")}</td>
                      <td>{String(e.duration_ms ?? "")}</td>
                      <td>{String(e.input_summary || "").slice(0, 120)}</td>
                      <td>{String(e.output_summary || "—").slice(0, 120)}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5}>No audit entries.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className={`panel${tab === "agents" ? " active" : ""}`}>
          <h2>Agent trace</h2>
          <p className="hint">Grouped from agent_trace.json string lines.</p>
          {(["Frontend Analyst", "Backend Analyst", "Contract Reviewer", "Report Writer", "Other"] as const).map(
            (name) => {
              const lines = agentGrouped[name] || [];
              return (
                <div key={name} className="agent-block">
                  <h4>
                    {name} ({lines.length})
                  </h4>
                  <ul>
                    {lines.length ? (
                      lines.map((line, i) => <li key={i}>{line}</li>)
                    ) : (
                      <li style={{ color: "var(--muted)" }}>—</li>
                    )}
                  </ul>
                </div>
              );
            },
          )}
        </section>

        <section className={`panel${tab === "findings" ? " active" : ""}`}>
          <h2>Findings</h2>
          <h3>Frontend expectations</h3>
          <pre className="json-block">{JSON.stringify(fe, null, 2)}</pre>
          <h3>Backend reality</h3>
          <pre className="json-block">{JSON.stringify(be, null, 2)}</pre>
          <h3>Mismatches</h3>
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>Area</th>
                  <th>Risk</th>
                  <th>Frontend</th>
                  <th>Backend</th>
                  <th>Suggestion</th>
                </tr>
              </thead>
              <tbody>
                {(mm as Record<string, unknown>[]).length ? (
                  (mm as Record<string, unknown>[]).map((m, i) => (
                    <tr key={i}>
                      <td>
                        <code>{String(m.area || "")}</code>
                      </td>
                      <td className={riskClass(m.risk)}>{String(m.risk || "")}</td>
                      <td>{String(m.frontend_expects || "")}</td>
                      <td>{String(m.backend_provides || "")}</td>
                      <td>{String(m.suggestion || "")}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5}>No mismatches.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className={`panel${tab === "report" ? " active" : ""}`}>
          <h2>Report viewer</h2>
          <p className="hint">Markdown rendered server-side for the selected snapshot.</p>
          <div className="report-actions">
            {rp.html_abs ? (
              <a href={`/open/html-report?${qRun(runId)}`} target="_blank" rel="noopener noreferrer">
                Open standalone HTML report
              </a>
            ) : (
              <span className="hint">No HTML report on disk — generate with --html.</span>
            )}
          </div>
          <div className="report-frame-wrap">
            <article
              className="report-html markdown-body"
              dangerouslySetInnerHTML={{ __html: reportHtml || "<p class='hint'>Open this tab to load.</p>" }}
            />
          </div>
        </section>

        <section className={`panel${tab === "compare" ? " active" : ""}`}>
          <h2>Compare runs</h2>
          <p className="hint">Mismatch rows keyed by area + frontend/backend expectation.</p>
          <div className="diff-toolbar">
            <label>
              Left{" "}
              <select value={diffLeft} onChange={(e) => setDiffLeft(e.target.value)}>
                <option value="latest">latest</option>
                {(runsMeta.runs || []).map((row) =>
                  row.run_id ? (
                    <option key={`l-${row.run_id}`} value={row.run_id}>
                      {row.run_id}
                    </option>
                  ) : null,
                )}
              </select>
            </label>
            <label>
              Right{" "}
              <select value={diffRight} onChange={(e) => setDiffRight(e.target.value)}>
                <option value="latest">latest</option>
                {(runsMeta.runs || []).map((row) =>
                  row.run_id ? (
                    <option key={`r-${row.run_id}`} value={row.run_id}>
                      {row.run_id}
                    </option>
                  ) : null,
                )}
              </select>
            </label>
            <button type="button" className="btn-secondary" onClick={() => void runDiff()}>
              Compare
            </button>
          </div>
          <div className="diff-out" dangerouslySetInnerHTML={{ __html: diffHtml || "<p class='hint'>Run compare.</p>" }} />
        </section>
      </main>

      <footer className="footer">
        <span>{hint}</span>
      </footer>
    </>
  );
}

function FragmentRow({ k, v }: { k: string; v: unknown }) {
  return (
    <>
      <dt>{k}</dt>
      <dd>{v !== undefined && v !== null ? String(v) : "—"}</dd>
    </>
  );
}
