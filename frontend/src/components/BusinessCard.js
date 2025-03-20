import React from "react";
import { Link } from "react-router-dom";

const BusinessCard = ({ business }) => {
  return (
    <div className="col-md-4 mb-4">
      <div className="card">
        <div className="card-body">
          <h5 className="card-title">{business.name}</h5>
          <p className="card-text">{business.address}</p>
          <p className="card-text">{business.contact_info}</p>
          <Link to={`/business/${business.id}`} className="btn btn-primary">
            View Details
          </Link>
        </div>
      </div>
    </div>
  );
};

export default BusinessCard;
