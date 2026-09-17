import React from "react";
import { Link } from "react-router-dom";
import "./BusinessCard.css";

const PLACEHOLDER_IMAGE =
  "https://via.placeholder.com/400x220/2E6E6E/FDF6E3?text=SBD";

const BusinessCard = ({ business }) => {
  return (
    <div className="col-md-4 mb-4">
      <div className="sbd-card">
        <div className="sbd-card-image-wrap">
          <img
            src={business.image || PLACEHOLDER_IMAGE}
            alt={business.name}
            className="sbd-card-image"
          />
          {business.is_verified && (
            <span className="sbd-verified-badge">✓ Verified</span>
          )}
        </div>
        <div className="sbd-card-body">
          {business.category && (
            <span className="sbd-category-pill">{business.category.name}</span>
          )}
          <h5 className="sbd-card-title">{business.name}</h5>
          <p className="sbd-card-text">{business.address}</p>
          <p className="sbd-card-text">{business.contact_info}</p>
          <Link to={`/business/${business.id}`} className="sbd-btn">
            View Details
          </Link>
        </div>
      </div>
    </div>
  );
};

export default BusinessCard;