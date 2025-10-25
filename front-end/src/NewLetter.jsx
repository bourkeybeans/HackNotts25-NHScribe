import React, { useMemo, useState } from "react";
import "./NHScribeDashboard.css";
import "./NewLetter.css";
import Nhscribe from "./assets/Nhscribe.png";
import { useNavigate } from "react-router-dom";

export default function NewLetter() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    // patient fields
    patientId: "",
    name: "",
    address: "",
    age: "",
    sex: "",
    conditions: "",
    // letter fields
    testType: "",
    rawData: "",
    urgency: "Routine",
    notes: "",
  });

  const [checkStatus, setCheckStatus] = useState(null); // "found" | "not_found" | "error" | null
  const [checkMessage, setCheckMessage] = useState("");
  const [csvFile, setCsvFile] = useState(null);
  const [csvStatus, setCsvStatus] = useState("");
  const [csvResponse, setCsvResponse] = useState(null);

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const previewEmpty = useMemo(
    () => !form.testType && !form.rawData && !form.notes,
    [form]
  );

  // ---- Helpers ----
  const norm = (s) => (s || "").trim().toLowerCase();

  // ---- Handlers for patient lookup using your FastAPI routes ----
  async function handleCheckPatient() {
    try {
      setCheckStatus(null);
      setCheckMessage("Checking…");

      // GET /patients/
      const res = await fetch("/patients/");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const patients = await res.json();

      // Matching: name exact (case-insensitive), age exact (if given), address contains (if given)
      const nameQ = norm(form.name);
      const ageQ = form.age ? Number(form.age) : null;
      const addrQ = norm(form.address);

      const match = patients.find((p) => {
        const nameMatch = norm(p.name) === nameQ;
        const ageMatch = ageQ === null || Number(p.age) === ageQ;
        const addrMatch = !addrQ || norm(p.address || "").includes(addrQ);
        return nameMatch && ageMatch && addrMatch;
      });

      if (match) {
        setForm((f) => ({
          ...f,
          patientId: String(match.id),
          name: match.name ?? f.name,
          address: match.address ?? f.address,
          age: match.age ?? f.age,
          sex: match.sex ?? f.sex,
          conditions: match.conditions ?? f.conditions,
        }));
        setCheckStatus("found");
        setCheckMessage(`Patient found: ${match.name} (ID ${match.id})`);
      } else {
        setCheckStatus("not_found");
        setCheckMessage("No matching patient found. You can create a new one.");
      }
    } catch (e) {
      console.error(e);
      setCheckStatus("error");
      setCheckMessage("Error checking patient. Please try again.");
    }
  }

  async function handleCreatePatient() {
    // Validate to respect DB constraints
    if (!form.name?.trim()) {
      setCheckStatus("error");
      setCheckMessage("Please enter at least a Name to create a patient.");
      return;
    }
    if (!form.sex) {
      setCheckStatus("error");
      setCheckMessage("Please select Sex (M, F, Other).");
      return;
    }

    try {
      // FastAPI function signature expects form-encoded fields
      const body = new URLSearchParams();
      body.set("name", form.name.trim());
      if (form.age) body.set("age", String(Number(form.age)));
      body.set("sex", form.sex);
      body.set("address", form.address?.trim() || "");
      body.set("conditions", form.conditions?.trim() || "");

      const res = await fetch("/patients/", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });

      if (!res.ok) {
        const msg = await res.text();
        throw new Error(msg || `HTTP ${res.status}`);
      }
      const p = await res.json();

      setForm((f) => ({ ...f, patientId: String(p.id) }));
      setCheckStatus("found");
      setCheckMessage(`New patient created: ${p.name} (ID ${p.id})`);
    } catch (e) {
      console.error(e);
      setCheckStatus("error");
      setCheckMessage("Error creating patient. Please review fields and try again.");
    }
  }

  // ---- Optional CSV upload (uses your /upload-results/ route) ----
  async function handleUploadCsv() {
    if (!form.patientId) {
      setCsvStatus("Please Check/Create a patient first.");
      return;
    }
    if (!csvFile) {
      setCsvStatus("Please choose a CSV file to upload.");
      return;
    }

    try {
      setCsvStatus("Uploading…");
      setCsvResponse(null);

      const fd = new FormData();
      fd.append("patient_id", form.patientId);
      fd.append("file", csvFile);

      const res = await fetch("/upload-results/", {
        method: "POST",
        body: fd,
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data?.detail || `Upload failed (HTTP ${res.status})`);
      }

      setCsvResponse(data);
      setCsvStatus(`Uploaded ${data?.results?.length || 0} results (batch ${data?.batch_id}).`);
      // Optionally surface results into preview:
      if (!form.rawData && data?.results?.length) {
        const summary = data.results
          .map((r) => {
            const ref = [r.reference_low, r.reference_high].filter(Boolean).join(" - ");
            return `${r.test_name}: ${r.value}${r.unit ? " " + r.unit : ""}${ref ? ` (Ref: ${ref})` : ""}${r.flag ? ` [${r.flag}]` : ""}`;
          })
          .join("\n");
        setForm((f) => ({ ...f, testType: f.testType || "CSV", rawData: summary }));
      }
    } catch (e) {
      console.error(e);
      setCsvStatus(e.message || "Error uploading CSV.");
    }
  }

  return (
    <div className="page newletter-page">
      {/* Top Bar */}
      <header className="nav">
        <div className="container nav-inner">
          <div className="brand">
            <div className="Nhscribe">
              <img src={Nhscribe} alt="NHScribe" className="Nhscribe" />
            </div>
            <div>
              <div className="title">NHScribe</div>
              <div className="subtitle">AI Medical Letter Assistant</div>
            </div>
          </div>

          <div className="nav-actions">
            <button className="btn" onClick={() => navigate("/")}>⬅ Back</button>
          </div>
        </div>
      </header>

      <main className="container newletter-grid">
        {/* LEFT COLUMN */}
        <section className="card panel">
          <div className="panel-head">
            <h2>Letter Details</h2>
          </div>
          <div className="panel-body">
            {/* --- Patient Lookup Block --- */}
            <div className="block-title">Patient Search</div>
            <div className="patient-grid">
              <div>
                <label className="label">Name</label>
                <input
                  className="input"
                  name="name"
                  placeholder="e.g., Jane Smith"
                  value={form.name}
                  onChange={onChange}
                />
              </div>

              <div>
                <label className="label">Age</label>
                <input
                  className="input"
                  name="age"
                  type="number"
                  min="0"
                  placeholder="e.g., 54"
                  value={form.age}
                  onChange={onChange}
                />
              </div>

              <div>
                <label className="label">Sex</label>
                <div className="select-wrap">
                  <select
                    className="input select"
                    name="sex"
                    value={form.sex}
                    onChange={onChange}
                  >
                    <option value="">Select…</option>
                    <option value="M">M</option>
                    <option value="F">F</option>
                    <option value="Other">Other</option>
                  </select>
                  <span className="select-caret">▾</span>
                </div>
              </div>

              <div className="span-2">
                <label className="label">Address</label>
                <input
                  className="input"
                  name="address"
                  placeholder="House, street, city, postcode…"
                  value={form.address}
                  onChange={onChange}
                />
              </div>

              <div className="span-2">
                <label className="label">Conditions (history)</label>
                <textarea
                  className="input textarea"
                  rows={2}
                  name="conditions"
                  placeholder="e.g., Type 2 diabetes; Hypertension"
                  value={form.conditions}
                  onChange={onChange}
                />
              </div>
            </div>

            <div className="lookup-actions">
              <button type="button" className="btn primary" onClick={handleCheckPatient}>
                Check Patient
              </button>
              <button type="button" className="btn" onClick={handleCreatePatient}>
                ➕ Create New Patient
              </button>
              {checkStatus && (
                <span
                  className={
                    checkStatus === "found"
                      ? "pill success"
                      : checkStatus === "not_found"
                      ? "pill muted"
                      : "pill danger"
                  }
                  style={{ marginLeft: 8 }}
                >
                  {checkMessage}
                </span>
              )}
            </div>

            {/* --- Patient ID (read-only) --- */}
            <label className="label">Patient ID</label>
            <input
              className="input disabled"
              name="patientId"
              placeholder="Auto-populated after Check/Create"
              value={form.patientId}
              disabled
            />
            <div className="help">Auto-populated from hospital system</div>

            {/* --- Letter fields --- */}
            <label className="label" style={{ marginTop: 16 }}>Data Type</label>
            <div className="select-wrap">
              <select
                className="input select"
                name="testType"
                value={form.testType}
                onChange={onChange}
              >
                <option value="">Select data type...</option>
                <option value="Text">Text</option>
                <option value="CSV">CSV</option>
              </select>
              <span className="select-caret">▾</span>
            </div>

            {/* Optional CSV upload UI */}
            {form.testType === "CSV" && (
              <div style={{ marginTop: 8 }}>
                <label className="label">Upload CSV Results</label>
                <input
                  className="input"
                  type="file"
                  accept=".csv,text/csv"
                  onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                />
                <div className="actions" style={{ marginTop: 8 }}>
                  <button
                    className="btn"
                    type="button"
                    onClick={handleUploadCsv}
                    disabled={!form.patientId}
                  >
                    ⬆ Upload CSV to Patient
                  </button>
                  {!form.patientId && (
                    <span className="help" style={{ marginLeft: 8 }}>
                      (Check or create a patient first)
                    </span>
                  )}
                </div>
                {csvStatus && <div className="help" style={{ marginTop: 6 }}>{csvStatus}</div>}
              </div>
            )}

            <label className="label">Raw Results Data</label>
            <textarea
              className="input textarea"
              rows={5}
              name="rawData"
              placeholder="Enter lab values, observations, measurements..."
              value={form.rawData}
              onChange={onChange}
            />

            <label className="label">Urgency Level</label>
            <div className="urgency-row">
              <button
                type="button"
                className={`urgency ${form.urgency === "Routine" ? "active" : ""}`}
                onClick={() => setForm((f) => ({ ...f, urgency: "Routine" }))}
              >
                Routine
              </button>
              <button
                type="button"
                className={`urgency ${form.urgency === "Urgent" ? "active" : ""}`}
                onClick={() => setForm((f) => ({ ...f, urgency: "Urgent" }))}
              >
                Urgent
              </button>
            </div>

            <label className="label">Doctor's Additional Notes (Optional)</label>
            <textarea
              className="input textarea"
              rows={4}
              name="notes"
              placeholder="Add any additional clinical notes or context..."
              value={form.notes}
              onChange={onChange}
            />

            <div className="actions">
              <button className="btn primary" disabled={!form.patientId}>
                Generate Letter
              </button>
              {!form.patientId && (
                <span className="help" style={{ marginLeft: 8 }}>
                  (Check or create a patient first)
                </span>
              )}
            </div>
          </div>
        </section>

        {/* RIGHT COLUMN */}
        <section className="card panel">
          <div className="panel-head">
            <h2>Letter Preview</h2>
            <span className="badge chip">Draft</span>
          </div>
          <div className="panel-body preview">
            {previewEmpty ? (
              <div className="preview-empty">
                <div className="sparkles">✧</div>
                <div className="muted">Fill in the form to preview your letter</div>
              </div>
            ) : (
              <article className="letter">
                <h3>Patient Results Letter</h3>
                <p>
                  <strong>Patient:</strong> {form.name || "—"}{" "}
                  {form.patientId ? `(${form.patientId})` : ""}
                </p>
                <p><strong>Data Type:</strong> {form.testType || "—"}</p>
                <p><strong>Urgency:</strong> {form.urgency}</p>
                {form.rawData && (
                  <>
                    <h4>Results Summary</h4>
                    <pre className="pre">{form.rawData}</pre>
                  </>
                )}
                {form.notes && (
                  <>
                    <h4>Clinician Notes</h4>
                    <p>{form.notes}</p>
                  </>
                )}
                {csvResponse?.results?.length ? (
                  <>
                    <h4>Uploaded Results (latest batch)</h4>
                    <ul>
                      {csvResponse.results.slice(0, 6).map((r, idx) => (
                        <li key={idx}>
                          {r.test_name}: {r.value}
                          {r.unit ? ` ${r.unit}` : ""}{" "}
                          {r.flag ? `[${r.flag}]` : ""}
                        </li>
                      ))}
                    </ul>
                    {csvResponse.results.length > 6 && (
                      <div className="help">
                        +{csvResponse.results.length - 6} more…
                      </div>
                    )}
                  </>
                ) : null}
              </article>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
