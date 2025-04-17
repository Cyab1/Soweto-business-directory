import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./Navbar.css"; // We'll create this CSS file

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-brand">
          <span className="logo-text">Soweto</span>
          <span className="logo-highlight">Business</span>
        </Link>

        <button
          className={`nav-toggle ${isOpen ? "active" : ""}`}
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle navigation"
        >
          <span className="hamburger"></span>
        </button>

        <nav className={`nav-links ${isOpen ? "active" : ""}`}>
          <Link to="/" className="nav-link" onClick={() => setIsOpen(false)}>
            Home
          </Link>

          <Link
            to="/about"
            className="nav-link"
            onClick={() => setIsOpen(false)}
          >
            About Us
          </Link>
          <Link to="/contact" className="nav-link">
            Contact Us
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Navbar;
