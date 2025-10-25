import React, { useMemo, useState } from "react";
import "./NHScribeDashboard.css";
import "./NewLetter.css";
import Nhscribe from "./assets/Nhscribe.png";
import { useNavigate } from "react-router-dom";

/* ------------------------ TEMP LOCAL STORAGE LAYER -------------------------
   Replace these functions with your real SQL calls later.
   For now, they simulate a patient DB using localStorage.
-----------------------------------------------------------------------------*/
const LS_KEY = "nhscribe_patients";

function loadPatients() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}
function savePatients(arr) {
  localStorage.setItem(LS_KEY, JSON.stringify(arr));
}
function genPatientId() {
  // simple readable id; replace with DB autoincrement id later
  return `PT-${Math.random().toString(36).slice(2, 6).toUpperCase()}${Date.now()
    .toString()
    .slice(-3)}`;
}
// naive match: name + age (+ optional address substring)
function findPatient({ name, age, address }) {
  const all = loadPatients();
  return all.find((p) => {
    const nameMatch =
      p.name?.trim().toLowerCase() === (name || "").trim().toLowerCase();
    const ageMatch = Number(p.age) === Number(age);
    const addressHint = (address || "").trim().toLowerCase();
    const addressMatch = !addressHint || p.address?.toLowerCase().includes(addressHint);
    return nameMatch && ageMatch && addressMatch;
  });
}
function createPatient(p) {
  const all = loadPatients();
  const id = genPatientId();
  const record = { ...p, id };
  all.push(record);
  savePatients(all);
  return record;
}
/* --------------------------------------------------------------------------*/

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

  const [checkStatus, setCheckStatus] = useState(null); // null | "found" | "not_found" | "error"
  const [checkMessage, setCheckMessage] = useState("");

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const previewEmpty = useMemo(() => {
    return !form.testType && !form.rawData && !form.notes;
  }, [form]);

  // ---- Handlers for patient lookup ----
  async function handleCheckPatient() {
    // PLACEHOLDER: replace this whole function with your SQL call.
    // e.g. const res = await fetch('/api/patients/search', { method:'POST', body: JSON.stringify({name, age, address})})
    try {
      setCheckStatus(null);
      setCheckMessage("Checking… (mock, replace with SQL later)");

      const match = findPatient({
        name: form.name,
        age: form.age,
        address: form.address,
      });

      if (match) {
        setForm((f) => ({
          ...f,
          patientId: match.id,
          // hydrate optional fields from DB
          name: match.name || f.name,
          address: match.address || f.address,
          age: match.age ?? f.age,
          sex: match.sex || f.sex,
          conditions: match.conditions || f.conditions,
        }));
        setCheckStatus("found");
        setCheckMessage(`Patient found: ${match.name} (${match.id})`);
      } else {
        setCheckStatus("not_found");
        setCheckMessage("No matching patient found. You can create a new one.");
      }
    } catch (e) {
      setCheckStatus("error");
      setCheckMessage("Error checking patient (mock layer).");
    }
  }

  function handleCreatePatient() {
    // Minimal validation
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

    // PLACEHOLDER: Replace with SQL INSERT and returned id
    const record = createPatient({
      name: form.name.trim(),
      address: form.address?.trim() || "",
      age: form.age ? Number(form.age) : null,
      sex: form.sex,
      conditions: form.conditions?.trim() || "",
    });

    setForm((f) => ({ ...f, patientId: record.id }));
    setCheckStatus("found");
    setCheckMessage(`New patient created: ${record.name} (${record.id})`);
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
                ✅ Check Patient
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
                🧠 Generate Letter
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
                <p><strong>Patient:</strong> {form.name || "—"} {form.patientId ? `(${form.patientId})` : ""}</p>
                <p><strong>Test Type:</strong> {form.testType || "—"}</p>
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
              </article>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
