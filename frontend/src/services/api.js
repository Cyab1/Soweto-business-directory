import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api";

// Attach the JWT to every outgoing request automatically, if we have one.
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem("sbd_access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getBusinesses = async () => {
  const response = await axios.get(`${API_URL}/businesses/`);
  return response.data.results;
};

export const getCategories = async () => {
  const response = await axios.get(`${API_URL}/categories/`);
  return response.data.results;
};

export const getReviews = async (businessId) => {
  const response = await axios.get(
    `${API_URL}/reviews/?business=${businessId}`
  );
  return response.data.results;
};

export const getBusiness = async (id) => {
  const response = await axios.get(`${API_URL}/businesses/${id}/`);
  return response.data;
};

export const submitReview = async (businessId, review) => {
  const response = await axios.post(`${API_URL}/reviews/`, {
    ...review,
    business: businessId,
  });
  return response.data;
};

// --- Auth ---

export const registerUser = async (username, email, password) => {
  const response = await axios.post(`${API_URL}/register/`, {
    username,
    email,
    password,
  });
  return response.data;
};

export const loginUser = async (username, password) => {
  const response = await axios.post(`${API_URL}/token/`, {
    username,
    password,
  });
  return response.data; // { access, refresh }
};

export const getNearbyBusinesses = async (lat, lng, radiusKm = 5) => {
  const response = await axios.get(
    `${API_URL}/businesses/nearby/?lat=${lat}&lng=${lng}&radius_km=${radiusKm}`
  );
  return response.data.results;
};