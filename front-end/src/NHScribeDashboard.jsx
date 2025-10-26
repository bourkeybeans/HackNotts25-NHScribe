import { useState, useEffect } from "react";
import "./NHScribeDashboard.css";
import Nhscribe from "./assets/Nhscribe.png";
import { useNavigate } from "react-router-dom";

function StatusBadge({ status, letterId, onStatusChange }) {
  const normalized = (status || "").toLowerCase();

  const colorMap = {
    approved: "success",
    draft: "warning",
    rejected: "danger",
  };

  const labelMap = {
    approved: "✔ Approved",
    draft: "Draft",
    rejected: "Rejected",
  };

  const variant = colorMap[normalized] || "muted";
  const label = labelMap[normalized] || status || "Unknown";

  async function handleClick() {
    const next =
      normalized === "draft"
        ? "Approved"
        : normalized === "approved"
        ? "Rejected"
        : "Draft";

    try {
      const res = await fetch(`http://10.249.73.28:8000/letters/${letterId}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_status: next }),
      });

      if (!res.ok) throw new Error("Failed to update status");
      const data = await res.json();
      onStatusChange(letterId, data.status, data.approvedAt);
    } catch (err) {
      console.error("Error updating status:", err);
    }
  }

  return (
    <span
      className={`badge ${variant}`}
      onClick={handleClick}
      style={{ cursor: "pointer" }}
    >
      {label}
    </span>
  );
}

function Pill({ label, variant }) {
  return <span className={`pill ${variant || "default"}`}>{label}</span>;
}

export default function NHScribeDashboard() {
  const navigate = useNavigate();
  const [recentLetters, setRecentLetters] = useState([]);
  const [loading, setLoading] = useState(true);

  function handleStatusChange(letterId, newStatus, approvedAt) {
    setRecentLetters((letters) =>
      letters.map((l) =>
        l.id === letterId
          ? { ...l, status: newStatus, approvedAt }
          : l
      )
    );
  }

  useEffect(() => {
    async function fetchLetters() {
      try {
        const res = await fetch("http://10.249.73.28:8000/letters/recent");
        const text = await res.text();

        let data;
        try {
          data = JSON.parse(text);
        } catch {
          data = [];
        }

        setRecentLetters(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Fetch error:", err);
        setRecentLetters([]);
      } finally {
        setLoading(false);
      }
    }

    fetchLetters();
  }, []);

  const draftCount = recentLetters.filter(
    (l) => (l.status || "").toLowerCase() === "draft"
  ).length;

  const topStats = [
    { title: "Current Queue", value: `${draftCount} pending`},
  ];

  return (
    <div className="page">
      <header className="nav">
        <div className="container nav-inner">
          <div className="brand">
            <img src={Nhscribe} alt="Nhscribe" className="Nhscribe" />
            <div>
              <div className="title">NHScribe</div>
              <div className="subtitle">AI Medical Letter Assistant</div>
            </div>
          </div>
          <div className="nav-actions">
            <Pill label="Offline AI Active" variant="success" />
            <Pill label="Raspberry Pi 5" variant="muted" />
          </div>
        </div>
      </header>

      <br />

      <main className="container">
        {/* --- Stats section --- */}
        <section className="stats">
          {topStats.map((s, i) => (
            <div className="card" key={i}>
              <div className="head">{s.title}</div>
              <div className="body">
                <div className="stat-value">{s.value}</div>
              </div>
            </div>
          ))}
        </section>

        {/* --- CTA --- */}
        <section className="cta">
          <div>
            <h2>Ready to generate a new letter?</h2>
            <p>Create professional patient results letters in seconds with local AI processing.</p>
          </div>
          <button className="btn" onClick={() => navigate("/new-letter")}>
            ➕ New Letter
          </button>
        </section>

        {/* --- Recent Letters Table --- */}
        <section className="table-wrap">
          <div className="table-head">Recent Letters</div>
          <div className="table-scroll">
            {loading ? (
              <div className="table-placeholder">
                <div className="message">Loading recent letters...</div>
              </div>
            ) : recentLetters.length === 0 ? (
              <div className="table-placeholder">
                <div className="message">No letters currently need approval.</div>
              </div>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Letter ID</th>
                    <th>Patient ID</th>
                    <th>Doctor Name</th>
                    <th>Status</th>
                    <th>Details</th>
                    <th>Time</th>
                    <th>Date</th>
                    <th>Approved At</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {recentLetters.map((row) => (
                    <tr key={row.id}>
                      <td className="bold">{row.id}</td>
                      <td>{row.patientId}</td>
                      <td>{row.doctorName}</td>
                      <td>
                        <StatusBadge
                          status={row.status}
                          letterId={row.id}
                          onStatusChange={handleStatusChange}
                        />
                      </td>
                      <td>{row.details}</td>
                      <td>{row.time}</td>
                      <td>{row.date}</td>
                      <td
                        style={{
                          color: row.approvedAt ? "#22c55e" : "#999",
                          fontWeight: row.approvedAt ? 600 : 400,
                        }}
                      >
                        {row.approvedAt || "—"}
                      </td>
                      <td>
                        <button
                          className="btn-link"
                          onClick={() => navigate(`/review/${row.id}`)}
                          title="Review and edit letter"
                        >
                          📝 Review
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
