import React from "react";
import { Link } from "react-router-dom";
import "./About.css";

const About = () => {
  return (
    <div className="about-container">
      <div className="about-background"></div>

      <div className="about-content">
        <header className="about-header">
          <h1>About Soweto Business Directory</h1>
        </header>

        <main className="about-main">
          <section className="about-section">
            <h2>Our Mission</h2>
            <p>
              Connecting the vibrant businesses of Soweto with the community
              since 2025. We're dedicated to promoting local entrepreneurship
              and making it easier for residents and visitors to discover
              authentic Soweto experiences.
            </p>
          </section>

          <section className="about-section">
            <h2>Features</h2>
            <div className="features-grid">
              <div className="feature-card">
                <h3>Search & Discover</h3>
                <p>Find businesses by name, category, or location</p>
              </div>
              <div className="feature-card">
                <h3>Verified Listings</h3>
                <p>All businesses are personally verified by our team</p>
              </div>
              <div className="feature-card">
                <h3>Community Focus</h3>
                <p>Supporting local economic growth</p>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2>Contact Us</h2>
            <p>
              Have questions or want to list your business?
              <br />
              Email:{" "}
              <a href="mailto:hello@sowetobusiness.co.za">
                hello@sowetobusiness.co.za
              </a>
              <br />
              Phone: <a href="tel:+27115551234">011 555 1234</a>
            </p>
          </section>

          <Link to="/" className="home-link">
            ← Back to Home
          </Link>
        </main>
      </div>
    </div>
  );
};

export default About;
