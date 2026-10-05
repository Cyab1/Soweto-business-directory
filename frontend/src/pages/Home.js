import React, { useEffect, useState } from "react";
import { getBusinesses, getNearbyBusinesses } from "../services/api";
import SearchBar from "../components/SearchBar";
import BusinessCard from "../components/BusinessCard";
import "./Home.css";

const Home = () => {
  const [businesses, setBusinesses] = useState([]);
  const [filteredBusinesses, setFilteredBusinesses] = useState([]);
  const [mode, setMode] = useState("loading");
  const [radiusKm, setRadiusKm] = useState(5);

  const loadNearby = (radius) => {
    setMode("loading");
    if (!navigator.geolocation) {
      loadAll();
      return;
    }
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords;
          const nearby = await getNearbyBusinesses(latitude, longitude, radius);
          setBusinesses(nearby);
          setFilteredBusinesses(nearby);
          setMode("nearby");
        } catch (error) {
          console.error("Error fetching nearby businesses:", error);
          loadAll();
        }
      },
      () => {
        setMode("denied");
        loadAll();
      },
    );
  };

  const loadAll = async () => {
    try {
      const all = await getBusinesses();
      setBusinesses(all);
      setFilteredBusinesses(all);
      setMode((current) => (current === "loading" ? "all" : current));
    } catch (error) {
      console.error("Error fetching businesses:", error);
    }
  };

  useEffect(() => {
    loadNearby(radiusKm);
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  const handleRadiusChange = (newRadius) => {
    setRadiusKm(newRadius);
    loadNearby(newRadius);
  };

  return (
    <div className="sbd-home">
      <div className="sbd-hero">
        <div className="sbd-container">
          <h1 className="sbd-hero-title">Discover Soweto's Local Businesses</h1>
          <p className="sbd-hero-subtitle">
            Verified local businesses near you — support local, discover more.
          </p>
          <div className="sbd-searchbar-wrap">
            <SearchBar onSearch={handleSearch} />
          </div>

          {mode === "nearby" && (
            <div className="sbd-radius-control">
              <span>Showing verified businesses within {radiusKm} km</span>
              <div className="sbd-radius-buttons">
                {[2, 5, 10, 25].map((r) => (
                  <button
                    key={r}
                    className={
                      "sbd-radius-btn" +
                      (r === radiusKm ? " sbd-radius-btn-active" : "")
                    }
                    onClick={() => handleRadiusChange(r)}
                  >
                    {r} km
                  </button>
                ))}
              </div>
            </div>
          )}

          {mode === "denied" && (
            <p className="sbd-location-note">
              Location access wasn't available, so we're showing all businesses
              instead.
            </p>
          )}
        </div>
      </div>

      <div className="sbd-container sbd-content">
        {mode === "loading" ? (
          <p className="sbd-empty-state">Finding businesses near you...</p>
        ) : filteredBusinesses.length === 0 ? (
          <p className="sbd-empty-state">
            {mode === "nearby"
              ? "No verified businesses found nearby — try a larger radius."
              : "No businesses found."}
          </p>
        ) : (
          <div className="sbd-grid">
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
