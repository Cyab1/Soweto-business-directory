import React, { useState } from "react";
import { submitReview } from "../services/api";
import "./ReviewForm.css";

const ReviewForm = ({ businessId }) => {
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await submitReview(businessId, { rating, comment });
      alert("Review submitted successfully!");
      setRating(0);
      setComment("");
    } catch (error) {
      alert("Couldn't submit review — you may need to log in first.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="sbd-review-form">
      <div className="mb-3">
        <label className="sbd-form-label">Rating</label>
        <input
          type="number"
          min="1"
          max="5"
          value={rating}
          onChange={(e) => setRating(e.target.value)}
          className="form-control"
        />
      </div>
      <div className="mb-3">
        <label className="sbd-form-label">Comment</label>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          className="form-control"
        />
      </div>
      <button type="submit" className="sbd-btn">
        Submit Review
      </button>
    </form>
  );
};

export default ReviewForm;
