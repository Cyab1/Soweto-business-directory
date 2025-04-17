import React from "react";
import { Link } from "react-router-dom";
import "./Footer.css"; // We'll create this CSS file

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-content">
          <p className="footer-copyright">
            &copy; 2025 Soweto Business Directory. All rights reserved.
          </p>
          <div className="footer-links">
            <Link to="/about" className="footer-link">
              About Us
            </Link>
            <span className="footer-divider">|</span>
            <Link to="/contact" className="footer-link">
              Contact
            </Link>
            <span className="footer-divider">|</span>
            <Link to="/privacy" className="footer-link">
              Privacy Policy
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
