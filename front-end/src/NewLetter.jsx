import React, { useMemo, useState } from "react";
import "./NHScribeDashboard.css";   // re-use variables & base styles
import "./NewLetter.css";           // page-specific layout/styles
import Nhscribe from "./assets/Nhscribe.png";
import { useNavigate } from "react-router-dom";

export default function NewLetter() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    patientId: "",
    testType: "",
    rawData: "",
    urgency: "Routine",
    notes: "",
  });

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const previewEmpty = useMemo(() => {
    return !form.testType && !form.rawData && !form.notes;
  }, [form]);

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

      {/* Main */}
      <main className="container newletter-grid">
        {/* LEFT: Form */}
        <section className="card panel">
          <div className="panel-head">
            <h2>Letter Details</h2>
          </div>
          <div className="panel-body">
            <label className="label">Patient ID</label>
            <input
              className="input disabled"
              name="patientId"
              placeholder="e.g., PT-1234"
              value={form.patientId}
              onChange={onChange}
              disabled
            />
            <div className="help">Auto-populated from hospital system</div>

            <label className="label">Test Type</label>
            <div className="select-wrap">
              <select
                className="input select"
                name="testType"
                value={form.testType}
                onChange={onChange}
              >
                <option value="">Select test type...</option>
                <option value="Full Blood Count">Full Blood Count</option>
                <option value="U&E Panel">U&amp;E Panel</option>
                <option value="LFTs">LFTs</option>
                <option value="Chest X-Ray">Chest X-Ray</option>
                <option value="MRI Brain">MRI Brain</option>
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
              <button className="btn primary">🧠 Generate Letter</button>
            </div>
          </div>
        </section>

        {/* RIGHT: Preview */}
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
