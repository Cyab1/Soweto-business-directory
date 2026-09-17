import React from "react";
import "./About.css";

const About = () => {
  return (
    <div className="container mt-5 mb-5 sbd-about">
      <h1 className="sbd-page-title">About SBD</h1>
      <p className="sbd-lead">
        Soweto Business Directory (SBD) helps you discover local businesses
        near you — even the ones you'd never have thought to search for.
      </p>

      <div className="sbd-about-section">
        <h2>Why "Verified" Matters</h2>
        <p>
          Every business marked <strong>✓ Verified</strong> on SBD has been
          checked by our team before it appears in your nearby feed. We're
          not just listing businesses — we're vouching for them, so you can
          walk into a place you've never heard of and feel confident you're
          somewhere safe and legitimate.
        </p>
      </div>

      <div className="sbd-about-section">
        <h2>Support Local, Discover More</h2>
        <p>
          Most directories only work if you already know what you're looking
          for. SBD works differently — it surfaces the local spaza shops,
          traders, and service providers around you, so discovering your
          next favourite local business doesn't depend on knowing it exists
          first.
        </p>
      </div>
    </div>
  );
};

export default About;