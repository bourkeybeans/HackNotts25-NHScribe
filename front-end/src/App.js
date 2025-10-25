import React from 'react';
import NHScribeDashboard from './NHScribeDashboard';
import Footer from "./Footer";
import NewLetterDashboard from "./NewLetter";

function App() {
  return (
    <div className="App">
      <NHScribeDashboard />
      <Footer />
      <NewLetterDashboard />
    </div>
  );
}

export default App;
