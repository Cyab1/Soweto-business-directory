import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api"; // Replace with your backend URL

// Fetch all businesses
export const getBusinesses = async () => {
  const response = await axios.get(`${API_URL}/businesses/`);
  return response.data;
};

// Fetch all Categories
export const getCategories = async () => {
  const response = await axios.get(`${API_URL}/categories/`);
  return response.data;
};

// Fetch reviews for a specific business
export const getReviews = async (businessId) => {
  const response = await axios.get(
    `${API_URL}/reviews/?business=${businessId}`
  );
  return response.data;
};

// Fetch a single business by ID
export const getBusiness = async (id) => {
  const response = await axios.get(`${API_URL}/businesses/${id}/`);
  return response.data;
};

// Submit a review for a business
export const submitReview = async (businessId, review) => {
  const response = await axios.post(`${API_URL}/reviews/`, {
    ...review,
    business: businessId,
  });
  return response.data;
};
