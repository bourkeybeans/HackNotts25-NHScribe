import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import NHScribeDashboard from "./NHScribeDashboard";
import NewLetter from "./NewLetter";
import Footer from "./Footer";

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<NHScribeDashboard />} />
          <Route path="/new-letter" element={<NewLetter />} />
        </Routes>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
