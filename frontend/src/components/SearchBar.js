import React, { useState } from "react";
import "./SearchBar.css";

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState("");

  const handleSearch = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <form onSubmit={handleSearch} className="sbd-searchbar-form">
      <input
        type="text"
        placeholder="Search businesses..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="sbd-search-input"
      />
      <button type="submit" className="sbd-search-btn">
        Search
      </button>
    </form>
  );
};

export default SearchBar;