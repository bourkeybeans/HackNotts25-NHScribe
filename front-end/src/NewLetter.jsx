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
    testType: "", // "Text" | "CSV"
    rawData: "",
    urgency: "Routine",
    notes: "",
  });

  const [checkStatus, setCheckStatus] = useState(null); // "found" | "not_found" | "error" | null
  const [checkMessage, setCheckMessage] = useState("");

  // CSV upload state
  const [csvFile, setCsvFile] = useState(null);
  const [csvStatus, setCsvStatus] = useState("");        // status message
  const [csvResponse, setCsvResponse] = useState(null);  // server JSON on success
  const [pdfPath, setPdfPath] = useState(null);

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
    if (name === "testType" && value !== "CSV") {
      setCsvFile(null);
      setCsvResponse(null);
      setCsvStatus("");
    }
  };

  const previewEmpty = useMemo(() => {
    if (form.testType === "CSV") return !csvResponse && !form.notes;
    return !form.testType && !form.rawData && !form.notes;
  }, [form, csvResponse]);

  const norm = (s) => (s || "").trim().toLowerCase();

  async function handleCheckPatient() {
    try {
      setCheckStatus(null);
      setCheckMessage("Checking…");

      const res = await fetch("http://10.249.84.213:8000/patients/");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const patients = await res.json();

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
      const body = new URLSearchParams();
      body.set("name", form.name.trim());
      if (form.age) body.set("age", String(Number(form.age)));
      body.set("sex", form.sex);
      body.set("address", form.address?.trim() || "");
      body.set("conditions", form.conditions?.trim() || "");

      const res = await fetch("http://10.249.84.213:8000/patients/", {
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

  // ---- Upload CSV to /upload-results/ ----
  async function handleUploadCSV() {
    try {
      setCsvStatus("");
      setCsvResponse(null);

      if (!form.patientId) {
        setCsvStatus("Please select or create a patient first (Patient ID required).");
        return;
      }
      if (!csvFile) {
        setCsvStatus("Please choose a CSV file to upload.");
        return;
      }

      const fd = new FormData();
      fd.append("patient_id", String(Number(form.patientId)));
      fd.append("file", csvFile);

      const res = await fetch("http://10.249.84.213:8000/upload-results/", {
        method: "POST",
        body: fd,
      });

      if (!res.ok) {
        const msg = await res.text();
        throw new Error(msg || `HTTP ${res.status}`);
      }

      const data = await res.json();
      setCsvResponse(data);
      setCsvStatus(`Uploaded ${csvFile.name} • ${data.results?.length || 0} results saved • batch ${data.batch_id}`);
    } catch (err) {
      console.error(err);
      setCsvStatus("Upload failed. Please confirm CSV format and try again.");
    }
  }

  async function handleGenerateLetter() {
    try {

      if (!csvResponse) {
        return;
      }

      const res = await fetch("http://10.249.84.213:8000/letters/generate/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          letter_data: csvResponse
        })
      });

      if (!res.ok) {
        const msg = await res.text();
        throw new Error(msg || `HTTP ${res.status}`);
      }

      const data = await res.json();

      let pdf_path = "http://10.249.84.213:8000/static/" + data.pdf_url

      setPdfPath(pdf_path);
    
    } catch (err) {
      console.error(err);
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

            <label className="label">Patient ID</label>
            <input
              className="input disabled"
              name="patientId"
              placeholder="Auto-populated after Check/Create"
              value={form.patientId}
              disabled
            />
            <div className="help">Auto-populated from hospital system</div>

            <label className="label" style={{ marginTop: 16 }}>
              Data Type
            </label>
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

            {form.testType === "Text" && (
              <>
                <label className="label">Raw Results Data</label>
                <textarea
                  className="input textarea"
                  rows={5}
                  name="rawData"
                  placeholder="Enter lab values, observations, measurements..."
                  value={form.rawData}
                  onChange={onChange}
                />
              </>
            )}

            {form.testType === "CSV" && (
              <>
                <label className="label">Upload CSV Results</label>
                <input
                  type="file"
                  accept=".csv,text/csv"
                  className="input"
                  onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                />
                <div className="help">
                  Expected columns (case-insensitive): <em>Test Name/Test</em>, <em>Result/Value</em>, optional <em>Units</em>, <em>Flag</em>, <em>Reference Range</em>.
                </div>
                <div className="actions">
                  <button
                    type="button"
                    className="btn primary"
                    onClick={handleUploadCSV}
                    disabled={!form.patientId || !csvFile}
                  >
                    ⬆ Upload to Patient
                  </button>
                </div>
                {csvStatus && (
                  <div className="help" style={{ marginTop: 8 }}>
                    {csvStatus}
                  </div>
                )}
              </>
            )}

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
              <button className="btn primary" disabled={!form.patientId} onClick={handleGenerateLetter}>
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
            {pdfPath ? (
              <iframe
                src={pdfPath}
                title="Generated Letter"
                style={{
                  width: "100%",
                  height: "80vh",
                  border: "none",
                  borderRadius: "8px",
                }}
              />
            ) : previewEmpty ? (
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

                {form.testType === "Text" && form.rawData && (
                  <>
                    <h4>Results Summary</h4>
                    <pre className="pre">{form.rawData}</pre>
                  </>
                )}

                {form.testType === "CSV" && csvResponse && (
                  <>
                    <h4>Results Summary (CSV batch)</h4>
                    <p className="muted">
                      Batch: <code>{csvResponse.batch_id}</code> • Source: <code>{csvResponse.results?.[0]?.source_file || csvFile?.name}</code>
                    </p>
                    <div className="table-scroll" style={{ border: "1px solid #e5e7eb", borderRadius: 10 }}>
                      <table>
                        <thead>
                          <tr>
                            <th>Test</th>
                            <th>Value</th>
                            <th>Unit</th>
                            <th>Flag</th>
                            <th>Ref Low</th>
                            <th>Ref High</th>
                          </tr>
                        </thead>
                        <tbody>
                          {csvResponse.results.map((r, idx) => (
                            <tr key={idx}>
                              <td className="bold">{r.test_name}</td>
                              <td>{r.value}</td>
                              <td>{r.unit || "—"}</td>
                              <td>{r.flag || "—"}</td>
                              <td>{r.reference_low || "—"}</td>
                              <td>{r.reference_high || "—"}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </>
                )}

                {form.notes && (
                  <>
                    <h4>Clinician Notes</h4>
                    <p>{form.notes}</p>
                  </>
                )}
              </article>
            )}
          </div>
        </section>
      </main>
    </div>
  );

}