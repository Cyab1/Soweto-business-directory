import React, { useEffect, useState } from "react";
import { getBusinesses, getCategories } from "../services/api";
import SearchBar from "../components/SearchBar";
import BusinessCard from "../components/BusinessCard";

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
        setFilteredBusinesses(businessesData); // Initialize filtered businesses with all businesses
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
        business.category.name.toLowerCase().includes(query.toLowerCase())
    );
    setFilteredBusinesses(filtered);
  };

  return (
    <div className="container mt-5">
      <h1>Soweto Business Directory</h1>
      <SearchBar onSearch={handleSearch} />
      <div className="row">
        {filteredBusinesses.map((business) => (
          <BusinessCard key={business.id} business={business} />
        ))}
      </div>
    </div>
  );
};

export default Home;
