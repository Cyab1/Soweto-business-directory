import React, { useState } from "react";
import "./About.css";

const Contact = () => {
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    // No backend contact endpoint yet — this just confirms the form works.
    setSubmitted(true);
  };

  return (
    <div className="container mt-5 mb-5 sbd-about">
      <h1 className="sbd-page-title">Contact Us</h1>
      <p className="sbd-lead">
        Have a question, or want to get your business verified? Reach out.
      </p>

      {submitted ? (
        <p style={{ color: "#1f5c5c", fontWeight: 600 }}>
          Thanks — we'll be in touch soon.
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="sbd-contact-form">
          <div className="mb-3">
            <label className="form-label">Name</label>
            <input type="text" className="form-control" required />
          </div>
          <div className="mb-3">
            <label className="form-label">Email</label>
            <input type="email" className="form-control" required />
          </div>
          <div className="mb-3">
            <label className="form-label">Message</label>
            <textarea className="form-control" rows="4" required></textarea>
          </div>
          <button type="submit" className="sbd-btn">
            Send Message
          </button>
        </form>
      )}
    </div>
  );
};

export default Contact;
