import React from "react";
import "./Footer.css";

const Footer = () => {
  return (
    <footer className="sbd-footer">
      <div className="container">
        <p>&copy; 2026 Soweto Business Directory. All rights reserved.</p>
        <p>
          <a href="/about">About Us</a> | <a href="/contact">Contact</a> |{" "}
          <a href="/privacy">Privacy Policy</a>
        </p>
      </div>
    </footer>
  );
};

export default Footer;