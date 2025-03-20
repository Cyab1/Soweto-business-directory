import React, { useState } from "react";
import { submitReview } from "../services/api";

const ReviewForm = ({ businessId }) => {
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    await submitReview(businessId, { rating, comment });
    alert("Review submitted successfully!");
    setRating(0);
    setComment("");
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-3">
        <label>Rating</label>
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
        <label>Comment</label>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          className="form-control"
        />
      </div>
      <button type="submit" className="btn btn-primary">
        Submit Review
      </button>
    </form>
  );
};

export default ReviewForm;
