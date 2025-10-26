import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "./ReviewLetter.css";
import Nhscribe from "./assets/Nhscribe.png";
import { API_BASE_URL } from "./config";

function Pill({ label, variant }) {
  return <span className={`pill ${variant || "default"}`}>{label}</span>;
}

export default function ReviewLetter() {
  const { letterId } = useParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [letter, setLetter] = useState(null);
  const [content, setContent] = useState("");
  const [error, setError] = useState(null);
  const [saveMessage, setSaveMessage] = useState("");

  // Fetch letter data on mount
  useEffect(() => {
    async function fetchLetter() {
      try {
        const res = await fetch(`${API_BASE_URL}/letters/${letterId}`);
        if (!res.ok) {
          throw new Error("Letter not found");
        }
        const data = await res.json();
        setLetter(data);
        setContent(data.content || "");
      } catch (err) {
        console.error("Error fetching letter:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchLetter();
  }, [letterId]);

  // Auto-save functionality
  useEffect(() => {
    if (!letter || content === letter.content) return;

    const timeoutId = setTimeout(() => {
      handleSave(true); // silent auto-save
    }, 2000);

    return () => clearTimeout(timeoutId);
  }, [content, letter]);

  async function handleSave(silent = false) {
    if (!silent) setSaving(true);
    
    try {
      const res = await fetch(`${API_BASE_URL}/letters/${letterId}/content`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ content }),
      });

      if (!res.ok) throw new Error("Failed to save");
      
      const data = await res.json();
      setLetter(data);
      
      if (!silent) {
        setSaveMessage("✓ Saved successfully");
        setTimeout(() => setSaveMessage(""), 3000);
      }
    } catch (err) {
      console.error("Error saving:", err);
      if (!silent) {
        setSaveMessage("✗ Save failed");
        setTimeout(() => setSaveMessage(""), 3000);
      }
    } finally {
      if (!silent) setSaving(false);
    }
  }

  async function handleDownloadPDF() {
    try {
      const res = await fetch(`${API_BASE_URL}/letters/${letterId}/pdf`);
      if (!res.ok) throw new Error("Failed to generate PDF");
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `letter_${letterId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error("Error downloading PDF:", err);
      alert("Failed to download PDF");
    }
  }

  function handlePrint() {
    window.print();
  }

  if (loading) {
    return (
      <div className="page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading letter...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button className="btn" onClick={() => navigate("/")}>
            ← Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <header className="nav">
        <div className="container nav-inner">
          <div className="brand">
            <img src={Nhscribe} alt="Nhscribe" className="Nhscribe" />
            <div>
              <div className="title">NHScribe</div>
              <div className="subtitle">Review & Edit Letter</div>
            </div>
          </div>
          <div className="nav-actions">
            <Pill label="Offline AI Active" variant="success" />
            <Pill label="Raspberry Pi 5" variant="muted" />
          </div>
        </div>
      </header>

      <main className="container review-container">
        {/* Header Section */}
        <div className="review-header">
          <button className="btn-secondary" onClick={() => navigate("/")}>
            ← Back to Dashboard
          </button>
          
          <div className="review-actions">
            {saveMessage && (
              <span className={`save-message ${saveMessage.includes("✓") ? "success" : "error"}`}>
                {saveMessage}
              </span>
            )}
            <button 
              className="btn-secondary" 
              onClick={() => handleSave(false)}
              disabled={saving}
            >
              {saving ? "Saving..." : "Save"}
            </button>
            <button className="btn-secondary" onClick={handlePrint}>
              Print
            </button>
            <button className="btn" onClick={handleDownloadPDF}>
              Download PDF
            </button>
          </div>
        </div>

        {/* Letter Info Card */}
        <div className="letter-info-card">
          <div className="info-row">
            <div className="info-item">
              <span className="info-label">Letter ID:</span>
              <span className="info-value">{letter.letterUid}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Patient:</span>
              <span className="info-value">{letter.patientName}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Doctor:</span>
              <span className="info-value">{letter.doctorName}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Status:</span>
              <span className={`status-badge ${letter.status.toLowerCase()}`}>
                {letter.status}
              </span>
            </div>
          </div>
          <div className="info-row">
            <div className="info-item">
              <span className="info-label">Created:</span>
              <span className="info-value">{letter.createdAt}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Details:</span>
              <span className="info-value">{letter.details}</span>
            </div>
          </div>
        </div>

        {/* Letter Editor */}
        <div className="letter-editor-card">
          <div className="editor-header">
            <h2>Letter Content</h2>
            <p className="editor-hint">
              Edit the letter content below. Changes are auto-saved after 2 seconds of inactivity.
            </p>
          </div>
          
          <div className="letter-document">
            {/* Letterhead */}
            <div className="letterhead">
              <div className="sender-info">NHS</div>
              <div className="sender-address">
                Computer Science Building<br />
                Jubilee Campus<br />
                University of Nottingham<br />
              </div>
            </div>

            {/* Date */}
            <div className="letter-date">
              {new Date().toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </div>

            {/* Recipient */}
            <div className="letter-recipient">
              Dear {letter.patientName},
            </div>

            {/* Editable Content */}
            <textarea
              className="letter-content-editor"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Enter letter content here..."
            />

            {/* Signature */}
            <div className="letter-signature">
              <div className="signature-line">Sincerely,</div>
              <div className="signature-name">{letter.doctorName}</div>
              <div className="signature-title">NHS Medical Professional</div>
            </div>
          </div>
        </div>

        {/* Action Buttons (Bottom) */}
        <div className="bottom-actions">
          <button className="btn-secondary" onClick={() => navigate("/")}>
            ← Back to Dashboard
          </button>
          <div className="action-group">
            <button 
              className="btn-secondary" 
              onClick={() => handleSave(false)}
              disabled={saving}
            >
              {saving ? "Saving..." : "Save Changes"}
            </button>
            <button className="btn" onClick={handleDownloadPDF}>
              Download PDF
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

