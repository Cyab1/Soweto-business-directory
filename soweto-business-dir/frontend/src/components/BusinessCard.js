import React from "react";
import { Link } from "react-router-dom";
import "./BusinessCard.css"; // We'll create this CSS file

const BusinessCard = ({ business }) => {
  return (
    <div className="business-card">
      <div className="card-content">
        <h3 className="business-name">{business.name}</h3>
        <div className="business-details">
          <p className="business-address">
            <span className="icon">📍</span> {business.address}
          </p>
          <p className="business-contact">
            <span className="icon">📞</span> {business.contact_info}
          </p>
        </div>
        <Link to={`/business/${business.id}`} className="view-details-btn">
          View Details →
        </Link>
      </div>
    </div>
  );
};

export default BusinessCard;
