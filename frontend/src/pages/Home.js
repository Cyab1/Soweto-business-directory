import React, { useEffect, useState } from "react";
import { getBusinesses, getCategories } from "../services/api";
import SearchBar from "../components/SearchBar";
import BusinessCard from "../components/BusinessCard";
import "./Home.css";

const Home = () => {
  const [businesses, setBusinesses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [filteredBusinesses, setFilteredBusinesses] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const businessesData = await getBusinesses();
        const categoriesData = await getCategories();
        setBusinesses(businessesData);
        setCategories(categoriesData);
        setFilteredBusinesses(businessesData);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
    fetchData();
  }, []);

  const handleSearch = (query) => {
    const filtered = businesses.filter(
      (business) =>
        business.name.toLowerCase().includes(query.toLowerCase()) ||
        (business.category &&
          business.category.name.toLowerCase().includes(query.toLowerCase())),
    );
    setFilteredBusinesses(filtered);
  };

  return (
    <div className="sbd-home">
      <div className="sbd-hero">
        <div className="container">
          <h1 className="sbd-hero-title">Discover Soweto's Local Businesses</h1>
          <p className="sbd-hero-subtitle">
            Verified local businesses near you — support local, discover more.
          </p>
          <div className="sbd-searchbar-wrap">
            <SearchBar onSearch={handleSearch} />
          </div>
        </div>
      </div>

      <div className="container mt-5 mb-5">
        {filteredBusinesses.length === 0 ? (
          <p className="sbd-empty-state">No businesses found.</p>
        ) : (
          <div className="row">
            {filteredBusinesses.map((business) => (
              <BusinessCard key={business.id} business={business} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
