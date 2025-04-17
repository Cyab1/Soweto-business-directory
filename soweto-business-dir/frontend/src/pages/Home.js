import React, { useEffect, useState } from "react";
import { getBusinesses, getCategories } from "../services/api";
import SearchBar from "../components/SearchBar";
import BusinessCard from "../components/BusinessCard";
import "./Home.css";

// Mock business data
const mockBusinesses = [
  {
    id: 1001,
    name: "Vilakazi Restaurant",
    address: "Vilakazi Street, Orlando West",
    contact_info: "011 123 4567",
    category: { name: "Restaurant" },
    description: "Authentic South African cuisine",
  },
  {
    id: 1002,
    name: "Soweto Fashion House",
    address: "Mofolo Centre, Shop 12",
    contact_info: "011 234 5678",
    category: { name: "Clothing" },
    description: "Traditional and modern African attire",
  },
  {
    id: 1003,
    name: "Orlando Auto Repairs",
    address: "Chris Hani Road",
    contact_info: "011 345 6789",
    category: { name: "Automotive" },
    description: "Quality car repairs since 1995",
  },
];

const Home = () => {
  const [businesses, setBusinesses] = useState([]);
  const [filteredBusinesses, setFilteredBusinesses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const [businessesData] = await Promise.all([
          getBusinesses(),
          getCategories(),
        ]);
        // Combine API data with mock data
        setBusinesses([...businessesData, ...mockBusinesses]);
        setFilteredBusinesses([...businessesData, ...mockBusinesses]);
      } catch (error) {
        console.error("Error fetching data:", error);
        // Fallback to mock data if API fails
        setBusinesses(mockBusinesses);
        setFilteredBusinesses(mockBusinesses);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSearch = (query) => {
    const filtered = businesses.filter(
      (business) =>
        business.name.toLowerCase().includes(query.toLowerCase()) ||
        business.category?.name.toLowerCase().includes(query.toLowerCase())
    );
    setFilteredBusinesses(filtered);
  };

  return (
    <div className="home-container">
      {/* Background Image Layer */}
      <div className="home-background"></div>

      {/* Content Layer */}
      <div className="home-content">
        <header className="home-header">
          <h1 className="home-title">Soweto Business Directory</h1>
          <p className="home-subtitle">
            Find and support local businesses in your community
          </p>
        </header>

        <main className="home-main">
          <div className="search-container">
            <SearchBar onSearch={handleSearch} />
          </div>

          {isLoading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading businesses...</p>
            </div>
          ) : filteredBusinesses.length === 0 ? (
            <div className="empty-state">
              <img
                src="/images/no-results.svg"
                alt="No results found"
                className="empty-image"
              />
              <p className="empty-message">No businesses match your search</p>
            </div>
          ) : (
            <div className="business-grid">
              {filteredBusinesses.map((business) => (
                <BusinessCard key={business.id} business={business} />
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Home;
