import React from "react";
import "./Footer.css";

export default function Footer() {
  return (
    <footer className="global-footer">
      <div className="footer-left">
        <span className="secure">100% Local Processing - No Cloud Upload</span>
        <span className="divider">|</span>
      
        <span className="storage">Letters stored locally for 24hrs only</span>
      </div>
      <div className="footer-right">
        ⚙️ Powered by <span className="highlight">ARM Architecture</span>
      </div>
    </footer>
  );
}
