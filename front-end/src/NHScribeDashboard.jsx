import React from "react";
import './NHScribeDashboard.css';
import Nhscribe from './assets/Nhscribe.png';


const topStats = [
  { title: "Current Queue", value: "0 pending", icon: "🕒" },
];

const recentLetters = [
{ id: "L2025-1023", patientId: "PT-4892", doctorName: "Dr. Sarah Lang", status: "Approved", details: "Blood Test - Full Panel", time: "09:30", date: "2025-10-25", approvedAt: "09:35" },
{ id: "L2025-1024", patientId: "PT-3421", doctorName: "Dr. Michael Harris", status: "Approved", details: "X-Ray - Chest", time: "10:15", date: "2025-10-25", approvedAt: "10:20" },
{ id: "L2025-1025", patientId: "PT-5678", doctorName: "Dr. Priya Nair", status: "Approved", details: "MRI - Brain", time: "11:00", date: "2025-10-25", approvedAt: "11:05" },
];

function Pill({ label, variant }) {
  return <span className={`pill ${variant || "default"}`}>{label}</span>;
}



function ApprovedBadge() {
  return <span className="badge success">✔ Approved</span>;
}

export default function NHScribeDashboard() {
  return (
    <div className="page">
      <header className="nav">
        <div className="container nav-inner">
          <div className="brand">
            <div className="Nhscribe"><img src={Nhscribe} alt="Nhscribe" className="Nhscribe" /></div>
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
      <br></br>
      <main className="container">
        <section className="stats">
          {topStats.map((s, i) => (
            <div className="card" key={i}>
              <div className="head">{s.title}</div>
              <div className="body">
                <div className="stat-value">{s.value}</div>
                <div className="stat-icon">{s.icon}</div>
              </div>
            </div>
          ))}
        </section>

        <section className="cta">
          <div>
            <h2>Ready to generate a new letter?</h2>
            <p>Create professional patient results letters in seconds with local AI processing</p>
          </div>
          <button className="btn" onClick={() => alert('New Letter')}>➕ New Letter</button>
        </section>

        <section className="table-wrap">
          <div className="table-head">Recent Letters</div>
          <div className="table-scroll">
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
                </tr>
              </thead>
              <tbody>
                {recentLetters.map((row) => (
                  <tr key={row.id}>
                    <td className="bold">{row.id}</td>
                    <td>{row.patientId}</td>
                    <td>{row.doctorName}</td>
                    <td><ApprovedBadge /></td>
                    <td>{row.details}</td>
                    <td>{row.time}</td>
                    <td>{row.date}</td>
                    <td>{row.approvedAt}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}
