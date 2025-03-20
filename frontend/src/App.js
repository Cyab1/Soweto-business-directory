import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import BusinessDetails from "./pages/BusinessDetails";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import "bootstrap/dist/css/bootstrap.min.css";
import "./index.css";

function App() {
  return (
    <Router>
      <div className="d-flex flex-column min-vh-100">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/business/:id" element={<BusinessDetails />} />
        </Routes>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
